import logging
from typing import List, Dict, Any
import chess

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.is_initialized = False
        
    async def load_models(self):
        """Load ML models"""
        try:
            # Try to import ML libraries
            import sklearn
            import numpy as np
            logger.info("ML libraries available")
            self.is_initialized = True
        except ImportError:
            logger.warning("ML libraries not available, using rule-based analysis")
            self.is_initialized = False
    
    async def get_position_insights(self, fen: str) -> List[str]:
        """Get position insights"""
        try:
            board = chess.Board(fen)
            insights = []
            
            # Basic rule-based insights
            material_balance = self._calculate_material_balance(board)
            if material_balance > 3:
                insights.append("White has a material advantage")
            elif material_balance < -3:
                insights.append("Black has a material advantage")
            
            # King safety check
            if board.is_check():
                insights.append("King is under attack - consider defensive moves")
            
            # Development in opening
            if len(board.move_stack) < 15:
                insights.append("Focus on piece development and king safety")
            
            # Center control
            center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
            center_control = sum(1 for sq in center_squares 
                               if board.piece_at(sq))
            
            if center_control >= 2:
                insights.append("Good central control in this position")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting position insights: {e}")
            return ["Position analysis unavailable"]
    
    def _calculate_material_balance(self, board: chess.Board) -> float:
        """Calculate material balance"""
        piece_values = {
            chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
            chess.ROOK: 5, chess.QUEEN: 9
        }
        
        white_material = sum(piece_values.get(piece.piece_type, 0)
                           for piece in board.piece_map().values()
                           if piece.color == chess.WHITE)
        
        black_material = sum(piece_values.get(piece.piece_type, 0)
                           for piece in board.piece_map().values()
                           if piece.color == chess.BLACK)
        
        return white_material - black_material

# Create global instance
ml_service = MLService()