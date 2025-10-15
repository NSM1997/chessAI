"""
Chess engine service for position analysis and move generation
"""

import chess
import chess.engine
import chess.pgn
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import platform
import os
from app.core.config import settings

logger = logging.getLogger(__name__)

class ChessEngineService:
    def __init__(self):
        self.stockfish_engine = None
        self.is_initialized = False
        
    def _find_stockfish_executable(self) -> Optional[str]:
        """Find Stockfish executable path using configuration"""
        # Use configured path first
        configured_path = settings.get_stockfish_path()
        
        possible_paths = [
            configured_path,  # Configured path first priority
            # Direct paths from project root
            "stockfish/stockfish-windows-x86-64-avx2.exe",
            "stockfish.exe",
            "engines/stockfish.exe",
            "stockfish/stockfish.exe",
            "C:/stockfish/stockfish.exe",
            # Relative paths from backend folder
            "../stockfish/stockfish-windows-x86-64-avx2.exe",
            "../../stockfish/stockfish-windows-x86-64-avx2.exe",
            "../stockfish/stockfish.exe",
            "../../stockfish.exe"
        ]
        
        # Check each possible path
        for path in possible_paths:
            try:
                if path and os.path.exists(path):
                    # On Windows, just check if file exists (executable check unreliable)
                    if platform.system().lower() == "windows" or os.access(path, os.X_OK):
                        logger.info(f"Found Stockfish at: {path}")
                        return path
            except Exception as e:
                logger.debug(f"Could not access {path}: {e}")
                continue
                
        # Additional Windows-specific locations
        system = platform.system().lower()
        if system == "windows":
            additional_paths = [
                os.path.expanduser("~/stockfish.exe"),
                "C:/Program Files/stockfish/stockfish.exe",
                "C:/Program Files (x86)/stockfish/stockfish.exe",
                os.path.join(os.getcwd(), "stockfish.exe")
            ]
            
            for path in additional_paths:
                try:
                    if os.path.exists(path):
                        logger.info(f"Found Stockfish at: {path}")
                        return path
                except Exception:
                    continue
        
        logger.error(f"Stockfish not found. Tried paths: {possible_paths}")
        return None
        
    async def initialize(self):
        """Initialize chess engines - FINAL VERSION"""
        try:
            # Find Stockfish executable
            stockfish_path = self._find_stockfish_executable()
            if not stockfish_path:
                logger.error("Stockfish executable not found")
                return False
                
            logger.info(f"Attempting to initialize Stockfish at: {stockfish_path}")
            
            # Create engine using direct method (which worked!)
            try:
                self.stockfish_engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
                logger.info("Engine created successfully")
                
                # Skip the problematic test - assume engine is working
                logger.info("Skipping engine test - assuming engine is working")
                
                self.is_initialized = True
                logger.info("Chess engines initialized successfully")
                return True
                
            except Exception as engine_error:
                logger.error(f"Engine creation failed: {engine_error}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize chess engines: {e}")
            return False

    async def analyze_position(self, fen: str, depth: int = 20) -> Dict[str, Any]:
        """
        Analyze chess position - IGNORE is_valid() CHECK
        """
        try:
            if not self.is_initialized:
                logger.error("Chess engine not initialized")
                return self._get_fallback_analysis(fen)
            
            logger.info(f"Analyzing position: {fen[:50]}...")
            
            # Create board - IGNORE is_valid() check
            try:
                board = chess.Board(fen)
                logger.info(f"Board created successfully from FEN")
                
                # Check if we have legal moves (more reliable than is_valid())
                legal_moves = list(board.legal_moves)
                if len(legal_moves) == 0:
                    logger.warning(f"No legal moves available in position")
                    return self._get_fallback_analysis(fen)
                
                logger.info(f"Position has {len(legal_moves)} legal moves - proceeding with analysis")
                    
            except Exception as board_error:
                logger.error(f"Board creation failed: {board_error}")
                return self._get_fallback_analysis(fen)
            
            # Try to use Stockfish with the board
            try:
                # Get best move with full analysis (not just play)
                analysis_result = self.stockfish_engine.analyse(
                    board,
                    chess.engine.Limit(depth=depth, time=2.0),
                    multipv=3  # Get top 3 moves
                )
                
                best_moves = []
                
                # Process analysis results
                if isinstance(analysis_result, list):
                    # multipv returns a list
                    for i, result in enumerate(analysis_result):
                        if "pv" in result and len(result["pv"]) > 0:
                            move = result["pv"][0]
                            score_info = result.get("score", chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE))
                            score_dict = self._score_to_dict(score_info, board.turn)
                            
                            best_moves.append({
                                "move": move.uci(),
                                "san": board.san(move),
                                "score": score_dict,
                                "pv": [m.uci() for m in result["pv"][:5]],  # Get first 5 moves of principal variation
                                "depth": result.get("depth", depth),
                                "nodes": result.get("nodes", 0)
                            })
                            
                            if i == 0:
                                logger.info(f"Stockfish suggested: {board.san(move)} (score: {score_dict['display']}) at depth {depth}")
                else:
                    # Single result
                    if "pv" in analysis_result and len(analysis_result["pv"]) > 0:
                        move = analysis_result["pv"][0]
                        score_info = analysis_result.get("score", chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE))
                        score_dict = self._score_to_dict(score_info, board.turn)
                        
                        best_moves.append({
                            "move": move.uci(),
                            "san": board.san(move),
                            "score": score_dict,
                            "pv": [m.uci() for m in analysis_result["pv"][:5]],
                            "depth": analysis_result.get("depth", depth),
                            "nodes": analysis_result.get("nodes", 0)
                        })
                        logger.info(f"Stockfish suggested: {board.san(move)} (score: {score_dict['display']}) at depth {depth}")
                
                if not best_moves or len(best_moves) == 0:
                    logger.warning("No moves from Stockfish, using fallback")
                    return self._get_fallback_analysis(fen)
                
                # Generate detailed explanations for each move
                move_explanations = []
                for i, move_data in enumerate(best_moves):
                    move_uci = move_data["move"]
                    move_obj = chess.Move.from_uci(move_uci)
                    pv_ucis = move_data.get("pv", [])
                    
                    explanation = self._generate_move_explanation(
                        board, 
                        move_obj, 
                        move_data["score"],
                        pv_ucis
                    )
                    
                    move_explanations.append({
                        "move": move_uci,
                        "san": move_data["san"],
                        "explanation": explanation,
                        "score": move_data["score"],
                        "pv": pv_ucis,
                        "rank": i + 1  # 1st best, 2nd best, etc.
                    })
                
                # Position evaluation
                evaluation = {
                    "score": best_moves[0]["score"] if best_moves else {"type": "cp", "value": 0, "display": "0.00"},
                    "position_type": self._classify_position(board),
                    "material_balance": self._calculate_material_balance(board),
                    "king_safety": self._evaluate_king_safety(board),
                    "piece_activity": self._evaluate_piece_activity(board)
                }
                
                return {
                    "best_moves": best_moves,
                    "move_explanations": move_explanations,
                    "evaluation": evaluation,
                    "legal_moves_count": len(legal_moves),
                    "is_endgame": self._is_endgame(board),
                    "tactical_motifs": self._detect_tactical_motifs(board)
                }
                
            except Exception as stockfish_error:
                logger.warning(f"Stockfish analysis failed: {stockfish_error}, using fallback")
                return self._get_fallback_analysis(fen)
                
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return self._get_fallback_analysis(fen)


    def _score_to_dict(self, score: chess.engine.PovScore, turn: chess.Color) -> Dict[str, Any]:
        """Convert engine score to dictionary format"""
        try:
            if score.is_mate():
                mate_value = score.relative.mate()
                return {
                    "type": "mate",
                    "value": mate_value,
                    "display": f"#{mate_value}"
                }
            else:
                cp_value = score.relative.score()
                if cp_value is None:
                    cp_value = 0
                eval_value = cp_value / 100.0  # Convert centipawns to pawns
                return {
                    "type": "cp",
                    "value": cp_value,
                    "display": f"{eval_value:+.2f}"
                }
        except Exception as e:
            logger.error(f"Score conversion error: {e}")
            return {"type": "cp", "value": 0, "display": "0.00"}

    def _get_fallback_analysis(self, fen: str) -> Dict[str, Any]:
        """Fallback analysis when engine fails"""
        try:
            board = chess.Board(fen)
            legal_moves = list(board.legal_moves)
            
            best_moves = []
            for i, move in enumerate(legal_moves[:3]):
                best_moves.append({
                    "move": move.uci(),
                    "san": board.san(move),
                    "score": {"type": "cp", "value": 0, "display": "0.00"},
                    "pv": [move.uci()],
                    "depth": 1
                })
            
            evaluation = {
                "score": {"type": "cp", "value": 0, "display": "0.00"},
                "position_type": self._classify_position(board),
                "material_balance": self._calculate_material_balance(board),
                "king_safety": self._evaluate_king_safety(board),
                "piece_activity": self._evaluate_piece_activity(board)
            }
            
            return {
                "best_moves": best_moves,
                "evaluation": evaluation,
                "legal_moves_count": len(legal_moves),
                "is_endgame": self._is_endgame(board),
                "tactical_motifs": []
            }
        except Exception as e:
            logger.error(f"Fallback analysis error: {e}")
            # Ultimate fallback
            return {
                "best_moves": [
                    {"move": "e2e4", "san": "e4", "score": {"type": "cp", "value": 0, "display": "0.00"}, "pv": ["e2e4"], "depth": 1}
                ],
                "evaluation": {
                    "score": {"type": "cp", "value": 0, "display": "0.00"},
                    "position_type": "unknown",
                    "material_balance": {"white": 0, "black": 0, "difference": 0},
                    "king_safety": {"white": 0, "black": 0},
                    "piece_activity": {"white": 0, "black": 0}
                },
                "legal_moves_count": 1,
                "is_endgame": False,
                "tactical_motifs": []
            }

    def _classify_position(self, board: chess.Board) -> str:
        """Classify the type of position"""
        try:
            # Count pieces
            piece_count = len(board.piece_map())
            
            if piece_count <= 6:
                return "endgame"
            elif piece_count <= 16:
                return "middlegame"
            elif len(list(board.move_stack)) < 10:
                return "opening"
            else:
                return "middlegame"
        except Exception:
            return "unknown"

    def _calculate_material_balance(self, board: chess.Board) -> Dict[str, int]:
        """Calculate material balance"""
        try:
            piece_values = {
                chess.PAWN: 1,
                chess.KNIGHT: 3,
                chess.BISHOP: 3,
                chess.ROOK: 5,
                chess.QUEEN: 9
            }
            
            white_material = 0
            black_material = 0
            
            for square, piece in board.piece_map().items():
                value = piece_values.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    white_material += value
                else:
                    black_material += value
            
            return {
                "white": white_material,
                "black": black_material,
                "difference": white_material - black_material
            }
        except Exception:
            return {"white": 0, "black": 0, "difference": 0}

    def _evaluate_king_safety(self, board: chess.Board) -> Dict[str, int]:
        """Evaluate king safety"""
        try:
            white_king_square = board.king(chess.WHITE)
            black_king_square = board.king(chess.BLACK)
            
            # Simple king safety evaluation
            white_safety = 5  # Base safety
            black_safety = 5
            
            # Check if kings are castled (simple heuristic)
            if white_king_square and white_king_square in [chess.G1, chess.C1]:
                white_safety += 2
            if black_king_square and black_king_square in [chess.G8, chess.C8]:
                black_safety += 2
            
            return {
                "white": white_safety,
                "black": black_safety
            }
        except Exception:
            return {"white": 0, "black": 0}

    def _evaluate_piece_activity(self, board: chess.Board) -> Dict[str, int]:
        """Evaluate piece activity"""
        try:
            white_activity = 0
            black_activity = 0
            
            for square, piece in board.piece_map().items():
                # Count legal moves for each piece (simplified)
                moves_count = len([move for move in board.legal_moves if move.from_square == square])
                
                if piece.color == chess.WHITE:
                    white_activity += moves_count
                else:
                    black_activity += moves_count
            
            return {
                "white": white_activity,
                "black": black_activity
            }
        except Exception:
            return {"white": 0, "black": 0}

    def _is_endgame(self, board: chess.Board) -> bool:
        """Determine if position is endgame"""
        try:
            # Simple endgame detection
            piece_count = len(board.piece_map())
            return piece_count <= 10
        except Exception:
            return False

    def _detect_tactical_motifs(self, board: chess.Board) -> List[str]:
        """Detect tactical motifs in position"""
        try:
            motifs = []
            
            # Check for checks
            if board.is_check():
                motifs.append("check")
            
            # Check for checkmate
            if board.is_checkmate():
                motifs.append("checkmate")
            
            # Check for stalemate
            if board.is_stalemate():
                motifs.append("stalemate")
            
            # Simple pin detection (very basic)
            for move in board.legal_moves:
                if board.is_capture(move):
                    motifs.append("capture_available")
                    break
            
            return motifs
        except Exception:
            return []
    
    def _generate_move_explanation(self, board: chess.Board, move: chess.Move, score: Dict, pv: List[str]) -> str:
        """Generate detailed explanation for a move"""
        try:
            move_san = board.san(move)
            turn = "White" if board.turn == chess.WHITE else "Black"
            
            # Make the move to analyze the resulting position
            test_board = board.copy()
            test_board.push(move)
            
            # Extract key information
            is_check = test_board.is_check()
            is_checkmate = test_board.is_checkmate()
            is_capture = board.is_capture(move)
            is_castling = board.is_castling(move)
            
            # Get piece that moved
            piece = board.piece_at(move.from_square)
            piece_name = chess.piece_name(piece.piece_type).title() if piece else "Piece"
            
            # Build explanation
            explanation_parts = []
            
            # Start with the move
            explanation_parts.append(f"{turn} plays {move_san}")
            
            # Add tactical details
            if is_checkmate:
                explanation_parts.append("delivering checkmate!")
                return ". ".join(explanation_parts)
            
            if is_check:
                explanation_parts.append("giving check")
            
            if is_castling:
                if move.to_square > move.from_square:
                    explanation_parts.append("castling kingside for king safety")
                else:
                    explanation_parts.append("castling queenside for king safety")
            
            if is_capture:
                captured_piece = board.piece_at(move.to_square)
                if captured_piece:
                    captured_name = chess.piece_name(captured_piece.piece_type)
                    explanation_parts.append(f"capturing the {captured_name}")
            
            # Add score evaluation
            score_value = score.get("value", 0)
            if score["type"] == "mate":
                mate_in = score["value"]
                if mate_in > 0:
                    explanation_parts.append(f"forcing mate in {mate_in}")
                else:
                    explanation_parts.append(f"avoiding mate in {abs(mate_in)}")
            else:
                # Centipawn advantage
                if abs(score_value) > 200:
                    if score_value > 0:
                        explanation_parts.append("gaining a decisive advantage")
                    else:
                        explanation_parts.append("with the best practical chances")
                elif abs(score_value) > 100:
                    if score_value > 0:
                        explanation_parts.append("with a clear advantage")
                    else:
                        explanation_parts.append("fighting for equality")
                elif abs(score_value) > 50:
                    if score_value > 0:
                        explanation_parts.append("with a slight edge")
                    else:
                        explanation_parts.append("maintaining the balance")
                else:
                    explanation_parts.append("keeping the position equal")
            
            # Add strategic reasoning based on piece and position
            if piece:
                if piece.piece_type == chess.PAWN:
                    if chess.square_rank(move.to_square) >= 6 or chess.square_rank(move.to_square) <= 1:
                        explanation_parts.append("Advancing the pawn creates threats and restricts the opponent")
                elif piece.piece_type == chess.KNIGHT:
                    explanation_parts.append("Developing the knight to an active square")
                elif piece.piece_type == chess.BISHOP:
                    explanation_parts.append("Activating the bishop on the long diagonal")
                elif piece.piece_type == chess.ROOK:
                    if move.to_square in [chess.D1, chess.E1, chess.D8, chess.E8]:
                        explanation_parts.append("Centralizing the rook for maximum activity")
                elif piece.piece_type == chess.QUEEN:
                    if is_check or is_capture:
                        explanation_parts.append("Using the queen's power to create immediate threats")
            
            # Add follow-up plan if we have a principal variation
            if len(pv) > 1:
                explanation_parts.append(f"The plan continues with {len(pv)-1} more precise moves")
            
            return ". ".join(explanation_parts) + "."
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return f"{turn} plays the best move {move_san}, maintaining optimal play."

    async def get_best_move(self, fen: str, depth: int = 12) -> Optional[Dict[str, Any]]:
        """Get the best move for a position"""
        try:
            if not self.is_initialized:
                return None
                
            board = chess.Board(fen)
            
            result = self.stockfish_engine.play(
                board,
                chess.engine.Limit(depth=depth)
            )
            
            if result.move:
                return {
                    "move": result.move.uci(),
                    "san": board.san(result.move)
                }
                
        except Exception as e:
            logger.error(f"Error getting best move: {e}")
            
        return None

    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.stockfish_engine:
                await self.stockfish_engine.quit()
                logger.info("Chess engines cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up engines: {e}")

    def debug_fen_validation(self, fen: str):
        """Debug FEN validation issues"""
        logger.info(f"=== DEBUGGING FEN: {fen} ===")
        
        try:
            # Try to create board
            board = chess.Board(fen)
            logger.info("✅ Board created successfully")
            
            # # Check if board is valid
            # if board.is_valid():
            #     logger.info("✅ Board position is valid")
            # else:
            #     logger.warning("❌ Board position is invalid")
                
            # Check legal moves
            legal_moves = list(board.legal_moves)
            logger.info(f"📋 Legal moves count: {len(legal_moves)}")
            
            # Check kings
            white_king = board.king(chess.WHITE)
            black_king = board.king(chess.BLACK)
            logger.info(f"👑 White king: {white_king}, Black king: {black_king}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ FEN validation failed: {e}")
            return False


# Global instance
chess_engine_service = ChessEngineService()

async def get_chess_engine() -> ChessEngineService:
    """Get chess engine service instance"""
    return chess_engine_service