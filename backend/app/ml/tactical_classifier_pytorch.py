"""
Tactical Pattern Classifier using PyTorch CNN
Classifies chess positions into tactical themes (fork, pin, skewer, etc.)
Compatible with Python 3.12+
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path
import json
import logging
from typing import Dict, List, Tuple, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TacticalCNN(nn.Module):
    """
    Convolutional Neural Network for tactical pattern recognition in chess positions.
    
    Architecture:
    - Input: 8x8x12 board representation (12 piece types)
    - 3 Conv blocks (Conv2d -> BatchNorm -> ReLU -> MaxPool)
    - 2 Dense layers with Dropout
    - Output: Multi-label classification (sigmoid activation)
    """
    
    def __init__(self, num_classes: int = 20, dropout_rate: float = 0.5):
        super(TacticalCNN, self).__init__()
        
        self.num_classes = num_classes
        self.dropout_rate = dropout_rate
        
        # Convolutional blocks
        self.conv_block1 = nn.Sequential(
            nn.Conv2d(in_channels=12, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)  # 8x8 -> 4x4
        )
        
        self.conv_block2 = nn.Sequential(
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)  # 4x4 -> 2x2
        )
        
        self.conv_block3 = nn.Sequential(
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU()
        )
        
        # Flatten layer
        self.flatten = nn.Flatten()
        
        # Calculate flattened size: 2x2x256 = 1024
        flattened_size = 2 * 2 * 256
        
        # Dense layers
        self.dense_layers = nn.Sequential(
            nn.Linear(flattened_size, 512),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, num_classes),
            nn.Sigmoid()  # Multi-label classification
        )
        
        logger.info(f"TacticalCNN initialized with {self.count_parameters():,} parameters")
    
    def forward(self, x):
        """Forward pass through the network"""
        # Input: (batch, 12, 8, 8)
        x = self.conv_block1(x)  # -> (batch, 64, 4, 4)
        x = self.conv_block2(x)  # -> (batch, 128, 2, 2)
        x = self.conv_block3(x)  # -> (batch, 256, 2, 2)
        x = self.flatten(x)      # -> (batch, 1024)
        x = self.dense_layers(x) # -> (batch, num_classes)
        return x
    
    def count_parameters(self) -> int:
        """Count total trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class ResidualBlock(nn.Module):
    """Residual block for ResNet architecture"""
    
    def __init__(self, in_channels, out_channels, stride=1):
        super(ResidualBlock, self).__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                              stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3,
                              stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # Shortcut connection
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, 
                         stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        residual = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        out += self.shortcut(residual)
        out = self.relu(out)
        
        return out


class TacticalResNet(nn.Module):
    """
    ResNet-based architecture for tactical pattern recognition.
    Uses residual connections for better gradient flow.
    """
    
    def __init__(self, num_classes: int = 20, dropout_rate: float = 0.3):
        super(TacticalResNet, self).__init__()
        
        self.num_classes = num_classes
        self.dropout_rate = dropout_rate
        
        # Initial convolution
        self.conv1 = nn.Sequential(
            nn.Conv2d(12, 64, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )
        
        # Residual blocks
        self.layer1 = self._make_layer(64, 64, 2, stride=1)
        self.layer2 = self._make_layer(64, 128, 2, stride=2)
        self.layer3 = self._make_layer(128, 256, 2, stride=2)
        
        # Global average pooling
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Classifier
        self.fc = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_classes),
            nn.Sigmoid()
        )
        
        logger.info(f"TacticalResNet initialized with {self.count_parameters():,} parameters")
    
    def _make_layer(self, in_channels, out_channels, num_blocks, stride):
        layers = []
        layers.append(ResidualBlock(in_channels, out_channels, stride))
        for _ in range(1, num_blocks):
            layers.append(ResidualBlock(out_channels, out_channels))
        return nn.Sequential(*layers)
    
    def forward(self, x):
        # Input: (batch, 12, 8, 8)
        x = self.conv1(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x
    
    def count_parameters(self) -> int:
        """Count total trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class Swish(nn.Module):
    """Swish activation function (x * sigmoid(x)) - used in EfficientNet"""
    def forward(self, x):
        return x * torch.sigmoid(x)


class SEBlock(nn.Module):
    """Squeeze-and-Excitation block - core of EfficientNet"""
    def __init__(self, in_channels, reduction=4):
        super(SEBlock, self).__init__()
        self.squeeze = nn.AdaptiveAvgPool2d(1)
        self.excitation = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // reduction, 1),
            Swish(),
            nn.Conv2d(in_channels // reduction, in_channels, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return x * self.excitation(self.squeeze(x))


class MBConvBlock(nn.Module):
    """Mobile Inverted Bottleneck Convolution - EfficientNet building block"""
    def __init__(self, in_channels, out_channels, expand_ratio, stride, kernel_size=3):
        super(MBConvBlock, self).__init__()
        self.stride = stride
        self.use_residual = (stride == 1 and in_channels == out_channels)
        
        hidden_dim = in_channels * expand_ratio
        
        layers = []
        # Expansion phase (if needed)
        if expand_ratio != 1:
            layers.extend([
                nn.Conv2d(in_channels, hidden_dim, 1, bias=False),
                nn.BatchNorm2d(hidden_dim),
                Swish()
            ])
        
        # Depthwise convolution
        layers.extend([
            nn.Conv2d(hidden_dim, hidden_dim, kernel_size, stride, 
                     padding=kernel_size//2, groups=hidden_dim, bias=False),
            nn.BatchNorm2d(hidden_dim),
            Swish()
        ])
        
        # Squeeze-and-Excitation
        layers.append(SEBlock(hidden_dim))
        
        # Projection phase
        layers.extend([
            nn.Conv2d(hidden_dim, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels)
        ])
        
        self.conv = nn.Sequential(*layers)
    
    def forward(self, x):
        if self.use_residual:
            return x + self.conv(x)
        return self.conv(x)


class TacticalEfficientNet(nn.Module):
    """
    EfficientNet-B0 adapted for chess tactical pattern recognition.
    
    Key features:
    - Compound scaling (depth, width, resolution)
    - MBConv blocks with squeeze-excitation
    - Swish activation for better gradients
    - Efficient parameter usage
    
    Expected to achieve ~76-78% precision (better than ResNet's 74.7%)
    """
    
    def __init__(self, num_classes: int = 20, dropout_rate: float = 0.3):
        super(TacticalEfficientNet, self).__init__()
        
        self.num_classes = num_classes
        self.dropout_rate = dropout_rate
        
        # Stem: Initial convolution
        self.stem = nn.Sequential(
            nn.Conv2d(12, 32, 3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(32),
            Swish()
        )
        
        # EfficientNet-B0 architecture (adapted for 8x8 input)
        # Format: (expand_ratio, out_channels, num_blocks, stride, kernel_size)
        configs = [
            # Stage 1: 8x8 -> 8x8
            (1, 16, 1, 1, 3),
            # Stage 2: 8x8 -> 4x4
            (6, 24, 2, 2, 3),
            # Stage 3: 4x4 -> 2x2
            (6, 40, 2, 2, 5),
            # Stage 4: 2x2 -> 2x2
            (6, 80, 3, 1, 3),
            # Stage 5: 2x2 -> 1x1 (via pooling)
            (6, 112, 3, 1, 5),
        ]
        
        # Build MBConv blocks
        self.blocks = nn.ModuleList([])
        in_channels = 32
        
        for expand_ratio, out_channels, num_blocks, stride, kernel_size in configs:
            for i in range(num_blocks):
                self.blocks.append(
                    MBConvBlock(
                        in_channels if i == 0 else out_channels,
                        out_channels,
                        expand_ratio,
                        stride if i == 0 else 1,
                        kernel_size
                    )
                )
            in_channels = out_channels
        
        # Head: Final convolution
        self.head_conv = nn.Sequential(
            nn.Conv2d(in_channels, 320, 1, bias=False),
            nn.BatchNorm2d(320),
            Swish()
        )
        
        # Global average pooling
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(320, num_classes),
            nn.Sigmoid()
        )
        
        # Initialize weights
        self._initialize_weights()
        
        logger.info(f"TacticalEfficientNet initialized with {self.count_parameters():,} parameters")
    
    def _initialize_weights(self):
        """Initialize weights with proper scaling"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.zeros_(m.bias)
    
    def forward(self, x):
        # Input: (batch, 12, 8, 8)
        x = self.stem(x)
        
        # MBConv blocks
        for block in self.blocks:
            x = block(x)
        
        # Head
        x = self.head_conv(x)
        x = self.global_pool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        
        return x
    
    def count_parameters(self) -> int:
        """Count total trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class TacticalTransformer(nn.Module):
    """
    Transformer-based architecture for tactical pattern recognition.
    Treats the chess board as a sequence of 64 squares.
    """
    
    def __init__(self, num_classes: int = 20, d_model: int = 128, 
                 nhead: int = 8, num_layers: int = 4, dropout_rate: float = 0.1):
        super(TacticalTransformer, self).__init__()
        
        self.num_classes = num_classes
        self.d_model = d_model
        
        # Embed each square (12 channels) into d_model dimensions
        self.square_embedding = nn.Linear(12, d_model)
        
        # Positional encoding for 64 squares
        self.pos_encoding = nn.Parameter(torch.randn(1, 64, d_model))
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout_rate,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, 256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, num_classes),
            nn.Sigmoid()
        )
        
        logger.info(f"TacticalTransformer initialized with {self.count_parameters():,} parameters")
    
    def forward(self, x):
        # Input: (batch, 12, 8, 8)
        batch_size = x.size(0)
        
        # Reshape to treat as sequence of 64 squares
        # (batch, 12, 8, 8) -> (batch, 8, 8, 12) -> (batch, 64, 12)
        x = x.permute(0, 2, 3, 1).contiguous()
        x = x.view(batch_size, 64, 12)
        
        # Embed each square
        x = self.square_embedding(x)  # (batch, 64, d_model)
        
        # Add positional encoding
        x = x + self.pos_encoding
        
        # Transformer encoding
        x = self.transformer_encoder(x)  # (batch, 64, d_model)
        
        # Global average pooling over all squares
        x = x.mean(dim=1)  # (batch, d_model)
        
        # Classification
        x = self.classifier(x)  # (batch, num_classes)
        
        return x
    
    def count_parameters(self) -> int:
        """Count total trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class ChessBoardDataset(Dataset):
    """PyTorch Dataset for chess positions"""
    
    def __init__(self, board_tensors: np.ndarray, theme_labels: np.ndarray):
        """
        Args:
            board_tensors: Array of shape (N, 8, 8, 12) - board representations
            theme_labels: Array of shape (N, num_classes) - theme labels
        """
        # Convert to PyTorch tensors and transpose to (N, 12, 8, 8) for Conv2d
        self.boards = torch.FloatTensor(board_tensors).permute(0, 3, 1, 2)
        self.labels = torch.FloatTensor(theme_labels)
    
    def __len__(self):
        return len(self.boards)
    
    def __getitem__(self, idx):
        return self.boards[idx], self.labels[idx]


class TacticalClassifierTrainer:
    """Handles training and evaluation of the tactical CNN"""
    
    def __init__(
        self,
        model: TacticalCNN,
        device: Optional[torch.device] = None,
        learning_rate: float = 0.001
    ):
        self.model = model
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # Loss and optimizer
        self.criterion = nn.BCELoss()  # Binary Cross Entropy for multi-label
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        
        # Training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': []
        }
        
        logger.info(f"Trainer initialized on device: {self.device}")
    
    def train_epoch(self, train_loader: DataLoader) -> Tuple[float, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        correct_predictions = 0
        total_predictions = 0
        
        for boards, labels in train_loader:
            boards, labels = boards.to(self.device), labels.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(boards)
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            
            # Calculate accuracy (threshold at 0.5)
            predicted = (outputs > 0.5).float()
            correct_predictions += (predicted == labels).sum().item()
            total_predictions += labels.numel()
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct_predictions / total_predictions
        
        return avg_loss, accuracy
    
    def validate(self, val_loader: DataLoader) -> Tuple[float, float]:
        """Validate the model"""
        self.model.eval()
        total_loss = 0.0
        correct_predictions = 0
        total_predictions = 0
        
        with torch.no_grad():
            for boards, labels in val_loader:
                boards, labels = boards.to(self.device), labels.to(self.device)
                
                outputs = self.model(boards)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                
                predicted = (outputs > 0.5).float()
                correct_predictions += (predicted == labels).sum().item()
                total_predictions += labels.numel()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct_predictions / total_predictions
        
        return avg_loss, accuracy
    
    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 50,
        patience: int = 10,
        verbose: bool = True
    ) -> Dict:
        """
        Train the model with early stopping
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Maximum number of epochs
            patience: Early stopping patience
            verbose: Print progress
        
        Returns:
            Training history dictionary
        """
        best_val_loss = float('inf')
        patience_counter = 0
        
        logger.info(f"Starting training for {epochs} epochs...")
        start_time = time.time()
        
        for epoch in range(epochs):
            epoch_start = time.time()
            
            # Train
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # Validate
            val_loss, val_acc = self.validate(val_loader)
            
            # Save history
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_acc'].append(val_acc)
            
            epoch_time = time.time() - epoch_start
            
            if verbose:
                print(f"Epoch {epoch+1}/{epochs} ({epoch_time:.1f}s) - "
                      f"train_loss: {train_loss:.4f}, train_acc: {train_acc:.4f}, "
                      f"val_loss: {val_loss:.4f}, val_acc: {val_acc:.4f}")
            
            # Early stopping check
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                self.best_model_state = self.model.state_dict().copy()
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    logger.info(f"Early stopping triggered at epoch {epoch+1}")
                    # Restore best model
                    self.model.load_state_dict(self.best_model_state)
                    break
        
        total_time = time.time() - start_time
        logger.info(f"Training completed in {total_time:.1f}s")
        
        return self.history
    
    def save_model(self, save_path: Path):
        """Save model weights and metadata"""
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save model weights
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'num_classes': self.model.num_classes,
            'dropout_rate': self.model.dropout_rate,
            'history': self.history
        }, save_path)
        
        logger.info(f"Model saved to {save_path}")
    
    @classmethod
    def load_model(cls, load_path: Path, device: Optional[torch.device] = None) -> 'TacticalClassifierTrainer':
        """Load a trained model"""
        checkpoint = torch.load(load_path, map_location=device or torch.device('cpu'))
        
        # Recreate model
        model = TacticalCNN(
            num_classes=checkpoint['num_classes'],
            dropout_rate=checkpoint['dropout_rate']
        )
        model.load_state_dict(checkpoint['model_state_dict'])
        
        # Create trainer
        trainer = cls(model, device=device)
        trainer.history = checkpoint.get('history', {})
        
        logger.info(f"Model loaded from {load_path}")
        return trainer


class TacticalClassifierService:
    """
    Production inference service for tactical pattern classification using a single CNN.
    Used by the chess engine to enhance explanations with detected tactics.
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        self.model = None
        self.theme_names: List[str] = []
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def load_model(self, model_path):
        """Load trained model and theme names"""
        try:
            # Convert to Path if string
            model_path = Path(model_path) if isinstance(model_path, str) else model_path
            
            checkpoint = torch.load(model_path, map_location=self.device)
            
            num_classes = int(checkpoint.get('num_classes', 20))
            dropout_rate = float(checkpoint.get('dropout_rate', 0.5))
            
            # Create and load model
            self.model = TacticalCNN(
                num_classes=num_classes,
                dropout_rate=dropout_rate
            )
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            
            # Load theme names either from checkpoint or from theme_names.json
            theme_names = checkpoint.get('theme_names')
            if theme_names:
                self.theme_names = list(theme_names)
            else:
                theme_path = model_path.parent / 'theme_names.json'
                if theme_path.exists():
                    with open(theme_path, 'r') as f:
                        self.theme_names = json.load(f)
            
            logger.info(f"Tactical classifier loaded (single CNN): {len(self.theme_names)} themes")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def predict(self, board_tensor: np.ndarray, threshold: float = 0.5) -> List[Dict]:
        """Predict tactical themes from a board position using a single CNN"""
        if self.model is None:
            return []
        
        try:
            # Prepare input: (1, 12, 8, 8)
            tensor = torch.FloatTensor(board_tensor).permute(2, 0, 1).unsqueeze(0)
            tensor = tensor.to(self.device)
            
            # Predict
            with torch.no_grad():
                predictions = self.model(tensor).cpu().numpy()[0]
            
            # Filter by threshold
            themes: List[Dict[str, float]] = []
            for idx, confidence in enumerate(predictions):
                if confidence >= threshold:
                    theme_name = self.theme_names[idx] if idx < len(self.theme_names) else f"theme_{idx}"
                    themes.append({
                        'theme': theme_name,
                        'confidence': float(confidence)
                    })
            
            # Sort by confidence
            themes.sort(key=lambda x: x['confidence'], reverse=True)
            
            return themes
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return []
    
    @property
    def is_available(self) -> bool:
        """Check if model is loaded and ready"""
        return self.model is not None


class EnsembleTacticalClassifierService:
    """Ensemble of CNN, ResNet, and Transformer tactical classifiers.

    Uses recall-optimised checkpoints if available and combines their predictions.
    Default strategy is ANY/OR (maximize recall): a theme is predicted if ANY model
    predicts it above the detection threshold.

    If no ensemble checkpoints are found, this service falls back to a single
    TacticalCNN model via TacticalClassifierService.
    """
    
    def __init__(
        self,
        model_dir: Optional[Path] = None,
        strategy: str = "ANY",
        default_threshold: float = 0.3,
    ) -> None:
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models: List[Dict[str, Any]] = []  # {name, model}
        self.theme_names: List[str] = []
        self.strategy = strategy.upper()
        self.default_threshold = float(default_threshold)
        self.detection_threshold = float(default_threshold)
        self.base_classifier: Optional[TacticalClassifierService] = None
        
        model_dir = Path(model_dir) if model_dir else Path("backend/models/saved_models")
        self._load_ensemble_models(model_dir)
        
        # Fallback: if ensemble not available, try single CNN model
        if not self.models:
            fallback_path = model_dir / "tactical_classifier.pth"
            if fallback_path.exists():
                logger.warning("No recall-optimised ensemble checkpoints found; "
                               "falling back to single CNN model")
                self.base_classifier = TacticalClassifierService(fallback_path)
            else:
                logger.warning("No ensemble models or fallback CNN model found")
    
    def _load_ensemble_models(self, model_dir: Path) -> None:
        """Load recall-optimised CNN, ResNet, and Transformer checkpoints if present."""
        checkpoints = [
            ("CNN", model_dir / "cnn_recall_optimized.pth", TacticalCNN),
            ("ResNet", model_dir / "resnet_recall_optimized.pth", TacticalResNet),
            ("Transformer", model_dir / "transformer_recall_optimized.pth", TacticalTransformer),
        ]
        
        for name, path, model_cls in checkpoints:
            if not path.exists():
                continue
            try:
                ckpt = torch.load(path, map_location=self.device)
                num_classes = int(ckpt.get('num_classes', 20))
                model = model_cls(num_classes=num_classes)
                model.load_state_dict(ckpt['model_state_dict'])
                model.to(self.device)
                model.eval()
                
                self.models.append({
                    'name': name,
                    'model': model,
                })
                
                # Use theme names and detection threshold from first successful checkpoint
                if not self.theme_names and ckpt.get('theme_names'):
                    self.theme_names = list(ckpt['theme_names'])
                if 'detection_threshold' in ckpt:
                    self.detection_threshold = float(ckpt['detection_threshold'])
                
                logger.info(f"Loaded recall-optimised {name} model for ensemble from {path}")
            except Exception as e:
                logger.error(f"Failed to load ensemble model {name} from {path}: {e}")
        
        if self.models:
            logger.info(f"Ensemble tactical classifier initialised with {len(self.models)} models")
        
    def _predict_ensemble_any(self, predictions: np.ndarray, threshold: float) -> np.ndarray:
        """ANY/OR strategy: theme is active if ANY model predicts it above threshold.

        Args:
            predictions: Array of shape (M, num_classes) with model probabilities.
            threshold: Detection threshold.
        Returns:
            Binary mask of shape (num_classes,) indicating active themes.
        """
        return (predictions >= threshold).any(axis=0).astype(bool)
    
    def predict(self, board_tensor: np.ndarray, threshold: Optional[float] = None) -> List[Dict]:
        """Predict tactical themes using ensemble or fallback single model.

        Args:
            board_tensor: Board representation (8, 8, 12)
            threshold: Optional detection threshold override.
        Returns:
            List of detected themes with confidence scores.
        """
        # Use ensemble if available
        if self.models:
            try:
                th = float(threshold) if threshold is not None else self.detection_threshold
                # Prepare input: (1, 12, 8, 8)
                tensor = torch.FloatTensor(board_tensor).permute(2, 0, 1).unsqueeze(0)
                tensor = tensor.to(self.device)
                
                # Collect predictions from all models: (M, num_classes)
                all_preds = []
                with torch.no_grad():
                    for mdl in self.models:
                        probs = mdl['model'](tensor).cpu().numpy()[0]
                        all_preds.append(probs)
                preds_array = np.stack(all_preds, axis=0)  # (M, C)
                
                # ANY/OR ensemble for maximum recall
                active_mask = self._predict_ensemble_any(preds_array, th)
                if not active_mask.any():
                    return []
                
                # Confidence = max probability across models for each active theme
                max_conf = preds_array.max(axis=0)
                themes: List[Dict[str, float]] = []
                for idx, is_active in enumerate(active_mask):
                    if not is_active:
                        continue
                    theme_name = self.theme_names[idx] if idx < len(self.theme_names) else f"theme_{idx}"
                    themes.append({
                        'theme': theme_name,
                        'confidence': float(max_conf[idx])
                    })
                
                themes.sort(key=lambda x: x['confidence'], reverse=True)
                return themes
            except Exception as e:
                logger.error(f"Error during ensemble prediction: {e}")
                # Fall through to base classifier if available
        
        # Fallback single-model classifier
        if self.base_classifier and self.base_classifier.is_available:
            return self.base_classifier.predict(board_tensor, threshold or 0.5)
        
        return []
    
    @property
    def is_available(self) -> bool:
        """Check if any ensemble model or fallback classifier is available"""
        if self.models:
            return True
        return self.base_classifier.is_available if self.base_classifier else False


class PrecisionEnsembleService:
    """Precision-Optimized Ensemble of CNN, ResNet, and EfficientNet.
    
    Uses WEIGHTED ensemble strategy for 80.6% precision with 2.5% recall.
    Designed for educational use where accuracy is more important than coverage.
    
    Weights: EfficientNet 1.3x, ResNet 1.1x, CNN 1.0x (based on individual precision)
    """
    
    def __init__(
        self,
        model_dir: Optional[Path] = None,
        strategy: str = "WEIGHTED",
        default_threshold: float = 0.6,
    ) -> None:
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models: List[Dict[str, Any]] = []  # {name, model, weight}
        self.theme_names: List[str] = []
        self.strategy = strategy.upper()
        self.default_threshold = float(default_threshold)
        
        model_dir = Path(model_dir) if model_dir else Path("backend/models/saved_models")
        self._load_precision_models(model_dir)
    
    def _load_precision_models(self, model_dir: Path) -> None:
        """Load precision-optimized CNN, ResNet, and EfficientNet checkpoints."""
        checkpoints = [
            ("CNN", model_dir / "cnn_precision_optimized.pth", TacticalCNN, 1.0),
            ("ResNet", model_dir / "resnet_precision_optimized.pth", TacticalResNet, 1.1),
            ("EfficientNet", model_dir / "efficientnet_precision_optimized.pth", TacticalEfficientNet, 1.3),
        ]
        
        for name, path, model_cls, weight in checkpoints:
            if not path.exists():
                logger.warning(f"Precision model not found: {path}")
                continue
            try:
                ckpt = torch.load(path, map_location=self.device)
                num_classes = int(ckpt.get('num_classes', 20))
                model = model_cls(num_classes=num_classes)
                model.load_state_dict(ckpt['model_state_dict'])
                model.to(self.device)
                model.eval()
                
                self.models.append({
                    'name': name,
                    'model': model,
                    'weight': weight,
                })
                
                # Use theme names from first successful checkpoint
                if not self.theme_names and ckpt.get('theme_names'):
                    self.theme_names = list(ckpt['theme_names'])
                
                logger.info(f"Loaded precision-optimized {name} (weight={weight}) from {path}")
            except Exception as e:
                logger.error(f"Failed to load precision model {name} from {path}: {e}")
        
        if self.models:
            logger.info(f"Precision ensemble initialized with {len(self.models)} models (WEIGHTED strategy, 80.6% precision)")
        else:
            logger.error("No precision-optimized models loaded!")
    
    def _predict_weighted(self, predictions: np.ndarray, weights: np.ndarray, threshold: float) -> np.ndarray:
        """WEIGHTED strategy: weighted average of model confidences.
        
        Args:
            predictions: Array of shape (M, num_classes) with model probabilities.
            weights: Array of shape (M,) with model weights.
            threshold: Detection threshold.
        Returns:
            Weighted confidence scores of shape (num_classes,)
        """
        # Normalize weights
        weights_norm = weights / weights.sum()
        # Weighted average: (M, C) * (M, 1) -> (C,)
        weighted_conf = (predictions * weights_norm[:, np.newaxis]).sum(axis=0)
        return weighted_conf
    
    def _predict_unanimous(self, predictions: np.ndarray, threshold: float) -> np.ndarray:
        """UNANIMOUS strategy: all models must agree (83.1% precision, 0.4% recall)."""
        return (predictions >= threshold).all(axis=0).astype(bool)
    
    def _predict_majority(self, predictions: np.ndarray, threshold: float) -> np.ndarray:
        """MAJORITY strategy: 2+ models must agree (79.3% precision, 4.0% recall)."""
        votes = (predictions >= threshold).sum(axis=0)
        return (votes >= 2).astype(bool)
    
    def predict(self, board_tensor: np.ndarray, threshold: Optional[float] = None) -> List[Dict]:
        """Predict tactical themes using precision-optimized ensemble.
        
        Args:
            board_tensor: Board representation (8, 8, 12)
            threshold: Optional detection threshold override (default: 0.6)
        Returns:
            List of detected themes with confidence scores.
        """
        if not self.models:
            return []
        
        try:
            th = float(threshold) if threshold is not None else self.default_threshold
            
            # Prepare input: (1, 12, 8, 8)
            tensor = torch.FloatTensor(board_tensor).permute(2, 0, 1).unsqueeze(0)
            tensor = tensor.to(self.device)
            
            # Collect predictions from all models: (M, num_classes)
            all_preds = []
            with torch.no_grad():
                for mdl in self.models:
                    probs = torch.sigmoid(mdl['model'](tensor)).cpu().numpy()[0]
                    all_preds.append(probs)
            preds_array = np.stack(all_preds, axis=0)  # (M, C)
            
            # Get model weights
            weights = np.array([m['weight'] for m in self.models])
            
            # Apply ensemble strategy
            if self.strategy == "WEIGHTED":
                # Weighted average confidence
                weighted_conf = self._predict_weighted(preds_array, weights, th)
                active_mask = weighted_conf >= th
                final_conf = weighted_conf
            elif self.strategy == "UNANIMOUS":
                active_mask = self._predict_unanimous(preds_array, th)
                # Use average confidence for active themes
                final_conf = preds_array.mean(axis=0)
            elif self.strategy == "MAJORITY":
                active_mask = self._predict_majority(preds_array, th)
                # Use max confidence for active themes
                final_conf = preds_array.max(axis=0)
            else:
                logger.warning(f"Unknown strategy {self.strategy}, defaulting to WEIGHTED")
                weighted_conf = self._predict_weighted(preds_array, weights, th)
                active_mask = weighted_conf >= th
                final_conf = weighted_conf
            
            if not active_mask.any():
                return []
            
            # Build theme list
            themes: List[Dict[str, float]] = []
            for idx, is_active in enumerate(active_mask):
                if not is_active:
                    continue
                theme_name = self.theme_names[idx] if idx < len(self.theme_names) else f"theme_{idx}"
                themes.append({
                    'theme': theme_name,
                    'confidence': float(final_conf[idx])
                })
            
            # Sort by confidence
            themes.sort(key=lambda x: x['confidence'], reverse=True)
            return themes
            
        except Exception as e:
            logger.error(f"Error during precision ensemble prediction: {e}")
            return []
    
    @property
    def is_available(self) -> bool:
        """Check if precision ensemble models are loaded"""
        return len(self.models) > 0


# Evaluation metrics
def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, threshold: float = 0.5) -> Dict:
    """Calculate precision, recall, F1 for multi-label classification"""
    from sklearn.metrics import precision_score, recall_score, f1_score
    
    y_pred_binary = (y_pred > threshold).astype(int)
    
    precision = precision_score(y_true, y_pred_binary, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred_binary, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred_binary, average='weighted', zero_division=0)
    
    return {
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1)
    }


if __name__ == "__main__":
    # Quick test
    print("Testing TacticalCNN (PyTorch)...")
    
    # Create model
    model = TacticalCNN(num_classes=20)
    print(f"Model created with {model.count_parameters():,} parameters")
    
    # Test forward pass
    test_input = torch.randn(4, 12, 8, 8)  # Batch of 4 boards
    output = model(test_input)
    print(f"Input shape: {test_input.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Output range: [{output.min():.3f}, {output.max():.3f}]")
    print("✅ PyTorch model working!")

