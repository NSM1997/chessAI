"""
Create Comprehensive Visualizations for Precision Models and Ensembles
For thesis presentation and documentation
"""
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("=" * 80)
print("CREATING COMPREHENSIVE VISUALIZATIONS")
print("=" * 80)

# Load data
json_path = Path('backend/models/comparison/ensemble_all_3_precision.json')
with open(json_path, 'r') as f:
    data = json.load(f)

print(f"\nLoaded data: {len(data['strategies'])} strategies")

# Separate individual models and ensemble strategies
individuals = [s for s in data['strategies'] if 'Individual' in s['name']]
ensembles = [s for s in data['strategies'] if 'Individual' not in s['name'] and 'BEST MODEL' not in s['name']]

print(f"  Individual models: {len(individuals)}")
print(f"  Ensemble strategies: {len(ensembles)}")

# Create comprehensive figure
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Title
fig.suptitle('Precision-Optimized Models: Comprehensive Analysis\n'
             'CNN + ResNet + EfficientNet | Goal: >80% Precision',
             fontsize=18, fontweight='bold', y=0.98)

# ============================================================================
# Plot 1: Individual Models Comparison (Bar Chart)
# ============================================================================
ax1 = fig.add_subplot(gs[0, 0])

models = sorted(individuals, key=lambda x: x['precision'], reverse=True)
names = [m['name'].replace(' (Individual)', '') for m in models]
precisions = [m['precision'] * 100 for m in models]
colors_ind = ['#3b82f6', '#10b981', '#f59e0b']

bars = ax1.bar(names, precisions, color=colors_ind, alpha=0.8, edgecolor='black', linewidth=2)
ax1.set_ylabel('Precision (%)', fontweight='bold', fontsize=11)
ax1.set_title('Individual Model Performance', fontweight='bold', fontsize=13)
ax1.set_ylim(0, 100)
ax1.axhline(y=80, color='red', linestyle='--', linewidth=2, alpha=0.7, label='80% Target')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Add value labels
for bar, prec in zip(bars, precisions):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
            f'{prec:.1f}%',
            ha='center', va='bottom', fontweight='bold', fontsize=10)

# ============================================================================
# Plot 2: Ensemble Strategies Comparison (Horizontal Bar)
# ============================================================================
ax2 = fig.add_subplot(gs[0, 1:])

ensemble_sorted = sorted(ensembles, key=lambda x: x['precision'], reverse=True)
ens_names = [e['name'] for e in ensemble_sorted]
ens_prec = [e['precision'] * 100 for e in ensemble_sorted]

# Color code: green if >80%, yellow if >75%, red otherwise
colors_ens = []
for p in ens_prec:
    if p >= 80:
        colors_ens.append('#10b981')  # Green
    elif p >= 75:
        colors_ens.append('#f59e0b')  # Yellow
    else:
        colors_ens.append('#ef4444')  # Red

bars = ax2.barh(ens_names, ens_prec, color=colors_ens, alpha=0.8, edgecolor='black', linewidth=2)
ax2.axvline(x=80, color='red', linestyle='--', linewidth=2, alpha=0.7, label='80% Target')
ax2.set_xlabel('Precision (%)', fontweight='bold', fontsize=11)
ax2.set_title('Ensemble Strategy Performance', fontweight='bold', fontsize=13)
ax2.set_xlim(0, 100)
ax2.legend()
ax2.grid(axis='x', alpha=0.3)

# Add value labels
for bar, prec in zip(bars, ens_prec):
    width = bar.get_width()
    label = f'{prec:.1f}%'
    if prec >= 80:
        label += ' ✓'
    ax2.text(width + 2, bar.get_y() + bar.get_height()/2.,
            label,
            ha='left', va='center', fontweight='bold', fontsize=10)

# ============================================================================
# Plot 3: Precision vs Recall Scatter (All Strategies)
# ============================================================================
ax3 = fig.add_subplot(gs[1, :2])

# Plot individuals
for ind in individuals:
    name = ind['name'].replace(' (Individual)', '')
    ax3.scatter(ind['recall']*100, ind['precision']*100, 
               s=300, alpha=0.7, marker='s', edgecolors='black', linewidth=2,
               label=name)

# Plot ensembles
markers = ['o', 'v', '^', '<', '>', 'D']
for i, ens in enumerate(ensembles):
    ax3.scatter(ens['recall']*100, ens['precision']*100,
               s=250, alpha=0.7, marker=markers[i % len(markers)],
               edgecolors='black', linewidth=2, label=ens['name'])

ax3.axhline(y=80, color='red', linestyle='--', linewidth=2, alpha=0.5, label='80% Precision')
ax3.set_xlabel('Recall (%)', fontweight='bold', fontsize=11)
ax3.set_ylabel('Precision (%)', fontweight='bold', fontsize=11)
ax3.set_title('Precision vs Recall Trade-off (All Strategies)', fontweight='bold', fontsize=13)
ax3.legend(loc='best', fontsize=8, ncol=2)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(-1, 15)
ax3.set_ylim(65, 90)

# Add annotations for top performers
top_prec = max(ensembles, key=lambda x: x['precision'])
ax3.annotate(f"Best: {top_prec['name']}\n{top_prec['precision']:.1%}",
            xy=(top_prec['recall']*100, top_prec['precision']*100),
            xytext=(10, 85), fontsize=9, fontweight='bold',
            arrowprops=dict(arrowstyle='->', lw=2, color='green'),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))

# ============================================================================
# Plot 4: F1 Score Comparison
# ============================================================================
ax4 = fig.add_subplot(gs[1, 2])

all_strats = ensembles + individuals
all_strats_sorted = sorted(all_strats, key=lambda x: x['f1'], reverse=True)[:8]
f1_names = [s['name'].replace(' (Individual)', '').replace('BEST MODEL ', '')[:20] for s in all_strats_sorted]
f1_scores = [s['f1'] * 100 for s in all_strats_sorted]

bars = ax4.barh(f1_names, f1_scores, alpha=0.8, edgecolor='black', linewidth=1.5)
ax4.set_xlabel('F1 Score (%)', fontweight='bold', fontsize=11)
ax4.set_title('F1 Score (Top 8)', fontweight='bold', fontsize=13)
ax4.grid(axis='x', alpha=0.3)

for bar, score in zip(bars, f1_scores):
    width = bar.get_width()
    ax4.text(width + 0.5, bar.get_y() + bar.get_height()/2.,
            f'{score:.1f}%',
            ha='left', va='center', fontsize=9)

# ============================================================================
# Plot 5: Model Evolution (Line Chart)
# ============================================================================
ax5 = fig.add_subplot(gs[2, 0])

evolution = [
    ('CNN', 72.1),
    ('ResNet', 74.7),
    ('EfficientNet', 79.5),
    ('WEIGHTED\nEnsemble', 80.6),
    ('UNANIMOUS\nEnsemble', 83.1)
]

x_pos = np.arange(len(evolution))
labels = [e[0] for e in evolution]
values = [e[1] for e in evolution]

ax5.plot(x_pos, values, marker='o', linewidth=3, markersize=12, color='#3b82f6')
ax5.fill_between(x_pos, values, alpha=0.3, color='#3b82f6')
ax5.axhline(y=80, color='red', linestyle='--', linewidth=2, alpha=0.7, label='80% Target')
ax5.set_xticks(x_pos)
ax5.set_xticklabels(labels, fontsize=9)
ax5.set_ylabel('Precision (%)', fontweight='bold', fontsize=11)
ax5.set_title('Model Evolution → Ensemble', fontweight='bold', fontsize=13)
ax5.set_ylim(70, 85)
ax5.legend()
ax5.grid(True, alpha=0.3)

# Add value labels
for i, (x, y) in enumerate(zip(x_pos, values)):
    ax5.text(x, y + 1, f'{y:.1f}%', ha='center', fontweight='bold', fontsize=10)
    
# Add improvement arrow
ax5.annotate('', xy=(4, 83.1), xytext=(0, 72.1),
            arrowprops=dict(arrowstyle='->', lw=2, color='green', alpha=0.5))
ax5.text(2, 77, '+11.0%\nImprovement', ha='center', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

# ============================================================================
# Plot 6: Precision Distribution (Box Plot)
# ============================================================================
ax6 = fig.add_subplot(gs[2, 1])

precision_data = [
    [m['precision']*100 for m in individuals],
    [e['precision']*100 for e in ensembles]
]

bp = ax6.boxplot(precision_data, labels=['Individual\nModels', 'Ensemble\nStrategies'],
                patch_artist=True, showmeans=True)

for patch, color in zip(bp['boxes'], ['#3b82f6', '#10b981']):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)

ax6.axhline(y=80, color='red', linestyle='--', linewidth=2, alpha=0.7, label='80% Target')
ax6.set_ylabel('Precision (%)', fontweight='bold', fontsize=11)
ax6.set_title('Precision Distribution', fontweight='bold', fontsize=13)
ax6.legend()
ax6.grid(axis='y', alpha=0.3)

# ============================================================================
# Plot 7: Summary Statistics Table
# ============================================================================
ax7 = fig.add_subplot(gs[2, 2])
ax7.axis('off')

# Calculate statistics
best_ind = max(individuals, key=lambda x: x['precision'])
best_ens = max(ensembles, key=lambda x: x['precision'])
avg_ind_prec = np.mean([m['precision'] for m in individuals]) * 100
avg_ens_prec = np.mean([e['precision'] for e in ensembles]) * 100

summary_text = f"""
SUMMARY STATISTICS
{'='*30}

Best Individual Model:
  {best_ind['name'].replace(' (Individual)', '')}
  Precision: {best_ind['precision']:.1%}
  Recall: {best_ind['recall']:.1%}

Best Ensemble Strategy:
  {best_ens['name']}
  Precision: {best_ens['precision']:.1%}
  Recall: {best_ens['recall']:.1%}

Average Performance:
  Individual: {avg_ind_prec:.1f}%
  Ensemble: {avg_ens_prec:.1f}%

Key Achievement:
  🏆 {best_ens['precision']:.1%} Precision
  ✅ Exceeds 80% target
  📈 +{(best_ens['precision'] - best_ind['precision'])*100:.1f}% vs best model

Recommendation:
  Use UNANIMOUS ensemble
  (83.1% precision)
"""

ax7.text(0.1, 0.9, summary_text, transform=ax7.transAxes,
        fontsize=10, verticalalignment='top', family='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Save figure
output_dir = Path('backend/models/comparison')
output_path = output_dir / 'precision_models_comprehensive_analysis.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Saved: {output_path}")

# ============================================================================
# Create additional thesis-ready figures
# ============================================================================

# Figure 2: Clean comparison for thesis
fig2, axes = plt.subplots(2, 2, figsize=(16, 12))
fig2.suptitle('Precision-Optimized Models: Performance Comparison\n'
              'Chess Tactical Recognition',
              fontsize=16, fontweight='bold')

# 2.1: Individual Models
ax = axes[0, 0]
models = sorted(individuals, key=lambda x: x['precision'], reverse=True)
names = [m['name'].replace(' (Individual)', '') for m in models]
precisions = [m['precision'] * 100 for m in models]
bars = ax.bar(names, precisions, color=['#f59e0b', '#10b981', '#3b82f6'], 
             alpha=0.8, edgecolor='black', linewidth=2)
ax.set_ylabel('Precision (%)', fontweight='bold')
ax.set_title('Individual Models', fontweight='bold', fontsize=14)
ax.set_ylim(0, 100)
ax.axhline(y=80, color='red', linestyle='--', linewidth=2, label='Target: 80%')
ax.legend()
ax.grid(axis='y', alpha=0.3)
for bar, prec in zip(bars, precisions):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
            f'{prec:.1f}%', ha='center', fontweight='bold')

# 2.2: Top 4 Ensemble Strategies
ax = axes[0, 1]
top_ens = sorted(ensembles, key=lambda x: x['precision'], reverse=True)[:4]
ens_names = [e['name'] for e in top_ens]
ens_prec = [e['precision'] * 100 for e in top_ens]
colors = ['#10b981' if p >= 80 else '#f59e0b' for p in ens_prec]
bars = ax.bar(ens_names, ens_prec, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
ax.set_ylabel('Precision (%)', fontweight='bold')
ax.set_title('Top Ensemble Strategies', fontweight='bold', fontsize=14)
ax.set_ylim(0, 100)
ax.axhline(y=80, color='red', linestyle='--', linewidth=2, label='Target: 80%')
ax.legend()
ax.grid(axis='y', alpha=0.3)
ax.tick_params(axis='x', rotation=15)
for bar, prec in zip(bars, ens_prec):
    marker = ' ✓' if prec >= 80 else ''
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
            f'{prec:.1f}%{marker}', ha='center', fontweight='bold')

# 2.3: Precision-Recall Tradeoff
ax = axes[1, 0]
all_strategies = individuals + ensembles
for s in all_strategies:
    is_ind = 'Individual' in s['name']
    marker = 's' if is_ind else 'o'
    size = 200 if is_ind else 300
    label = s['name'].replace(' (Individual)', '')
    ax.scatter(s['recall']*100, s['precision']*100, 
              s=size, alpha=0.7, marker=marker, 
              edgecolors='black', linewidth=2, label=label)

ax.axhline(y=80, color='red', linestyle='--', linewidth=2, alpha=0.5)
ax.set_xlabel('Recall (%)', fontweight='bold')
ax.set_ylabel('Precision (%)', fontweight='bold')
ax.set_title('Precision vs Recall Trade-off', fontweight='bold', fontsize=14)
ax.legend(loc='best', fontsize=8, ncol=2)
ax.grid(True, alpha=0.3)

# 2.4: Improvement Metrics
ax = axes[1, 1]
metrics = ['Precision', 'Recall', 'F1 Score']
cnn_vals = [individuals[2]['precision']*100, individuals[2]['recall']*100, individuals[2]['f1']*100]
resnet_vals = [individuals[1]['precision']*100, individuals[1]['recall']*100, individuals[1]['f1']*100]
efficient_vals = [individuals[0]['precision']*100, individuals[0]['recall']*100, individuals[0]['f1']*100]
ensemble_vals = [best_ens['precision']*100, best_ens['recall']*100, best_ens['f1']*100]

x = np.arange(len(metrics))
width = 0.2

ax.bar(x - 1.5*width, cnn_vals, width, label='CNN', alpha=0.8)
ax.bar(x - 0.5*width, resnet_vals, width, label='ResNet', alpha=0.8)
ax.bar(x + 0.5*width, efficient_vals, width, label='EfficientNet', alpha=0.8)
ax.bar(x + 1.5*width, ensemble_vals, width, label='UNANIMOUS Ens.', alpha=0.8, edgecolor='red', linewidth=2)

ax.set_ylabel('Score (%)', fontweight='bold')
ax.set_title('Comprehensive Metric Comparison', fontweight='bold', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.legend()
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
output_path2 = output_dir / 'precision_models_thesis_ready.png'
plt.savefig(output_path2, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✓ Saved: {output_path2}")

print("\n" + "=" * 80)
print("VISUALIZATIONS COMPLETE!")
print("=" * 80)
print("\nGenerated files:")
print(f"  1. {output_path}")
print(f"  2. {output_path2}")
print("\nReady for thesis presentation!")
