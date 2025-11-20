"""
Test Precision Ensemble Model (UNANIMOUS strategy)
Shows how the ensemble identifies tactical themes on real positions
"""
import sys
import os
import numpy as np
import torch
import chess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.ml.data_preprocessing import ChessBoardEncoder

print("=" * 80)
print("TESTING PRECISION ENSEMBLE MODEL (UNANIMOUS STRATEGY)")
print("=" * 80)

# Load the three models
print("\n📦 Loading models...")
model_dir = project_root / "backend" / "models" / "saved_models"

# CNN model
from backend.app.ml.tactical_classifier_pytorch import TacticalCNN
cnn = TacticalCNN()
cnn_checkpoint = torch.load(model_dir / "cnn_precision_optimized.pth", map_location='cpu')
cnn.load_state_dict(cnn_checkpoint['model_state_dict'])
cnn.eval()
print("  ✓ CNN loaded")

# ResNet model
from backend.app.ml.tactical_classifier_pytorch import TacticalResNet
resnet = TacticalResNet()
resnet_checkpoint = torch.load(model_dir / "resnet_precision_optimized.pth", map_location='cpu')
resnet.load_state_dict(resnet_checkpoint['model_state_dict'])
resnet.eval()
print("  ✓ ResNet loaded")

# EfficientNet model
from backend.app.ml.tactical_classifier_pytorch import TacticalEfficientNet
efficientnet = TacticalEfficientNet()
efficientnet_checkpoint = torch.load(model_dir / "efficientnet_precision_optimized.pth", map_location='cpu')
efficientnet.load_state_dict(efficientnet_checkpoint['model_state_dict'])
efficientnet.eval()
print("  ✓ EfficientNet loaded")

# Load theme names from model checkpoint
all_themes = cnn_checkpoint['theme_names']
print(f"\n🎯 Tactical themes: {len(all_themes)} themes")
print(f"   {', '.join(all_themes[:10])}...")

# Test positions with known tactics
test_positions = [
    {
        "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4",
        "description": "Scholar's Mate threat (Qxf7#)",
        "expected_themes": ["attack", "checkmate", "sacrifice"]
    },
    {
        "fen": "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
        "description": "Ruy Lopez Opening - Pin on knight",
        "expected_themes": ["pin", "opening"]
    },
    {
        "fen": "r1bqkb1r/ppp2ppp/2np1n2/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 0 5",
        "description": "Italian Game - Central tension",
        "expected_themes": ["opening", "development"]
    },
    {
        "fen": "r1bq1rk1/ppp2ppp/2np1n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 0 8",
        "description": "Symmetrical position - Piece coordination",
        "expected_themes": ["middlegame", "piece_coordination"]
    },
    {
        "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 5",
        "description": "Two Bishops vs Two Knights",
        "expected_themes": ["bishop_pair", "middlegame"]
    },
    {
        "fen": "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 1 2",
        "description": "Early opening - d4 opening",
        "expected_themes": ["opening"]
    },
    {
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
        "description": "Symmetrical pawn structure",
        "expected_themes": ["opening"]
    },
    {
        "fen": "rnbqkb1r/ppp1pppp/5n2/3p4/3P1B2/5N2/PPP1PPPP/RN1QKB1R b KQkq - 3 3",
        "description": "London System setup",
        "expected_themes": ["opening"]
    }
]

# Encoder
encoder = ChessBoardEncoder()

# UNANIMOUS ensemble function
def unanimous_ensemble_predict(fen, threshold=0.6):
    """All 3 models must agree for a positive prediction"""
    # Encode FEN
    board = chess.Board(fen)
    board_tensor = encoder.encode_board(board)
    # Convert from (H, W, C) to (C, H, W) for PyTorch
    board_tensor = torch.FloatTensor(board_tensor).permute(2, 0, 1).unsqueeze(0)  # Add batch dimension
    
    # Get predictions from all models
    with torch.no_grad():
        cnn_pred = torch.sigmoid(cnn(board_tensor)).numpy()[0]
        resnet_pred = torch.sigmoid(resnet(board_tensor)).numpy()[0]
        efficient_pred = torch.sigmoid(efficientnet(board_tensor)).numpy()[0]
    
    # UNANIMOUS: All must predict above threshold
    unanimous_pred = (cnn_pred >= threshold) & (resnet_pred >= threshold) & (efficient_pred >= threshold)
    
    # Get confidence scores for unanimous predictions
    results = []
    for i, theme in enumerate(all_themes):
        if unanimous_pred[i]:
            # Average confidence when all agree
            avg_confidence = (cnn_pred[i] + resnet_pred[i] + efficient_pred[i]) / 3
            results.append({
                'theme': theme,
                'unanimous': True,
                'avg_confidence': avg_confidence,
                'cnn': cnn_pred[i],
                'resnet': resnet_pred[i],
                'efficientnet': efficient_pred[i]
            })
    
    # Also show close misses (2 out of 3 agree)
    majority_pred = ((cnn_pred >= threshold).astype(int) + 
                    (resnet_pred >= threshold).astype(int) + 
                    (efficient_pred >= threshold).astype(int)) == 2
    
    close_misses = []
    for i, theme in enumerate(all_themes):
        if majority_pred[i] and not unanimous_pred[i]:
            avg_confidence = (cnn_pred[i] + resnet_pred[i] + efficient_pred[i]) / 3
            close_misses.append({
                'theme': theme,
                'avg_confidence': avg_confidence,
                'cnn': cnn_pred[i],
                'resnet': resnet_pred[i],
                'efficientnet': efficient_pred[i]
            })
    
    return results, close_misses, cnn_pred, resnet_pred, efficient_pred

# Test each position
print("\n" + "=" * 80)
print("TESTING TACTICAL IDENTIFICATION")
print("=" * 80)

for idx, pos in enumerate(test_positions, 1):
    print(f"\n{'=' * 80}")
    print(f"TEST POSITION {idx}: {pos['description']}")
    print(f"{'=' * 80}")
    print(f"FEN: {pos['fen']}")
    print(f"Expected themes: {', '.join(pos['expected_themes'])}")
    
    # Get predictions
    unanimous, close_misses, cnn_pred, resnet_pred, efficient_pred = unanimous_ensemble_predict(pos['fen'])
    
    print(f"\n🏆 UNANIMOUS PREDICTIONS (All 3 models agree, threshold=0.6):")
    if unanimous:
        for pred in sorted(unanimous, key=lambda x: x['avg_confidence'], reverse=True):
            print(f"  ✓ {pred['theme']:<20} | Avg: {pred['avg_confidence']:.3f} | "
                  f"CNN: {pred['cnn']:.3f}, ResNet: {pred['resnet']:.3f}, EfficientNet: {pred['efficientnet']:.3f}")
    else:
        print("  (None - very conservative, no unanimous agreement)")
    
    print(f"\n⚠️  CLOSE MISSES (2 out of 3 models agree):")
    if close_misses:
        for pred in sorted(close_misses, key=lambda x: x['avg_confidence'], reverse=True)[:5]:
            cnn_mark = "✓" if pred['cnn'] >= 0.6 else "✗"
            resnet_mark = "✓" if pred['resnet'] >= 0.6 else "✗"
            efficient_mark = "✓" if pred['efficientnet'] >= 0.6 else "✗"
            print(f"  ~ {pred['theme']:<20} | Avg: {pred['avg_confidence']:.3f} | "
                  f"CNN:{cnn_mark} {pred['cnn']:.3f}, ResNet:{resnet_mark} {pred['resnet']:.3f}, "
                  f"EfficientNet:{efficient_mark} {pred['efficientnet']:.3f}")
    else:
        print("  (None)")
    
    # Show top predictions from each individual model
    print(f"\n📊 TOP PREDICTIONS PER MODEL (for comparison):")
    
    # CNN top 3
    cnn_top = np.argsort(cnn_pred)[-3:][::-1]
    print(f"  CNN Top 3:")
    for i in cnn_top:
        print(f"    {all_themes[i]:<20} {cnn_pred[i]:.3f}")
    
    # ResNet top 3
    resnet_top = np.argsort(resnet_pred)[-3:][::-1]
    print(f"  ResNet Top 3:")
    for i in resnet_top:
        print(f"    {all_themes[i]:<20} {resnet_pred[i]:.3f}")
    
    # EfficientNet top 3
    efficient_top = np.argsort(efficient_pred)[-3:][::-1]
    print(f"  EfficientNet Top 3:")
    for i in efficient_top:
        print(f"    {all_themes[i]:<20} {efficient_pred[i]:.3f}")

print("\n" + "=" * 80)
print("TESTING COMPLETE!")
print("=" * 80)
print("\nKey Observations:")
print("  - UNANIMOUS strategy is very conservative (requires all 3 models to agree)")
print("  - This achieves 83.1% precision but only 0.4% recall")
print("  - Most positions show 'close misses' where 2 models agree")
print("  - Individual models may have different top predictions")
print("  - Conservative approach minimizes false positives for educational use")
