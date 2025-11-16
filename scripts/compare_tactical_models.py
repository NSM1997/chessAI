"""
Comparative Study: CNN vs ResNet vs Transformer for Tactical Pattern Classification

Uses existing trained CNN model and trains ResNet and Transformer for comparison.

Research Question:
Which architecture is most effective for chess tactical pattern recognition?
"""

import sys
import os
from pathlib import Path
import numpy as np
import json
import matplotlib.pyplot as plt
import time
import pandas as pd

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.ml.data_preprocessing import ChessDataset, ChessBoardEncoder, TacticalThemeEncoder

# Import all model architectures
try:
    import torch
    from torch.utils.data import DataLoader
    
    # CNN
    from backend.app.ml.tactical_classifier_pytorch import (
        TacticalCNN, 
        ChessBoardDataset, 
        TacticalClassifierTrainer,
        calculate_metrics
    )
    
    # ResNet
    from backend.app.ml.tactical_resnet import TacticalResNetLight
    
    # Transformer
    from backend.app.ml.tactical_transformer import TacticalTransformerLight
    
    PYTORCH_AVAILABLE = True
except ImportError as e:
    PYTORCH_AVAILABLE = False
    print(f"⚠️  PyTorch not installed. Error: {e}")


def prepare_data(dataset, board_encoder, theme_encoder):
    """Convert ChessDataset to numpy arrays"""
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


def evaluate_model(model, test_loader, device):
    """
    Evaluate model and return detailed metrics
    
    Returns:
        dict: accuracy, precision, recall, f1, inference_time_per_sample
    """
    model.eval()
    all_predictions = []
    all_labels = []
    
    start_time = time.time()
    num_samples = 0
    
    with torch.no_grad():
        for boards, labels in test_loader:
            boards, labels = boards.to(device), labels.to(device)
            outputs = model(boards)
            
            predicted = (outputs > 0.5).cpu().numpy()
            all_predictions.append(predicted)
            all_labels.append(labels.cpu().numpy())
            
            num_samples += boards.size(0)
    
    inference_time = time.time() - start_time
    
    # Concatenate all batches
    y_pred = np.concatenate(all_predictions, axis=0)
    y_true = np.concatenate(all_labels, axis=0)
    
    # Calculate metrics
    metrics = calculate_metrics(y_true, y_pred)
    metrics['inference_time_total'] = inference_time
    metrics['inference_time_per_sample'] = inference_time / num_samples
    
    return metrics


def evaluate_pretrained_cnn(model_path, test_loader, device, num_classes):
    """Load and evaluate pre-trained CNN model"""
    print("\n" + "=" * 60)
    print("EVALUATING: Pre-trained CNN")
    print("=" * 60)
    
    # Load model
    model = TacticalCNN(num_classes=num_classes)
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    param_count = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Parameters: {param_count:,}")
    
    # Evaluate
    print("Evaluating on test set...")
    test_metrics = evaluate_model(model, test_loader, device)
    
    results = {
        'model_name': 'CNN (Pre-trained)',
        'parameters': param_count,
        'training_time': None,  # Already trained
        'test_precision': test_metrics['precision'],
        'test_recall': test_metrics['recall'],
        'test_f1': test_metrics['f1_score'],
        'inference_time_per_sample': test_metrics['inference_time_per_sample'],
    }
    
    print(f"\nCNN Results:")
    print(f"  Test F1-score: {test_metrics['f1_score']:.4f}")
    print(f"  Test Precision: {test_metrics['precision']:.4f}")
    print(f"  Test Recall: {test_metrics['recall']:.4f}")
    print(f"  Inference time: {test_metrics['inference_time_per_sample']*1000:.2f}ms per sample")
    
    return results


def train_single_model(
    model_name: str,
    model,
    train_loader,
    val_loader,
    test_loader,
    device,
    epochs: int = 30,
    learning_rate: float = 0.001,
    patience: int = 10
):
    """Train a single model and return results"""
    print("\n" + "=" * 60)
    print(f"TRAINING: {model_name}")
    print("=" * 60)
    
    # Model info
    param_count = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Parameters: {param_count:,}")
    
    # Create trainer
    trainer = TacticalClassifierTrainer(model, device=device, learning_rate=learning_rate)
    
    # Train
    start_time = time.time()
    history = trainer.fit(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=epochs,
        patience=patience,
        verbose=True
    )
    training_time = time.time() - start_time
    
    # Evaluate on test set
    print("\nEvaluating on test set...")
    test_metrics = evaluate_model(model, test_loader, device)
    
    # Compile results
    results = {
        'model_name': model_name,
        'parameters': param_count,
        'training_time': training_time,
        'epochs_trained': len(history['train_loss']),
        'final_val_acc': history['val_acc'][-1],
        'test_precision': test_metrics['precision'],
        'test_recall': test_metrics['recall'],
        'test_f1': test_metrics['f1_score'],
        'inference_time_per_sample': test_metrics['inference_time_per_sample'],
        'history': history
    }
    
    print(f"\n{model_name} Results:")
    print(f"  Training time: {training_time:.2f}s ({training_time/60:.1f} min)")
    print(f"  Test F1-score: {test_metrics['f1_score']:.4f}")
    print(f"  Test Precision: {test_metrics['precision']:.4f}")
    print(f"  Test Recall: {test_metrics['recall']:.4f}")
    print(f"  Inference time: {test_metrics['inference_time_per_sample']*1000:.2f}ms per sample")
    
    return results


def plot_comparison_results(all_results, save_dir: str):
    """Create comparison visualizations"""
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    
    model_names = [r['model_name'] for r in all_results]
    
    # 1. Performance Metrics Comparison
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    metrics = ['test_precision', 'test_recall', 'test_f1']
    titles = ['Precision', 'Recall', 'F1-Score']
    colors = ['#3b82f6', '#10b981', '#f59e0b']
    
    for idx, (metric, title) in enumerate(zip(metrics, titles)):
        ax = axes[idx]
        values = [r[metric] for r in all_results]
        bars = ax.bar(model_names, values, color=colors)
        ax.set_title(f'{title} Comparison', fontsize=12, fontweight='bold')
        ax.set_ylabel(title)
        ax.set_ylim([0, 1])
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_xticklabels(model_names, rotation=15, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(save_dir / 'performance_comparison.png', dpi=150, bbox_inches='tight')
    print(f"✅ Saved: {save_dir / 'performance_comparison.png'}")
    plt.close()
    
    # 2. Efficiency Metrics
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Parameters
    params = [r['parameters'] / 1000 for r in all_results]  # in thousands
    bars = axes[0].bar(model_names, params, color=colors)
    axes[0].set_title('Model Size', fontweight='bold')
    axes[0].set_ylabel('Parameters (thousands)')
    axes[0].grid(True, alpha=0.3, axis='y')
    axes[0].set_xticklabels(model_names, rotation=15, ha='right')
    for bar in bars:
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}K',
                   ha='center', va='bottom', fontsize=9)
    
    # Inference time
    inf_times = [r['inference_time_per_sample'] * 1000 for r in all_results]  # in ms
    bars = axes[1].bar(model_names, inf_times, color=colors)
    axes[1].set_title('Inference Speed', fontweight='bold')
    axes[1].set_ylabel('Time per sample (ms)')
    axes[1].grid(True, alpha=0.3, axis='y')
    axes[1].set_xticklabels(model_names, rotation=15, ha='right')
    for bar in bars:
        height = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(save_dir / 'efficiency_comparison.png', dpi=150, bbox_inches='tight')
    print(f"✅ Saved: {save_dir / 'efficiency_comparison.png'}")
    plt.close()


def save_results_table(all_results, save_dir: str):
    """Save results as CSV and formatted text"""
    save_dir = Path(save_dir)
    
    # Create DataFrame
    df = pd.DataFrame(all_results)
    
    # Select columns for table
    columns = [
        'model_name', 'parameters',
        'test_precision', 'test_recall', 'test_f1',
        'inference_time_per_sample'
    ]
    
    df_table = df[columns].copy()
    df_table['parameters'] = df_table['parameters'].apply(lambda x: f"{x:,}")
    df_table['inference_time_per_sample'] = df_table['inference_time_per_sample'].apply(lambda x: f"{x*1000:.2f}ms")
    
    # Rename columns for readability
    df_table.columns = ['Model', 'Parameters', 'Precision', 'Recall', 'F1-Score', 'Inference Time']
    
    # Save CSV
    df_table.to_csv(save_dir / 'comparison_results.csv', index=False)
    print(f"✅ Saved: {save_dir / 'comparison_results.csv'}")
    
    # Save formatted text
    with open(save_dir / 'comparison_results.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("TACTICAL CLASSIFIER ARCHITECTURE COMPARISON\n")
        f.write("=" * 80 + "\n\n")
        f.write(df_table.to_string(index=False))
        f.write("\n\n")
        
        # Find best model for each metric
        best_f1_idx = df['test_f1'].idxmax()
        best_speed_idx = df['inference_time_per_sample'].idxmin()
        best_params_idx = df['parameters'].idxmin()
        
        f.write("SUMMARY:\n")
        f.write(f"  🏆 Best F1-Score: {all_results[best_f1_idx]['model_name']} ({all_results[best_f1_idx]['test_f1']:.4f})\n")
        f.write(f"  ⚡ Fastest Inference: {all_results[best_speed_idx]['model_name']} ({all_results[best_speed_idx]['inference_time_per_sample']*1000:.2f}ms)\n")
        f.write(f"  📦 Smallest Model: {all_results[best_params_idx]['model_name']} ({all_results[best_params_idx]['parameters']:,} params)\n")
    
    print(f"✅ Saved: {save_dir / 'comparison_results.txt'}")
    
    # Print to console
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(df_table.to_string(index=False))
    print("\n" + "=" * 80)


def main():
    """Main comparison study"""
    
    if not PYTORCH_AVAILABLE:
        print("[ERROR] PyTorch not available. Cannot run comparison.")
        return
    
    print("\n" + "=" * 80)
    print("COMPARATIVE STUDY: CNN vs ResNet vs Transformer")
    print("Tactical Pattern Classification for Chess")
    print("=" * 80)
    
    # Configuration
    data_path = "backend/data/raw/lichess_puzzles_sample.json"
    cnn_model_path = "backend/models/saved_models/tactical_classifier.pth"
    output_dir = Path("backend/models/comparison")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    EPOCHS = 30
    BATCH_SIZE = 32
    LEARNING_RATE = 0.001
    PATIENCE = 10
    
    # Check if CNN model exists
    if not Path(cnn_model_path).exists():
        print(f"[ERROR] Pre-trained CNN model not found at: {cnn_model_path}")
        print("Please train CNN first or update the path.")
        return
    
    # Load and prepare data
    print("\n[1/4] Loading dataset...")
    board_encoder = ChessBoardEncoder()
    theme_encoder = TacticalThemeEncoder()
    
    full_dataset = ChessDataset(data_path, board_encoder, theme_encoder)
    train_dataset, val_dataset, test_dataset = full_dataset.split_train_val_test(
        train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
    )
    
    print("\n[2/4] Preparing data...")
    X_train, y_train = prepare_data(train_dataset, board_encoder, theme_encoder)
    X_val, y_val = prepare_data(val_dataset, board_encoder, theme_encoder)
    X_test, y_test = prepare_data(test_dataset, board_encoder, theme_encoder)
    
    # Create PyTorch datasets
    train_pytorch = ChessBoardDataset(X_train, y_train)
    val_pytorch = ChessBoardDataset(X_val, y_val)
    test_pytorch = ChessBoardDataset(X_test, y_test)
    
    train_loader = DataLoader(train_pytorch, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_pytorch, batch_size=BATCH_SIZE, shuffle=False)
    test_loader = DataLoader(test_pytorch, batch_size=BATCH_SIZE, shuffle=False)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    num_classes = theme_encoder.num_classes
    all_results = []
    
    # Evaluate pre-trained CNN
    print("\n[3/4] Evaluating models...")
    cnn_results = evaluate_pretrained_cnn(cnn_model_path, test_loader, device, num_classes)
    all_results.append(cnn_results)
    
    # Train ResNet
    resnet = TacticalResNetLight(num_classes=num_classes)
    resnet_results = train_single_model(
        model_name="ResNet",
        model=resnet,
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader,
        device=device,
        epochs=EPOCHS,
        learning_rate=LEARNING_RATE,
        patience=PATIENCE
    )
    all_results.append(resnet_results)
    
    # Save ResNet model
    torch.save(resnet.state_dict(), output_dir / "resnet_model.pth")
    
    # Train Transformer
    transformer = TacticalTransformerLight(num_classes=num_classes)
    transformer_results = train_single_model(
        model_name="Transformer",
        model=transformer,
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader,
        device=device,
        epochs=EPOCHS,
        learning_rate=LEARNING_RATE,
        patience=PATIENCE
    )
    all_results.append(transformer_results)
    
    # Save Transformer model
    torch.save(transformer.state_dict(), output_dir / "transformer_model.pth")
    
    # Generate comparison plots
    print("\n[4/4] Generating results...")
    plot_comparison_results(all_results, output_dir)
    save_results_table(all_results, output_dir)
    
    # Save full results as JSON
    results_json = output_dir / 'comparison_results.json'
    with open(results_json, 'w') as f:
        # Remove history for cleaner JSON
        clean_results = [{k: v for k, v in r.items() if k != 'history'} for r in all_results]
        json.dump(clean_results, f, indent=2)
    print(f"✅ Saved: {results_json}")
    
    print("\n" + "=" * 80)
    print("✅ COMPARISON STUDY COMPLETE!")
    print(f"📁 Results saved to: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
