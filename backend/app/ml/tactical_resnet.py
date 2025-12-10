"""
ResNet (Residual Network) for Tactical Pattern Classification
Uses skip connections for better gradient flow and deeper architecture
Inspired by AlphaZero and Leela Chess Zero
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResidualBlock(nn.Module):
    """
    Residual block with skip connection
    
    Architecture:
    - Conv2d -> BatchNorm -> ReLU -> Conv2d -> BatchNorm
    - Skip connection: input + output
    - Final ReLU
    """
    
    def __init__(self, in_channels: int, out_channels: int):
        super(ResidualBlock, self).__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # If input and output channels differ, use 1x1 conv for skip connection
        self.skip_conv = None
        if in_channels != out_channels:
            self.skip_conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)
            self.skip_bn = nn.BatchNorm2d(out_channels)
    
    def forward(self, x):
        identity = x
        
        # First conv block
        out = self.conv1(x)
        out = self.bn1(out)
        out = F.relu(out)
        
        # Second conv block
        out = self.conv2(out)
        out = self.bn2(out)
        
        # Skip connection
        if self.skip_conv is not None:
            identity = self.skip_conv(identity)
            identity = self.skip_bn(identity)
        
        # Add skip connection and apply ReLU
        out += identity
        out = F.relu(out)
        
        return out


class TacticalResNet(nn.Module):
    """
    ResNet architecture for chess tactical pattern recognition
    
    Architecture:
    - Input: 8x8x12 board representation
    - Initial conv block
    - Multiple residual blocks (configurable depth)
    - Global Average Pooling
    - Fully connected layers
    - Output: Multi-label classification
    
    Advantages over vanilla CNN:
    - Deeper architecture without gradient vanishing
    - Skip connections preserve information flow
    - Used in top chess engines (AlphaZero, Leela)
    """
    
    def __init__(
        self, 
        num_classes: int = 20, 
        num_residual_blocks: int = 5,
        base_channels: int = 128,
        dropout_rate: float = 0.3
    ):
        super(TacticalResNet, self).__init__()
        
        self.num_classes = num_classes
        self.num_residual_blocks = num_residual_blocks
        self.base_channels = base_channels
        self.dropout_rate = dropout_rate
        
        # Initial convolutional layer
        self.initial_conv = nn.Sequential(
            nn.Conv2d(12, base_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(base_channels),
            nn.ReLU()
        )
        
        # Residual blocks
        self.residual_blocks = nn.ModuleList([
            ResidualBlock(base_channels, base_channels) 
            for _ in range(num_residual_blocks)
        ])
        
        # Global Average Pooling (reduces 8x8 spatial dims to 1x1)
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Fully connected layers
        self.fc_layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(base_channels, 256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_classes),
            nn.Sigmoid()  # Multi-label classification
        )
        
        logger.info(f"TacticalResNet initialized:")
        logger.info(f"  - Residual blocks: {num_residual_blocks}")
        logger.info(f"  - Base channels: {base_channels}")
        logger.info(f"  - Total parameters: {self.count_parameters():,}")
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: Input tensor (batch, 12, 8, 8)
        
        Returns:
            Output predictions (batch, num_classes)
        """
        # Initial conv
        x = self.initial_conv(x)  # -> (batch, base_channels, 8, 8)
        
        # Residual blocks
        for block in self.residual_blocks:
            x = block(x)  # -> (batch, base_channels, 8, 8)
        
        # Global pooling
        x = self.global_avg_pool(x)  # -> (batch, base_channels, 1, 1)
        
        # Fully connected layers
        x = self.fc_layers(x)  # -> (batch, num_classes)
        
        return x
    
    def count_parameters(self) -> int:
        """Count total trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class TacticalResNetLight(nn.Module):
    """
    Lighter version of ResNet for faster training/inference
    Fewer residual blocks and channels
    """
    
    def __init__(self, num_classes: int = 20, dropout_rate: float = 0.3):
        super(TacticalResNetLight, self).__init__()
        
        self.num_classes = num_classes
        self.dropout_rate = dropout_rate
        
        # Initial conv
        self.initial_conv = nn.Sequential(
            nn.Conv2d(12, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU()
        )
        
        # 3 Residual blocks
        self.res_block1 = ResidualBlock(64, 64)
        self.res_block2 = ResidualBlock(64, 128)
        self.res_block3 = ResidualBlock(128, 128)
        
        # Global pooling
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # FC layers
        self.fc_layers = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, num_classes),
            nn.Sigmoid()
        )
        
        logger.info(f"TacticalResNetLight initialized with {self.count_parameters():,} parameters")
    
    def forward(self, x):
        x = self.initial_conv(x)
        x = self.res_block1(x)
        x = self.res_block2(x)
        x = self.res_block3(x)
        x = self.global_avg_pool(x)
        x = self.fc_layers(x)
        return x
    
    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


if __name__ == "__main__":
    # Test ResNet architectures
    print("Testing TacticalResNet...")
    
    # Full ResNet
    model = TacticalResNet(num_classes=20, num_residual_blocks=5, base_channels=128)
    test_input = torch.randn(4, 12, 8, 8)
    output = model(test_input)
    print(f"Full ResNet:")
    print(f"  Input shape: {test_input.shape}")
    print(f"  Output shape: {output.shape}")
    print(f"  Parameters: {model.count_parameters():,}")
    print(f"  Output range: [{output.min():.3f}, {output.max():.3f}]")
    
    print("\nTesting TacticalResNetLight...")
    
    # Light ResNet
    model_light = TacticalResNetLight(num_classes=20)
    output_light = model_light(test_input)
    print(f"Light ResNet:")
    print(f"  Output shape: {output_light.shape}")
    print(f"  Parameters: {model_light.count_parameters():,}")
    print(f"  Output range: [{output_light.min():.3f}, {output_light.max():.3f}]")
    
    print("\n✅ ResNet models working!")
