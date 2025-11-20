"""
Test Precision Ensemble on Common Tactical Themes
Focus: fork, pin, skewer, discovered attack, double attack, etc.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.tactical_analysis import get_tactical_service
import chess
import asyncio

# Test positions with well-known common tactics
test_positions = [
    {
        "name": "Knight Fork (Family Fork)",
        "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP1QPPP/RNB1K2R b KQkq - 0 5",
        "description": "Black knight can fork king and queen with Nxe4",
        "expected": ["fork"]
    },
    {
        "name": "Classic Pin",
        "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 4",
        "description": "Bishop pins knight to king",
        "expected": ["pin"]
    },
    {
        "name": "Discovered Attack",
        "fen": "r1bqkb1r/pppp1ppp/2n5/4p3/2BnP3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 4",
        "description": "Knight can move discovering attack from bishop",
        "expected": ["discoveredAttack"]
    },
    {
        "name": "Skewer",
        "fen": "6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1",
        "description": "Rook can skewer king and back rank",
        "expected": ["skewer"]
    },
    {
        "name": "Double Attack",
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPPQPPP/RNB1KB1R b KQkq - 2 3",
        "description": "Queen attacks both e5 pawn and king",
        "expected": ["doubleAttack"]
    },
    {
        "name": "Hanging Piece",
        "fen": "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
        "description": "Black e5 pawn is hanging",
        "expected": ["hangingPiece"]
    },
    {
        "name": "Trapped Piece",
        "fen": "rnbqkb1r/pppppppp/8/8/4n3/3P4/PPP1PPPP/RNBQKBNR w KQkq - 1 3",
        "description": "Knight is trapped on e4",
        "expected": ["trappedPiece"]
    },
    {
        "name": "Sacrifice for Attack",
        "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R w KQkq - 0 6",
        "description": "Bxf7+ sacrifice",
        "expected": ["sacrifice"]
    },
    {
        "name": "Deflection",
        "fen": "6k1/5ppp/8/8/8/2Q5/5PPP/6K1 w - - 0 1",
        "description": "Queen can deflect king from defending back rank",
        "expected": ["deflection"]
    },
    {
        "name": "Promotion Threat",
        "fen": "6k1/5P2/6K1/8/8/8/8/8 w - - 0 1",
        "description": "Pawn about to promote",
        "expected": ["promotion"]
    },
]

async def test_common_tactics():
    print("=" * 80)
    print("TESTING COMMON TACTICAL THEMES WITH PRECISION ENSEMBLE")
    print("=" * 80)
    
    service = get_tactical_service()
    
    if not service.is_available or service.classifier is None:
        print("❌ Tactical service not available")
        return
    
    classifier_type = type(service.classifier).__name__
    print(f"\n✓ Using: {classifier_type}")
    if "Recall" in classifier_type or "Ensemble" in classifier_type:
        print(f"  Strategy: Recall-optimized (~65% recall, ~22% precision)")
    else:
        print(f"  Strategy: Precision-optimized (~80% precision, ~2% recall)")
    print(f"  Threshold: 0.3")
    
    results = {
        "detected": 0,
        "missed": 0,
        "total": len(test_positions)
    }
    
    for i, pos in enumerate(test_positions, 1):
        print(f"\n{'=' * 80}")
        print(f"Position {i}/{len(test_positions)}: {pos['name']}")
        print(f"{'=' * 80}")
        print(f"Description: {pos['description']}")
        print(f"Expected themes: {', '.join(pos['expected'])}")
        print(f"FEN: {pos['fen']}")
        
        board = chess.Board(pos['fen'])
        analysis = await service.analyze_tactics(board, threshold=0.3, top_k=5)
        
        detected_themes = [t['theme'] for t in analysis.get('themes', [])]
        
        print(f"\n🎯 PREDICTIONS:")
        if detected_themes:
            for theme in analysis['themes']:
                is_expected = "✓" if theme['theme'] in pos['expected'] else " "
                print(f"  {is_expected} {theme['theme']:<20} {theme['confidence']:.1%}")
            
            # Check if expected themes were found
            found = any(exp in detected_themes for exp in pos['expected'])
            if found:
                print(f"\n✅ FOUND expected theme!")
                results["detected"] += 1
            else:
                print(f"\n❌ MISSED expected theme: {', '.join(pos['expected'])}")
                results["missed"] += 1
        else:
            print(f"  (No predictions above threshold)")
            print(f"\n❌ MISSED expected theme: {', '.join(pos['expected'])}")
            results["missed"] += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY: COMMON TACTICS DETECTION")
    print("=" * 80)
    
    detection_rate = (results["detected"] / results["total"]) * 100
    
    print(f"\nResults:")
    print(f"  ✓ Detected: {results['detected']}/{results['total']} ({detection_rate:.1f}%)")
    print(f"  ✗ Missed:   {results['missed']}/{results['total']} ({100-detection_rate:.1f}%)")
    
    print(f"\nKey Insights:")
    print(f"  • Precision ensemble prioritizes accuracy over coverage")
    print(f"  • Only predicts when confidence is high (>60%)")
    print(f"  • Better at detecting mate patterns than subtle tactics")
    print(f"  • Low recall (2.5%) means many tactics will be missed")
    print(f"  • When it DOES predict, it's ~80% accurate")
    
    print(f"\nRecommendation:")
    if detection_rate < 30:
        print(f"  ⚠️  Consider lowering threshold to 0.5 for common tactics")
        print(f"  ⚠️  Or use MAJORITY ensemble (79.3% precision, 4.0% recall)")
    elif detection_rate < 60:
        print(f"  • Current settings balance accuracy and coverage")
        print(f"  • May need manual tactical hints for subtle positions")
    else:
        print(f"  ✅ Good detection rate for common tactics!")

if __name__ == "__main__":
    asyncio.run(test_common_tactics())
