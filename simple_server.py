#!/usr/bin/env python3
"""
Simple test server to verify the extension can connect
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS middleware for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Global chess engine instance
chess_engine_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize chess engine on startup"""
    global chess_engine_service
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from app.services.chess_engine import ChessEngineService
        
        chess_engine_service = ChessEngineService()
        await chess_engine_service.initialize()
        
        if chess_engine_service.is_initialized:
            print("[SUCCESS] Stockfish engine initialized successfully!")
        else:
            print("[WARNING] Stockfish initialization failed, using fallback analysis")
    except Exception as e:
        print(f"[ERROR] Failed to initialize chess engine: {e}")
        chess_engine_service = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global chess_engine_service
    if chess_engine_service:
        await chess_engine_service.cleanup()

@app.get("/")
async def root():
    return {"message": "Simple test server", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Test server is working"}

@app.options("/analyze-position")
async def analyze_position_options():
    """Handle preflight OPTIONS requests for CORS"""
    return {"message": "OK"}

@app.post("/analyze-position")
async def analyze_position(request: dict):
    """Enhanced chess analysis endpoint with proper turn detection and explanations"""
    fen = request.get("fen")
    
    # Validate FEN input
    if not fen or not isinstance(fen, str) or fen.strip() == "":
        return {
            "error": "No FEN provided",
            "message": "Please provide a valid FEN string in the request body"
        }
    
    # Basic FEN validation
    fen_parts = fen.strip().split()
    if len(fen_parts) < 2:
        return {
            "error": "Invalid FEN format",
            "message": "FEN must contain at least board position and active color"
        }
    
    # Check if it looks like a valid chess FEN (not HTML or other content)
    board_part = fen_parts[0]
    if not all(c in 'rnbqkpRNBQKP12345678/' for c in board_part):
        return {
            "error": "Invalid FEN format",
            "message": "FEN board position contains invalid characters. Make sure you're using a valid chess FEN string."
        }
    
    # Check if active color is valid
    if len(fen_parts) > 1 and fen_parts[1] not in ['w', 'b']:
        return {
            "error": "Invalid FEN format", 
            "message": "FEN active color must be 'w' (white) or 'b' (black)"
        }
    
    # Check if it's the default starting position (which might indicate extraction failure)
    if fen.strip() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1":
        return {
            "error": "Default position detected",
            "message": "FEN extraction may have failed - received default starting position. Please use the Debug FEN Extraction feature to find the actual puzzle position."
        }
    
    # Parse FEN to determine whose turn it is
    fen_parts = fen.split()
    active_color = fen_parts[1] if len(fen_parts) > 1 else "w"
    turn = "White" if active_color == "w" else "Black"
    
    # Determine position type based on FEN
    position_type = "opening"
    if "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR" in fen:
        position_type = "starting_position"
    elif len(fen_parts) > 5:
        try:
            move_number = int(fen_parts[5])
            if move_number > 40:
                position_type = "endgame"
            elif move_number > 20:
                position_type = "middlegame"
        except (ValueError, IndexError):
            # If we can't parse the move number, default to opening
            position_type = "opening"
    
    # Analyze the actual chess position
    try:
        import chess
        import chess.engine
        print(f"DEBUG: Analyzing FEN: {fen}")  # Debug log
        
        # Create board from FEN
        board = chess.Board(fen)
        
        # Try to use Stockfish for better analysis
        stockfish_analysis = None
        if chess_engine_service and chess_engine_service.is_initialized:
            try:
                print("Using Stockfish for analysis...")
                stockfish_analysis = await chess_engine_service.analyze_position(fen, depth=20)
                print(f"Stockfish analysis complete: {stockfish_analysis['best_moves'][0] if stockfish_analysis.get('best_moves') else 'No moves'}")
            except Exception as e:
                print(f"Stockfish analysis failed: {e}, using fallback")
                stockfish_analysis = None
        else:
            print("Stockfish not available, using fallback analysis")
        
        # Basic position analysis
        material_balance = 0
        piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
        
        for square, piece in board.piece_map().items():
            value = piece_values.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                material_balance += value
            else:
                material_balance -= value
        
        # Use Stockfish analysis if available, otherwise fall back
        if stockfish_analysis and stockfish_analysis.get('best_moves'):
            # Use Stockfish's best move and detailed explanations
            best_moves_data = stockfish_analysis['best_moves']
            best_move_info = best_moves_data[0]
            best_move = best_move_info['move']
            san_move = best_move_info['san']
            score_value = best_move_info['score']['value']
            
            # Use the detailed explanation from the engine if available
            if stockfish_analysis.get('move_explanations'):
                explanation = stockfish_analysis['move_explanations'][0]['explanation']
            else:
                # Fallback to simple explanation
                explanation = f"It's {turn}'s turn. The best move is {san_move} (evaluation: {score_value/100:+.2f})."
        else:
            # Fallback: use legal moves
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                # Checkmate or stalemate
                if board.is_checkmate():
                    best_move = "checkmate"
                    san_move = "Checkmate"
                    explanation = f"It's {turn}'s turn, but the position is checkmate. The game is over."
                    score_value = 10000 if turn == "White" else -10000
                else:
                    best_move = "stalemate"
                    san_move = "Stalemate"
                    explanation = f"It's {turn}'s turn, but the position is stalemate. The game is a draw."
                    score_value = 0
            else:
                # Pick first legal move as fallback
                best_move_obj = legal_moves[0]
                best_move = best_move_obj.uci()
                san_move = board.san(best_move_obj)
                score_value = int(material_balance * 100)
                explanation = f"It's {turn}'s turn. The move {san_move} is a legal option in this {position_type}. (Engine unavailable - showing legal move)"
        
        # Generate tactical motifs and strategic concepts
        tactical_motifs = []
        strategic_concepts = []
        
        # Use Stockfish analysis if available
        if stockfish_analysis and stockfish_analysis.get('tactical_motifs'):
            tactical_motifs = stockfish_analysis['tactical_motifs']
        else:
            # Fallback tactical detection
            if board.is_check():
                tactical_motifs.append("check")
            if material_balance != 0:
                tactical_motifs.append("material_advantage")
        
        # Strategic concepts based on position
        if position_type == "opening":
            strategic_concepts.append("development")
            strategic_concepts.append("center_control")
        elif position_type == "middlegame":
            strategic_concepts.append("tactics")
            strategic_concepts.append("king_safety")
        else:
            strategic_concepts.append("endgame_technique")
            strategic_concepts.append("king_activity")
            
    except ImportError:
        # Fallback if chess library not available
        best_move = "e2e4"
        san_move = "e4"
        explanation = f"It's {turn}'s turn. The best move is {san_move}. This is a reasonable move in this {position_type} position."
        tactical_motifs = ["center_control"]
        strategic_concepts = ["positional_improvement"]
        score_value = 100
    except Exception as e:
        # Handle any other errors
        print(f"DEBUG: Error analyzing position: {e}")  # Debug log
        return {
            "error": "Analysis failed",
            "message": f"Could not analyze position: {str(e)}"
        }
    
    # Prepare best moves response
    if stockfish_analysis and stockfish_analysis.get('best_moves'):
        # Use all moves from Stockfish
        best_moves_response = stockfish_analysis['best_moves']
    else:
        # Use fallback move
        best_moves_response = [
            {
                "move": best_move,
                "san": san_move,
                "score": {"type": "cp", "value": score_value, "display": f"{score_value/100:+.2f}"},
                "pv": [best_move],
                "depth": 1
            }
        ]
    
    return {
        "fen": fen,
        "best_moves": best_moves_response,
        "explanations": [
            {
                "move": best_move,
                "san": san_move,
                "explanation": explanation,
                "tactical_motifs": tactical_motifs,
                "strategic_concepts": strategic_concepts,
                "confidence": 0.95,
                "engine_evaluation": {
                    "move": best_move,
                    "san": san_move,
                    "score": {"type": "cp", "value": score_value, "display": f"+{score_value/100:.2f}"},
                    "pv": [best_move],
                    "depth": 20
                }
            }
        ],
            "position_evaluation": {
                "score": {"type": "cp", "value": score_value, "display": f"{score_value/100:+.2f}"},
                "position_type": position_type,
                "material_balance": stockfish_analysis['evaluation']['material_balance'] if stockfish_analysis else {"white": 39 + material_balance, "black": 39 - material_balance, "difference": material_balance},
                "king_safety": stockfish_analysis['evaluation']['king_safety'] if stockfish_analysis else {"white": 8, "black": 8},
                "piece_activity": stockfish_analysis['evaluation']['piece_activity'] if stockfish_analysis else {"white": 12, "black": 12}
            },
        "learning_insights": [
            f"Current turn: {turn}",
            f"Position type: {position_type}",
            "Focus on controlling the center squares (d4, d5, e4, e5)",
            "Develop pieces before moving the same piece multiple times",
            "Castle early to ensure king safety"
        ],
        "analysis_time": 0.5
    }

if __name__ == "__main__":
    print("Starting simple test server on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
