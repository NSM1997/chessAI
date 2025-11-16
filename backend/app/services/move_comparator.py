"""
Move Comparator Service
Compares user moves to engine's best moves and classifies move quality.
"""

import chess
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class MoveComparator:
    """
    Compares user moves to best moves and provides quality ratings.
    """
    
    # Move quality thresholds (in centipawns)
    QUALITY_THRESHOLDS = {
        'best': 10,           # 0-10 cp worse than best
        'excellent': 25,      # 10-25 cp worse
        'good': 50,           # 25-50 cp worse
        'inaccuracy': 100,    # 50-100 cp worse
        'mistake': 200,       # 100-200 cp worse
        'blunder': float('inf')  # 200+ cp worse
    }
    
    def __init__(self):
        self.logger = logger
    
    def classify_move_quality(self, cp_loss: int) -> str:
        """
        Classify move quality based on centipawn loss.
        
        Args:
            cp_loss: Centipawns lost compared to best move (absolute value)
            
        Returns:
            Quality string: 'best', 'excellent', 'good', 'inaccuracy', 'mistake', or 'blunder'
        """
        cp_loss = abs(cp_loss)
        
        if cp_loss <= self.QUALITY_THRESHOLDS['best']:
            return 'best'
        elif cp_loss <= self.QUALITY_THRESHOLDS['excellent']:
            return 'excellent'
        elif cp_loss <= self.QUALITY_THRESHOLDS['good']:
            return 'good'
        elif cp_loss <= self.QUALITY_THRESHOLDS['inaccuracy']:
            return 'inaccuracy'
        elif cp_loss <= self.QUALITY_THRESHOLDS['mistake']:
            return 'mistake'
        else:
            return 'blunder'
    
    def calculate_quality_score(self, cp_loss: int) -> int:
        """
        Calculate a 0-100 quality score for the move.
        
        Args:
            cp_loss: Centipawns lost compared to best move
            
        Returns:
            Score from 0 (terrible) to 100 (perfect)
        """
        cp_loss = abs(cp_loss)
        
        # Perfect move
        if cp_loss == 0:
            return 100
        
        # Use exponential decay for scoring
        # 10cp loss = ~95, 50cp = ~85, 100cp = ~70, 200cp = ~50, 500cp = ~20
        score = max(0, 100 - (cp_loss * 0.3) - (cp_loss ** 1.3) * 0.01)
        
        return int(score)
    
    def get_quality_display(self, quality: str) -> Dict[str, str]:
        """
        Get display properties for move quality.
        
        Args:
            quality: Quality classification
            
        Returns:
            Dictionary with badge_color, emoji, and label
        """
        displays = {
            'best': {
                'badge_color': '#10b981',  # Green
                'emoji': '🌟',
                'label': 'Best Move!',
                'description': 'Perfect choice!'
            },
            'excellent': {
                'badge_color': '#06b6d4',  # Cyan
                'emoji': '✨',
                'label': 'Excellent',
                'description': 'Outstanding move!'
            },
            'good': {
                'badge_color': '#3b82f6',  # Blue
                'emoji': '👍',
                'label': 'Good Move',
                'description': 'Solid choice'
            },
            'inaccuracy': {
                'badge_color': '#f59e0b',  # Yellow/Orange
                'emoji': '⚠️',
                'label': 'Inaccuracy',
                'description': 'Not the best option'
            },
            'mistake': {
                'badge_color': '#f97316',  # Orange
                'emoji': '❌',
                'label': 'Mistake',
                'description': 'This weakens your position'
            },
            'blunder': {
                'badge_color': '#ef4444',  # Red
                'emoji': '💥',
                'label': 'Blunder',
                'description': 'Critical error!'
            }
        }
        
        return displays.get(quality, displays['good'])
    
    def compare_moves(self, 
                     user_move_eval: Dict[str, Any],
                     best_move_eval: Dict[str, Any],
                     board: chess.Board) -> Dict[str, Any]:
        """
        Compare user's move to the best move.
        
        Args:
            user_move_eval: Evaluation of user's move (with score)
            best_move_eval: Evaluation of best move (with score)
            board: Chess board position before the move
            
        Returns:
            Comparison dictionary with quality rating and advice
        """
        # Extract scores (handle both cp and mate scores)
        user_score = self._normalize_score(user_move_eval.get('score', {}))
        best_score = self._normalize_score(best_move_eval.get('score', {}))
        
        # Calculate centipawn loss
        # Note: scores are from the perspective of the side to move
        cp_loss = best_score - user_score
        
        # Classify quality
        quality = self.classify_move_quality(cp_loss)
        quality_score = self.calculate_quality_score(cp_loss)
        quality_display = self.get_quality_display(quality)
        
        # Determine if moves are the same
        is_best_move = (user_move_eval.get('move') == best_move_eval.get('move'))
        
        return {
            'score_difference': cp_loss,
            'quality': quality,
            'quality_score': quality_score,
            'quality_display': quality_display,
            'is_best_move': is_best_move,
            'comparison_text': self._generate_comparison_text(
                quality, 
                cp_loss, 
                is_best_move,
                user_move_eval.get('san', ''),
                best_move_eval.get('san', '')
            )
        }
    
    def _normalize_score(self, score_dict: Dict[str, Any]) -> int:
        """
        Normalize score to centipawns for comparison.
        
        Args:
            score_dict: Score dictionary with 'type' and 'value'
            
        Returns:
            Score in centipawns (positive = good for side to move)
        """
        score_type = score_dict.get('type', 'cp')
        value = score_dict.get('value', 0)
        
        if score_type == 'mate':
            # Convert mate scores to very high centipawn values
            if value > 0:
                return 10000 - value  # Mate in N moves
            else:
                return -10000 - value  # Getting mated in N moves
        else:
            # Already in centipawns
            return value
    
    def _generate_comparison_text(self, 
                                  quality: str, 
                                  cp_loss: int,
                                  is_best_move: bool,
                                  user_move: str,
                                  best_move: str) -> str:
        """
        Generate human-readable comparison text.
        
        Args:
            quality: Move quality classification
            cp_loss: Centipawns lost
            is_best_move: Whether user played the best move
            user_move: User's move in SAN
            best_move: Best move in SAN
            
        Returns:
            Comparison text string
        """
        if is_best_move:
            return "Perfect! This was the engine's top choice."
        
        if quality == 'best' or quality == 'excellent':
            return f"Great move! Only slightly less accurate than {best_move} ({abs(cp_loss)} cp difference)."
        elif quality == 'good':
            return f"Solid move, though {best_move} was better ({abs(cp_loss)} cp difference)."
        elif quality == 'inaccuracy':
            return f"This works, but {best_move} was more accurate ({abs(cp_loss)} cp difference)."
        elif quality == 'mistake':
            return f"This weakens your position. {best_move} was much stronger ({abs(cp_loss)} cp difference)."
        else:  # blunder
            return f"Critical mistake! This seriously hurts your position. {best_move} was the way to go ({abs(cp_loss)} cp difference)."
    
    def generate_detailed_feedback(self,
                                   user_move_data: Dict[str, Any],
                                   best_move_data: Dict[str, Any],
                                   comparison: Dict[str, Any],
                                   board_analysis: Optional[Dict] = None) -> str:
        """
        Generate detailed feedback about the user's move.
        
        Args:
            user_move_data: User's move information
            best_move_data: Best move information
            comparison: Comparison results
            board_analysis: Optional board analysis data
            
        Returns:
            Detailed feedback string
        """
        quality = comparison['quality']
        user_move_san = user_move_data.get('san', '')
        
        feedback_parts = []
        
        # Opening statement based on quality
        if quality == 'best':
            feedback_parts.append(f"🌟 Excellent! {user_move_san} is the best move in this position.")
        elif quality == 'excellent':
            feedback_parts.append(f"✨ Outstanding! {user_move_san} is an excellent choice.")
        elif quality == 'good':
            feedback_parts.append(f"👍 Good move. {user_move_san} is a solid option.")
        elif quality == 'inaccuracy':
            feedback_parts.append(f"⚠️ {user_move_san} is playable but not optimal.")
        elif quality == 'mistake':
            feedback_parts.append(f"❌ {user_move_san} is a mistake that weakens your position.")
        else:  # blunder
            feedback_parts.append(f"💥 {user_move_san} is a serious blunder!")
        
        # Add comparison to best move if different
        if not comparison['is_best_move']:
            best_move_san = best_move_data.get('san', '')
            feedback_parts.append(f"The engine prefers {best_move_san}.")
        
        # Add tactical/positional context if available
        if board_analysis:
            tactical_info = self._extract_tactical_feedback(user_move_data, board_analysis)
            if tactical_info:
                feedback_parts.append(tactical_info)
        
        return ' '.join(feedback_parts)
    
    def _extract_tactical_feedback(self, 
                                   move_data: Dict[str, Any],
                                   board_analysis: Dict) -> str:
        """
        Extract tactical feedback from board analysis.
        
        Args:
            move_data: Move information
            board_analysis: Board analysis results
            
        Returns:
            Tactical feedback string or empty string
        """
        feedback = []
        
        # Check if move creates threats
        if board_analysis.get('creates_attacks'):
            feedback.append("This creates new attacking opportunities.")
        
        # Check if move defends
        if board_analysis.get('defends_pieces'):
            feedback.append("This defends vulnerable pieces.")
        
        # Check if move removes threats
        if board_analysis.get('removes_threats'):
            feedback.append("This addresses immediate threats.")
        
        return ' '.join(feedback) if feedback else ''
