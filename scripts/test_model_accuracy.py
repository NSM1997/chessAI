"""
Test Model Accuracy - Tactical Classifier CNN
Evaluates the trained CNN model on test dataset and generates detailed metrics
"""

import sys
import os
from pathlib import Path
import numpy as np
import json
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    precision_recall_fscore_support,
    accuracy_score,
    hamming_loss,
    jaccard_score
)
import seaborn as sns

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.ml.data_preprocessing import ChessDataset, ChessBoardEncoder, TacticalThemeEncoder

# Import PyTorch components
try:
    import torch
    from torch.utils.data import DataLoader
    from backend.app.ml.tactical_classifier_pytorch import (
        TacticalCNN, 
        ChessBoardDataset,
        calculate_metrics
    )
    PYTORCH_AVAILABLE = True
except ImportError as e:
    PYTORCH_AVAILABLE = False
    print(f"⚠️  PyTorch not installed: {e}")


def load_trained_model(model_path: str, device: torch.device):
    """
    Load the trained CNN model
    
    Args:
        model_path: Path to saved model (.pth file)
        device: torch device (cpu/cuda)
    
    Returns:
        model: Loaded TacticalCNN model
        num_classes: Number of output classes
    """
    print(f"\n[LOAD] Loading trained model from {model_path}...")
    
    checkpoint = torch.load(model_path, map_location=device)
    
    model = TacticalCNN(
        num_classes=checkpoint['num_classes'],
        dropout_rate=checkpoint.get('dropout_rate', 0.5)
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    print(f"[OK] Model loaded: {checkpoint['num_classes']} classes")
    print(f"[OK] Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    return model, checkpoint['num_classes']


def prepare_test_data(data_path: str, board_encoder, theme_encoder, test_ratio: float = 0.15):
    """
    Load and prepare test dataset
    
    Args:
        data_path: Path to puzzle JSON
        board_encoder: ChessBoardEncoder
        theme_encoder: TacticalThemeEncoder
        test_ratio: Fraction for test set
    
    Returns:
        X_test: Test board tensors
        y_test: Test labels
    """
    print(f"\n[DATA] Loading dataset from {data_path}...")
    
    full_dataset = ChessDataset(data_path, board_encoder, theme_encoder)
    
    # Split dataset
    train_dataset, val_dataset, test_dataset = full_dataset.split_train_val_test(
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=test_ratio
    )
    
    print(f"[OK] Test dataset size: {len(test_dataset)} examples")
    
    # Convert to numpy arrays
    X_test = []
    y_test = []
    
    for i in range(len(test_dataset)):
        board_tensor, theme_label, metadata = test_dataset[i]
        X_test.append(board_tensor)
        y_test.append(theme_label)
        
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(test_dataset)}")
    
    X_test = np.array(X_test, dtype=np.float32)
    y_test = np.array(y_test, dtype=np.float32)
    
    print(f"[OK] Test data prepared: X shape={X_test.shape}, y shape={y_test.shape}")
    
    return X_test, y_test


def evaluate_model(model, test_loader, device, threshold: float = 0.5):
    """
    Evaluate model on test set
    
    Args:
        model: TacticalCNN model
        test_loader: DataLoader for test data
        device: torch device
        threshold: Confidence threshold for predictions
    
    Returns:
        y_true: True labels
        y_pred: Predicted probabilities
        y_pred_binary: Binary predictions (after threshold)
    """
    print(f"\n[EVAL] Evaluating model on test set (threshold={threshold})...")
    
    model.eval()
    y_true_list = []
    y_pred_list = []
    
    with torch.no_grad():
        for boards, labels in test_loader:
            boards = boards.to(device)
            
            # Get predictions
            outputs = model(boards)
            
            y_true_list.append(labels.cpu().numpy())
            y_pred_list.append(outputs.cpu().numpy())
    
    if len(y_true_list) == 0:
        raise ValueError("Test dataset is empty. Cannot evaluate model on 0 samples.")
    
    y_true = np.vstack(y_true_list)
    y_pred = np.vstack(y_pred_list)
    y_pred_binary = (y_pred > threshold).astype(int)
    
    print(f"[OK] Evaluation complete: {y_true.shape[0]} samples")
    
    return y_true, y_pred, y_pred_binary


def calculate_detailed_metrics(y_true, y_pred, y_pred_binary, theme_names):
    """
    Calculate comprehensive accuracy metrics
    
    Args:
        y_true: True labels (n_samples, n_classes)
        y_pred: Predicted probabilities (n_samples, n_classes)
        y_pred_binary: Binary predictions (n_samples, n_classes)
        theme_names: List of theme names
    
    Returns:
        metrics: Dictionary of metrics
    """
    print("\n[METRICS] Calculating detailed metrics...")
    
    metrics = {}
    
    # 1. Overall Accuracy (exact match)
    exact_match_accuracy = accuracy_score(y_true, y_pred_binary)
    metrics['exact_match_accuracy'] = exact_match_accuracy
    
    # 2. Hamming Loss (label-wise accuracy)
    hamming = hamming_loss(y_true, y_pred_binary)
    metrics['hamming_loss'] = hamming
    metrics['label_wise_accuracy'] = 1 - hamming
    
    # 3. Jaccard Score (IoU for multi-label)
    jaccard = jaccard_score(y_true, y_pred_binary, average='samples', zero_division=0)
    metrics['jaccard_score'] = jaccard
    
    # 4. Precision, Recall, F1 (weighted)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred_binary, average='weighted', zero_division=0
    )
    metrics['precision_weighted'] = precision
    metrics['recall_weighted'] = recall
    metrics['f1_weighted'] = f1
    
    # 5. Per-class metrics
    precision_per_class, recall_per_class, f1_per_class, support_per_class = precision_recall_fscore_support(
        y_true, y_pred_binary, average=None, zero_division=0
    )
    
    metrics['per_class'] = []
    for i, theme in enumerate(theme_names):
        metrics['per_class'].append({
            'theme': theme,
            'precision': float(precision_per_class[i]),
            'recall': float(recall_per_class[i]),
            'f1': float(f1_per_class[i]),
            'support': int(support_per_class[i])
        })
    
    return metrics


def print_metrics_report(metrics):
    """Print formatted metrics report"""
    print("\n" + "="*70)
    print("MODEL ACCURACY REPORT")
    print("="*70)
    
    print(f"\n📊 OVERALL METRICS:")
    print(f"  Exact Match Accuracy:    {metrics['exact_match_accuracy']:.4f} ({metrics['exact_match_accuracy']*100:.2f}%)")
    print(f"  Label-wise Accuracy:     {metrics['label_wise_accuracy']:.4f} ({metrics['label_wise_accuracy']*100:.2f}%)")
    print(f"  Hamming Loss:            {metrics['hamming_loss']:.4f}")
    print(f"  Jaccard Score (IoU):     {metrics['jaccard_score']:.4f}")
    
    print(f"\n📈 CLASSIFICATION METRICS (Weighted):")
    print(f"  Precision:               {metrics['precision_weighted']:.4f}")
    print(f"  Recall:                  {metrics['recall_weighted']:.4f}")
    print(f"  F1-Score:                {metrics['f1_weighted']:.4f}")
    
    print(f"\n🎯 PER-CLASS PERFORMANCE:")
    print(f"{'Theme':<25} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>10}")
    print("-"*70)
    
    # Sort by F1 score
    sorted_classes = sorted(metrics['per_class'], key=lambda x: x['f1'], reverse=True)
    
    for class_metrics in sorted_classes:
        theme = class_metrics['theme'][:24]  # Truncate long names
        print(f"{theme:<25} {class_metrics['precision']:>10.3f} {class_metrics['recall']:>10.3f} "
              f"{class_metrics['f1']:>10.3f} {class_metrics['support']:>10d}")


def plot_confusion_matrix_per_class(y_true, y_pred_binary, theme_names, save_path: str = None):
    """
    Plot confusion matrices for top classes
    
    Args:
        y_true: True labels
        y_pred_binary: Binary predictions
        theme_names: List of theme names
        save_path: Path to save plot
    """
    print("\n[PLOT] Generating confusion matrices...")
    
    # Select top 9 most frequent themes
    theme_counts = y_true.sum(axis=0)
    top_indices = np.argsort(theme_counts)[-9:][::-1]
    
    fig, axes = plt.subplots(3, 3, figsize=(20, 18))
    axes = axes.flatten()
    
    for idx, theme_idx in enumerate(top_indices):
        cm = confusion_matrix(y_true[:, theme_idx], y_pred_binary[:, theme_idx])
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                    xticklabels=['Absent', 'Present'],
                    yticklabels=['Absent', 'Present'],
                    cbar_kws={'shrink': 0.7})
        
        axes[idx].set_title(f"{theme_names[theme_idx]}", fontsize=10, pad=12)
        axes[idx].set_ylabel('True', fontsize=9)
        axes[idx].set_xlabel('Predicted', fontsize=9)
        axes[idx].tick_params(labelsize=8)
    
    plt.subplots_adjust(left=0.05, right=0.98, top=0.96, bottom=0.05, hspace=0.4, wspace=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"[OK] Confusion matrices saved to {save_path}")
    
    plt.show()


def plot_accuracy_by_theme(metrics, save_path: str = None):
    """
    Plot F1 scores by theme
    
    Args:
        metrics: Metrics dictionary
        save_path: Path to save plot
    """
    print("\n[PLOT] Generating F1 score by theme plot...")
    
    themes = [m['theme'] for m in metrics['per_class']]
    f1_scores = [m['f1'] for m in metrics['per_class']]
    
    # Sort by F1 score
    sorted_indices = np.argsort(f1_scores)[::-1]
    themes_sorted = [themes[i] for i in sorted_indices]
    f1_sorted = [f1_scores[i] for i in sorted_indices]
    
    plt.figure(figsize=(12, 8))
    plt.barh(themes_sorted, f1_sorted, color='steelblue')
    plt.xlabel('F1 Score')
    plt.title('Model Performance by Tactical Theme')
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"[OK] F1 score plot saved to {save_path}")
    
    plt.show()


def save_metrics_report(metrics, save_path: str):
    """Save metrics to JSON file"""
    with open(save_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[SAVE] Metrics saved to {save_path}")


def main():
    """Main testing function"""
    
    if not PYTORCH_AVAILABLE:
        print("[ERROR] PyTorch not available. Install with: pip install torch")
        return
    
    print("="*70)
    print("TACTICAL CLASSIFIER - MODEL ACCURACY TESTING")
    print("="*70)
    
    # Configuration
    model_path = "backend/models/saved_models/tactical_classifier.pth"
    data_path = "backend/data/raw/lichess_puzzles.json"
    theme_names_path = "backend/models/saved_models/theme_names.json"
    output_dir = Path("backend/models/evaluation")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    batch_size = 32
    threshold = 0.5
    
    # Check if model exists
    if not Path(model_path).exists():
        print(f"\n[ERROR] Model not found: {model_path}")
        print("Train the model first: python scripts/train_tactical_classifier.py")
        return
    
    # Check if data exists
    if not Path(data_path).exists():
        print(f"\n[ERROR] Data not found: {data_path}")
        print("Try sample data: backend/data/raw/lichess_puzzles_sample.json")
        sample_path = "backend/data/raw/lichess_puzzles_sample.json"
        if Path(sample_path).exists():
            data_path = sample_path
            print(f"[OK] Using sample data: {data_path}")
        else:
            return
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n[DEVICE] Using device: {device}")
    
    # Initialize encoders
    board_encoder = ChessBoardEncoder()
    theme_encoder = TacticalThemeEncoder()
    
    # Load theme names
    if Path(theme_names_path).exists():
        with open(theme_names_path, 'r') as f:
            theme_names = json.load(f)
    else:
        theme_names = theme_encoder.themes
    
    print(f"[OK] Number of themes: {len(theme_names)}")
    
    # Load model
    model, num_classes = load_trained_model(model_path, device)
    
    # Prepare test data
    X_test, y_test = prepare_test_data(data_path, board_encoder, theme_encoder)
    
    # Check if test data is empty
    if len(X_test) == 0:
        print(f"\n[ERROR] Test dataset is empty. The file {data_path} contains no puzzles.")
        print("Please ensure the data file is properly populated with puzzle data.")
        return
    
    # Create PyTorch dataset
    test_dataset = ChessBoardDataset(X_test, y_test)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    # Evaluate model
    y_true, y_pred, y_pred_binary = evaluate_model(model, test_loader, device, threshold)
    
    # Calculate metrics
    metrics = calculate_detailed_metrics(y_true, y_pred, y_pred_binary, theme_names)
    
    # Print report
    print_metrics_report(metrics)
    
    # Save metrics
    save_metrics_report(metrics, output_dir / "accuracy_metrics.json")
    
    # Generate plots
    plot_confusion_matrix_per_class(
        y_true, y_pred_binary, theme_names,
        save_path=output_dir / "confusion_matrices.png"
    )
    
    plot_accuracy_by_theme(
        metrics,
        save_path=output_dir / "f1_by_theme.png"
    )
    
    print("\n" + "="*70)
    print("✅ MODEL ACCURACY TESTING COMPLETE")
    print("="*70)
    print(f"\nResults saved to: {output_dir}")


if __name__ == "__main__":
    main()
