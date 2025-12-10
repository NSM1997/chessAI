"""
Test Detection Rate for Hybrid Tactical Ensemble
Calculates detection rates (recall) and false positive rates for common and critical themes
Matches the format described in section 5.5.3 of the thesis

Usage:
    # Test on all positions in test_puzzles.json
    python scripts/test_detection_rate.py
    
    # Test on first 100 positions
    python scripts/test_detection_rate.py --num-positions 100
    
    # Test on custom manually annotated positions
    python scripts/test_detection_rate.py --custom-file path/to/annotated_positions.json

Custom JSON format:
    [
        {
            "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
            "themes": ["fork", "pin"]
        },
        ...
    ]
"""
import sys
import json
import chess
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.ml.data_preprocessing import ChessBoardEncoder
from backend.app.ml.tactical_classifier_pytorch import HybridTacticalEnsemble

# Theme categories (matching the hybrid ensemble definition)
COMMON_THEMES = {
    'fork', 'pin', 'skewer', 'discoveredAttack', 'doubleAttack',
    'hangingPiece', 'trappedPiece', 'sacrifice', 'deflection',
    'attraction', 'clearance', 'promotion'
}

CRITICAL_THEMES = {
    'mate', 'mateIn1', 'mateIn2', 'backRankMate'
}

def categorize_themes(themes: List[str]) -> Dict[str, List[str]]:
    """Categorize themes into common, critical, and other."""
    common = [t for t in themes if t in COMMON_THEMES]
    critical = [t for t in themes if t in CRITICAL_THEMES]
    other = [t for t in themes if t not in COMMON_THEMES and t not in CRITICAL_THEMES]
    return {
        'common': common,
        'critical': critical,
        'other': other
    }

def test_detection_rate(
    positions: List[Dict],
    ensemble: HybridTacticalEnsemble,
    encoder: ChessBoardEncoder,
    max_positions: int = None
) -> Dict:
    """
    Test detection rate on a set of positions.
    
    Args:
        positions: List of position dicts with 'fen' and 'themes' keys
        ensemble: HybridTacticalEnsemble instance
        encoder: ChessBoardEncoder instance
        max_positions: Maximum number of positions to test (None = all)
    
    Returns:
        Dictionary with detection rate metrics
    """
    if max_positions:
        positions = positions[:max_positions]
    
    # Statistics
    stats = {
        'common': {
            'detected': 0,
            'total': 0,
            'false_positives': 0,
            'total_predictions': 0
        },
        'critical': {
            'detected': 0,
            'total': 0,
            'false_positives': 0,
            'total_predictions': 0
        },
        'overall': {
            'detected': 0,
            'total': 0,
            'false_positives': 0,
            'total_predictions': 0
        }
    }
    
    # Per-position results for detailed analysis
    position_results = []
    
    print(f"\n{'=' * 80}")
    print(f"TESTING {len(positions)} POSITIONS")
    print(f"{'=' * 80}\n")
    
    for i, pos in enumerate(positions, 1):
        fen = pos.get('fen') or pos.get('FEN', '')
        if not fen:
            print(f"⚠️  Position {i}: Missing FEN, skipping")
            continue
        
        # Get ground truth themes
        ground_truth = pos.get('themes', [])
        if isinstance(ground_truth, str):
            ground_truth = [ground_truth]
        
        # Filter to only tactical themes (exclude 'opening', 'middlegame', etc.)
        tactical_themes = [t for t in ground_truth 
                          if t in COMMON_THEMES or t in CRITICAL_THEMES]
        
        if not tactical_themes:
            # Skip positions without tactical themes
            continue
        
        # Categorize ground truth
        gt_categorized = categorize_themes(tactical_themes)
        
        # Encode board and get predictions
        try:
            board = chess.Board(fen)
            board_tensor = encoder.encode_board(board)
            predictions = ensemble.predict(board_tensor, top_k=10)
            
            # Extract predicted theme names
            predicted_themes = [p['theme'] for p in predictions]
            predicted_categorized = categorize_themes(predicted_themes)
            
            # Calculate metrics for this position
            # Common themes
            common_detected = set(gt_categorized['common']) & set(predicted_categorized['common'])
            common_missed = set(gt_categorized['common']) - set(predicted_categorized['common'])
            common_fp = set(predicted_categorized['common']) - set(gt_categorized['common'])
            
            # Critical themes
            critical_detected = set(gt_categorized['critical']) & set(predicted_categorized['critical'])
            critical_missed = set(gt_categorized['critical']) - set(predicted_categorized['critical'])
            critical_fp = set(predicted_categorized['critical']) - set(gt_categorized['critical'])
            
            # Update statistics
            stats['common']['detected'] += len(common_detected)
            stats['common']['total'] += len(gt_categorized['common'])
            stats['common']['false_positives'] += len(common_fp)
            stats['common']['total_predictions'] += len(predicted_categorized['common'])
            
            stats['critical']['detected'] += len(critical_detected)
            stats['critical']['total'] += len(gt_categorized['critical'])
            stats['critical']['false_positives'] += len(critical_fp)
            stats['critical']['total_predictions'] += len(predicted_categorized['critical'])
            
            # Overall (all tactical themes)
            all_gt = set(tactical_themes)
            all_pred = set(predicted_themes)
            stats['overall']['detected'] += len(all_gt & all_pred)
            stats['overall']['total'] += len(all_gt)
            stats['overall']['false_positives'] += len(all_pred - all_gt)
            stats['overall']['total_predictions'] += len(all_pred)
            
            # Store per-position result
            position_results.append({
                'position': i,
                'fen': fen,
                'ground_truth': tactical_themes,
                'predicted': predicted_themes,
                'common_detected': list(common_detected),
                'common_missed': list(common_missed),
                'common_fp': list(common_fp),
                'critical_detected': list(critical_detected),
                'critical_missed': list(critical_missed),
                'critical_fp': list(critical_fp)
            })
            
            # Print progress every 10 positions
            if i % 10 == 0:
                print(f"  Processed {i}/{len(positions)} positions...")
        
        except Exception as e:
            print(f"⚠️  Position {i}: Error processing - {e}")
            continue
    
    # Calculate final metrics
    results = {
        'stats': stats,
        'position_results': position_results,
        'metrics': {}
    }
    
    # Detection rates (recall)
    if stats['common']['total'] > 0:
        results['metrics']['common_detection_rate'] = stats['common']['detected'] / stats['common']['total']
    else:
        results['metrics']['common_detection_rate'] = 0.0
    
    if stats['critical']['total'] > 0:
        results['metrics']['critical_detection_rate'] = stats['critical']['detected'] / stats['critical']['total']
    else:
        results['metrics']['critical_detection_rate'] = 0.0
    
    if stats['overall']['total'] > 0:
        results['metrics']['overall_detection_rate'] = stats['overall']['detected'] / stats['overall']['total']
    else:
        results['metrics']['overall_detection_rate'] = 0.0
    
    # False positive rates
    if stats['common']['total_predictions'] > 0:
        results['metrics']['common_fp_rate'] = stats['common']['false_positives'] / stats['common']['total_predictions']
    else:
        results['metrics']['common_fp_rate'] = 0.0
    
    if stats['critical']['total_predictions'] > 0:
        results['metrics']['critical_fp_rate'] = stats['critical']['false_positives'] / stats['critical']['total_predictions']
    else:
        results['metrics']['critical_fp_rate'] = 0.0
    
    return results

def print_results(results: Dict):
    """Print results in the format matching section 5.5.3"""
    stats = results['stats']
    metrics = results['metrics']
    
    print(f"\n{'=' * 80}")
    print("DETECTION RATE RESULTS")
    print(f"{'=' * 80}\n")
    
    # Overall detection rate
    overall_detected = stats['overall']['detected']
    overall_total = stats['overall']['total']
    overall_rate = metrics['overall_detection_rate'] * 100
    
    print(f"Overall Detection Rate: {overall_rate:.1f}% (detected {overall_detected} out of {overall_total} ground-truth themes)\n")
    
    # By category
    print("By Category:\n")
    
    # Common themes
    common_detected = stats['common']['detected']
    common_total = stats['common']['total']
    common_rate = metrics['common_detection_rate'] * 100
    common_fp = stats['common']['false_positives']
    common_fp_rate = metrics['common_fp_rate'] * 100
    
    print(f"  Common Themes ({common_total} total):")
    print(f"    ├─ Detected: {common_detected} ({common_rate:.1f}%)")
    print(f"    └─ False Positives: {common_fp} ({common_fp_rate:.1f}% FP rate)\n")
    
    # Critical themes
    critical_detected = stats['critical']['detected']
    critical_total = stats['critical']['total']
    critical_rate = metrics['critical_detection_rate'] * 100
    critical_fp = stats['critical']['false_positives']
    critical_fp_rate = metrics['critical_fp_rate'] * 100
    
    print(f"  Critical Themes ({critical_total} total):")
    print(f"    ├─ Detected: {critical_detected} ({critical_rate:.1f}%)")
    print(f"    └─ False Positives: {critical_fp} ({critical_fp_rate:.1f}% FP rate)\n")
    
    # Summary statistics
    print(f"{'=' * 80}")
    print("SUMMARY STATISTICS")
    print(f"{'=' * 80}\n")
    print(f"Total Positions Tested: {len(results['position_results'])}")
    print(f"Total Ground-Truth Themes: {overall_total}")
    print(f"  ├─ Common: {common_total}")
    print(f"  └─ Critical: {critical_total}")
    print(f"\nTotal Predicted Themes: {stats['overall']['total_predictions']}")
    print(f"  ├─ Common: {stats['common']['total_predictions']}")
    print(f"  └─ Critical: {stats['critical']['total_predictions']}")

def main():
    """Main function to run detection rate test"""
    import sys
    sys.stdout.flush()
    print("=" * 80, flush=True)
    print("HYBRID ENSEMBLE DETECTION RATE TEST", flush=True)
    print("=" * 80, flush=True)
    
    # Load hybrid ensemble
    print("\n📦 Loading Hybrid Tactical Ensemble...")
    model_dir = project_root / "backend" / "models" / "saved_models"
    ensemble = HybridTacticalEnsemble(model_dir=model_dir)
    
    if not ensemble.is_available:
        print("❌ Error: Hybrid ensemble not available. Please ensure models are trained.")
        return
    
    print("✓ Hybrid ensemble loaded")
    print(f"  Common themes: {len(ensemble.common_themes)}")
    print(f"  Critical themes: {len(ensemble.critical_themes)}")
    
    # Initialize encoder
    encoder = ChessBoardEncoder()
    
    # Load test data
    print("\n📂 Loading test positions...")
    test_data_path = project_root / "backend" / "data" / "processed" / "test_puzzles.json"
    
    if not test_data_path.exists():
        print(f"❌ Error: Test data not found at {test_data_path}")
        print("   Please run create_presplit_datasets.py first or provide a custom JSON file.")
        return
    
    with open(test_data_path, 'r') as f:
        test_data = json.load(f)
    
    print(f"✓ Loaded {len(test_data)} test positions from dataset")
    
    # Option to test subset or all
    import argparse
    parser = argparse.ArgumentParser(description='Test detection rate for hybrid ensemble')
    parser.add_argument('--num-positions', type=int, default=None,
                       help='Number of positions to test (default: all)')
    parser.add_argument('--custom-file', type=str, default=None,
                       help='Path to custom JSON file with manually annotated positions')
    
    args = parser.parse_args()
    
    # Use custom file if provided
    if args.custom_file:
        custom_path = Path(args.custom_file)
        if not custom_path.exists():
            print(f"❌ Error: Custom file not found at {custom_path}")
            return
        with open(custom_path, 'r') as f:
            test_data = json.load(f)
        print(f"✓ Loaded {len(test_data)} positions from custom file")
    
    # Run test
    results = test_detection_rate(
        positions=test_data,
        ensemble=ensemble,
        encoder=encoder,
        max_positions=args.num_positions
    )
    
    # Print results
    print_results(results)
    
    # Optionally save detailed results
    output_file = project_root / "scripts" / "detection_rate_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Detailed results saved to: {output_file}")
    

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        error_file = project_root / "scripts" / "detection_rate_error.txt"
        with open(error_file, 'w') as f:
            f.write(f"Error: {str(e)}\n\n")
            f.write(traceback.format_exc())
        print(f"Error occurred. Details saved to: {error_file}")
        raise
