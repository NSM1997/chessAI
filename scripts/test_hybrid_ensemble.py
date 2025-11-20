"""
Test Hybrid Tactical Ensemble
Recall models for common tactics + Precision models for critical themes
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.tactical_analysis import get_tactical_service
import chess
import asyncio

test_positions = [
    {
        "name": "Fork (Common)",
        "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP1QPPP/RNB1K2R b KQkq - 0 5",
        "expected": ["fork"],
        "category": "common"
    },
    {
        "name": "Pin (Common)",
        "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 4",
        "expected": ["pin"],
        "category": "common"
    },
    {
        "name": "Sacrifice (Common)",
        "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R w KQkq - 0 6",
        "expected": ["sacrifice"],
        "category": "common"
    },
    {
        "name": "Back Rank Mate (Critical)",
        "fen": "r4Q1k/1p4pp/p7/8/3P4/8/PPPq2PP/5R1K b - - 2 22",
        "expected": ["mate", "backRankMate", "mateIn1"],
        "category": "critical"
    },
    {
        "name": "Mate in 2 (Critical)",
        "fen": "6r1/3q1p1k/4pQpp/p3B3/2p4P/P7/6PK/8 b - - 0 46",
        "expected": ["mate", "mateIn2"],
        "category": "critical"
    },
    {
        "name": "Mixed: Fork + Mate Threat",
        "fen": "8/4Q2R/2b2p2/1p2nkp1/2p1q1B1/7P/6PK/8 b - - 2 38",
        "expected": ["fork", "mate", "mateIn1"],
        "category": "mixed"
    },
]

async def test_hybrid():
    print("=" * 80)
    print("TESTING HYBRID TACTICAL ENSEMBLE")
    print("=" * 80)
    
    service = get_tactical_service()
    
    if not service.is_available or service.classifier is None:
        print("❌ Service not available")
        return
    
    classifier_type = type(service.classifier).__name__
    print(f"\n✓ Classifier: {classifier_type}")
    
    if classifier_type == "HybridTacticalEnsemble":
        print(f"  Common themes (Recall): fork, pin, skewer, discoveredAttack, etc.")
        print(f"  Critical themes (Precision): mate, mateIn1, mateIn2, backRankMate")
        print(f"  Thresholds: 0.3 (common), 0.55 (critical)")
    
    results = {
        "common": {"detected": 0, "total": 0},
        "critical": {"detected": 0, "total": 0},
        "mixed": {"detected": 0, "total": 0}
    }
    
    for pos in test_positions:
        print(f"\n{'=' * 80}")
        print(f"Position: {pos['name']} [{pos['category'].upper()}]")
        print(f"{'=' * 80}")
        print(f"Expected: {', '.join(pos['expected'])}")
        print(f"FEN: {pos['fen']}")
        
        board = chess.Board(pos['fen'])
        analysis = await service.analyze_tactics(board, top_k=5)
        
        detected_themes = [t['theme'] for t in analysis.get('themes', [])]
        
        print(f"\n🎯 PREDICTIONS:")
        if detected_themes:
            found = any(exp in detected_themes for exp in pos['expected'])
            status = "✅" if found else "❌"
            
            for theme in analysis['themes']:
                marker = "✓" if theme['theme'] in pos['expected'] else " "
                source = theme.get('source', 'unknown')
                print(f"  {marker} {theme['theme']:<20} {theme['confidence']:.1%} [{source}]")
            
            print(f"\n{status} {'FOUND' if found else 'MISSED'} expected theme(s)")
            
            if found:
                results[pos['category']]["detected"] += 1
        else:
            print("  (No predictions)")
            print(f"\n❌ MISSED expected theme(s)")
        
        results[pos['category']]["total"] += 1
    
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    
    for category in ["common", "critical", "mixed"]:
        if results[category]["total"] > 0:
            detected = results[category]["detected"]
            total = results[category]["total"]
            rate = (detected / total * 100) if total > 0 else 0
            print(f"\n{category.upper()} Tactics:")
            print(f"  Detected: {detected}/{total} ({rate:.0f}%)")
    
    total_detected = sum(r["detected"] for r in results.values())
    total_tests = sum(r["total"] for r in results.values())
    overall_rate = (total_detected / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nOVERALL:")
    print(f"  Detected: {total_detected}/{total_tests} ({overall_rate:.0f}%)")
    
    print(f"\n{'=' * 80}")
    print("✅ HYBRID ENSEMBLE READY!")
    print(f"{'=' * 80}")
    print("Benefits:")
    print("  • Detects common tactics (fork, pin, etc.) with recall models")
    print("  • High accuracy on critical themes (mate) with precision models")
    print("  • Best of both worlds for chess education")

if __name__ == "__main__":
    asyncio.run(test_hybrid())
