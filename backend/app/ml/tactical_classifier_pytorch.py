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
    Production inference service for tactical pattern classification.
    Used by the chess engine to enhance explanations with detected tactics.
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        self.model = None
        self.theme_names = []
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def load_model(self, model_path):
        """Load trained model and theme names"""
        try:
            # Convert to Path if string
            model_path = Path(model_path) if isinstance(model_path, str) else model_path
            
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Create and load model
            self.model = TacticalCNN(
                num_classes=checkpoint['num_classes'],
                dropout_rate=checkpoint['dropout_rate']
            )
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            
            # Load theme names
            theme_path = model_path.parent / 'theme_names.json'
            if theme_path.exists():
                with open(theme_path, 'r') as f:
                    self.theme_names = json.load(f)
            
            logger.info(f"Tactical classifier loaded: {len(self.theme_names)} themes")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def predict(self, board_tensor: np.ndarray, threshold: float = 0.5) -> List[Dict]:
        """
        Predict tactical themes from a board position
        
        Args:
            board_tensor: Board representation (8, 8, 12)
            threshold: Confidence threshold for theme detection
        
        Returns:
            List of detected themes with confidence scores
        """
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
            themes = []
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

