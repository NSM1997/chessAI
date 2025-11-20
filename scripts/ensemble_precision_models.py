"""
Ensemble Precision-Optimized Models
Combines CNN and ResNet precision-optimized predictions

Strategies:
1. UNANIMOUS (AND): All models must agree -> Maximum Precision
2. MAJORITY: >=2 models agree -> Balanced
3. ANY (OR): Any model predicts -> Higher Recall
4. WEIGHTED: Confidence-weighted average
5. ADAPTIVE: Per-theme thresholds based on individual model strengths
"""
import sys
from pathlib import Path
import torch
import numpy as np
from datetime import datetime
import json
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.ml.data_preprocessing import ChessDataset
from backend.app.ml.tactical_classifier_pytorch import TacticalCNN, TacticalResNet
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import precision_recall_fscore_support

print("=" * 80)
print("ENSEMBLE PRECISION-OPTIMIZED MODELS")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load test dataset
print("[1/5] Loading test dataset...")
_, _, test_dataset = ChessDataset.load_presplit_datasets()
num_classes = len(test_dataset.theme_encoder.themes)
theme_names = test_dataset.theme_encoder.themes

X_test, y_test = [], []
for i in range(len(test_dataset)):
    board_tensor, theme_label, _ = test_dataset[i]
    X_test.append(board_tensor)
    y_test.append(theme_label)

X_test = torch.FloatTensor(np.array(X_test)).permute(0, 3, 1, 2)
y_test = torch.FloatTensor(np.array(y_test))
test_loader = DataLoader(TensorDataset(X_test, y_test), batch_size=32, shuffle=False)

print(f"  Test samples: {len(test_dataset)}")
print(f"  Themes: {num_classes}\n")

# Load precision-optimized models
print("[2/5] Loading precision-optimized models...")
models_info = [
    {
        'name': 'CNN',
        'path': 'backend/models/saved_models/cnn_precision_optimized.pth',
        'class': TacticalCNN,
        'weight': 1.0
    },
    {
        'name': 'ResNet',
        'path': 'backend/models/saved_models/resnet_precision_optimized.pth',
        'class': TacticalResNet,
        'weight': 1.1  # Slightly higher weight (better individual precision)
    }
]

models = []
device = 'cpu'

for model_info in models_info:
    if not Path(model_info['path']).exists():
        print(f"  ⚠️  Model not found: {model_info['path']}")
        continue
        
    checkpoint = torch.load(model_info['path'], map_location=device)
    model = model_info['class'](num_classes=num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    models.append({
        'name': model_info['name'],
        'model': model,
        'weight': model_info['weight'],
        'individual_precision': checkpoint.get('test_precision', 0),
        'individual_recall': checkpoint.get('test_recall', 0),
        'individual_f1': checkpoint.get('test_f1', 0),
        'threshold': checkpoint.get('precision_threshold', 0.6)
    })
    print(f"  ✓ {model_info['name']:8} | P: {checkpoint.get('test_precision', 0):.4f} | "
          f"R: {checkpoint.get('test_recall', 0):.4f} | F1: {checkpoint.get('test_f1', 0):.4f}")

if len(models) < 2:
    print("\n❌ ERROR: Need at least 2 models for ensemble!")
    exit(1)

print()

# Get predictions from all models
print("[3/5] Getting predictions from all models...")
all_model_predictions = []

for model_data in models:
    model = model_data['model']
    preds = []
    
    with torch.no_grad():
        for batch_X, _ in test_loader:
            outputs = model(batch_X)
            preds.append(outputs.numpy())
    
    model_preds = np.concatenate(preds, axis=0)
    all_model_predictions.append(model_preds)
    print(f"  {model_data['name']}: predictions shape {model_preds.shape}")

y_true = y_test.numpy()
print()

# Test different ensemble strategies
print("[4/5] Testing ensemble strategies...")
print("=" * 80)

strategies = []

# Strategy 1: UNANIMOUS (AND) - Maximum Precision
print("\n[Strategy 1: UNANIMOUS] ALL models must predict -> Maximum Precision")
print("-" * 80)

threshold = 0.6
unanimous_predictions = np.ones_like(all_model_predictions[0])
for preds in all_model_predictions:
    unanimous_predictions = np.minimum(unanimous_predictions, preds > threshold)

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true, unanimous_predictions.astype(int), average='micro', zero_division=0
)

print(f"  Precision: {precision:.4f} ({precision*100:.1f}%)")
print(f"  Recall:    {recall:.4f} ({recall*100:.1f}%)")
print(f"  F1:        {f1:.4f}")

strategies.append({
    'name': 'UNANIMOUS (AND)',
    'predictions': unanimous_predictions,
    'recall': recall,
    'precision': precision,
    'f1': f1,
    'threshold': threshold,
    'description': 'All models must agree (highest precision)'
})

# Strategy 2: MAJORITY - Balanced
print("\n[Strategy 2: MAJORITY] >=2 models predict -> Balanced")
print("-" * 80)

vote_count = np.zeros_like(all_model_predictions[0])
for preds in all_model_predictions:
    vote_count += (preds > threshold).astype(int)

# For 2 models, majority means both agree (same as unanimous)
# But we'll keep it for consistency when adding more models
majority_threshold = max(1, len(models) // 2)
majority_predictions = (vote_count > majority_threshold).astype(int)

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true, majority_predictions, average='micro', zero_division=0
)

print(f"  Precision: {precision:.4f} ({precision*100:.1f}%)")
print(f"  Recall:    {recall:.4f} ({recall*100:.1f}%)")
print(f"  F1:        {f1:.4f}")

strategies.append({
    'name': 'MAJORITY',
    'predictions': majority_predictions,
    'recall': recall,
    'precision': precision,
    'f1': f1,
    'threshold': threshold,
    'description': f'At least {majority_threshold+1} models agree'
})

# Strategy 3: ANY (OR) - Higher Recall
print("\n[Strategy 3: ANY] Any model predicts -> Higher Recall")
print("-" * 80)

any_predictions = np.zeros_like(all_model_predictions[0])
for preds in all_model_predictions:
    any_predictions = np.maximum(any_predictions, preds > threshold)

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true, any_predictions.astype(int), average='micro', zero_division=0
)

print(f"  Precision: {precision:.4f} ({precision*100:.1f}%)")
print(f"  Recall:    {recall:.4f} ({recall*100:.1f}%)")
print(f"  F1:        {f1:.4f}")

strategies.append({
    'name': 'ANY (OR)',
    'predictions': any_predictions,
    'recall': recall,
    'precision': precision,
    'f1': f1,
    'threshold': threshold,
    'description': 'Any model predicts (higher recall)'
})

# Strategy 4: WEIGHTED AVERAGE - Confidence-based
print("\n[Strategy 4: WEIGHTED] Confidence-weighted average")
print("-" * 80)

weighted_sum = np.zeros_like(all_model_predictions[0])
total_weight = sum(m['weight'] for m in models)

for model_data, preds in zip(models, all_model_predictions):
    weighted_sum += preds * model_data['weight']

weighted_avg = weighted_sum / total_weight
weighted_predictions = (weighted_avg > threshold).astype(int)

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true, weighted_predictions, average='micro', zero_division=0
)

weights_str = ", ".join([f"{m['name']}={m['weight']}" for m in models])
print(f"  Precision: {precision:.4f} ({precision*100:.1f}%)")
print(f"  Recall:    {recall:.4f} ({recall*100:.1f}%)")
print(f"  F1:        {f1:.4f}")
print(f"  Weights:   {weights_str}")

strategies.append({
    'name': 'WEIGHTED',
    'predictions': weighted_predictions,
    'recall': recall,
    'precision': precision,
    'f1': f1,
    'threshold': threshold,
    'description': 'Weighted by model precision'
})

# Strategy 5: ADAPTIVE THRESHOLD - Lower threshold to balance precision/recall
print("\n[Strategy 5: ADAPTIVE] Lower threshold (0.5) for better balance")
print("-" * 80)

adaptive_threshold = 0.5
adaptive_any = np.zeros_like(all_model_predictions[0])
for preds in all_model_predictions:
    adaptive_any = np.maximum(adaptive_any, preds > adaptive_threshold)

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true, adaptive_any.astype(int), average='micro', zero_division=0
)

print(f"  Precision: {precision:.4f} ({precision*100:.1f}%)")
print(f"  Recall:    {recall:.4f} ({recall*100:.1f}%)")
print(f"  F1:        {f1:.4f}")
print(f"  Threshold: {adaptive_threshold}")

strategies.append({
    'name': 'ADAPTIVE (0.5)',
    'predictions': adaptive_any,
    'recall': recall,
    'precision': precision,
    'f1': f1,
    'threshold': adaptive_threshold,
    'description': 'Lower threshold for balance'
})

# Find best strategy
print("\n" + "=" * 80)
print("COMPARISON: ENSEMBLE vs INDIVIDUAL MODELS")
print("=" * 80)

# Add individual model results for comparison
for model_data in models:
    strategies.append({
        'name': f'{model_data["name"]} (Individual)',
        'precision': model_data['individual_precision'],
        'recall': model_data['individual_recall'],
        'f1': model_data['individual_f1'],
        'threshold': model_data['threshold'],
        'description': 'Individual model'
    })

# Sort by F1 score
strategies_sorted = sorted(strategies, key=lambda x: x['f1'], reverse=True)

print("\nRanked by F1 Score:")
print("-" * 80)
for i, s in enumerate(strategies_sorted, 1):
    print(f"{i}. {s['name']:<22} | P: {s['precision']:.4f} | R: {s['recall']:.4f} | F1: {s['f1']:.4f}")

# Find best precision
best_precision = max(strategies, key=lambda x: x['precision'])
print(f"\n🏆 Best Precision: {best_precision['name']} ({best_precision['precision']:.4f})")

# Find best recall
best_recall = max(strategies, key=lambda x: x['recall'])
print(f"🏆 Best Recall:    {best_recall['name']} ({best_recall['recall']:.4f})")

# Find best F1
best_f1 = max(strategies, key=lambda x: x['f1'])
print(f"🏆 Best F1:        {best_f1['name']} ({best_f1['f1']:.4f})")

# Save results
print("\n[5/5] Saving results...")
output_dir = Path('backend/models/comparison')
output_dir.mkdir(parents=True, exist_ok=True)

results = {
    'timestamp': datetime.now().isoformat(),
    'model_type': 'ensemble_precision_optimized',
    'num_models': len(models),
    'models': [m['name'] for m in models],
    'strategies': [
        {
            'name': s['name'],
            'precision': float(s['precision']),
            'recall': float(s['recall']),
            'f1': float(s['f1']),
            'threshold': s['threshold'],
            'description': s['description']
        }
        for s in strategies
    ],
    'best_precision': {
        'strategy': best_precision['name'],
        'value': float(best_precision['precision'])
    },
    'best_recall': {
        'strategy': best_recall['name'],
        'value': float(best_recall['recall'])
    },
    'best_f1': {
        'strategy': best_f1['name'],
        'value': float(best_f1['f1'])
    }
}

json_path = output_dir / 'ensemble_precision_comparison.json'
with open(json_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"  ✓ Results saved to: {json_path}")

# Create visualization
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Ensemble Precision-Optimized Models\nComparison of Strategies', 
             fontsize=16, fontweight='bold')

# Filter out individual models for ensemble comparison
ensemble_strategies = [s for s in strategies if 'Individual' not in s['name']]
individual_strategies = [s for s in strategies if 'Individual' in s['name']]

# Plot 1: Precision vs Recall
ax = axes[0]
for s in ensemble_strategies:
    ax.scatter(s['recall']*100, s['precision']*100, s=200, alpha=0.7, 
               label=s['name'], marker='o', edgecolors='black', linewidth=2)

for s in individual_strategies:
    ax.scatter(s['recall']*100, s['precision']*100, s=150, alpha=0.5, 
               label=s['name'], marker='s')

ax.set_xlabel('Recall (%)', fontweight='bold', fontsize=12)
ax.set_ylabel('Precision (%)', fontweight='bold', fontsize=12)
ax.set_title('Precision vs Recall Trade-off', fontweight='bold', fontsize=14)
ax.legend(loc='best', fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

# Add diagonal line for F1
x_line = np.linspace(0, 100, 100)
ax.plot(x_line, x_line, 'k--', alpha=0.3, linewidth=1, label='Precision=Recall')

# Plot 2: F1 Score Comparison
ax = axes[1]
strategy_names = [s['name'] for s in ensemble_strategies]
f1_scores = [s['f1']*100 for s in ensemble_strategies]
colors = plt.cm.viridis(np.linspace(0, 1, len(strategy_names)))

bars = ax.barh(strategy_names, f1_scores, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
ax.set_xlabel('F1 Score (%)', fontweight='bold', fontsize=12)
ax.set_title('F1 Score by Strategy', fontweight='bold', fontsize=14)
ax.set_xlim(0, 100)
ax.grid(axis='x', alpha=0.3)

# Add value labels
for bar in bars:
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height()/2., 
            f'{width:.1f}%',
            ha='left', va='center', fontweight='bold', fontsize=10)

plt.tight_layout()

viz_path = output_dir / 'ensemble_precision_strategies.png'
plt.savefig(viz_path, dpi=300, bbox_inches='tight')
print(f"  ✓ Visualization saved to: {viz_path}")

print("\n" + "=" * 80)
print("RECOMMENDATION FOR BEGINNERS")
print("=" * 80)

if best_f1['precision'] > 0.7:
    print(f"\n✅ Use: {best_f1['name']}")
    print(f"   Precision: {best_f1['precision']:.1%} | Recall: {best_f1['recall']:.1%} | F1: {best_f1['f1']:.3f}")
    print("\nThis provides the best balance of correctness and detection rate.")
else:
    print(f"\n⚠️  Best F1 ({best_f1['f1']:.3f}) still has low precision.")
    print(f"   Consider using: {best_precision['name']} for maximum correctness")
    print(f"   Precision: {best_precision['precision']:.1%} | Recall: {best_precision['recall']:.1%}")

print("\n" + "=" * 80)
print("ENSEMBLE COMPLETE!")
print("=" * 80)
