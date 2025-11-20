import torch

checkpoint = torch.load('backend/models/saved_models/efficientnet_precision_optimized.pth', map_location='cpu')

print('=' * 80)
print('EFFICIENTNET-B0 MODEL RESULTS (GPU-TRAINED)')
print('=' * 80)

print(f'\nTest Set Performance:')
print(f'  Precision: {checkpoint["test_precision"]:.4f} ({checkpoint["test_precision"]*100:.1f}%)')
print(f'  Recall:    {checkpoint["test_recall"]:.4f} ({checkpoint["test_recall"]*100:.1f}%)')
print(f'  F1 Score:  {checkpoint["test_f1"]:.4f}')

print(f'\nTraining Info:')
print(f'  Epochs:     {checkpoint["epochs_trained"]}')
print(f'  Parameters: {checkpoint["total_parameters"]:,}')
print(f'  Threshold:  {checkpoint["precision_threshold"]}')
print(f'  Date:       {checkpoint["training_date"]}')
print(f'  Techniques: {checkpoint["techniques"]}')

print('\n' + '=' * 80)
print('COMPARISON WITH OTHER MODELS')
print('=' * 80)

models = [
    ('CNN', 0.721),
    ('ResNet', 0.747),
    ('EfficientNet', checkpoint["test_precision"])
]

models_sorted = sorted(models, key=lambda x: x[1], reverse=True)

print('\nRanked by Precision:')
for i, (name, prec) in enumerate(models_sorted, 1):
    marker = '🥇' if i == 1 else '🥈' if i == 2 else '🥉'
    print(f'  {marker} {i}. {name:15} {prec*100:.1f}%')

efficientnet_prec = checkpoint["test_precision"]

print('\n' + '=' * 80)
if efficientnet_prec > 0.747:
    print('🏆 SUCCESS! EfficientNet BEATS ResNet!')
    print(f'   EfficientNet: {efficientnet_prec*100:.1f}% > ResNet: 74.7%')
    print(f'   Improvement: +{(efficientnet_prec - 0.747)*100:.1f}%')
elif efficientnet_prec > 0.721:
    print('✅ GOOD! EfficientNet beats CNN, close to ResNet')
    print(f'   EfficientNet: {efficientnet_prec*100:.1f}%')
    print(f'   Gap to ResNet: {(0.747 - efficientnet_prec)*100:.1f}%')
else:
    print('⚠️  EfficientNet underperformed (needs more training)')
    print(f'   EfficientNet: {efficientnet_prec*100:.1f}%')

print('=' * 80)

print('\nRecommendation:')
if efficientnet_prec > 0.747:
    print('  → Use 3-model ensemble: CNN + ResNet + EfficientNet')
    print('  → EfficientNet as best individual model')
elif efficientnet_prec > 0.721:
    print('  → Use 3-model ensemble for diversity')
    print('  → ResNet as best individual model')
else:
    print('  → Use 2-model ensemble: CNN + ResNet')
    print('  → EfficientNet needs retraining')

print('\nNext step: Run ensemble comparison')
print('  python scripts/ensemble_precision_models.py')
