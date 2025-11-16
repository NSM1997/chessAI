"""
Saliency-based Explanation Methods

Additional explainability techniques:
- Vanilla Gradients
- Integrated Gradients
- SmoothGrad

RESEARCH CONTRIBUTION:
- Compare multiple XAI techniques for chess
- Identify which methods work best for tactical classification
"""

import torch
import torch.nn.functional as F
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SaliencyAnalyzer:
    """
    Generate saliency maps showing input importance
    """
    
    def __init__(self, model: torch.nn.Module):
        self.model = model
        
    def vanilla_gradients(
        self, 
        board_tensor: torch.Tensor, 
        target_class: int
    ) -> np.ndarray:
        """
        Simple gradient-based saliency
        
        Args:
            board_tensor: (1, 12, 8, 8)
            target_class: Tactical theme index
            
        Returns:
            saliency: (8, 8) importance map
        """
        self.model.eval()
        board_tensor = board_tensor.requires_grad_(True)
        
        # Forward pass
        output = self.model(board_tensor)
        
        # Backward for target class
        self.model.zero_grad()
        output[0, target_class].backward()
        
        # Get gradients
        gradients = board_tensor.grad  # (1, 12, 8, 8)
        
        # Aggregate across piece channels (take max absolute value)
        saliency = gradients[0].abs().max(dim=0)[0]  # (8, 8)
        
        # Normalize
        saliency = saliency.cpu().numpy()
        if saliency.max() > 0:
            saliency = saliency / saliency.max()
        
        return saliency
    
    def integrated_gradients(
        self,
        board_tensor: torch.Tensor,
        target_class: int,
        baseline: Optional[torch.Tensor] = None,
        steps: int = 50
    ) -> np.ndarray:
        """
        Integrated Gradients (Sundararajan et al., 2017)
        More robust than vanilla gradients
        
        Args:
            board_tensor: (1, 12, 8, 8)
            target_class: Tactical theme
            baseline: Baseline input (default: empty board)
            steps: Integration steps
            
        Returns:
            attribution: (8, 8) importance map
        """
        self.model.eval()
        
        if baseline is None:
            # Empty board as baseline
            baseline = torch.zeros_like(board_tensor)
        
        # Generate interpolated inputs
        alphas = torch.linspace(0, 1, steps)
        
        gradients = []
        for alpha in alphas:
            interpolated = baseline + alpha * (board_tensor - baseline)
            interpolated = interpolated.requires_grad_(True)
            
            output = self.model(interpolated)
            self.model.zero_grad()
            output[0, target_class].backward()
            
            gradients.append(interpolated.grad)
        
        # Average gradients
        avg_gradients = torch.stack(gradients).mean(dim=0)
        
        # Multiply by input difference
        attribution = (board_tensor - baseline) * avg_gradients
        
        # Aggregate across channels
        attribution = attribution[0].abs().max(dim=0)[0].cpu().numpy()
        
        # Normalize
        if attribution.max() > 0:
            attribution = attribution / attribution.max()
        
        return attribution
    
    def smooth_grad(
        self,
        board_tensor: torch.Tensor,
        target_class: int,
        num_samples: int = 50,
        noise_level: float = 0.1
    ) -> np.ndarray:
        """
        SmoothGrad (Smilkov et al., 2017)
        Reduces noise in gradient-based methods
        
        Args:
            board_tensor: (1, 12, 8, 8)
            target_class: Tactical theme
            num_samples: Number of noisy samples
            noise_level: Std of Gaussian noise
            
        Returns:
            smooth_saliency: (8, 8) smoothed importance map
        """
        self.model.eval()
        
        saliencies = []
        for _ in range(num_samples):
            # Add Gaussian noise
            noise = torch.randn_like(board_tensor) * noise_level
            noisy_input = board_tensor + noise
            noisy_input = torch.clamp(noisy_input, 0, 1)
            noisy_input = noisy_input.requires_grad_(True)
            
            # Compute gradients
            output = self.model(noisy_input)
            self.model.zero_grad()
            output[0, target_class].backward()
            
            saliency = noisy_input.grad[0].abs().max(dim=0)[0]
            saliencies.append(saliency)
        
        # Average across samples
        smooth_saliency = torch.stack(saliencies).mean(dim=0).cpu().numpy()
        
        # Normalize
        if smooth_saliency.max() > 0:
            smooth_saliency = smooth_saliency / smooth_saliency.max()
        
        return smooth_saliency


if __name__ == "__main__":
    """Test saliency methods"""
    print("✅ Saliency module loaded")

