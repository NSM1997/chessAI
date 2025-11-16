"""
Ensemble Models for Maximum Recall
Combines CNN, ResNet, and Transformer predictions using voting strategies

Strategies:
1. ANY (OR): If ANY model predicts theme -> predict it (maximize recall)
2. MAJORITY: If >=2 models predict -> predict it (balance precision/recall)
3. WEIGHTED: Weight predictions by model confidence
"""
import sys
from pathlib import Path
import torch
import numpy as np
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.ml.data_preprocessing import ChessDataset
from backend.app.ml.tactical_classifier_pytorch import TacticalCNN, TacticalResNet, TacticalTransformer
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import precision_recall_fscore_support

print("=" * 80)
print("ENSEMBLE MODELS FOR MAXIMUM RECALL")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load test dataset
print("[1/4] Loading test dataset...")
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

print(f"  Test samples: {len(test_dataset)}\n")

# Load all three recall-optimized models
print("[2/4] Loading recall-optimized models...")
models_info = [
    {
        'name': 'CNN',
        'path': 'backend/models/saved_models/cnn_recall_optimized.pth',
        'class': TacticalCNN,
        'weight': 1.0  # Equal weight initially
    },
    {
        'name': 'ResNet',
        'path': 'backend/models/saved_models/resnet_recall_optimized.pth',
        'class': TacticalResNet,
        'weight': 0.5  # Lower weight (worst individual performance)
    },
    {
        'name': 'Transformer',
        'path': 'backend/models/saved_models/transformer_recall_optimized.pth',
        'class': TacticalTransformer,
        'weight': 1.2  # Higher weight (best individual performance)
    }
]

models = []
device = 'cpu'

for model_info in models_info:
    checkpoint = torch.load(model_info['path'], map_location=device)
    model = model_info['class'](num_classes=num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    models.append({
        'name': model_info['name'],
        'model': model,
        'weight': model_info['weight'],
        'individual_recall': checkpoint.get('test_recall', 0)
    })
    print(f"  Loaded {model_info['name']} (recall: {checkpoint.get('test_recall', 0):.4f})")

print()

# Get predictions from all models
print("[3/4] Getting predictions from all models...")
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
print("[4/4] Testing ensemble strategies...")
print("=" * 80)

strategies = []

# Strategy 1: ANY (OR) - Maximum Recall
print("\n[Strategy 1: ANY] Any model predicts -> ensemble predicts")
print("-" * 80)

threshold = 0.3
any_predictions = np.zeros_like(all_model_predictions[0])
for preds in all_model_predictions:
    any_predictions = np.maximum(any_predictions, preds > threshold)

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true, any_predictions.astype(int), average='micro', zero_division=0
)

print(f"  Recall: {recall:.4f} ({recall*100:.1f}%)")
print(f"  Precision: {precision:.4f}")
print(f"  F1: {f1:.4f}")

strategies.append({
    'name': 'ANY (OR)',
    'predictions': any_predictions,
    'recall': recall,
    'precision': precision,
    'f1': f1,
    'description': 'Predicts theme if ANY model detects it'
})

# Per-theme analysis for ANY strategy
print("\n  Per-theme detection:")
for i, theme in enumerate(theme_names):
    theme_true = y_true[:, i]
    theme_pred = any_predictions[:, i]
    if theme_true.sum() > 0:
        theme_recall = (theme_true * theme_pred).sum() / theme_true.sum()
        if theme_recall > 0.1:  # Only show if >10%
            status = "[OK]" if theme_recall > 0.5 else "[LOW]"
            print(f"    {theme:<20} {theme_recall:.4f} ({theme_recall*100:.1f}%) {status}")

# Strategy 2: MAJORITY (≥2 votes) - Balanced
print("\n[Strategy 2: MAJORITY] >=2 models predict -> ensemble predicts")
print("-" * 80)

vote_count = np.zeros_like(all_model_predictions[0])
for preds in all_model_predictions:
    vote_count += (preds > threshold).astype(int)

majority_predictions = (vote_count >= 2).astype(int)

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true, majority_predictions, average='micro', zero_division=0
)

print(f"  Recall: {recall:.4f} ({recall*100:.1f}%)")
print(f"  Precision: {precision:.4f}")
print(f"  F1: {f1:.4f}")

strategies.append({
    'name': 'MAJORITY',
    'predictions': majority_predictions,
    'recall': recall,
    'precision': precision,
    'f1': f1,
    'description': 'Predicts if >=2 models agree'
})

# Strategy 3: WEIGHTED - Smart Combination
print("\n[Strategy 3: WEIGHTED] Weighted average by model performance")
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

print(f"  Recall: {recall:.4f} ({recall*100:.1f}%)")
print(f"  Precision: {precision:.4f}")
print(f"  F1: {f1:.4f}")
print(f"  Weights used: CNN={models[0]['weight']}, ResNet={models[1]['weight']}, Transformer={models[2]['weight']}")

strategies.append({
    'name': 'WEIGHTED',
    'predictions': weighted_predictions,
    'recall': recall,
    'precision': precision,
    'f1': f1,
    'description': f'Weighted by performance (Transformer={models[2]["weight"]}x)'
})

# Strategy 4: ALL (AND) - Maximum Precision
print("\n[Strategy 4: ALL (AND)] All models must agree -> ensemble predicts")
print("-" * 80)

all_predictions = np.ones_like(all_model_predictions[0])
for preds in all_model_predictions:
    all_predictions = np.minimum(all_predictions, preds > threshold)

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true, all_predictions.astype(int), average='micro', zero_division=0
)

print(f"  Recall: {recall:.4f} ({recall*100:.1f}%)")
print(f"  Precision: {precision:.4f}")
print(f"  F1: {f1:.4f}")

strategies.append({
    'name': 'ALL (AND)',
    'predictions': all_predictions,
    'recall': recall,
    'precision': precision,
    'f1': f1,
    'description': 'Predicts only if ALL models agree'
})

# Summary comparison
print("\n" + "=" * 80)
print("ENSEMBLE STRATEGY COMPARISON")
print("=" * 80)
print(f"\n{'Strategy':<20} {'Recall':>10} {'Precision':>10} {'F1':>10} {'Description':<40}")
print("-" * 95)

# Add individual models for comparison
print(f"{'CNN (single)':<20} {models[0]['individual_recall']:>10.4f} {'N/A':>10} {'N/A':>10} {'Individual model':<40}")
print(f"{'ResNet (single)':<20} {models[1]['individual_recall']:>10.4f} {'N/A':>10} {'N/A':>10} {'Individual model':<40}")
print(f"{'Transformer (best)':<20} {models[2]['individual_recall']:>10.4f} {'N/A':>10} {'N/A':>10} {'Individual model':<40}")
print("-" * 95)

for s in strategies:
    print(f"{s['name']:<20} {s['recall']:>10.4f} {s['precision']:>10.4f} {s['f1']:>10.4f} {s['description']:<40}")

# Find best strategy
best_recall = max(strategies, key=lambda x: x['recall'])
best_f1 = max(strategies, key=lambda x: x['f1'])

print("\n" + "-" * 95)
print(f"BEST FOR DETECTION: {best_recall['name']} (Recall: {best_recall['recall']*100:.1f}%)")
print(f"BEST FOR BALANCE:   {best_f1['name']} (F1: {best_f1['f1']:.4f})")
print("=" * 95)

# Calculate improvement
best_single = max(m['individual_recall'] for m in models)
improvement = ((best_recall['recall'] - best_single) / best_single) * 100

print(f"\nIMPROVEMENT OVER BEST SINGLE MODEL:")
print(f"  Best single model:  {best_single:.4f} ({best_single*100:.1f}%)")
print(f"  Best ensemble:      {best_recall['recall']:.4f} ({best_recall['recall']*100:.1f}%)")
print(f"  Improvement:        {improvement:+.1f}%")

# Save ensemble results
output_dir = Path('backend/models/comparison')
output_dir.mkdir(parents=True, exist_ok=True)

ensemble_results = {
    'timestamp': datetime.now().isoformat(),
    'test_dataset_size': len(test_dataset),
    'num_classes': num_classes,
    'theme_names': theme_names,
    'individual_models': [
        {
            'name': m['name'],
            'recall': float(m['individual_recall']),
            'weight': float(m['weight'])
        }
        for m in models
    ],
    'ensemble_strategies': [
        {
            'name': s['name'],
            'recall': float(s['recall']),
            'precision': float(s['precision']),
            'f1': float(s['f1']),
            'description': s['description']
        }
        for s in strategies
    ],
    'best_recall_strategy': best_recall['name'],
    'best_recall_value': float(best_recall['recall']),
    'improvement_over_single': float(improvement)
}

json_path = output_dir / 'ensemble_results.json'
with open(json_path, 'w') as f:
    json.dump(ensemble_results, f, indent=2)

print(f"\nResults saved to: {json_path}")

# Recommendation
print("\n" + "=" * 80)
print("RECOMMENDATION:")
if best_recall['recall'] > 0.75:
    print(f"  [EXCELLENT] {best_recall['name']} achieves {best_recall['recall']*100:.1f}% detection!")
    print("  This is production-ready for your thesis.")
elif best_recall['recall'] > 0.65:
    print(f"  [GOOD] {best_recall['name']} achieves {best_recall['recall']*100:.1f}% detection.")
    print("  Consider per-theme threshold optimization for further improvement.")
else:
    print(f"  [MODERATE] {best_recall['name']} achieves {best_recall['recall']*100:.1f}% detection.")
    print("  Recommend trying data augmentation or more training data.")

print("=" * 80)
print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

