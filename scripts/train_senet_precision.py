"""
Train SENet Model for Precision
Quick training script for the SE-CNN model only
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
from backend.app.ml.tactical_classifier_pytorch import TacticalSENet
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import precision_recall_fscore_support

print("=" * 80)
print("TRAINING SE-CNN FOR PRECISION")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load datasets
print("[1/4] Loading datasets...")
train_dataset, val_dataset, test_dataset = ChessDataset.load_presplit_datasets()
num_classes = len(train_dataset.theme_encoder.themes)
theme_names = train_dataset.theme_encoder.themes
print(f"  Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
print(f"  Themes: {num_classes}\n")

# Prepare data
print("[2/4] Preparing data...")
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

# Calculate class weights
print("[3/4] Calculating class weights...")
class_counts = y_train.sum(dim=0)
total_samples = len(y_train)
neg_counts = total_samples - class_counts
pos_weights = neg_counts / (class_counts + 1e-5)
pos_weights = torch.clamp(pos_weights, min=1.0, max=5.0)
print()

# Create dataloaders
BATCH_SIZE = 32
train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(TensorDataset(X_val, y_val), batch_size=BATCH_SIZE, shuffle=False)
test_loader = DataLoader(TensorDataset(X_test, y_test), batch_size=BATCH_SIZE, shuffle=False)

# Training
print("[4/4] Training SENet...")
start_time = time.time()
device = 'cuda' if torch.cuda.is_available() else 'cpu'

model = TacticalSENet(num_classes=num_classes, dropout_rate=0.4)
model = model.to(device)
print(f"  Parameters: {model.count_parameters():,}")
print(f"  Device: {device}\n")

criterion = nn.BCELoss(weight=pos_weights.to(device))
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.05)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=7)

best_val_precision = 0
patience_counter = 0
patience = 15
PRECISION_THRESHOLD = 0.6
epochs = 80

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
    
    # Calculate metrics
    y_pred = np.concatenate(all_preds, axis=0)
    y_true = np.concatenate(all_labels, axis=0)
    y_pred_binary = (y_pred > PRECISION_THRESHOLD).astype(int)
    
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred_binary, average='micro', zero_division=0
    )
    
    scheduler.step(precision)
    current_lr = optimizer.param_groups[0]['lr']
    
    print(f"Epoch {epoch+1}/{epochs} - "
          f"train_loss: {train_loss:.4f}, val_loss: {val_loss:.4f}, "
          f"precision: {precision:.4f}, recall: {recall:.4f}, f1: {f1:.4f}, "
          f"lr: {current_lr:.6f}")
    
    # Early stopping
    if precision > best_val_precision:
        best_val_precision = precision
        patience_counter = 0
        
        # Test set evaluation
        print(f"\n  NEW BEST PRECISION: {precision:.4f}! Evaluating on test set...")
        
        model.eval()
        test_preds, test_labels = [], []
        with torch.no_grad():
            for batch_X, batch_y in test_loader:
                batch_X = batch_X.to(device)
                outputs = model(batch_X)
                test_preds.append(outputs.cpu().numpy())
                test_labels.append(batch_y.cpu().numpy())
        
        y_test_pred = np.concatenate(test_preds, axis=0)
        y_test_true = np.concatenate(test_labels, axis=0)
        y_test_binary = (y_test_pred > PRECISION_THRESHOLD).astype(int)
        
        test_precision, test_recall, test_f1, _ = precision_recall_fscore_support(
            y_test_true, y_test_binary, average='micro', zero_division=0
        )
        
        # Per-theme metrics
        per_theme_precision, per_theme_recall, per_theme_f1, per_theme_support = precision_recall_fscore_support(
            y_test_true, y_test_binary, average=None, zero_division=0
        )
        
        per_theme_metrics = {}
        detected_count = 0
        
        for i, theme in enumerate(theme_names):
            per_theme_metrics[theme] = {
                'precision': float(per_theme_precision[i]),
                'recall': float(per_theme_recall[i]),
                'f1': float(per_theme_f1[i]),
                'support': int(per_theme_support[i])
            }
            if per_theme_recall[i] > 0.1:
                detected_count += 1
        
        print(f"\n  Test Set Results:")
        print(f"    Precision: {test_precision:.4f} ({test_precision*100:.1f}%)")
        print(f"    Recall:    {test_recall:.4f} ({test_recall*100:.1f}%)")
        print(f"    F1 Score:  {test_f1:.4f}")
        print(f"    Detected themes: {detected_count}/{num_classes}")
        
        # Save
        checkpoint = {
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'epochs_trained': epoch + 1,
            'total_parameters': model.count_parameters(),
            'best_val_precision': best_val_precision,
            'test_precision': test_precision,
            'test_recall': test_recall,
            'test_f1': test_f1,
            'per_theme_metrics': per_theme_metrics,
            'detected_themes_count': detected_count,
            'avg_per_theme_precision': float(np.mean(per_theme_precision)),
            'precision_threshold': PRECISION_THRESHOLD,
            'training_date': datetime.now().isoformat(),
            'optimization_target': 'precision',
            'techniques': 'SE_attention + balanced_loss + high_threshold',
            'theme_names': theme_names
        }
        
        save_path = 'backend/models/saved_models/senet_precision_optimized.pth'
        torch.save(checkpoint, save_path)
        print(f"  ✓ Model saved to {save_path}\n")
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"\n  Early stopping: No improvement for {patience} epochs")
            break

training_time = time.time() - start_time
print(f"\nTraining complete!")
print(f"  Time: {training_time/60:.1f} minutes")
print(f"  Best validation precision: {best_val_precision:.4f}")
print(f"  Final test precision: {test_precision:.4f}")
print(f"  Final test recall: {test_recall:.4f}")
print(f"  Final test F1: {test_f1:.4f}")

print("\n" + "=" * 80)
print("SE-CNN TRAINING COMPLETE!")
print("=" * 80)
