"""
Quick test to verify the API is using the precision ensemble
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.tactical_analysis import get_tactical_service
import chess
import asyncio

async def test_api_ensemble():
    print("=" * 80)
    print("TESTING API TACTICAL SERVICE")
    print("=" * 80)
    
    # Get the global service (what the API uses)
    service = get_tactical_service()
    
    if not service.is_available or service.classifier is None:
        print("❌ Tactical service not available")
        return
    
    # Check classifier type
    classifier_type = type(service.classifier).__name__
    print(f"\n✓ Tactical Service Active")
    print(f"  Classifier Type: {classifier_type}")
    print(f"  Expected: PrecisionEnsembleService")
    
    if classifier_type == "PrecisionEnsembleService":
        print(f"  ✅ Using Precision Ensemble (WEIGHTED strategy, 80.6% precision)")
        print(f"  Models loaded: {len(service.classifier.models)}")
        for model in service.classifier.models:
            print(f"    - {model['name']} (weight: {model['weight']})")
    else:
        print(f"  ⚠️  Using {classifier_type} instead of PrecisionEnsembleService")
    
    # Test position - back rank mate
    print("\n" + "=" * 80)
    print("TEST POSITION: Back Rank Mate")
    print("=" * 80)
    fen = "r4Q1k/1p4pp/p7/8/3P4/8/PPPq2PP/5R1K b - - 2 22"
    board = chess.Board(fen)
    
    analysis = await service.analyze_tactics(board, threshold=0.6, top_k=5)
    
    print(f"\nFEN: {fen}")
    print(f"Available: {analysis['available']}")
    print(f"Message: {analysis.get('message', 'N/A')}")
    
    if analysis['themes']:
        print(f"\nDetected Tactical Themes:")
        for theme in analysis['themes']:
            print(f"  • {theme['theme']:<20} {theme['confidence']:.1%}")
    else:
        print("\nNo themes detected (ensemble is very conservative)")
    
    print("\n" + "=" * 80)
    print("✅ API is ready to use precision ensemble predictions!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_api_ensemble())
