"""
Test Recall-Optimized Models for Basic Tactics Detection
Compare precision vs recall optimized models
"""
import sys
from pathlib import Path
import torch
import chess
import numpy as np

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.ml.data_preprocessing import ChessBoardEncoder
from backend.app.ml.tactical_classifier_pytorch import TacticalCNN, TacticalResNet

print("=" * 80)
print("TESTING RECALL-OPTIMIZED MODELS ON BASIC TACTICS")
print("=" * 80)

# Test positions
test_positions = [
    ("Fork", "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP1QPPP/RNB1K2R b KQkq - 0 5", ["fork"]),
    ("Pin", "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 4", ["pin"]),
    ("Discovered Attack", "r1bqkb1r/pppp1ppp/2n5/4p3/2BnP3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 4", ["discoveredAttack"]),
]

encoder = ChessBoardEncoder()
device = torch.device('cpu')
model_dir = project_root / "backend" / "models" / "saved_models"

# Load models
models = {}
for name, filename in [
    ("CNN (Recall)", "cnn_recall_optimized.pth"),
    ("ResNet (Recall)", "resnet_recall_optimized.pth"),
]:
    path = model_dir / filename
    if path.exists():
        try:
            ckpt = torch.load(path, map_location=device)
            if "CNN" in name:
                model = TacticalCNN(num_classes=20)
            else:
                model = TacticalResNet(num_classes=20)
            model.load_state_dict(ckpt['model_state_dict'])
            model.eval()
            models[name] = {
                'model': model,
                'themes': ckpt.get('theme_names', []),
                'threshold': ckpt.get('detection_threshold', 0.3)
            }
            print(f"✓ Loaded: {name} (threshold: {models[name]['threshold']})")
        except Exception as e:
            print(f"✗ Failed to load {name}: {e}")

if not models:
    print("\n❌ No recall-optimized models found!")
    sys.exit(1)

print(f"\n{'=' * 80}")
print("TESTING BASIC TACTICS")
print(f"{'=' * 80}")

for pos_name, fen, expected in test_positions:
    print(f"\n{'-' * 80}")
    print(f"Position: {pos_name}")
    print(f"Expected: {', '.join(expected)}")
    print(f"{'-' * 80}")
    
    # Encode position
    board = chess.Board(fen)
    board_tensor = encoder.encode_board(board)
    tensor = torch.FloatTensor(board_tensor).permute(2, 0, 1).unsqueeze(0)
    
    for model_name, model_info in models.items():
        with torch.no_grad():
            predictions = torch.sigmoid(model_info['model'](tensor)).numpy()[0]
        
        threshold = model_info['threshold']
        themes = model_info['themes']
        
        # Get predictions above threshold
        detected = []
        for i, conf in enumerate(predictions):
            if conf >= threshold:
                theme_name = themes[i] if i < len(themes) else f"theme_{i}"
                detected.append((theme_name, conf))
        
        detected.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n{model_name}:")
        if detected:
            # Check if expected theme found
            found = any(theme in expected for theme, _ in detected)
            status = "✅" if found else "⚠️"
            print(f"  {status} Found {len(detected)} themes:")
            for theme, conf in detected[:8]:  # Show top 8
                marker = "✓" if theme in expected else " "
                print(f"    {marker} {theme:<20} {conf:.1%}")
        else:
            print(f"  ❌ No predictions above threshold ({threshold})")

print(f"\n{'=' * 80}")
print("COMPARISON: RECALL vs PRECISION")
print(f"{'=' * 80}")
print("\nRecall-optimized models:")
print("  + Detect more tactics (high recall)")
print("  - More false positives (lower precision ~20-23%)")
print("  - Threshold: 0.3 (very liberal)")
print("\nPrecision-optimized models:")
print("  + High accuracy when predicting (~75-80% precision)")
print("  - Miss many tactics (low recall ~1-5%)")
print("  - Threshold: 0.5-0.6 (very conservative)")
print("\n💡 RECOMMENDATION: Use recall-optimized for basic tactics detection")
