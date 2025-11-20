"""
Comprehensive Test: All 20 Tactical Themes with Hybrid Ensemble
Tests both common tactics and critical themes
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.tactical_analysis import get_tactical_service
import chess
import asyncio

# Comprehensive test positions covering all themes
test_positions = [
    # COMMON THEMES (Recall models, threshold 0.3)
    {
        "name": "Knight Fork",
        "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP1QPPP/RNB1K2R b KQkq - 0 5",
        "expected": ["fork"],
        "category": "common"
    },
    {
        "name": "Pin",
        "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 4",
        "expected": ["pin"],
        "category": "common"
    },
    {
        "name": "Skewer",
        "fen": "1k6/8/1K6/8/8/8/8/1R6 w - - 0 1",
        "expected": ["skewer"],
        "category": "common"
    },
    {
        "name": "Discovered Attack",
        "fen": "r1bqkb1r/pppp1ppp/2n5/4p3/2BnP3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 4",
        "expected": ["discoveredAttack"],
        "category": "common"
    },
    {
        "name": "Double Attack",
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPPQPPP/RNB1KB1R b KQkq - 2 3",
        "expected": ["doubleAttack"],
        "category": "common"
    },
    {
        "name": "Hanging Piece",
        "fen": "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
        "expected": ["hangingPiece"],
        "category": "common"
    },
    {
        "name": "Trapped Piece",
        "fen": "rnbqkb1r/pppppppp/8/8/4n3/3P4/PPP1PPPP/RNBQKBNR w KQkq - 1 3",
        "expected": ["trappedPiece"],
        "category": "common"
    },
    {
        "name": "Sacrifice",
        "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R w KQkq - 0 6",
        "expected": ["sacrifice"],
        "category": "common"
    },
    {
        "name": "Deflection",
        "fen": "6k1/5ppp/8/8/8/2Q5/5PPP/6K1 w - - 0 1",
        "expected": ["deflection"],
        "category": "common"
    },
    {
        "name": "Attraction",
        "fen": "6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1",
        "expected": ["attraction"],
        "category": "common"
    },
    {
        "name": "Clearance",
        "fen": "6k1/1p2pp1p/p5p1/1bqP4/5N1P/6Q1/PPr2PP1/3R2K1 b - - 2 31",
        "expected": ["clearance"],
        "category": "common"
    },
    {
        "name": "Promotion",
        "fen": "6k1/5P2/6K1/8/8/8/8/8 w - - 0 1",
        "expected": ["promotion"],
        "category": "common"
    },
    
    # CRITICAL THEMES (Precision models, threshold 0.55)
    {
        "name": "Checkmate",
        "fen": "r4Q1k/1p4pp/p7/8/3P4/8/PPPq2PP/5R1K b - - 2 22",
        "expected": ["mate"],
        "category": "critical"
    },
    {
        "name": "Mate in 1",
        "fen": "6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1",
        "expected": ["mateIn1"],
        "category": "critical"
    },
    {
        "name": "Mate in 2",
        "fen": "6r1/3q1p1k/4pQpp/p3B3/2p4P/P7/6PK/8 b - - 0 46",
        "expected": ["mateIn2"],
        "category": "critical"
    },
    {
        "name": "Back Rank Mate",
        "fen": "6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1",
        "expected": ["backRankMate"],
        "category": "critical"
    },
    
    # ADDITIONAL THEMES (from recall models if detected)
    {
        "name": "X-Ray Attack",
        "fen": "6k1/5ppp/8/2r5/8/8/R4PPP/6K1 w - - 0 1",
        "expected": ["xRayAttack"],
        "category": "additional"
    },
    {
        "name": "Interference",
        "fen": "6k1/5ppp/8/8/8/8/5PPP/6K1 w - - 0 1",
        "expected": ["interference"],
        "category": "additional"
    },
    {
        "name": "Zugzwang",
        "fen": "8/8/8/8/8/4k3/4P3/4K3 b - - 0 1",
        "expected": ["zugzwang"],
        "category": "additional"
    },
    {
        "name": "Exposed King",
        "fen": "4k3/8/8/8/8/8/PPPPPPPP/RNBQKBNR w KQ - 0 1",
        "expected": ["exposedKing"],
        "category": "additional"
    },
]

async def test_all_themes():
    print("=" * 80)
    print("COMPREHENSIVE TEST: ALL TACTICAL THEMES")
    print("=" * 80)
    
    service = get_tactical_service()
    
    if not service.is_available or service.classifier is None:
        print("❌ Service not available")
        return
    
    classifier_type = type(service.classifier).__name__
    print(f"\n✓ Using: {classifier_type}")
    
    if classifier_type == "HybridTacticalEnsemble":
        print("\n🔍 Hybrid Configuration:")
        print("  • COMMON themes → Recall models (threshold 0.3)")
        print("  • CRITICAL themes → Precision models (threshold 0.55)")
        print("  • Top-5 predictions returned")
    
    results_by_category = {
        "common": {"detected": 0, "total": 0, "themes": []},
        "critical": {"detected": 0, "total": 0, "themes": []},
        "additional": {"detected": 0, "total": 0, "themes": []}
    }
    
    all_detected_themes = set()
    
    for i, pos in enumerate(test_positions, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {i}/{len(test_positions)}: {pos['name']} [{pos['category'].upper()}]")
        print(f"{'=' * 80}")
        print(f"Expected: {', '.join(pos['expected'])}")
        
        board = chess.Board(pos['fen'])
        analysis = await service.analyze_tactics(board, top_k=5)
        
        detected_themes = [t['theme'] for t in analysis.get('themes', [])]
        all_detected_themes.update(detected_themes)
        
        if detected_themes:
            found = any(exp in detected_themes for exp in pos['expected'])
            status = "✅" if found else "❌"
            
            print(f"\n{status} Predictions:")
            for theme in analysis['themes']:
                marker = "✓" if theme['theme'] in pos['expected'] else " "
                source = theme.get('source', '?')
                print(f"  {marker} {theme['theme']:<20} {theme['confidence']:.1%} [{source}]")
            
            if found:
                results_by_category[pos['category']]["detected"] += 1
                results_by_category[pos['category']]["themes"].extend(
                    [t for t in pos['expected'] if t in detected_themes]
                )
        else:
            print(f"\n❌ No predictions (missed: {', '.join(pos['expected'])})")
        
        results_by_category[pos['category']]["total"] += 1
    
    # Summary
    print(f"\n{'=' * 80}")
    print("RESULTS BY CATEGORY")
    print(f"{'=' * 80}")
    
    total_detected = 0
    total_tests = 0
    
    for category in ["common", "critical", "additional"]:
        stats = results_by_category[category]
        if stats["total"] > 0:
            rate = (stats["detected"] / stats["total"] * 100)
            total_detected += stats["detected"]
            total_tests += stats["total"]
            
            print(f"\n{category.upper()} THEMES:")
            print(f"  Detection Rate: {stats['detected']}/{stats['total']} ({rate:.0f}%)")
            if stats["themes"]:
                unique_detected = set(stats["themes"])
                print(f"  Detected: {', '.join(sorted(unique_detected))}")
    
    overall_rate = (total_detected / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{'=' * 80}")
    print(f"OVERALL: {total_detected}/{total_tests} ({overall_rate:.0f}%)")
    print(f"{'=' * 80}")
    
    print(f"\nUnique themes detected across all tests:")
    print(f"  {', '.join(sorted(all_detected_themes))}")
    print(f"  Total: {len(all_detected_themes)} different themes")
    
    print(f"\n{'=' * 80}")
    print("ANALYSIS")
    print(f"{'=' * 80}")
    
    if overall_rate >= 70:
        print("✅ Excellent coverage across theme categories!")
    elif overall_rate >= 50:
        print("✓ Good coverage, some themes need improvement")
    elif overall_rate >= 30:
        print("⚠️ Moderate coverage, many themes not detected")
    else:
        print("❌ Low coverage, significant gaps in detection")
    
    print("\nStrengths:")
    if results_by_category["critical"]["detected"] / max(results_by_category["critical"]["total"], 1) > 0.7:
        print("  • Strong detection of critical/mate themes")
    if results_by_category["common"]["detected"] / max(results_by_category["common"]["total"], 1) > 0.5:
        print("  • Good coverage of common tactical themes")
    
    print("\nRecommendations:")
    if overall_rate < 70:
        print("  • Consider adjusting thresholds for better coverage")
        print("  • Some themes may need additional training data")
    print("  • Hybrid approach successfully combines recall + precision")

if __name__ == "__main__":
    asyncio.run(test_all_themes())
