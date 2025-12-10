"""
Tactical Analysis Service
Integrates CNN-based tactical pattern recognition with chess analysis
"""

import chess
import numpy as np
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
import sys
import os

logger = logging.getLogger(__name__)

# Try to import ML components
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from app.ml.data_preprocessing import ChessBoardEncoder
    from app.ml.tactical_classifier_pytorch import (
        TacticalClassifierService, 
        EnsembleTacticalClassifierService,
        PrecisionEnsembleService,
        HybridTacticalEnsemble
    )
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML components not available: {e}")
    ML_AVAILABLE = False


class TacticalAnalysisService:
    """
    Service for detecting tactical patterns using ML
    Integrates with ChessEngineService for enhanced explanations
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize tactical analysis service
        
        Args:
            model_path: Path to trained CNN model
        """
        self.is_available = ML_AVAILABLE
        self.board_encoder = None
        self.classifier = None
        
        if not ML_AVAILABLE:
            logger.info("Tactical ML classifier not available (PyTorch not installed)")
            return
        
        # Default model path
        if model_path is None:
            model_path = "backend/models/saved_models/tactical_classifier.pth"
        
        # Initialize encoders
        try:
            self.board_encoder = ChessBoardEncoder()
            logger.info("Board encoder initialized")
        except Exception as e:
            logger.error(f"Failed to initialize board encoder: {e}")
            self.is_available = False
            return
        
        # Try hybrid ensemble first (recall for common tactics + precision for critical themes)
        try:
            self.classifier = HybridTacticalEnsemble()
            if self.classifier.is_available:
                logger.info("Hybrid tactical ensemble initialised (Recall for common tactics, Precision for critical themes)")
            else:
                self.classifier = None
        except Exception as e:
            logger.warning(f"Could not initialise hybrid tactical ensemble: {e}")
            self.classifier = None
        
        # If ensemble is not available, fall back to single CNN model if present
        if self.classifier is None:
            if Path(model_path).exists():
                try:
                    # PyTorch version loads theme_names.json/checkpoint metadata automatically
                    self.classifier = TacticalClassifierService(model_path)
                    if self.classifier.is_available:
                        logger.info(f"Single-model tactical classifier loaded from {model_path}")
                    else:
                        self.classifier = None
                except Exception as e:
                    logger.warning(f"Could not load tactical classifier: {e}")
                    logger.info("Run training script to create model: python scripts/train_tactical_classifier.py")
                    self.classifier = None
            else:
                logger.info(f"No trained model found at {model_path}")
                logger.info("Tactical classification disabled. Train model with: python scripts/train_tactical_classifier.py")
                self.classifier = None
    
    async def analyze_tactics(self, 
                              board: chess.Board,
                              threshold: float = None,
                              top_k: int = 5) -> Dict[str, Any]:
        """
        Analyze tactical patterns in a position
        
        Args:
            board: Chess board position
            threshold: Confidence threshold for themes
            top_k: Number of top themes to return
            
        Returns:
            analysis: Dict with tactical themes and confidence scores
        """
        if not self.is_available or self.classifier is None:
            return {
                'available': False,
                'themes': [],
                'message': 'Tactical classifier not available'
            }
        
        try:
            # Encode board to tensor
            board_tensor = self.board_encoder.encode_board(board)
            
            # Classify tactical themes using PyTorch model
            # Note: HybridTacticalEnsemble doesn't use threshold param (uses internal thresholds)
            if hasattr(self.classifier, 'predict') and 'top_k' in self.classifier.predict.__code__.co_varnames:
                # HybridTacticalEnsemble
                themes = self.classifier.predict(board_tensor, top_k=top_k)
            else:
                # Legacy classifiers
                themes = self.classifier.predict(
                    board_tensor,
                    threshold=threshold if threshold else 0.3
                )
            
            # Limit to top_k themes
            if len(themes) > top_k:
                themes = themes[:top_k]
            
            return {
                'available': True,
                'themes': themes,
                'message': f"Detected {len(themes)} tactical patterns"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing tactics: {e}")
            return {
                'available': False,
                'themes': [],
                'error': str(e)
            }
    
    def enhance_explanation(self, 
                           base_explanation: str,
                           tactical_themes: List[Dict]) -> str:
        """
        Enhance a move explanation with detected tactical themes
        
        Args:
            base_explanation: Original explanation from chess engine
            tactical_themes: List of detected themes with confidence
            
        Returns:
            enhanced_explanation: Enriched explanation
        """
        if not tactical_themes:
            return base_explanation
        
        # Build tactical context
        theme_descriptions = {
            'fork': 'This move creates a fork, attacking multiple pieces simultaneously',
            'pin': 'This position involves a pin, restricting piece movement',
            'skewer': 'A skewer tactic is present, forcing the valuable piece to move',
            'discoveredAttack': 'This creates a discovered attack by moving a piece',
            'doubleAttack': 'Multiple pieces are under attack',
            'mate': 'Checkmate is threatened',
            'mateIn1': 'Checkmate can be delivered in one move',
            'mateIn2': 'Checkmate in two moves is available',
            'backRankMate': 'Back rank mate threat is present',
            'hangingPiece': 'A piece is hanging (undefended)',
            'trappedPiece': 'A piece is trapped and cannot escape',
            'sacrifice': 'This involves a tactical sacrifice',
            'deflection': 'This deflects a key defensive piece',
            'attraction': 'This attracts a piece to a vulnerable square',
            'clearance': 'This clears a key square or line',
            'xRayAttack': 'An X-ray attack is targeting through pieces',
        }
        
        # Get top theme
        top_theme = tactical_themes[0]
        theme_name = top_theme['theme']
        confidence = top_theme['confidence']
        
        # Add tactical context if confidence is high enough
        if confidence >= 0.6:
            tactical_note = theme_descriptions.get(
                theme_name,
                f"This position contains a {theme_name} pattern"
            )
            
            # Combine explanations
            if not base_explanation.endswith('.'):
                base_explanation += '.'
            
            enhanced = f"{base_explanation} {tactical_note}."
            
            # Add additional themes if multiple high-confidence detections
            if len(tactical_themes) > 1:
                additional = [t['theme'] for t in tactical_themes[1:3] if t['confidence'] >= 0.5]
                if additional:
                    enhanced += f" Also note: {', '.join(additional)}."
            
            return enhanced
        
        return base_explanation
    
    def get_tactical_motifs(self, themes: List[Dict]) -> List[str]:
        """
        Convert ML-detected themes to motif strings for API response
        
        Args:
            themes: List of detected themes
            
        Returns:
            motifs: List of tactical motif names
        """
        return [theme['theme'] for theme in themes if theme['confidence'] >= 0.5]


# Global instance (initialized on first use)
_tactical_service: Optional[TacticalAnalysisService] = None


def get_tactical_service() -> TacticalAnalysisService:
    """
    Get or create the global tactical analysis service
    
    Returns:
        service: TacticalAnalysisService instance
    """
    global _tactical_service
    
    if _tactical_service is None:
        _tactical_service = TacticalAnalysisService()
    
    return _tactical_service


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_tactical_analysis():
        """Test the tactical analysis service"""
        
        print("=== Tactical Analysis Service Test ===\n")
        
        # Initialize service
        service = TacticalAnalysisService()
        
        if not service.is_available:
            print("⚠️  Tactical analysis not available")
            print("Install TensorFlow: pip install tensorflow")
            return
        
        if service.classifier is None:
            print("⚠️  No trained model found")
            print("Train model with: python scripts/train_tactical_classifier.py")
            return
        
        # Test positions
        test_positions = [
            {
                'name': 'Italian Game Opening',
                'fen': 'r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4'
            },
            {
                'name': 'Back Rank Mate',
                'fen': '6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1'
            },
            {
                'name': 'Pin Position',
                'fen': 'r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5'
            }
        ]
        
        for pos in test_positions:
            print(f"\n{'='*50}")
            print(f"Position: {pos['name']}")
            print(f"FEN: {pos['fen']}")
            
            board = chess.Board(pos['fen'])
            
            # Analyze tactics
            analysis = await service.analyze_tactics(board, threshold=0.3, top_k=5)
            
            print(f"\nTactical Analysis:")
            print(f"  Available: {analysis['available']}")
            print(f"  Message: {analysis.get('message', 'N/A')}")
            
            if analysis['themes']:
                print(f"  Detected Themes:")
                for theme in analysis['themes']:
                    print(f"    - {theme['theme']}: {theme['confidence']:.2%}")
                
                # Test explanation enhancement
                base_explanation = "This is a strong move in the position."
                enhanced = service.enhance_explanation(base_explanation, analysis['themes'])
                print(f"\n  Base Explanation: {base_explanation}")
                print(f"  Enhanced: {enhanced}")
            else:
                print("  No tactical themes detected")
    
    # Run test
    asyncio.run(test_tactical_analysis())


