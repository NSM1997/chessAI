import chess
from typing import List, Dict, Any, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class ExplanationEngine:
    def __init__(self):
        self.tactical_patterns = self._load_tactical_patterns()
        self.strategic_templates = self._load_strategic_templates()
        
    async def generate_explanations(
        self, 
        fen: str, 
        engine_result: Dict, 
        skill_level: str = "intermediate",
        explanation_type: str = "comprehensive"
    ) -> List[Dict]:
        """Generate explanations for the top moves"""
        try:
            board = chess.Board(fen)
            explanations = []
            
            # Try to get ML insights if available
            ml_insights = []
            try:
                # Import here to avoid circular imports
                from app.services.ml_service import ml_service
                ml_insights = await ml_service.get_position_insights(fen)
            except ImportError:
                logger.warning("ML service not available, using rule-based explanations")
            except Exception as e:
                logger.warning(f"ML service error: {e}, falling back to rule-based")
            
            for move_info in engine_result["best_moves"][:3]:
                move_uci = move_info["move"]
                move = chess.Move.from_uci(move_uci)
                
                explanation = await self._explain_move(
                    board, move, move_info, skill_level, explanation_type, ml_insights
                )
                
                explanations.append({
                    "move": move_uci,
                    "san": move_info["san"],
                    "explanation": explanation["text"],
                    "tactical_motifs": explanation["tactical_motifs"],
                    "strategic_concepts": explanation["strategic_concepts"],
                    "confidence": explanation["confidence"],
                    "engine_evaluation": move_info
                })
            
            return explanations
            
        except Exception as e:
            logger.error(f"Explanation generation error: {e}")
            return []
    
    async def _explain_move(
        self, 
        board: chess.Board, 
        move: chess.Move, 
        move_info: Dict, 
        skill_level: str,
        explanation_type: str,
        ml_insights: List[str] = None
    ) -> Dict:
        """Generate detailed explanation for a specific move"""
        explanation_parts = []
        tactical_motifs = []
        strategic_concepts = []
        
        # Make the move to analyze the resulting position
        board_copy = board.copy()
        board_copy.push(move)
        
        # Basic move description
        piece = board.piece_at(move.from_square)
        piece_name = self._get_piece_name(piece) if piece else 'piece'
        move_desc = f"Moving the {piece_name} from {chess.square_name(move.from_square)} to {chess.square_name(move.to_square)}"
        
        # Check for captures
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                move_desc += f", capturing the {self._get_piece_name(captured_piece)}"
                tactical_motifs.append("capture")
        
        explanation_parts.append(move_desc)
        
        # Analyze tactical motifs
        tactical_analysis = self._analyze_tactical_motifs(board, move, board_copy)
        if tactical_analysis:
            explanation_parts.extend(tactical_analysis["explanations"])
            tactical_motifs.extend(tactical_analysis["motifs"])
        
        # Analyze strategic concepts
        strategic_analysis = self._analyze_strategic_concepts(board, move, board_copy)
        if strategic_analysis:
            explanation_parts.extend(strategic_analysis["explanations"])
            strategic_concepts.extend(strategic_analysis["concepts"])
        
        # Score-based explanation
        score_explanation = self._explain_evaluation(move_info.get("score", {}))
        if score_explanation:
            explanation_parts.append(score_explanation)
        
        # Add ML insights if available
        if ml_insights:
            relevant_insights = [insight for insight in ml_insights 
                               if any(keyword in insight.lower() for keyword in 
                                    ['tactical', 'pattern', 'advantage', 'position'])]
            if relevant_insights:
                explanation_parts.extend(relevant_insights[:2])  # Add top 2 ML insights
        
        # Adjust explanation complexity based on skill level
        final_explanation = self._adjust_for_skill_level(explanation_parts, skill_level)
        
        return {
            "text": " ".join(final_explanation),
            "tactical_motifs": list(set(tactical_motifs)),  # Remove duplicates
            "strategic_concepts": list(set(strategic_concepts)),
            "confidence": 0.8  # Base confidence score
        }
    
    def _analyze_tactical_motifs(self, board: chess.Board, move: chess.Move, resulting_board: chess.Board) -> Optional[Dict]:
        """Analyze tactical motifs in the move"""
        motifs = []
        explanations = []
        
        # Check for check
        if resulting_board.is_check():
            motifs.append("check")
            explanations.append("This move gives check to the enemy king.")
        
        # Check for fork (simplified detection)
        fork_analysis = self._detect_fork(board, move, resulting_board)
        if fork_analysis:
            motifs.append("fork")
            explanations.append(fork_analysis)
        
        # Check for pin (simplified detection)
        if self._move_creates_pin(board, move):
            motifs.append("pin")
            explanations.append("This move creates a pin, restricting the opponent's piece movement.")
        
        # Check for discovered attacks
        if self._creates_discovered_attack(board, move):
            motifs.append("discovered_attack")
            explanations.append("This move reveals an attack from another piece.")
        
        if motifs:
            return {"motifs": motifs, "explanations": explanations}
        return None
    
    def _detect_fork(self, board: chess.Board, move: chess.Move, resulting_board: chess.Board) -> Optional[str]:
        """Detect fork patterns (simplified)"""
        try:
            # Get all squares attacked by the moved piece
            attacked_squares = list(resulting_board.attacks(move.to_square))
            
            # Count valuable enemy pieces attacked
            valuable_targets = []
            for square in attacked_squares:
                piece = resulting_board.piece_at(square)
                if (piece and piece.color != board.turn and 
                    piece.piece_type in [chess.QUEEN, chess.ROOK, chess.KING]):
                    valuable_targets.append(piece)
            
            if len(valuable_targets) >= 2:
                return "This move creates a fork, attacking multiple valuable pieces."
            
        except Exception:
            pass
        
        return None
    
    def _move_creates_pin(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move creates a pin (very simplified)"""
        try:
            piece = board.piece_at(move.from_square)
            if not piece or piece.piece_type not in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
                return False
            
            # This is a simplified check - real pin detection would be more complex
            return False
        except:
            return False
    
    def _creates_discovered_attack(self, board: chess.Board, move: chess.Move) -> bool:
        """Check if move creates discovered attack (simplified)"""
        try:
            # Check if moving piece reveals attack from behind
            from_square = move.from_square
            
            # Look for pieces behind the moving piece that could attack
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if (piece and piece.color == board.turn and 
                    piece.piece_type in [chess.BISHOP, chess.ROOK, chess.QUEEN]):
                    
                    # Simple line check (would need more sophisticated geometry)
                    if self._on_same_line(square, from_square):
                        return True
            
            return False
        except:
            return False
    
    def _on_same_line(self, square1: int, square2: int) -> bool:
        """Check if two squares are on same rank, file, or diagonal"""
        file1, rank1 = chess.square_file(square1), chess.square_rank(square1)
        file2, rank2 = chess.square_file(square2), chess.square_rank(square2)
        
        # Same file or rank
        if file1 == file2 or rank1 == rank2:
            return True
        
        # Same diagonal
        if abs(file1 - file2) == abs(rank1 - rank2):
            return True
        
        return False
    
    def _analyze_strategic_concepts(self, board: chess.Board, move: chess.Move, resulting_board: chess.Board) -> Optional[Dict]:
        """Analyze strategic concepts"""
        concepts = []
        explanations = []
        
        piece = board.piece_at(move.from_square)
        
        # Development
        if (piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP] and 
            len(board.move_stack) < 15):
            concepts.append("development")
            explanations.append(f"Developing the {self._get_piece_name(piece)} improves piece activity.")
        
        # Center control
        if move.to_square in [chess.E4, chess.E5, chess.D4, chess.D5]:
            concepts.append("center_control")
            explanations.append("This move controls important central squares.")
        
        # King safety (castling)
        if piece and piece.piece_type == chess.KING and abs(move.from_square - move.to_square) == 2:
            concepts.append("king_safety")
            explanations.append("Castling improves king safety.")
        
        # Pawn structure
        if piece and piece.piece_type == chess.PAWN:
            concepts.append("pawn_structure")
            explanations.append("This pawn move affects the position's structure.")
        
        if concepts:
            return {"concepts": concepts, "explanations": explanations}
        return None
    
    def _explain_evaluation(self, score: Dict) -> Optional[str]:
        """Explain the move's evaluation"""
        if not score:
            return None
        
        if score.get("type") == "mate":
            mate_in = score.get("value", 0)
            if mate_in > 0:
                return f"This leads to checkmate in {mate_in} moves."
            else:
                return f"This defends against mate in {abs(mate_in)} moves."
        elif score.get("type") == "cp":
            cp_value = score.get("value", 0)
            if cp_value > 150:
                return "This move gives a significant advantage."
            elif cp_value > 50:
                return "This move provides a slight advantage."
            elif cp_value < -150:
                return "This move is disadvantageous."
            elif cp_value < -50:
                return "This move gives a slight disadvantage."
        
        return None
    
    def _adjust_for_skill_level(self, explanation_parts: List[str], skill_level: str) -> List[str]:
        """Adjust explanation complexity for skill level"""
        if skill_level == "beginner":
            # Keep only the most basic explanations
            return explanation_parts[:2]
        elif skill_level == "advanced":
            # Include all explanations
            return explanation_parts
        else:  # intermediate
            # Moderate detail
            return explanation_parts[:3]
    
    def _get_piece_name(self, piece: chess.Piece) -> str:
        """Get human-readable piece name"""
        if not piece:
            return "piece"
        
        names = {
            chess.PAWN: "pawn",
            chess.KNIGHT: "knight", 
            chess.BISHOP: "bishop",
            chess.ROOK: "rook",
            chess.QUEEN: "queen",
            chess.KING: "king"
        }
        return names.get(piece.piece_type, "piece")
    
    def _load_tactical_patterns(self) -> Dict:
        """Load tactical pattern recognition rules"""
        return {
            "fork": {
                "description": "A move that attacks two or more enemy pieces simultaneously",
                "template": "This move creates a fork, attacking both the {piece1} and the {piece2}."
            },
            "pin": {
                "description": "A move that attacks a piece that cannot move without exposing a more valuable piece",
                "template": "This move pins the {piece}, which cannot move without exposing the {valuable_piece}."
            },
            "skewer": {
                "description": "A move that forces a valuable piece to move, exposing a less valuable piece behind it",
                "template": "This move skewers the {piece1}, forcing it to move and exposing the {piece2}."
            }
        }
    
    def _load_strategic_templates(self) -> Dict:
        """Load strategic explanation templates"""
        return {
            "development": "Piece development improves activity and prepares for the middlegame.",
            "center_control": "Controlling central squares provides better piece mobility.",
            "king_safety": "King safety is crucial - castle early and avoid exposing the king.",
            "pawn_structure": "Pawn structure determines long-term strategic plans."
        }
    
    async def explain_specific_move(self, fen: str, move: str, skill_level: str = "intermediate") -> Dict:
        """Explain a specific move"""
        try:
            board = chess.Board(fen)
            move_obj = chess.Move.from_uci(move)
            
            # Create mock move info
            move_info = {
                "move": move,
                "san": board.san(move_obj),
                "score": {"type": "cp", "value": 0, "display": "0.00"}
            }
            
            explanation = await self._explain_move(
                board, move_obj, move_info, skill_level, "comprehensive"
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Specific move explanation error: {e}")
            return {
                "text": "Unable to explain this move.", 
                "tactical_motifs": [], 
                "strategic_concepts": [], 
                "confidence": 0.0
            }