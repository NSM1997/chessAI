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
llm_explanation_service = None
board_analyzer = None
move_comparator = None

@app.on_event("startup")
async def startup_event():
    """Initialize chess engine, tactical classifier, board analyzer, and LLM explanation service on startup"""
    global chess_engine_service, tactical_analysis_service, llm_explanation_service, board_analyzer, move_comparator
    
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
    
    # Initialize Board Analyzer (Phase 3: Path B)
    try:
        from app.services.board_analyzer import BoardAnalyzer
        
        board_analyzer = BoardAnalyzer()
        print("[SUCCESS] Board analyzer initialized successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to initialize board analyzer: {e}")
        board_analyzer = None
    
    # Initialize Move Comparator
    try:
        from app.services.move_comparator import MoveComparator
        
        move_comparator = MoveComparator()
        print("[SUCCESS] Move comparator initialized successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to initialize move comparator: {e}")
        move_comparator = None
    
    # Initialize LLM Explanation Service (Phase 3: Path B)
    # Smart provider selection: OpenAI → Ollama → Fallback
    try:
        from app.services.llm_explanation import LLMExplanationService
        import os
        
        llm_explanation_service = None
        
        # Try 1: OpenAI GPT-4 (if API key available)
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("[INFO] OpenAI API key found, testing GPT-4o (best model)...")
            try:
                # Use GPT-4o (best balance of quality, speed, and cost)
                llm_explanation_service = LLMExplanationService(provider="openai-gpt4", api_key=api_key)
                success = await llm_explanation_service.initialize()
                
                if not success:
                    raise Exception("OpenAI initialization failed")
                    
                print("[SUCCESS] OpenAI initialized, ready to use!")
                    
            except Exception as e:
                print(f"[WARNING] OpenAI GPT-4 failed: {e}")
                if "insufficient_quota" in str(e) or "429" in str(e):
                    print("[INFO] Quota exceeded - falling back to local LLM")
                llm_explanation_service = None
        
        # Try 2: Ollama (local LLM)
        if llm_explanation_service is None:
            print("[INFO] Trying Ollama local LLM...")
            try:
                llm_explanation_service = LLMExplanationService(provider="ollama-local")
                success = await llm_explanation_service.initialize()
                
                if success:
                    print("[SUCCESS] Ollama local LLM initialized successfully!")
                else:
                    raise Exception("Ollama initialization failed")
                    
            except Exception as e:
                print(f"[WARNING] Ollama failed: {e}")
                llm_explanation_service = None
        
        # Try 3: Intelligent fallback (rule-based with board analysis)
        if llm_explanation_service is None:
            print("[INFO] Using intelligent fallback mode (context-aware rules)")
            llm_explanation_service = LLMExplanationService(provider="fallback")
            await llm_explanation_service.initialize()
            print("[SUCCESS] Fallback explanation system initialized!")
            
    except Exception as e:
        print(f"[ERROR] Critical failure in LLM service initialization: {e}")
        print("[FALLBACK] Creating minimal explanation service")
        try:
            llm_explanation_service = LLMExplanationService(provider="fallback")
            await llm_explanation_service.initialize()
        except:
            llm_explanation_service = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global chess_engine_service, llm_explanation_service
    
    if chess_engine_service:
        await chess_engine_service.cleanup()
    
    if llm_explanation_service:
        await llm_explanation_service.cleanup()

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
            
            # Get move number from board object (more reliable than FEN parsing)
            move_number = board.fullmove_number
            
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
            
            # Override with move number only if piece analysis suggests endgame
            if move_number > 50:
                position_type = "endgame"
            elif move_number > 25:
                position_type = "middlegame"
            # Don't force opening for early moves - let piece analysis decide
                    
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
            
            # Generate intelligent explanation using Board Analyzer + LLM (Phase 3: Path B)
            try:
                if board_analyzer and llm_explanation_service:
                    # Step 1: Analyze board position
                    board_analysis = board_analyzer.analyze_position(board)
                    
                    # Step 2: Analyze move impact
                    move_obj = chess.Move.from_uci(best_move)
                    move_impact = board_analyzer.analyze_move_impact(board, move_obj)
                    
                    # Step 3: Generate context-aware explanation
                    explanation = await llm_explanation_service.generate_explanation(
                        fen=fen,
                        move_san=san_move,
                        move_uci=best_move,
                        board_analysis=board_analysis,
                        move_impact=move_impact,
                        stockfish_eval=best_move_info['score'],
                        tactical_themes=[theme['theme'] for theme in ml_tactical_themes] if ml_tactical_themes else [],
                        position_type=position_type
                    )
                    
                    print(f"[INFO] Generated intelligent explanation for {san_move}")
                else:
                    # Simple fallback without exposing numeric engine score
                    adv = "a strong" if abs(score_value) > 150 else "a slight"
                    explanation = f"It's {turn}'s turn. The best move is {san_move}, giving {adv} advantage."
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
        tactical_motifs: list[str] = []
        strategic_concepts: list[str] = []
        
        # Use Stockfish analysis if available
        if stockfish_analysis and stockfish_analysis.get('tactical_motifs'):
            tactical_motifs = list(stockfish_analysis['tactical_motifs'])
        else:
            # Fallback tactical detection
            if board.is_check():
                tactical_motifs.append("check")
            if material_balance != 0:
                tactical_motifs.append("material_advantage")
        
        # Add ML-detected tactical themes to motifs (ensemble-based, already sorted by confidence)
        if ml_tactical_themes:
            for theme_info in ml_tactical_themes:
                theme_name = theme_info['theme']
                if theme_name not in tactical_motifs:
                    tactical_motifs.append(theme_name)
        
        # Limit motifs we expose in the API/extension UI to the top 2 for clarity
        if len(tactical_motifs) > 2:
            tactical_motifs = tactical_motifs[:2]
        
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

@app.options("/analyze-move")
async def analyze_move_options():
    """Handle preflight OPTIONS requests for CORS"""
    return {"message": "OK"}

@app.post("/analyze-move")
async def analyze_move(request: dict):
    """
    Analyze a user's move and compare it to the best move.
    
    Request:
    {
        "fen_before": "position before the move",
        "fen_after": "position after the move",
        "user_move": "e2e4" (optional, UCI format)
    }
    
    Response:
    {
        "user_move": {...},
        "best_move": {...},
        "comparison": {...},
        "explanation": "..."
    }
    """
    fen_before = request.get("fen_before")
    fen_after = request.get("fen_after")
    user_move_uci = request.get("user_move")
    
    # Validate input
    if not fen_before or not fen_after:
        return {
            "error": "Missing FEN data",
            "message": "Please provide both fen_before and fen_after"
        }
    
    try:
        import chess
        
        # Create boards
        board_before = chess.Board(fen_before)
        board_after = chess.Board(fen_after)
        
        # Detect the user's move if not provided
        if not user_move_uci:
            # Find the move by comparing boards
            possible_moves = []
            for move in board_before.legal_moves:
                test_board = board_before.copy()
                test_board.push(move)
                # Compare just the piece positions (ignore move counters)
                if test_board.board_fen() == board_after.board_fen():
                    possible_moves.append(move)
            
            if len(possible_moves) == 0:
                return {
                    "error": "Could not detect move",
                    "message": "Unable to determine the move made between the two positions. The positions may differ by more than one move, or FEN extraction may be inconsistent.",
                    "debug": {
                        "fen_before": fen_before,
                        "fen_after": fen_after,
                        "legal_moves_count": len(list(board_before.legal_moves))
                    }
                }
            elif len(possible_moves) > 1:
                # Multiple moves lead to same position (e.g., castling notation differences)
                # Just pick the first one
                user_move_uci = possible_moves[0].uci()
                print(f"[WARNING] Multiple moves detected, using first: {user_move_uci}")
            else:
                user_move_uci = possible_moves[0].uci()
        
        # Parse the user's move
        try:
            user_move = chess.Move.from_uci(user_move_uci)
            if user_move not in board_before.legal_moves:
                return {
                    "error": "Illegal move",
                    "message": f"The move {user_move_uci} is not legal in the given position"
                }
        except Exception as e:
            return {
                "error": "Invalid move format",
                "message": f"Could not parse move: {user_move_uci}"
            }
        
        user_move_san = board_before.san(user_move)
        
        # Get best move analysis from Stockfish
        if not chess_engine_service or not chess_engine_service.is_initialized:
            return {
                "error": "Engine not available",
                "message": "Chess engine is not initialized. Cannot analyze moves."
            }
        
        # Analyze the position before the move to get best move
        best_move_analysis = await chess_engine_service.analyze_position(fen_before, depth=20)
        
        if not best_move_analysis or not best_move_analysis.get('best_moves'):
            return {
                "error": "Analysis failed",
                "message": "Could not analyze the position"
            }
        
        best_move_data = best_move_analysis['best_moves'][0]
        
        # Analyze the user's move by playing it and evaluating the resulting position
        test_board = board_before.copy()
        test_board.push(user_move)
        user_position_analysis = await chess_engine_service.analyze_position(test_board.fen(), depth=20)
        
        # Get evaluation of user's move from the NEW position's perspective
        # Need to flip the score since it's from opponent's perspective now
        if user_position_analysis and user_position_analysis.get('best_moves'):
            user_eval_score = user_position_analysis['best_moves'][0]['score']
            # Flip the score (it's from opponent's view after the move)
            if user_eval_score['type'] == 'cp':
                user_eval_score['value'] = -user_eval_score['value']
            elif user_eval_score['type'] == 'mate':
                user_eval_score['value'] = -user_eval_score['value']
        else:
            user_eval_score = {"type": "cp", "value": 0, "display": "0.00"}
        
        # Create user move evaluation data
        user_move_eval = {
            "move": user_move_uci,
            "san": user_move_san,
            "score": user_eval_score
        }
        
        # Compare moves using MoveComparator
        comparison = None
        if move_comparator:
            try:
                comparison = move_comparator.compare_moves(
                    user_move_eval,
                    best_move_data,
                    board_before
                )
            except Exception as e:
                print(f"[WARNING] Move comparison failed: {e}")
        
        # Analyze move impact if board_analyzer is available
        move_impact = None
        if board_analyzer:
            try:
                move_impact = board_analyzer.analyze_move_impact(board_before, user_move)
            except Exception as e:
                print(f"[WARNING] Move impact analysis failed: {e}")
        
        # Generate detailed explanation using LLM with comparison
        explanation = ""
        if llm_explanation_service and comparison:
            try:
                # Create comprehensive comparison context for LLM
                user_move_san = user_move_eval['san']
                best_move_san = best_move_data['san']
                quality = comparison['quality']
                cp_loss = abs(comparison['score_difference'])
                
                # Build a detailed prompt for the LLM
                comparison_context = {
                    'user_move': user_move_san,
                    'best_move': best_move_san,
                    'quality': quality,
                    'cp_loss': cp_loss,
                    'user_score': user_eval_score,
                    'best_score': best_move_data['score'],
                    'move_impact': move_impact,
                    'position_fen': fen_before
                }
                
                # Generate comparative explanation using LLM
                from app.services.llm_explanation import LLMExplanationService
                
                # Build piece map to prevent hallucinations
                piece_map_str = ""
                piece_symbols = {chess.PAWN: 'pawn', chess.KNIGHT: 'knight', 
                                chess.BISHOP: 'bishop', chess.ROOK: 'rook',
                                chess.QUEEN: 'queen', chess.KING: 'king'}
                
                # List all pieces on the board for verification
                board_pieces = []
                for square, piece in board_before.piece_map().items():
                    square_name = chess.square_name(square)
                    piece_name = piece_symbols.get(piece.piece_type, 'piece')
                    color = 'White' if piece.color == chess.WHITE else 'Black'
                    board_pieces.append(f"{color} {piece_name} on {square_name}")
                
                piece_map_str = "\n".join(board_pieces)
                
                # Create a grounded prompt that avoids numeric evals and
                # discourages hallucinating non-existent pieces/squares.
                prompt = f"""You are a chess coach comparing two moves in the same position.

Position (FEN): {fen_before}

Pieces on the board:
{piece_map_str}

User move: {user_move_san}
Engine best move: {best_move_san}
Quality label for the user's move: {quality}.

Explain in 2–3 sentences why the engine's move is better from a chess point of view.
Focus on general ideas such as king safety, material, piece activity, development,
and tactical threats (e.g. forks, pins, back-rank mate, etc.).
Do NOT mention numeric evaluation scores or centipawn values.
IMPORTANT: Only mention pieces and squares that are explicitly listed above in the piece map.
If you're unsure about specific tactical details, keep the explanation more general.

{comparison['quality_display']['emoji']} Give a concise, instructive explanation suitable for a club-level player."""

                explanation = await llm_explanation_service.generate_raw_explanation(prompt)
                
                if not explanation or len(explanation) < 20:
                    # Fallback to move comparator
                    if move_comparator:
                        explanation = move_comparator.generate_detailed_feedback(
                            user_move_eval,
                            best_move_data,
                            comparison,
                            move_impact
                        )
                    else:
                        explanation = comparison.get('comparison_text', '')
                        
            except Exception as e:
                print(f"[WARNING] LLM explanation generation failed: {e}")
                # Fallback to move comparator
                if move_comparator:
                    explanation = move_comparator.generate_detailed_feedback(
                        user_move_eval,
                        best_move_data,
                        comparison,
                        move_impact
                    )
                else:
                    explanation = comparison.get('comparison_text', '') if comparison else ""
        elif comparison:
            # Fallback without LLM
            if move_comparator:
                explanation = move_comparator.generate_detailed_feedback(
                    user_move_eval,
                    best_move_data,
                    comparison,
                    move_impact
                )
            else:
                explanation = comparison.get('comparison_text', '')
        else:
            explanation = f"Your move: {user_move_san}. Best move: {best_move_data['san']}."
        
        # Build response
        response = {
            "fen_before": fen_before,
            "fen_after": fen_after,
            "user_move": {
                "move": user_move_uci,
                "san": user_move_san,
                "evaluation": user_eval_score,
            },
            "best_move": best_move_data,
            "comparison": comparison if comparison else {
                "quality": "unknown",
                "quality_display": {
                    "badge_color": "#gray",
                    "emoji": "❓",
                    "label": "Unknown",
                    "description": "Could not compare moves"
                }
            },
            "explanation": explanation,
            "move_impact": move_impact
        }
        
        return response
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Move analysis failed: {e}")
        print(traceback.format_exc())
        return {
            "error": "Analysis failed",
            "message": f"Could not analyze move: {str(e)}"
        }

if __name__ == "__main__":
    print("Starting simple test server on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
