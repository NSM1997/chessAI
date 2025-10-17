"""
Machine Learning module for chess pattern recognition and NLP
"""

from .data_preprocessing import ChessBoardEncoder, TacticalThemeEncoder, ChessDataset
from .tactical_classifier import TacticalCNN, TacticalClassifierService

__all__ = [
    'ChessBoardEncoder',
    'TacticalThemeEncoder',
    'ChessDataset',
    'TacticalCNN',
    'TacticalClassifierService'
]

