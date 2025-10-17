"""
Training script for Tactical Pattern Classifier
Trains CNN model on Lichess puzzle database
"""

import sys
import os
from pathlib import Path
import numpy as np
import json
import matplotlib.pyplot as plt

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.ml.data_preprocessing import ChessDataset, ChessBoardEncoder, TacticalThemeEncoder

# Use PyTorch (Python 3.12+ compatible)
try:
    import torch
    from torch.utils.data import DataLoader
    from backend.app.ml.tactical_classifier_pytorch import (
        TacticalCNN, 
        ChessBoardDataset, 
        TacticalClassifierTrainer,
        calculate_metrics
    )
    PYTORCH_AVAILABLE = True
except ImportError as e:
    PYTORCH_AVAILABLE = False
    print(f"⚠️  PyTorch not installed. Install with: pip install torch\nError: {e}")


def prepare_data(dataset, board_encoder, theme_encoder):
    """
    Convert ChessDataset to numpy arrays for training
    
    Args:
        dataset: ChessDataset object
        board_encoder: ChessBoardEncoder
        theme_encoder: TacticalThemeEncoder
        
    Returns:
        X: Board tensors (n, 8, 8, 12)
        y: Theme labels (n, num_classes)
    """
    print(f"Preparing {len(dataset)} examples...")
    
    X = []
    y = []
    
    for i in range(len(dataset)):
        board_tensor, theme_label, metadata = dataset[i]
        X.append(board_tensor)
        y.append(theme_label)
        
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{len(dataset)} examples")
    
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)
    
    print(f"[OK] Data prepared: X shape={X.shape}, y shape={y.shape}")
    
    return X, y


def plot_training_history(history, save_path: str = None):
    """
    Plot training metrics
    
    Args:
        history: Dictionary with training history (PyTorch format)
        save_path: Path to save plot
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # Loss
    if 'train_loss' in history and history['train_loss']:
        axes[0].plot(history['train_loss'], label='Train Loss')
        if 'val_loss' in history and history['val_loss']:
            axes[0].plot(history['val_loss'], label='Val Loss')
        axes[0].set_title('Model Loss')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].legend()
        axes[0].grid(True)
    
    # Accuracy
    if 'train_acc' in history and history['train_acc']:
        axes[1].plot(history['train_acc'], label='Train Accuracy')
        if 'val_acc' in history and history['val_acc']:
            axes[1].plot(history['val_acc'], label='Val Accuracy')
        axes[1].set_title('Model Accuracy')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Accuracy')
        axes[1].legend()
        axes[1].grid(True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"📊 Training plots saved to {save_path}")
    
    plt.show()


def train_model(
    data_path: str = "backend/data/raw/lichess_puzzles.json",
    output_dir: str = "backend/models/saved_models",
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    validation_split: float = 0.15
):
    """
    Main training function
    
    Args:
        data_path: Path to puzzle JSON
        output_dir: Directory to save model
        epochs: Number of training epochs
        batch_size: Batch size
        learning_rate: Learning rate
        validation_split: Fraction for validation
    """
    
    if not PYTORCH_AVAILABLE:
        print("[ERROR] PyTorch not available. Cannot train model.")
        print("Install with: pip install torch")
        return
    
    print("=" * 60)
    print("[TRAINING] TACTICAL PATTERN CLASSIFIER TRAINING")
    print("=" * 60)
    
    # Check if data exists
    if not Path(data_path).exists():
        print(f"\n[ERROR] Data file not found: {data_path}")
        print("Run this first: python scripts/download_puzzle_dataset.py")
        
        # Try sample dataset
        sample_path = "backend/data/raw/lichess_puzzles_sample.json"
        if Path(sample_path).exists():
            print(f"\n[OK] Using sample dataset: {sample_path}")
            data_path = sample_path
        else:
            return
    
    # Initialize encoders
    print("\n[INIT] Initializing encoders...")
    board_encoder = ChessBoardEncoder()
    theme_encoder = TacticalThemeEncoder()
    
    print(f"Board encoding: {board_encoder.input_shape}")
    print(f"Number of themes: {theme_encoder.num_classes}")
    print(f"Themes: {', '.join(theme_encoder.themes[:10])}...")
    
    # Load dataset
    print(f"\n[LOAD] Loading dataset from {data_path}...")
    full_dataset = ChessDataset(data_path, board_encoder, theme_encoder)
    
    # Split dataset
    print("\n[SPLIT] Splitting dataset...")
    train_dataset, val_dataset, test_dataset = full_dataset.split_train_val_test(
        train_ratio=0.7,
        val_ratio=validation_split,
        test_ratio=1.0 - 0.7 - validation_split
    )
    
    # Prepare data
    print("\n[PREP] Converting to numpy arrays...")
    X_train, y_train = prepare_data(train_dataset, board_encoder, theme_encoder)
    X_val, y_val = prepare_data(val_dataset, board_encoder, theme_encoder)
    X_test, y_test = prepare_data(test_dataset, board_encoder, theme_encoder)
    
    # Create PyTorch datasets
    print("\n[DATASET] Creating PyTorch datasets...")
    train_pytorch = ChessBoardDataset(X_train, y_train)
    val_pytorch = ChessBoardDataset(X_val, y_val)
    test_pytorch = ChessBoardDataset(X_test, y_test)
    
    # Create data loaders
    train_loader = DataLoader(train_pytorch, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_pytorch, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_pytorch, batch_size=batch_size, shuffle=False, num_workers=0)
    
    # Build model
    print("\n[MODEL] Building CNN model...")
    model = TacticalCNN(num_classes=theme_encoder.num_classes)
    
    # Create trainer
    print("\n[TRAINER] Creating trainer...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    trainer = TacticalClassifierTrainer(model, device=device, learning_rate=learning_rate)
    
    # Train model
    print("\n[TRAIN] Training model...")
    print(f"Epochs: {epochs}")
    print(f"Batch size: {batch_size}")
    print(f"Learning rate: {learning_rate}")
    print(f"Total parameters: {model.count_parameters():,}")
    
    history = trainer.fit(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=epochs,
        patience=10,
        verbose=True
    )
    
    # Evaluate on test set
    print("\n[EVAL] Evaluating on test set...")
    test_loss, test_acc = trainer.validate(test_loader)
    
    # Calculate detailed metrics
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for boards, labels in test_loader:
            boards = boards.to(device)
            outputs = model(boards).cpu().numpy()
            all_preds.append(outputs)
            all_labels.append(labels.numpy())
    
    all_preds = np.vstack(all_preds)
    all_labels = np.vstack(all_labels)
    detailed_metrics = calculate_metrics(all_labels, all_preds)
    
    metrics = {
        'test_loss': float(test_loss),
        'accuracy': float(test_acc),
        'precision': detailed_metrics['precision'],
        'recall': detailed_metrics['recall'],
        'f1_score': detailed_metrics['f1_score']
    }
    
    # Save model
    print("\n[SAVE] Saving model...")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    model_path = output_path / "tactical_classifier.pth"
    trainer.save_model(model_path)
    
    # Save theme names
    theme_list_path = output_path / "theme_names.json"
    with open(theme_list_path, 'w') as f:
        json.dump(theme_encoder.themes, f, indent=2)
    print(f"Theme names saved to {theme_list_path}")
    
    # Save training metrics
    metrics_path = output_path / "training_metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {metrics_path}")
    
    # Plot training history
    print("\n[PLOT] Generating training plots...")
    plot_path = output_path / "training_history.png"
    try:
        plot_training_history(history, str(plot_path))
    except Exception as e:
        print(f"Could not generate plots: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("[SUCCESS] TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Model saved to: {model_path}")
    print(f"Test Accuracy: {metrics['accuracy']:.4f}")
    print(f"Test F1 Score: {metrics['f1_score']:.4f}")
    print(f"Test Precision: {metrics['precision']:.4f}")
    print(f"Test Recall: {metrics['recall']:.4f}")
    print("=" * 60)
    
    return trainer, metrics


def test_model(model_path: str = "backend/models/saved_models/tactical_classifier.pth",
               theme_list_path: str = "backend/models/saved_models/theme_names.json"):
    """
    Test the trained model on sample positions
    
    Args:
        model_path: Path to saved model
        theme_list_path: Path to theme names
    """
    from app.ml.tactical_classifier_pytorch import TacticalClassifierService
    import chess
    
    print("\n[TEST] Tactical Classifier Testing...")
    
    # Load service
    classifier = TacticalClassifierService(model_path)
    
    if not classifier.is_available:
        print("[ERROR] Classifier not available!")
        return
        
    print(f"[OK] Model loaded with {len(classifier.theme_names)} themes")
    
    # Test positions
    test_positions = [
        {
            'name': 'Fork position',
            'fen': 'r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4'
        },
        {
            'name': 'Back rank mate',
            'fen': '6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1'
        },
        {
            'name': 'Pin',
            'fen': 'r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5'
        }
    ]
    
    board_encoder = ChessBoardEncoder()
    
    for pos in test_positions:
        print(f"\n{'=' * 40}")
        print(f"Position: {pos['name']}")
        print(f"FEN: {pos['fen']}")
        
        # Encode board
        board = chess.Board(pos['fen'])
        board_tensor = board_encoder.encode_board(board)
        
        # Classify
        themes = classifier.predict(board_tensor, threshold=0.3)
        
        if themes:
            print("Detected themes:")
            for theme in themes:
                print(f"  - {theme['theme']}: {theme['confidence']:.2%}")
        else:
            print("  No themes detected")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Tactical Pattern Classifier')
    parser.add_argument('--data-path', type=str, default='backend/data/raw/lichess_puzzles.json',
                       help='Path to puzzle dataset')
    parser.add_argument('--output-dir', type=str, default='backend/models/saved_models',
                       help='Output directory for model')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--validation-split', type=float, default=0.15,
                       help='Validation split fraction')
    parser.add_argument('--test-only', action='store_true',
                       help='Only test existing model')
    
    args = parser.parse_args()
    
    if args.test_only:
        # Test existing model
        test_model()
    else:
        # Train new model
        model, metrics = train_model(
            data_path=args.data_path,
            output_dir=args.output_dir,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            validation_split=args.validation_split
        )
        
        # Test the trained model
        if model is not None:
            test_model(
                model_path=f"{args.output_dir}/tactical_classifier.h5",
                theme_list_path=f"{args.output_dir}/theme_names.json"
            )

