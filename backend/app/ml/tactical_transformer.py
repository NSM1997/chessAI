"""
Transformer/Attention-Based Model for Tactical Pattern Classification
Uses self-attention to capture long-range piece interactions
Inspired by Vision Transformers (ViT) and modern NLP architectures
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PositionalEncoding(nn.Module):
    """
    Adds positional information to square embeddings
    Since chess board has fixed 8x8 structure, we use learnable positional embeddings
    """
    
    def __init__(self, d_model: int, max_len: int = 64):
        super(PositionalEncoding, self).__init__()
        self.pos_embedding = nn.Parameter(torch.randn(1, max_len, d_model))
    
    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, d_model)
        Returns:
            x with positional encoding added
        """
        return x + self.pos_embedding[:, :x.size(1), :]


class MultiHeadAttentionBlock(nn.Module):
    """
    Multi-head self-attention block with residual connection and layer norm
    """
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super(MultiHeadAttentionBlock, self).__init__()
        
        self.attention = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True
        )
        
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, d_model)
        Returns:
            Attention output with residual connection
        """
        # Self-attention with residual
        attn_output, _ = self.attention(x, x, x)
        x = x + self.dropout(attn_output)
        x = self.norm(x)
        return x


class FeedForwardBlock(nn.Module):
    """
    Feed-forward network with residual connection
    """
    
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super(FeedForwardBlock, self).__init__()
        
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
        
        self.norm = nn.LayerNorm(d_model)
    
    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, d_model)
        Returns:
            FFN output with residual connection
        """
        x = x + self.ff(x)
        x = self.norm(x)
        return x


class TransformerEncoderLayer(nn.Module):
    """
    Single Transformer encoder layer
    Combines attention and feed-forward blocks
    """
    
    def __init__(
        self, 
        d_model: int, 
        num_heads: int, 
        d_ff: int, 
        dropout: float = 0.1
    ):
        super(TransformerEncoderLayer, self).__init__()
        
        self.attention_block = MultiHeadAttentionBlock(d_model, num_heads, dropout)
        self.ff_block = FeedForwardBlock(d_model, d_ff, dropout)
    
    def forward(self, x):
        x = self.attention_block(x)
        x = self.ff_block(x)
        return x


class TacticalTransformer(nn.Module):
    """
    Transformer-based architecture for chess tactical pattern recognition
    
    Architecture:
    - Input: 8x8x12 board representation
    - Flatten to 64 squares, each with 12-dim piece encoding
    - Linear projection to embedding dimension
    - Positional encoding
    - Multiple Transformer encoder layers
    - Classification head with global pooling
    
    Advantages:
    - Captures long-range dependencies (e.g., discovered attacks across board)
    - Self-attention learns which pieces/squares are important
    - No spatial inductive bias (learns board structure from data)
    - State-of-the-art in many sequence modeling tasks
    """
    
    def __init__(
        self,
        num_classes: int = 20,
        d_model: int = 128,
        num_heads: int = 8,
        num_layers: int = 4,
        d_ff: int = 512,
        dropout: float = 0.1
    ):
        super(TacticalTransformer, self).__init__()
        
        self.num_classes = num_classes
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        
        # Input projection: 12 piece channels -> d_model
        self.input_projection = nn.Linear(12, d_model)
        
        # Positional encoding for 64 squares
        self.pos_encoding = PositionalEncoding(d_model, max_len=64)
        
        # Transformer encoder layers
        self.transformer_layers = nn.ModuleList([
            TransformerEncoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, 256),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes),
            nn.Sigmoid()  # Multi-label classification
        )
        
        logger.info(f"TacticalTransformer initialized:")
        logger.info(f"  - Embedding dim: {d_model}")
        logger.info(f"  - Attention heads: {num_heads}")
        logger.info(f"  - Encoder layers: {num_layers}")
        logger.info(f"  - Total parameters: {self.count_parameters():,}")
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: Input tensor (batch, 12, 8, 8) - chess board
        
        Returns:
            Output predictions (batch, num_classes)
        """
        batch_size = x.size(0)
        
        # Reshape: (batch, 12, 8, 8) -> (batch, 64, 12)
        # Each of 64 squares has 12-dim piece encoding
        x = x.view(batch_size, 12, 64).transpose(1, 2)  # -> (batch, 64, 12)
        
        # Project to embedding dimension
        x = self.input_projection(x)  # -> (batch, 64, d_model)
        
        # Add positional encoding
        x = self.pos_encoding(x)
        
        # Transformer encoder layers
        for layer in self.transformer_layers:
            x = layer(x)  # -> (batch, 64, d_model)
        
        # Global average pooling over all squares
        x = x.mean(dim=1)  # -> (batch, d_model)
        
        # Classification
        x = self.classifier(x)  # -> (batch, num_classes)
        
        return x
    
    def count_parameters(self) -> int:
        """Count total trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def get_attention_weights(self, x):
        """
        Extract attention weights for interpretability
        
        Args:
            x: Input tensor (batch, 12, 8, 8)
        
        Returns:
            List of attention weight tensors from each layer
        """
        batch_size = x.size(0)
        x = x.view(batch_size, 12, 64).transpose(1, 2)
        x = self.input_projection(x)
        x = self.pos_encoding(x)
        
        attention_weights = []
        for layer in self.transformer_layers:
            # Get attention from the layer
            attn_output, attn_weights = layer.attention_block.attention(x, x, x)
            attention_weights.append(attn_weights.detach())
            x = layer(x)
        
        return attention_weights


class TacticalTransformerLight(nn.Module):
    """
    Lighter Transformer for faster training
    Fewer layers, smaller embedding dimension
    """
    
    def __init__(
        self,
        num_classes: int = 20,
        d_model: int = 64,
        num_heads: int = 4,
        num_layers: int = 2,
        dropout: float = 0.1
    ):
        super(TacticalTransformerLight, self).__init__()
        
        self.num_classes = num_classes
        self.d_model = d_model
        
        # Input projection
        self.input_projection = nn.Linear(12, d_model)
        
        # Positional encoding
        self.pos_encoding = PositionalEncoding(d_model, max_len=64)
        
        # Transformer layers
        self.transformer_layers = nn.ModuleList([
            TransformerEncoderLayer(d_model, num_heads, d_model * 4, dropout)
            for _ in range(num_layers)
        ])
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, num_classes),
            nn.Sigmoid()
        )
        
        logger.info(f"TacticalTransformerLight initialized with {self.count_parameters():,} parameters")
    
    def forward(self, x):
        batch_size = x.size(0)
        x = x.view(batch_size, 12, 64).transpose(1, 2)
        x = self.input_projection(x)
        x = self.pos_encoding(x)
        
        for layer in self.transformer_layers:
            x = layer(x)
        
        x = x.mean(dim=1)
        x = self.classifier(x)
        return x
    
    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


if __name__ == "__main__":
    # Test Transformer architectures
    print("Testing TacticalTransformer...")
    
    # Full Transformer
    model = TacticalTransformer(
        num_classes=20, 
        d_model=128, 
        num_heads=8, 
        num_layers=4
    )
    test_input = torch.randn(4, 12, 8, 8)
    output = model(test_input)
    print(f"Full Transformer:")
    print(f"  Input shape: {test_input.shape}")
    print(f"  Output shape: {output.shape}")
    print(f"  Parameters: {model.count_parameters():,}")
    print(f"  Output range: [{output.min():.3f}, {output.max():.3f}]")
    
    print("\nTesting TacticalTransformerLight...")
    
    # Light Transformer
    model_light = TacticalTransformerLight(num_classes=20, d_model=64, num_layers=2)
    output_light = model_light(test_input)
    print(f"Light Transformer:")
    print(f"  Output shape: {output_light.shape}")
    print(f"  Parameters: {model_light.count_parameters():,}")
    print(f"  Output range: [{output_light.min():.3f}, {output_light.max():.3f}]")
    
    print("\n✅ Transformer models working!")
