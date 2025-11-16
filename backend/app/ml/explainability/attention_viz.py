"""
Attention Visualization for Chess Transformer

Visualizes self-attention patterns to understand which board squares
the model focuses on when classifying tactical themes.

RESEARCH CONTRIBUTION:
- Novel visualization of chess position attention
- Interpretable Transformer explanations
- Square-to-square interaction analysis
"""

import torch
import torch.nn.functional as F
import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AttentionVisualizer:
    """
    Visualize attention patterns in Transformer-based tactical classifier
    
    Usage:
        viz = AttentionVisualizer(transformer_model)
        attention_maps = viz.get_attention_maps(board_tensor)
        viz.visualize_square_attention(attention_maps, square='e4')
    """
    
    def __init__(self, model: torch.nn.Module):
        """
        Args:
            model: TacticalTransformer or TacticalTransformerLight model
        """
        self.model = model
        self.attention_weights = []
        self._register_hooks()
    
    def _register_hooks(self):
        """Register hooks to capture attention weights"""
        
        def attention_hook(module, input, output):
            """
            Capture attention weights from MultiheadAttention
            output is (attn_output, attn_weights)
            """
            if isinstance(output, tuple) and len(output) >= 2:
                attn_weights = output[1]
                if attn_weights is not None:
                    self.attention_weights.append(attn_weights.detach())
        
        # Register hooks on all attention layers
        for name, module in self.model.named_modules():
            if isinstance(module, torch.nn.MultiheadAttention):
                module.register_forward_hook(attention_hook)
                logger.info(f"Registered attention hook on: {name}")
    
    def get_attention_maps(
        self, 
        board_tensor: torch.Tensor,
        return_all_layers: bool = True
    ) -> List[torch.Tensor]:
        """
        Extract attention weights from all Transformer layers
        
        Args:
            board_tensor: (1, 12, 8, 8) board representation
            return_all_layers: If False, only return last layer attention
            
        Returns:
            List of attention weight tensors
            Each tensor: (num_heads, 64, 64) or (1, 64, 64) if averaged
        """
        self.attention_weights = []
        self.model.eval()
        
        with torch.no_grad():
            _ = self.model(board_tensor)
        
        if not return_all_layers and len(self.attention_weights) > 0:
            return [self.attention_weights[-1]]
        
        return self.attention_weights
    
    def get_aggregated_attention(
        self, 
        board_tensor: torch.Tensor,
        method: str = 'mean'
    ) -> np.ndarray:
        """
        Get aggregated attention across all heads and layers
        
        Args:
            board_tensor: (1, 12, 8, 8)
            method: 'mean', 'max', or 'last_layer'
            
        Returns:
            attention_matrix: (64, 64) aggregated attention
        """
        attention_maps = self.get_attention_maps(board_tensor)
        
        if method == 'last_layer':
            # Use only last layer, average across heads
            attn = attention_maps[-1]  # (batch, num_heads, 64, 64)
            attn = attn[0].mean(dim=0)  # (64, 64)
            
        elif method == 'mean':
            # Average across all layers and heads
            all_attn = []
            for attn in attention_maps:
                attn = attn[0].mean(dim=0)  # Average heads
                all_attn.append(attn)
            attn = torch.stack(all_attn).mean(dim=0)  # Average layers
            
        elif method == 'max':
            # Maximum attention across all layers
            all_attn = []
            for attn in attention_maps:
                attn = attn[0].max(dim=0)[0]  # Max across heads
                all_attn.append(attn)
            attn = torch.stack(all_attn).max(dim=0)[0]  # Max across layers
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return attn.cpu().numpy()
    
    def visualize_attention_matrix(
        self, 
        attention_matrix: np.ndarray,
        save_path: Optional[str] = None
    ):
        """
        Visualize 64x64 attention matrix as heatmap
        
        Args:
            attention_matrix: (64, 64) square-to-square attention
            save_path: Optional path to save figure
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot heatmap
        sns.heatmap(
            attention_matrix, 
            cmap='YlOrRd', 
            square=True,
            cbar_kws={'label': 'Attention Weight'},
            ax=ax
        )
        
        # Add chess board labels
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
        labels = [f"{f}{r}" for r in ranks for f in files]
        
        ax.set_xticks(np.arange(64) + 0.5)
        ax.set_yticks(np.arange(64) + 0.5)
        ax.set_xticklabels(labels, rotation=90, fontsize=6)
        ax.set_yticklabels(labels, fontsize=6)
        
        ax.set_title('Transformer Attention: Square-to-Square Interactions', fontsize=14)
        ax.set_xlabel('Target Square', fontsize=12)
        ax.set_ylabel('Source Square', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Saved attention matrix to {save_path}")
        
        plt.close()
    
    def visualize_square_attention(
        self, 
        board_tensor: torch.Tensor,
        square: str,
        board_fen: Optional[str] = None,
        save_path: Optional[str] = None
    ):
        """
        Visualize attention FROM one specific square to all others
        
        Args:
            board_tensor: (1, 12, 8, 8)
            square: Chess square notation ('e4', 'a1', etc.)
            board_fen: Optional FEN for board overlay
            save_path: Optional save path
        """
        import matplotlib.pyplot as plt
        
        # Get aggregated attention
        attention_matrix = self.get_aggregated_attention(board_tensor, method='mean')
        
        # Convert square to index
        square_idx = self._square_to_index(square)
        
        # Get attention from this square to all others
        attention_from_square = attention_matrix[square_idx]  # (64,)
        
        # Reshape to 8x8 board
        attention_board = attention_from_square.reshape(8, 8)
        
        # Visualize
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Flip for correct chess orientation
        attention_display = np.flipud(attention_board)
        
        im = ax.imshow(attention_display, cmap='YlOrRd', interpolation='bilinear')
        plt.colorbar(im, ax=ax, label='Attention Weight')
        
        # Chess board labels
        ax.set_xticks(range(8))
        ax.set_yticks(range(8))
        ax.set_xticklabels(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
        ax.set_yticklabels(['8', '7', '6', '5', '4', '3', '2', '1'])
        
        ax.set_title(f'Attention from {square.upper()} to other squares', fontsize=14)
        
        # Highlight source square
        source_file = ord(square[0]) - ord('a')
        source_rank = 8 - int(square[1])
        ax.scatter(source_file, source_rank, s=500, c='blue', marker='x', linewidths=3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Saved square attention to {save_path}")
        
        plt.close()
    
    def visualize_head_specialization(
        self, 
        board_tensor: torch.Tensor,
        layer_idx: int = -1,
        save_path: Optional[str] = None
    ):
        """
        Visualize what different attention heads learn
        
        Args:
            board_tensor: (1, 12, 8, 8)
            layer_idx: Which transformer layer (default: last layer)
            save_path: Optional save path
        """
        import matplotlib.pyplot as plt
        
        attention_maps = self.get_attention_maps(board_tensor)
        
        if len(attention_maps) == 0:
            logger.warning("No attention maps captured")
            return
        
        # Get attention from specific layer
        attn = attention_maps[layer_idx]  # (1, num_heads, 64, 64)
        attn = attn[0]  # (num_heads, 64, 64)
        
        num_heads = attn.shape[0]
        
        # Plot each head
        fig, axes = plt.subplots(2, num_heads // 2, figsize=(16, 8))
        axes = axes.flatten()
        
        for head_idx in range(num_heads):
            ax = axes[head_idx]
            
            # Average attention pattern for this head
            head_attn = attn[head_idx].mean(dim=0).cpu().numpy()  # (64,)
            head_attn_board = head_attn.reshape(8, 8)
            
            im = ax.imshow(np.flipud(head_attn_board), cmap='viridis')
            ax.set_title(f'Head {head_idx + 1}', fontsize=10)
            ax.set_xticks([])
            ax.set_yticks([])
            plt.colorbar(im, ax=ax, fraction=0.046)
        
        plt.suptitle(f'Attention Head Specialization (Layer {layer_idx})', fontsize=14)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Saved head specialization to {save_path}")
        
        plt.close()
    
    def get_important_squares(
        self, 
        board_tensor: torch.Tensor,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Identify most important squares for classification
        
        Args:
            board_tensor: (1, 12, 8, 8)
            top_k: Number of top squares to return
            
        Returns:
            List of (square_name, importance_score) tuples
        """
        # Get aggregated attention
        attention_matrix = self.get_aggregated_attention(board_tensor, method='mean')
        
        # Sum attention received by each square (column-wise sum)
        importance = attention_matrix.sum(axis=0)  # (64,)
        
        # Get top-k squares
        top_indices = np.argsort(importance)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            square_name = self._index_to_square(int(idx))
            score = importance[idx]
            results.append((square_name, float(score)))
        
        return results
    
    @staticmethod
    def _square_to_index(square: str) -> int:
        """Convert chess square notation to index (0-63)"""
        file = ord(square[0]) - ord('a')  # 0-7
        rank = int(square[1]) - 1  # 0-7
        return rank * 8 + file
    
    @staticmethod
    def _index_to_square(index: int) -> str:
        """Convert index (0-63) to chess square notation"""
        rank = index // 8
        file = index % 8
        return f"{chr(ord('a') + file)}{rank + 1}"


def compare_attention_vs_gradcam(
    transformer_model,
    cnn_model,
    board_tensor: torch.Tensor,
    board_fen: str,
    save_dir: str
):
    """
    Compare Transformer attention with CNN Grad-CAM
    Research question: Do different architectures focus on same squares?
    
    Args:
        transformer_model: Trained Transformer
        cnn_model: Trained CNN
        board_tensor: (1, 12, 8, 8)
        board_fen: FEN string
        save_dir: Directory to save comparison plots
    """
    from pathlib import Path
    from .gradcam import ChessGradCAM
    import matplotlib.pyplot as plt
    
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Get Transformer attention
    attn_viz = AttentionVisualizer(transformer_model)
    attention_matrix = attn_viz.get_aggregated_attention(board_tensor, method='mean')
    attention_importance = attention_matrix.sum(axis=0).reshape(8, 8)
    
    # Get CNN Grad-CAM
    # Find last conv layer
    target_layer = None
    for module in cnn_model.modules():
        if isinstance(module, torch.nn.Conv2d):
            target_layer = module
    
    gradcam = ChessGradCAM(cnn_model, target_layer)
    gradcam_heatmap = gradcam.generate_heatmap(board_tensor, target_class=0)
    
    # Plot comparison
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Transformer attention
    axes[0].imshow(np.flipud(attention_importance), cmap='YlOrRd')
    axes[0].set_title('Transformer Attention', fontsize=14)
    axes[0].set_xticks(range(8))
    axes[0].set_xticklabels(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
    axes[0].set_yticks(range(8))
    axes[0].set_yticklabels(['8', '7', '6', '5', '4', '3', '2', '1'])
    
    # CNN Grad-CAM
    axes[1].imshow(np.flipud(gradcam_heatmap), cmap='YlOrRd')
    axes[1].set_title('CNN Grad-CAM', fontsize=14)
    axes[1].set_xticks(range(8))
    axes[1].set_xticklabels(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
    axes[1].set_yticks(range(8))
    axes[1].set_yticklabels(['8', '7', '6', '5', '4', '3', '2', '1'])
    
    # Difference
    diff = np.abs(attention_importance - gradcam_heatmap)
    axes[2].imshow(np.flipud(diff), cmap='RdBu_r')
    axes[2].set_title('Absolute Difference', fontsize=14)
    axes[2].set_xticks(range(8))
    axes[2].set_xticklabels(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
    axes[2].set_yticks(range(8))
    axes[2].set_yticklabels(['8', '7', '6', '5', '4', '3', '2', '1'])
    
    plt.suptitle('Explainability Comparison: Transformer vs CNN', fontsize=16)
    plt.tight_layout()
    
    save_path = save_dir / 'attention_vs_gradcam_comparison.png'
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    logger.info(f"Saved comparison to {save_path}")
    plt.close()


if __name__ == "__main__":
    """Test attention visualization"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
    from backend.app.ml.tactical_transformer import TacticalTransformerLight
    
    # Create dummy model
    model = TacticalTransformerLight(num_classes=20)
    
    # Create visualizer
    viz = AttentionVisualizer(model)
    
    # Test on random board
    test_board = torch.randn(1, 12, 8, 8)
    
    # Get attention maps
    attention_maps = viz.get_attention_maps(test_board)
    
    print(f"✅ Attention visualization working!")
    print(f"   Captured {len(attention_maps)} attention layers")
    if len(attention_maps) > 0:
        print(f"   Attention shape: {attention_maps[0].shape}")
    
    # Test important squares
    important = viz.get_important_squares(test_board, top_k=5)
    print(f"   Top 5 important squares: {important}")

