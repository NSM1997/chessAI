"""
Test Precision Ensemble with Real Tactical Positions
Compare model predictions against ground truth labels
"""
import sys
import json
import numpy as np
import torch
import chess
from pathlib import Path
from collections import Counter

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.ml.data_preprocessing import ChessBoardEncoder

print("=" * 80)
print("TESTING ENSEMBLE WITH REAL TACTICAL POSITIONS")
print("=" * 80)

# Load models
print("\n📦 Loading models...")
model_dir = project_root / "backend" / "models" / "saved_models"

from backend.app.ml.tactical_classifier_pytorch import TacticalCNN, TacticalResNet, TacticalEfficientNet

cnn = TacticalCNN()
cnn_checkpoint = torch.load(model_dir / "cnn_precision_optimized.pth", map_location='cpu')
cnn.load_state_dict(cnn_checkpoint['model_state_dict'])
cnn.eval()

resnet = TacticalResNet()
resnet_checkpoint = torch.load(model_dir / "resnet_precision_optimized.pth", map_location='cpu')
resnet.load_state_dict(resnet_checkpoint['model_state_dict'])
resnet.eval()

efficientnet = TacticalEfficientNet()
efficientnet_checkpoint = torch.load(model_dir / "efficientnet_precision_optimized.pth", map_location='cpu')
efficientnet.load_state_dict(efficientnet_checkpoint['model_state_dict'])
efficientnet.eval()

all_themes = cnn_checkpoint['theme_names']
print(f"✓ All models loaded | {len(all_themes)} themes")

# Load test data
print("\n📂 Loading test dataset...")
test_data_path = project_root / "backend" / "data" / "processed" / "test_puzzles.json"
with open(test_data_path, 'r') as f:
    test_data = json.load(f)

print(f"✓ Loaded {len(test_data)} test positions")

# Sample positions with diverse tactics
print("\n🎯 Selecting diverse tactical positions...")
theme_samples = {}
for puzzle in test_data:
    for theme in puzzle['themes']:
        if theme in all_themes and theme not in theme_samples:
            theme_samples[theme] = puzzle
            if len(theme_samples) >= 15:  # Get 15 diverse positions
                break
    if len(theme_samples) >= 15:
        break

print(f"✓ Selected {len(theme_samples)} positions with diverse themes")

# Encoder
encoder = ChessBoardEncoder()

def ensemble_predict(fen, strategy='unanimous', threshold=0.6):
    """
    Get ensemble predictions
    Strategies:
    - unanimous: All 3 must agree (83.1% precision, 0.4% recall)
    - weighted: Weighted average (80.6% precision, 2.5% recall)
    - majority: 2+ models agree (79.3% precision, 4.0% recall)
    """
    board = chess.Board(fen)
    board_tensor = encoder.encode_board(board)
    board_tensor = torch.FloatTensor(board_tensor).permute(2, 0, 1).unsqueeze(0)
    
    with torch.no_grad():
        cnn_pred = torch.sigmoid(cnn(board_tensor)).numpy()[0]
        resnet_pred = torch.sigmoid(resnet(board_tensor)).numpy()[0]
        efficient_pred = torch.sigmoid(efficientnet(board_tensor)).numpy()[0]
    
    if strategy == 'unanimous':
        # All 3 must agree
        predictions = (cnn_pred >= threshold) & (resnet_pred >= threshold) & (efficient_pred >= threshold)
    elif strategy == 'weighted':
        # Weighted average (EfficientNet 1.3x, ResNet 1.1x, CNN 1.0x)
        weighted_pred = (efficient_pred * 1.3 + resnet_pred * 1.1 + cnn_pred * 1.0) / 3.4
        predictions = weighted_pred >= threshold
    elif strategy == 'majority':
        # 2+ models agree
        votes = ((cnn_pred >= threshold).astype(int) + 
                (resnet_pred >= threshold).astype(int) + 
                (efficient_pred >= threshold).astype(int))
        predictions = votes >= 2
    
    # Get predicted themes
    predicted_themes = [all_themes[i] for i in range(len(all_themes)) if predictions[i]]
    
    # Get confidence scores for all themes
    avg_confidence = (cnn_pred + resnet_pred + efficient_pred) / 3
    
    return predicted_themes, avg_confidence, cnn_pred, resnet_pred, efficient_pred

# Test with different ensemble strategies
strategies = [
    ('unanimous', 0.6, "UNANIMOUS (All 3 agree) - 83.1% precision"),
    ('weighted', 0.6, "WEIGHTED (Confidence-weighted) - 80.6% precision"),
    ('majority', 0.6, "MAJORITY (2+ agree) - 79.3% precision"),
]

for strategy_name, threshold, description in strategies:
    print("\n" + "=" * 80)
    print(f"TESTING: {description}")
    print("=" * 80)
    
    total_correct = 0
    total_predicted = 0
    total_actual = 0
    results = []
    
    for i, (main_theme, puzzle) in enumerate(list(theme_samples.items())[:10], 1):
        fen = puzzle['fen']
        actual_themes = [t for t in puzzle['themes'] if t in all_themes]
        
        predicted_themes, avg_conf, cnn_pred, resnet_pred, efficient_pred = ensemble_predict(
            fen, strategy=strategy_name, threshold=threshold
        )
        
        # Calculate metrics
        correct = set(predicted_themes) & set(actual_themes)
        total_correct += len(correct)
        total_predicted += len(predicted_themes)
        total_actual += len(actual_themes)
        
        print(f"\n{'─' * 80}")
        print(f"Position {i}: Puzzle {puzzle['puzzleId']} (Rating: {puzzle['rating']})")
        print(f"{'─' * 80}")
        print(f"FEN: {fen}")
        print(f"\n✓ ACTUAL THEMES ({len(actual_themes)}):")
        print(f"   {', '.join(actual_themes)}")
        
        print(f"\n🤖 PREDICTED THEMES ({len(predicted_themes)}):")
        if predicted_themes:
            for theme in predicted_themes:
                mark = "✓" if theme in actual_themes else "✗"
                idx = all_themes.index(theme)
                print(f"   {mark} {theme:<20} | Confidence: {avg_conf[idx]:.3f} "
                      f"(CNN:{cnn_pred[idx]:.2f} ResNet:{resnet_pred[idx]:.2f} Eff:{efficient_pred[idx]:.2f})")
        else:
            print("   (No predictions)")
        
        # Show what was missed
        missed = set(actual_themes) - set(predicted_themes)
        if missed:
            print(f"\n❌ MISSED THEMES:")
            for theme in missed:
                idx = all_themes.index(theme)
                print(f"   {theme:<20} | Confidence: {avg_conf[idx]:.3f} "
                      f"(CNN:{cnn_pred[idx]:.2f} ResNet:{resnet_pred[idx]:.2f} Eff:{efficient_pred[idx]:.2f})")
        
        # Show top 5 confidence scores for context
        top_5_idx = np.argsort(avg_conf)[-5:][::-1]
        print(f"\n📊 TOP 5 CONFIDENCE SCORES:")
        for idx in top_5_idx:
            theme = all_themes[idx]
            in_actual = "✓" if theme in actual_themes else " "
            in_pred = "🤖" if theme in predicted_themes else " "
            print(f"   {in_actual}{in_pred} {theme:<20} | {avg_conf[idx]:.3f}")
        
        results.append({
            'puzzle_id': puzzle['puzzleId'],
            'actual': actual_themes,
            'predicted': predicted_themes,
            'correct': list(correct),
            'precision': len(correct) / len(predicted_themes) if predicted_themes else 0,
            'recall': len(correct) / len(actual_themes) if actual_themes else 0
        })
    
    # Summary
    print("\n" + "=" * 80)
    print(f"SUMMARY: {strategy_name.upper()}")
    print("=" * 80)
    
    precision = total_correct / total_predicted if total_predicted > 0 else 0
    recall = total_correct / total_actual if total_actual > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\nOverall Metrics (10 test positions):")
    print(f"  Precision: {precision:.1%} ({total_correct}/{total_predicted} predicted themes correct)")
    print(f"  Recall:    {recall:.1%} ({total_correct}/{total_actual} actual themes found)")
    print(f"  F1 Score:  {f1:.3f}")
    
    per_position_metrics = [r for r in results if r['predicted']]
    if per_position_metrics:
        avg_precision = np.mean([r['precision'] for r in per_position_metrics])
        avg_recall = np.mean([r['recall'] for r in per_position_metrics])
        print(f"\nPer-Position Averages (positions with predictions):")
        print(f"  Avg Precision: {avg_precision:.1%}")
        print(f"  Avg Recall:    {avg_recall:.1%}")
    
    print(f"\nPrediction Coverage:")
    positions_with_pred = sum(1 for r in results if r['predicted'])
    print(f"  {positions_with_pred}/10 positions had at least one prediction")

print("\n" + "=" * 80)
print("TESTING COMPLETE!")
print("=" * 80)
print("\nKey Insights:")
print("  - UNANIMOUS: Most conservative, highest precision when it predicts")
print("  - WEIGHTED: Balanced approach, good precision with moderate coverage")
print("  - MAJORITY: More predictions, catches more themes but lower precision")
print("  - All strategies struggle with recall due to precision optimization")
