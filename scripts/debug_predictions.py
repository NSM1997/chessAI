"""
Debug script to see raw model predictions
"""

import sys
import os
import torch
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.ml.data_preprocessing import ChessBoardEncoder
from app.ml.tactical_classifier_pytorch import TacticalClassifierService
import chess

print("[DEBUG] Tactical Classifier Predictions\n")

# Load model
model_path = "backend/models/saved_models/tactical_classifier.pth"
service = TacticalClassifierService(model_path)

if not service.is_available:
    print("[ERROR] Model not loaded!")
    exit(1)

print(f"[OK] Model loaded with {len(service.theme_names)} themes\n")

# Test positions
test_positions = [
    {
        'name': 'Fork position',
        'fen': 'r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4'
    },
    {
        'name': 'Back rank mate',
        'fen': '6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1'
    },
    {
        'name': 'Pin',
        'fen': 'r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5'
    }
]

board_encoder = ChessBoardEncoder()

for pos in test_positions:
    print("=" * 60)
    print(f"Position: {pos['name']}")
    print(f"FEN: {pos['fen']}\n")
    
    # Encode board
    board = chess.Board(pos['fen'])
    board_tensor = board_encoder.encode_board(board)
    
    # Get RAW predictions (no threshold)
    tensor = torch.FloatTensor(board_tensor).permute(2, 0, 1).unsqueeze(0)
    tensor = tensor.to(service.device)
    
    service.model.eval()
    with torch.no_grad():
        predictions = service.model(tensor).cpu().numpy()[0]
    
    # Show ALL predictions (sorted by confidence)
    pred_list = [(service.theme_names[i], predictions[i]) for i in range(len(predictions))]
    pred_list.sort(key=lambda x: x[1], reverse=True)
    
    print("Raw Predictions (Top 10):")
    for theme, conf in pred_list[:10]:
        bar = "#" * int(conf * 50)
        print(f"  {theme:20s} {conf:.4f} {bar}")
    
    print(f"\nMax confidence: {predictions.max():.4f}")
    print(f"Min confidence: {predictions.min():.4f}")
    print(f"Mean confidence: {predictions.mean():.4f}")
    
    # Try different thresholds
    print("\nThemes detected at different thresholds:")
    for threshold in [0.5, 0.3, 0.2, 0.1, 0.05]:
        detected = [service.theme_names[i] for i in range(len(predictions)) if predictions[i] >= threshold]
        print(f"  Threshold {threshold:.2f}: {len(detected):2d} themes - {', '.join(detected[:5])}")
    
    print()

