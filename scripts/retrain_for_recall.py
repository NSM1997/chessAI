"""
Retrain Models to Maximize Recall (Detection Rate)
Focus: Detect as many tactical themes as possible, even if some false positives

Techniques Used:
1. Weighted BCE Loss (higher weight for positive class)
2. Class weights for imbalanced themes
3. Lower prediction threshold (0.3 instead of 0.5)
4. Focal Loss to focus on hard-to-detect examples
5. Recall-based early stopping
"""
import sys
from pathlib import Path
import torch
import torch.nn as nn
import numpy as np
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.ml.data_preprocessing import ChessDataset
from backend.app.ml.tactical_classifier_pytorch import TacticalCNN, TacticalResNet, TacticalTransformer
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import precision_recall_fscore_support

print("=" * 80)
print("RETRAINING MODELS FOR MAXIMUM RECALL (DETECTION RATE)")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Custom Focal Loss for hard examples
class FocalLoss(nn.Module):
    """Focal Loss focuses on hard-to-classify examples"""
    def __init__(self, alpha=0.75, gamma=2, pos_weight=None):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.pos_weight = pos_weight
        
    def forward(self, inputs, targets):
        bce_loss = nn.functional.binary_cross_entropy(inputs, targets, reduction='none')
        
        # Focal term: (1 - pt)^gamma
        pt = torch.exp(-bce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * bce_loss
        
        # Apply positive class weights if provided
        if self.pos_weight is not None:
            focal_loss = focal_loss * self.pos_weight
        
        return focal_loss.mean()

# Load datasets
print("[1/6] Loading datasets...")
train_dataset, val_dataset, test_dataset = ChessDataset.load_presplit_datasets()
num_classes = len(train_dataset.theme_encoder.themes)
theme_names = train_dataset.theme_encoder.themes
print(f"  Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
print(f"  Themes: {num_classes}\n")

# Prepare data
print("[2/6] Preparing data...")
def prepare_dataset(dataset):
    X, y = [], []
    for i in range(len(dataset)):
        board_tensor, theme_label, _ = dataset[i]
        X.append(board_tensor)
        y.append(theme_label)
        if (i + 1) % 2000 == 0:
            print(f"  {i+1}/{len(dataset)}...")
    X_tensor = torch.FloatTensor(np.array(X))
    X_tensor = X_tensor.permute(0, 3, 1, 2)
    return X_tensor, torch.FloatTensor(np.array(y))

X_train, y_train = prepare_dataset(train_dataset)
X_val, y_val = prepare_dataset(val_dataset)
X_test, y_test = prepare_dataset(test_dataset)
print(f"  Done!\n")

# Calculate positive class weights (favor detecting themes over missing them)
print("[3/6] Calculating positive class weights...")
class_counts = y_train.sum(dim=0)
total_samples = len(y_train)
neg_counts = total_samples - class_counts
pos_weights = neg_counts / (class_counts + 1e-5)  # Avoid division by zero
pos_weights = torch.clamp(pos_weights, min=1.0, max=20.0)  # Limit extreme weights

print(f"  Positive class weights (higher = more focus on detection):")
for i, theme in enumerate(theme_names):
    count = int(class_counts[i])
    weight = pos_weights[i].item()
    print(f"    {theme:<20} {count:>5} samples -> weight: {weight:.2f}x")
print()

# Create dataloaders
BATCH_SIZE = 32
train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(TensorDataset(X_val, y_val), batch_size=BATCH_SIZE, shuffle=False)
test_loader = DataLoader(TensorDataset(X_test, y_test), batch_size=BATCH_SIZE, shuffle=False)

# Training function optimized for recall
def train_for_recall(model_class, model_name, save_path, lr=0.001, epochs=80):
    """Train model optimized for high recall (detection rate)"""
    print("\n" + "=" * 80)
    print(f"TRAINING {model_name.upper()} FOR MAXIMUM RECALL")
    print("=" * 80)
    
    start_time = time.time()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Create model
    print(f"[1/5] Creating {model_name} model...")
    model = model_class(num_classes=num_classes, dropout_rate=0.3)
    model = model.to(device)
    print(f"  Parameters: {model.count_parameters():,}")
    print(f"  Device: {device}")
    
    # Focal Loss with positive class weights
    criterion = FocalLoss(alpha=0.75, gamma=2, pos_weight=pos_weights.to(device))
    
    # Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    
    # Learning rate scheduler
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=7
    )
    
    # Training loop
    print(f"[2/5] Training {model_name}...")
    best_val_recall = 0
    patience_counter = 0
    patience = 15
    history = {'train_loss': [], 'val_loss': [], 'val_recall': [], 'val_precision': [], 'val_f1': []}
    
    # Use lower threshold for better detection
    DETECTION_THRESHOLD = 0.3
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0
        all_preds, all_labels = [], []
        
        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                val_loss += loss.item()
                
                all_preds.append(outputs.cpu().numpy())
                all_labels.append(batch_y.cpu().numpy())
        
        val_loss /= len(val_loader)
        
        # Calculate metrics with detection threshold
        y_pred = np.concatenate(all_preds, axis=0)
        y_true = np.concatenate(all_labels, axis=0)
        y_pred_binary = (y_pred > DETECTION_THRESHOLD).astype(int)
        
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred_binary, average='micro', zero_division=0
        )
        
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['val_recall'].append(recall)
        history['val_precision'].append(precision)
        history['val_f1'].append(f1)
        
        # Learning rate scheduling based on recall
        scheduler.step(recall)
        current_lr = optimizer.param_groups[0]['lr']
        
        print(f"Epoch {epoch+1}/{epochs} - "
              f"train_loss: {train_loss:.4f}, val_loss: {val_loss:.4f}, "
              f"recall: {recall:.4f}, precision: {precision:.4f}, f1: {f1:.4f}, "
              f"lr: {current_lr:.6f}")
        
        # Early stopping based on recall
        if recall > best_val_recall:
            best_val_recall = recall
            patience_counter = 0
            best_model_state = model.state_dict().copy()
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  Early stopping at epoch {epoch+1}")
                break
    
    # Load best model
    model.load_state_dict(best_model_state)
    
    # Evaluate on test set
    print(f"[3/5] Evaluating {model_name} on test set...")
    model.eval()
    all_preds, all_labels = [], []
    
    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            batch_X = batch_X.to(device)
            outputs = model(batch_X)
            all_preds.append(outputs.cpu().numpy())
            all_labels.append(batch_y.numpy())
    
    y_pred = np.concatenate(all_preds, axis=0)
    y_true = np.concatenate(all_labels, axis=0)
    y_pred_binary = (y_pred > DETECTION_THRESHOLD).astype(int)
    
    test_precision, test_recall, test_f1, _ = precision_recall_fscore_support(
        y_true, y_pred_binary, average='micro', zero_division=0
    )
    
    print(f"  Detection Threshold: {DETECTION_THRESHOLD}")
    print(f"  Test Recall (Detection Rate): {test_recall:.4f} ({test_recall*100:.1f}%)")
    print(f"  Test Precision: {test_precision:.4f}")
    print(f"  Test F1: {test_f1:.4f}")
    
    # Per-theme recall analysis
    print(f"\n[4/5] Per-theme detection rates:")
    per_theme_metrics = {}
    detected_themes = 0
    total_themes_with_support = 0
    
    for i in range(num_classes):
        theme_pred = y_pred_binary[:, i]
        theme_true = y_true[:, i]
        if theme_true.sum() > 0:
            total_themes_with_support += 1
            p, r, f, _ = precision_recall_fscore_support(
                theme_true, theme_pred, average='binary', zero_division=0
            )
            per_theme_metrics[theme_names[i]] = {
                'precision': float(p),
                'recall': float(r),
                'f1': float(f),
                'support': int(theme_true.sum())
            }
            status = "[OK]" if r > 0.2 else "[LOW]"
            print(f"  {theme_names[i]:<20} Recall: {r:.4f} ({r*100:.1f}%) {status}")
            if r > 0.1:  # Count as detected if >10% recall
                detected_themes += 1
    
    avg_recall = np.mean([m['recall'] for m in per_theme_metrics.values()])
    print(f"\n  Themes with >10% detection: {detected_themes}/{total_themes_with_support}")
    print(f"  Average per-theme recall: {avg_recall:.4f}")
    
    # Save
    print(f"[5/5] Saving {model_name} model...")
    save_path_obj = Path(save_path)
    save_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    torch.save({
        'model_type': f'{model_name}_recall_optimized',
        'model_state_dict': model.state_dict(),
        'num_classes': num_classes,
        'theme_names': theme_names,
        'detection_threshold': DETECTION_THRESHOLD,
        'best_val_recall': best_val_recall,
        'test_precision': float(test_precision),
        'test_recall': float(test_recall),
        'test_f1': float(test_f1),
        'avg_per_theme_recall': float(avg_recall),
        'detected_themes_count': detected_themes,
        'per_theme_metrics': per_theme_metrics,
        'epochs_trained': len(history['train_loss']),
        'total_parameters': model.count_parameters(),
        'history': history,
        'training_date': datetime.now().isoformat(),
        'optimization_target': 'recall',
        'techniques': 'focal_loss + pos_weights + low_threshold'
    }, save_path_obj)
    
    elapsed = time.time() - start_time
    print(f"  Saved to: {save_path}")
    print(f"  Training time: {elapsed/60:.1f} min")
    
    return {
        'model_name': model_name,
        'test_recall': test_recall,
        'test_precision': test_precision,
        'test_f1': test_f1,
        'avg_per_theme_recall': avg_recall,
        'detected_themes': detected_themes,
        'epochs': len(history['train_loss']),
        'time': elapsed
    }

# Train all three models
print("[4/6] Training models...")
results = []

# CNN (fastest, good baseline)
results.append(train_for_recall(
    TacticalCNN,
    'CNN',
    'backend/models/saved_models/cnn_recall_optimized.pth',
    lr=0.001,
    epochs=80
))

# ResNet (best previous performance)
results.append(train_for_recall(
    TacticalResNet,
    'ResNet',
    'backend/models/saved_models/resnet_recall_optimized.pth',
    lr=0.0005,
    epochs=80
))

# Transformer (compact)
results.append(train_for_recall(
    TacticalTransformer,
    'Transformer',
    'backend/models/saved_models/transformer_recall_optimized.pth',
    lr=0.0001,
    epochs=80
))

# Final summary
print("\n[5/6] Training complete!")
print("=" * 80)
print("RECALL-OPTIMIZED MODEL RESULTS")
print("=" * 80)
print(f"\n{'Model':<15} {'Recall':>10} {'Precision':>10} {'F1':>10} {'Avg Theme':>12} {'Detected':>10} {'Time':>10}")
print("-" * 90)

for r in results:
    print(f"{r['model_name']:<15} {r['test_recall']:>10.4f} {r['test_precision']:>10.4f} "
          f"{r['test_f1']:>10.4f} {r['avg_per_theme_recall']:>12.4f} "
          f"{r['detected_themes']:>10} {r['time']/60:>9.1f}m")

# Compare with original models
print("\n" + "-" * 90)
print("IMPROVEMENT OVER ORIGINAL MODELS:")
print(f"  Original CNN Recall:     0.1370 (13.7%)")
print(f"  Optimized CNN Recall:    {results[0]['test_recall']:.4f} ({results[0]['test_recall']*100:.1f}%)")
print(f"  Improvement:             {((results[0]['test_recall'] - 0.1370) / 0.1370 * 100):+.1f}%")
print("=" * 90)

best_recall_model = max(results, key=lambda x: x['test_recall'])
print(f"\nBest Detection Rate: {best_recall_model['model_name']} "
      f"({best_recall_model['test_recall']*100:.1f}% of themes detected)")

print("\n[6/6] Next Steps:")
if best_recall_model['test_recall'] < 0.3:
    print("  [WARNING] Recall still low (<30%). Recommend trying:")
    print("     1. Ensemble methods (combine all 3 models)")
    print("     2. More training data")
    print("     3. Data augmentation (board flips/rotations)")
elif best_recall_model['test_recall'] < 0.5:
    print("  [MODERATE] Recall (30-50%). Can improve with:")
    print("     1. Ensemble methods for better performance")
    print("     2. Fine-tuning threshold per theme")
else:
    print("  [GOOD] Recall (>50%)! Models working well.")
    print("     Optional: Try ensemble for even better results")

print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

