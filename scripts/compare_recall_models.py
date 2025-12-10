"""
Compare Recall-Optimized Models
Save metrics to JSON and create visualizations
"""
import sys
from pathlib import Path
import torch
import numpy as np
import json
import matplotlib.pyplot as plt
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.ml.data_preprocessing import ChessDataset
from backend.app.ml.tactical_classifier_pytorch import TacticalCNN, TacticalResNet, TacticalTransformer
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import precision_recall_fscore_support

print("=" * 80)
print("COMPARING RECALL-OPTIMIZED MODELS")
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

# Model definitions
models_to_compare = [
    {
        'name': 'CNN',
        'path': 'backend/models/saved_models/cnn_recall_optimized.pth',
        'class': TacticalCNN,
        'color': '#3b82f6'
    },
    {
        'name': 'ResNet',
        'path': 'backend/models/saved_models/resnet_recall_optimized.pth',
        'class': TacticalResNet,
        'color': '#10b981'
    },
    {
        'name': 'Transformer',
        'path': 'backend/models/saved_models/transformer_recall_optimized.pth',
        'class': TacticalTransformer,
        'color': '#f59e0b'
    }
]

# Evaluate each model
print("[2/4] Loading and evaluating models...")
results = []
device = 'cpu'

for model_info in models_to_compare:
    print(f"\n  Loading {model_info['name']}...")
    
    # Load checkpoint
    checkpoint = torch.load(model_info['path'], map_location=device)
    
    # Extract stored metrics
    result = {
        'model': model_info['name'],
        'parameters': checkpoint.get('total_parameters', 0),
        'detection_threshold': checkpoint.get('detection_threshold', 0.3),
        'test_recall': checkpoint.get('test_recall', 0),
        'test_precision': checkpoint.get('test_precision', 0),
        'test_f1': checkpoint.get('test_f1', 0),
        'avg_per_theme_recall': checkpoint.get('avg_per_theme_recall', 0),
        'detected_themes_count': checkpoint.get('detected_themes_count', 0),
        'per_theme_metrics': checkpoint.get('per_theme_metrics', {}),
        'epochs_trained': checkpoint.get('epochs_trained', 0),
        'training_date': checkpoint.get('training_date', 'N/A'),
        'optimization_target': checkpoint.get('optimization_target', 'recall'),
        'techniques': checkpoint.get('techniques', 'N/A'),
        'color': model_info['color']
    }
    
    results.append(result)
    
    print(f"    Recall: {result['test_recall']:.4f} ({result['test_recall']*100:.1f}%)")
    print(f"    Precision: {result['test_precision']:.4f}")
    print(f"    F1: {result['test_f1']:.4f}")
    print(f"    Detected themes: {result['detected_themes_count']}/{num_classes}")

print("\n  All models loaded!\n")

# Save to JSON
print("[3/4] Saving comparison to JSON...")
output_dir = Path('backend/models/comparison')
output_dir.mkdir(parents=True, exist_ok=True)

comparison_data = {
    'timestamp': datetime.now().isoformat(),
    'model_type': 'recall_optimized',
    'test_dataset_size': len(test_dataset),
    'num_themes': num_classes,
    'theme_names': theme_names,
    'detection_threshold': 0.3,
    'models': results
}

json_path = output_dir / 'recall_models_comparison.json'
with open(json_path, 'w') as f:
    json.dump(comparison_data, f, indent=2)

print(f"  Saved to: {json_path}\n")

# Create visualizations
print("[4/4] Creating visualizations...")

plt.style.use('seaborn-v0_8-darkgrid')
model_names = [r['model'] for r in results]
colors = [r['color'] for r in results]

# Figure 1: Overall Metrics Comparison (3 subplots)
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.suptitle('Recall-Optimized Models Comparison', fontsize=16, fontweight='bold')

# Subplot 1: Recall (Detection Rate)
ax = axes[0]
recalls = [r['test_recall'] * 100 for r in results]
bars = ax.bar(model_names, recalls, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
ax.set_ylabel('Recall (Detection Rate %)', fontweight='bold', fontsize=12)
ax.set_title('Theme Detection Rate', fontweight='bold', fontsize=14)
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%',
            ha='center', va='bottom', fontweight='bold', fontsize=11)

# Subplot 2: Precision vs Recall
ax = axes[1]
precisions = [r['test_precision'] * 100 for r in results]
x = np.arange(len(model_names))
width = 0.35

bars1 = ax.bar(x - width/2, recalls, width, label='Recall', color='#3b82f6', alpha=0.8)
bars2 = ax.bar(x + width/2, precisions, width, label='Precision', color='#ef4444', alpha=0.8)

ax.set_ylabel('Score (%)', fontweight='bold', fontsize=12)
ax.set_title('Precision vs Recall Trade-off', fontweight='bold', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(model_names)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)

# Subplot 3: Detected Themes Count
ax = axes[2]
detected = [r['detected_themes_count'] for r in results]
bars = ax.bar(model_names, detected, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
ax.set_ylabel('Number of Themes', fontweight='bold', fontsize=12)
ax.set_title(f'Themes Detected (>10% recall)', fontweight='bold', fontsize=14)
ax.set_ylim(0, num_classes + 2)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}/{num_classes}',
            ha='center', va='bottom', fontweight='bold', fontsize=11)

plt.tight_layout()
viz_path = output_dir / 'recall_models_overall.png'
plt.savefig(viz_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {viz_path}")
plt.close()

# Figure 2: Per-Theme Recall Heatmap
fig, ax = plt.subplots(figsize=(14, 10))
fig.suptitle('Per-Theme Detection Rates (Recall)', fontsize=16, fontweight='bold')

# Prepare heatmap data
heatmap_data = []
theme_labels = []

for theme in theme_names:
    row = []
    has_data = False
    for result in results:
        if theme in result['per_theme_metrics']:
            recall = result['per_theme_metrics'][theme]['recall']
            row.append(recall)
            has_data = True
        else:
            row.append(0)
    
    if has_data:  # Only include themes that appear in test set
        heatmap_data.append(row)
        theme_labels.append(theme)

heatmap_array = np.array(heatmap_data)

# Create heatmap
im = ax.imshow(heatmap_array, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

# Set ticks
ax.set_xticks(np.arange(len(model_names)))
ax.set_yticks(np.arange(len(theme_labels)))
ax.set_xticklabels(model_names, fontweight='bold', fontsize=12)
ax.set_yticklabels(theme_labels, fontsize=11)

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Detection Rate (Recall)', rotation=270, labelpad=20, fontweight='bold', fontsize=12)

# Add text annotations
for i in range(len(theme_labels)):
    for j in range(len(model_names)):
        value = heatmap_array[i, j]
        text_color = 'white' if value < 0.5 else 'black'
        text = ax.text(j, i, f'{value:.0%}',
                      ha="center", va="center", color=text_color, 
                      fontsize=10, fontweight='bold')

ax.set_title('Detection Rate by Tactical Theme', pad=20, fontweight='bold', fontsize=14)
plt.tight_layout()
viz_path = output_dir / 'recall_models_per_theme.png'
plt.savefig(viz_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {viz_path}")
plt.close()

# Figure 3: Model Performance Radar Chart
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
fig.suptitle('Model Performance Profile', fontsize=16, fontweight='bold', y=0.98)

# Select top themes for radar (those with good detection)
top_themes = []
for theme in theme_labels[:10]:  # Top 10 themes
    top_themes.append(theme)

angles = np.linspace(0, 2 * np.pi, len(top_themes), endpoint=False).tolist()
angles += angles[:1]  # Complete the circle

for result in results:
    values = []
    for theme in top_themes:
        if theme in result['per_theme_metrics']:
            values.append(result['per_theme_metrics'][theme]['recall'])
        else:
            values.append(0)
    
    values += values[:1]  # Complete the circle
    
    ax.plot(angles, values, 'o-', linewidth=2, label=result['model'], color=result['color'])
    ax.fill(angles, values, alpha=0.15, color=result['color'])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(top_themes, fontsize=10)
ax.set_ylim(0, 1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
ax.grid(True)

plt.tight_layout()
viz_path = output_dir / 'recall_models_radar.png'
plt.savefig(viz_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {viz_path}")
plt.close()

# Figure 4: Improvement Over Original Models
fig, ax = plt.subplots(figsize=(12, 7))
fig.suptitle('Improvement: Original vs Recall-Optimized', fontsize=16, fontweight='bold')

# Original recalls (from previous training)
original_recalls = {
    'CNN': 0.1370,
    'ResNet': 0.1599,
    'Transformer': 0.0747
}

x = np.arange(len(model_names))
width = 0.35

original_vals = [original_recalls[name] * 100 for name in model_names]
optimized_vals = [r['test_recall'] * 100 for r in results]

bars1 = ax.bar(x - width/2, original_vals, width, label='Original', 
              color='#94a3b8', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x + width/2, optimized_vals, width, label='Recall-Optimized',
              color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_ylabel('Detection Rate (%)', fontweight='bold', fontsize=12)
ax.set_xlabel('Model', fontweight='bold', fontsize=12)
ax.set_title('Detection Rate Improvement', fontweight='bold', fontsize=14, pad=20)
ax.set_xticks(x)
ax.set_xticklabels(model_names, fontsize=12)
ax.legend(fontsize=12)
ax.grid(axis='y', alpha=0.3)

# Add value labels and improvement
for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
    height1 = bar1.get_height()
    height2 = bar2.get_height()
    
    ax.text(bar1.get_x() + bar1.get_width()/2., height1,
            f'{height1:.1f}%',
            ha='center', va='bottom', fontsize=10)
    
    ax.text(bar2.get_x() + bar2.get_width()/2., height2,
            f'{height2:.1f}%',
            ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Draw improvement arrow
    improvement = height2 - height1
    if improvement > 0:
        ax.annotate('', xy=(i, height2), xytext=(i, height1),
                   arrowprops=dict(arrowstyle='->', color='green', lw=2))
        ax.text(i + 0.3, (height1 + height2) / 2, f'+{improvement:.1f}%',
               fontsize=10, fontweight='bold', color='green')

plt.tight_layout()
viz_path = output_dir / 'recall_models_improvement.png'
plt.savefig(viz_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {viz_path}")
plt.close()

# Print summary
print("\n" + "=" * 80)
print("RECALL-OPTIMIZED MODELS SUMMARY")
print("=" * 80)
print(f"\n{'Model':<15} {'Recall':>10} {'Precision':>10} {'F1':>10} {'Detected':>12} {'Epochs':>8}")
print("-" * 80)

for r in results:
    print(f"{r['model']:<15} {r['test_recall']:>10.4f} {r['test_precision']:>10.4f} "
          f"{r['test_f1']:>10.4f} {r['detected_themes_count']:>12} {r['epochs_trained']:>8}")

# Find best model
best_recall = max(results, key=lambda x: x['test_recall'])
best_f1 = max(results, key=lambda x: x['test_f1'])

print("\n" + "-" * 80)
print(f"BEST DETECTION:  {best_recall['model']} ({best_recall['test_recall']*100:.1f}% recall)")
print(f"BEST F1 SCORE:   {best_f1['model']} (F1={best_f1['test_f1']:.4f})")
print("=" * 80)

print(f"\n[OK] All files saved to: {output_dir}/")
print("  - recall_models_comparison.json (metrics data)")
print("  - recall_models_overall.png (overall comparison)")
print("  - recall_models_per_theme.png (heatmap)")
print("  - recall_models_radar.png (performance profile)")
print("  - recall_models_improvement.png (before/after)")

print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

