"""
Explainability module for chess tactical classifiers

Implements various XAI techniques:
- Grad-CAM for CNNs
- Attention visualization for Transformers  
- Saliency maps
- Integrated Gradients
- SHAP values

This is the RESEARCH CONTRIBUTION component of the thesis.
"""

from .gradcam import ChessGradCAM
from .attention_viz import AttentionVisualizer
from .saliency import SaliencyAnalyzer
from .metrics import (
    faithfulness_score,
    consistency_score,
    human_agreement_score
)

__all__ = [
    'ChessGradCAM',
    'AttentionVisualizer', 
    'SaliencyAnalyzer',
    'faithfulness_score',
    'consistency_score',
    'human_agreement_score'
]

