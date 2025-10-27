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

# Global service instances
chess_engine_service = None
tactical_analysis_service = None
nlp_explanation_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize chess engine, tactical classifier, and NLP explanation service on startup"""
    global chess_engine_service, tactical_analysis_service, nlp_explanation_service
    
    # Initialize Stockfish engine
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
    
    # Initialize tactical ML classifier (Phase 2)
    try:
        from app.services.tactical_analysis import TacticalAnalysisService
        
        tactical_analysis_service = TacticalAnalysisService()
        
        if tactical_analysis_service.is_available and tactical_analysis_service.classifier:
            print(f"[SUCCESS] Tactical classifier initialized with {len(tactical_analysis_service.classifier.theme_names)} themes!")
        else:
            print("[WARNING] Tactical classifier not available (model not trained yet)")
    except Exception as e:
        print(f"[ERROR] Failed to initialize tactical classifier: {e}")
        tactical_analysis_service = None
    
    # Initialize NLP explanation service (Phase 3)
    try:
        from app.services.nlp_explanation import NLPExplanationService
        
        # Use the fine-tuned model
        nlp_explanation_service = NLPExplanationService(model_type="t5", model_name="models/chess_t5_finetuned")
        await nlp_explanation_service.initialize()
        
        if nlp_explanation_service.is_available:
            print("[SUCCESS] NLP explanation service initialized successfully!")
        else:
            print("[WARNING] NLP explanation service not available (using fallback explanations)")
    except Exception as e:
        print(f"[ERROR] Failed to initialize NLP explanation service: {e}")
        nlp_explanation_service = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global chess_engine_service, nlp_explanation_service
    
    if chess_engine_service:
        await chess_engine_service.cleanup()
    
    if nlp_explanation_service:
        await nlp_explanation_service.cleanup()

@app.get("/")
async def root():
    return {"message": "Simple test server", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Test server is working"}

def detect_opening(fen: str, pv_moves: list) -> dict:
    """Detect chess opening from FEN and principal variation"""
    try:
        import chess
        
        # Create board from FEN
        board = chess.Board(fen)
        
        # Count moves to determine if we're in opening
        fen_parts = fen.split()
        move_number = int(fen_parts[5]) if len(fen_parts) > 5 else 1
        halfmove_clock = int(fen_parts[4]) if len(fen_parts) > 4 else 0
        
        # Only detect openings in early game (first 10 moves)
        if move_number > 10:
            return {"name": None, "eco": None}
        
        # Get the position's move history from PV if available
        moves = []
        temp_board = chess.Board()
        
        # Try to reconstruct game from starting position
        # This is a simplified approach - for full opening detection,
        # you'd need an opening book database
        
        # Common opening patterns based on piece positions and moves
        pieces_str = fen.split()[0]
        
        # Check for common openings based on pawn structure and piece placement
        # Check for Queen's Pawn openings (d4 or d5 pawn)
        d4_piece = board.piece_at(chess.D4)
        d5_piece = board.piece_at(chess.D5)
        e4_piece = board.piece_at(chess.E4)
        e5_piece = board.piece_at(chess.E5)
        c5_piece = board.piece_at(chess.C5)
        
        # Check for d4 openings
        if d4_piece and d4_piece.piece_type == chess.PAWN and d4_piece.color == chess.WHITE:
            c4_piece = board.piece_at(chess.C4)
            f6_piece = board.piece_at(chess.F6)
            
            if c4_piece and c4_piece.piece_type == chess.PAWN and c4_piece.color == chess.WHITE:
                return {"name": "Queen's Gambit", "eco": "D06"}
            elif f6_piece and f6_piece.piece_type == chess.KNIGHT and f6_piece.color == chess.BLACK:
                return {"name": "Indian Defense", "eco": "E00"}
            else:
                return {"name": "Queen's Pawn Opening", "eco": "D00"}
        
        # Check for e4 openings
        if e4_piece and e4_piece.piece_type == chess.PAWN and e4_piece.color == chess.WHITE:
            if e5_piece and e5_piece.piece_type == chess.PAWN and e5_piece.color == chess.BLACK:
                f3_piece = board.piece_at(chess.F3)
                c6_knight = board.piece_at(chess.C6)
                
                if f3_piece and f3_piece.piece_type == chess.KNIGHT and f3_piece.color == chess.WHITE:
                    if c6_knight and c6_knight.piece_type == chess.KNIGHT and c6_knight.color == chess.BLACK:
                        return {"name": "Ruy Lopez", "eco": "C60"}
                    else:
                        return {"name": "King's Pawn Opening", "eco": "C20"}
                return {"name": "King's Pawn Game", "eco": "C20"}
            elif c5_piece and c5_piece.piece_type == chess.PAWN and c5_piece.color == chess.BLACK:
                return {"name": "Sicilian Defense", "eco": "B20"}
            elif board.piece_at(chess.E6) and board.piece_at(chess.E6).piece_type == chess.PAWN:
                return {"name": "French Defense", "eco": "C00"}
            elif board.piece_at(chess.C6) and board.piece_at(chess.C6).piece_type == chess.PAWN:
                return {"name": "Caro-Kann Defense", "eco": "B10"}
            else:
                return {"name": "King's Pawn Opening", "eco": "C20"}
        
        # English Opening
        c4_piece = board.piece_at(chess.C4)
        if c4_piece and c4_piece.piece_type == chess.PAWN and c4_piece.color == chess.WHITE and not d4_piece:
            return {"name": "English Opening", "eco": "A10"}
        
        # Réti Opening
        f3_piece = board.piece_at(chess.F3)
        g1_piece = board.piece_at(chess.G1)
        if f3_piece and f3_piece.piece_type == chess.KNIGHT and f3_piece.color == chess.WHITE and not g1_piece:
            return {"name": "Réti Opening", "eco": "A04"}
        
        # Default for opening phase
        if move_number <= 3:
            return {"name": "Opening Position", "eco": None}
        
        return {"name": None, "eco": None}
        
    except Exception as e:
        return {"name": None, "eco": None}

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
    
    # Determine position type based on FEN and piece analysis
    position_type = "middlegame"  # Default to middlegame instead of opening
    
    # Check if it's the starting position
    if "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR" in fen:
        position_type = "starting_position"
    else:
        # Analyze the position to determine game phase
        try:
            import chess
            board = chess.Board(fen)
            
            # Count pieces to determine game phase
            piece_count = len(board.piece_map())
            queens = len([p for p in board.piece_map().values() if p.piece_type == chess.QUEEN])
            
            # Count pawns to determine structure
            pawns = len([p for p in board.piece_map().values() if p.piece_type == chess.PAWN])
            
            # Count minor pieces (knights and bishops)
            minor_pieces = len([p for p in board.piece_map().values() if p.piece_type in [chess.KNIGHT, chess.BISHOP]])
            
            # Get move number for position type determination
            move_number = 0
            if len(fen_parts) > 5:
                try:
                    move_number = int(fen_parts[5])
                except (ValueError, IndexError):
                    move_number = 0
            
            # Determine position type based on piece count and structure
            if piece_count <= 12:  # Very few pieces left
                position_type = "endgame"
            elif piece_count <= 20 or queens == 0:  # Few pieces or no queens
                position_type = "endgame"
            elif piece_count <= 24 and minor_pieces <= 4:  # Reduced material
                position_type = "endgame"
            elif piece_count >= 30 and pawns >= 12 and move_number <= 8:  # Many pieces and pawns in early game
                position_type = "opening"
            elif piece_count >= 24:  # Good amount of pieces
                position_type = "middlegame"
            else:
                position_type = "middlegame"
            
            # Debug: Print position analysis
            print(f"[DEBUG] Position analysis: pieces={piece_count}, queens={queens}, pawns={pawns}, minor={minor_pieces}, type={position_type}")
                
            # Override with move number only if piece analysis suggests endgame
            if len(fen_parts) > 5:
                try:
                    move_number = int(fen_parts[5])
                    print(f"[DEBUG] Move number: {move_number}, current type: {position_type}")
                    if move_number > 50:
                        position_type = "endgame"
                    elif move_number > 25:
                        position_type = "middlegame"
                    # Don't force opening for early moves - let piece analysis decide
                except (ValueError, IndexError):
                    pass  # Keep the piece-based analysis
                    
        except Exception:
            # Fallback to move number analysis
            if len(fen_parts) > 5:
                try:
                    move_number = int(fen_parts[5])
                    if move_number > 40:
                        position_type = "endgame"
                    elif move_number > 20:
                        position_type = "middlegame"
                except (ValueError, IndexError):
                    position_type = "opening"
    
    # Initialize opening_info at function level
    opening_info = {"name": None, "eco": None}
    
    # Analyze the actual chess position
    try:
        import chess
        import chess.engine
        # Create board from FEN
        board = chess.Board(fen)
        
        # Try to use Stockfish for better analysis
        stockfish_analysis = None
        if chess_engine_service and chess_engine_service.is_initialized:
            try:
                stockfish_analysis = await chess_engine_service.analyze_position(fen, depth=20)
            except Exception as e:
                stockfish_analysis = None
        
        # Use ML Tactical Classifier for enhanced tactical detection (Phase 2)
        ml_tactical_themes = []
        if tactical_analysis_service and tactical_analysis_service.is_available:
            try:
                tactical_result = await tactical_analysis_service.analyze_tactics(board, threshold=0.3)
                if tactical_result.get('available') and tactical_result.get('themes'):
                    ml_tactical_themes = tactical_result['themes']
            except Exception as e:
                pass  # ML analysis failed, continue without it
        
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
            
            # Generate explanation using improved fallback system
            try:
                explanation = nlp_explanation_service._fallback_explanation(
                    move_san=san_move,
                    position_eval={
                        'score': best_move_info['score'],
                        'position_type': position_type,
                        'material_balance': stockfish_analysis.get('evaluation', {}).get('material_balance', {})
                    },
                    tactical_themes=[theme['theme'] for theme in ml_tactical_themes] if ml_tactical_themes else []
                )
            except Exception as e:
                print(f"[WARNING] Explanation generation failed: {e}, using simple fallback")
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
        
        # Add ML-detected tactical themes to motifs
        if ml_tactical_themes:
            for theme_info in ml_tactical_themes:
                theme_name = theme_info['theme']
                if theme_name not in tactical_motifs:
                    tactical_motifs.append(theme_name)
        
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
    
    # Detect opening if in opening phase
    if position_type == "opening" and best_moves_response:
        pv_moves = best_moves_response[0].get('pv', [])
        opening_info = detect_opening(fen, pv_moves)
    
    return {
        "fen": fen,
        "best_moves": best_moves_response,
        "opening_info": opening_info,
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
        "ml_tactical_analysis": {
            "available": len(ml_tactical_themes) > 0,
            "themes": ml_tactical_themes,
            "model": "PyTorch CNN (Phase 2)" if ml_tactical_themes else None
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
