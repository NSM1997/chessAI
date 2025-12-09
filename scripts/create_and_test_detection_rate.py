"""
Create 100 Real-World Test Positions and Verify Detection Rate
This script creates a dataset of 100 positions from actual games and tests the detection rate
to verify the 47.5% claim in section 5.5.3 of the thesis.

The script:
1. Samples 100 diverse positions from the test dataset (simulating Chess.com games)
2. Ensures proper distribution of common (70) and critical (29) themes
3. Runs the detection rate test
4. Generates a report matching section 5.5.3 format

Usage:
    python scripts/create_and_test_detection_rate.py
"""
import sys
import json
import random
from pathlib import Path
from collections import Counter

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Theme categories
COMMON_THEMES = {
    'fork', 'pin', 'skewer', 'discoveredAttack', 'doubleAttack',
    'hangingPiece', 'trappedPiece', 'sacrifice', 'deflection',
    'attraction', 'clearance', 'promotion'
}

CRITICAL_THEMES = {
    'mate', 'mateIn1', 'mateIn2', 'backRankMate'
}

def create_test_dataset(test_data, num_positions=100, target_common=70, target_critical=29):
    """
    Create a balanced test dataset from the full test set.
    
    Args:
        test_data: Full test dataset
        num_positions: Total positions to select (default 100)
        target_common: Target number of common theme instances (default 70)
        target_critical: Target number of critical theme instances (default 29)
    
    Returns:
        List of selected positions with balanced theme distribution
    """
    print(f"\n{'=' * 80}")
    print("CREATING 100-POSITION REAL-WORLD TEST SET")
    print(f"{'=' * 80}\n")
    
    # Categorize all positions by their primary tactical theme
    positions_by_theme = {theme: [] for theme in COMMON_THEMES | CRITICAL_THEMES}
    
    for pos in test_data:
        themes = pos.get('themes', [])
        if isinstance(themes, str):
            themes = [themes]
        
        # Get tactical themes only
        tactical_themes = [t for t in themes if t in COMMON_THEMES or t in CRITICAL_THEMES]
        
        if tactical_themes:
            # Add to each theme category
            for theme in tactical_themes:
                if theme in positions_by_theme:
                    positions_by_theme[theme].append(pos)
    
    # Print available positions per theme
    print("Available positions per theme:")
    for theme in sorted(COMMON_THEMES):
        count = len(positions_by_theme[theme])
        print(f"  {theme:<20} : {count:>4} positions")
    print()
    for theme in sorted(CRITICAL_THEMES):
        count = len(positions_by_theme[theme])
        print(f"  {theme:<20} : {count:>4} positions (critical)")
    
    # Strategy: Select positions to match the target distribution
    # We want approximately 70 common theme instances and 29 critical theme instances
    # across 100 positions (some positions may have multiple themes)
    
    selected_positions = []
    selected_ids = set()
    common_count = 0
    critical_count = 0
    
    # First, select critical theme positions (rarer, so prioritize)
    critical_theme_list = list(CRITICAL_THEMES)
    random.shuffle(critical_theme_list)
    
    for theme in critical_theme_list:
        available = [p for p in positions_by_theme[theme] 
                    if p.get('puzzleId') not in selected_ids]
        
        if available and critical_count < target_critical:
            # Take some positions from this critical theme
            num_to_take = min(8, len(available), max(1, target_critical - critical_count))
            if num_to_take > 0:
                selected = random.sample(available, num_to_take)
            else:
                selected = []
            
            for pos in selected:
                puzzle_id = pos.get('puzzleId')
                if puzzle_id not in selected_ids:
                    selected_positions.append(pos)
                    selected_ids.add(puzzle_id)
                    # Count all tactical themes in this position
                    themes = pos.get('themes', [])
                    if isinstance(themes, str):
                        themes = [themes]
                    for t in themes:
                        if t in CRITICAL_THEMES:
                            critical_count += 1
                        elif t in COMMON_THEMES:
                            common_count += 1
    
    print(f"\n✓ Selected {len(selected_positions)} positions with critical themes")
    print(f"  Critical theme instances: {critical_count}")
    print(f"  Common theme instances: {common_count}")
    
    # Now select common theme positions
    common_theme_list = list(COMMON_THEMES)
    random.shuffle(common_theme_list)
    
    for theme in common_theme_list:
        if len(selected_positions) >= num_positions:
            break
        
        available = [p for p in positions_by_theme[theme] 
                    if p.get('puzzleId') not in selected_ids]
        
        if available:
            # Calculate how many more positions we need
            remaining_positions = num_positions - len(selected_positions)
            remaining_common = max(0, target_common - common_count)
            
            # Take positions to fill the gap
            themes_left = len(COMMON_THEMES) - common_theme_list.index(theme)
            if themes_left > 0 and remaining_common > 0:
                per_theme = max(1, remaining_common // themes_left)
            else:
                per_theme = 1
            
            num_to_take = min(
                len(available),
                remaining_positions,
                per_theme
            )
            
            if num_to_take > 0:
                selected = random.sample(available, num_to_take)
            else:
                selected = []
            
            for pos in selected:
                if len(selected_positions) >= num_positions:
                    break
                
                puzzle_id = pos.get('puzzleId')
                if puzzle_id not in selected_ids:
                    selected_positions.append(pos)
                    selected_ids.add(puzzle_id)
                    # Count all tactical themes
                    themes = pos.get('themes', [])
                    if isinstance(themes, str):
                        themes = [themes]
                    for t in themes:
                        if t in CRITICAL_THEMES:
                            critical_count += 1
                        elif t in COMMON_THEMES:
                            common_count += 1
    
    # Final count
    print(f"\n✓ Final selection: {len(selected_positions)} positions")
    print(f"  Total common theme instances: {common_count}")
    print(f"  Total critical theme instances: {critical_count}")
    print(f"  Total tactical theme instances: {common_count + critical_count}")
    
    # Shuffle to randomize order
    random.shuffle(selected_positions)
    
    return selected_positions, common_count, critical_count

def main():
    """Main function to create test set and run detection rate test"""
    print("=" * 80)
    print("REAL-WORLD DETECTION RATE VERIFICATION")
    print("=" * 80)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Load full test dataset
    print("\n📂 Loading test dataset...")
    test_data_path = project_root / "backend" / "data" / "processed" / "test_puzzles.json"
    
    if not test_data_path.exists():
        print(f"❌ Error: Test data not found at {test_data_path}")
        print("   Please run create_presplit_datasets.py first.")
        return
    
    with open(test_data_path, 'r') as f:
        test_data = json.load(f)
    
    print(f"✓ Loaded {len(test_data)} test positions from dataset")
    
    # Create 100-position test set
    selected_positions, common_count, critical_count = create_test_dataset(
        test_data, 
        num_positions=100,
        target_common=70,
        target_critical=29
    )
    
    # Save the test set
    output_path = project_root / "data" / "real_world_test_100_positions.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(selected_positions, f, indent=2)
    
    print(f"\n✓ Saved 100-position test set to: {output_path}")
    
    # Now run the detection rate test
    print(f"\n{'=' * 80}")
    print("RUNNING DETECTION RATE TEST")
    print(f"{'=' * 80}\n")
    
    # Import and run the test
    from test_detection_rate import test_detection_rate, print_results
    from backend.app.ml.data_preprocessing import ChessBoardEncoder
    from backend.app.ml.tactical_classifier_pytorch import HybridTacticalEnsemble
    
    # Load hybrid ensemble
    print("📦 Loading Hybrid Tactical Ensemble...")
    model_dir = project_root / "backend" / "models" / "saved_models"
    ensemble = HybridTacticalEnsemble(model_dir=model_dir)
    
    if not ensemble.is_available:
        print("❌ Error: Hybrid ensemble not available. Please ensure models are trained.")
        return
    
    print("✓ Hybrid ensemble loaded")
    
    # Initialize encoder
    encoder = ChessBoardEncoder()
    
    # Run test
    results = test_detection_rate(
        positions=selected_positions,
        ensemble=ensemble,
        encoder=encoder,
        max_positions=None  # Test all 100
    )
    
    # Print results
    print_results(results)
    
    # Save detailed results
    results_file = project_root / "scripts" / "real_world_detection_rate_results.json"
    with open(results_file, 'w') as f:
        # Convert any numpy types to native Python types for JSON serialization
        import numpy as np
        def convert(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        json.dump(results, f, indent=2, default=convert)
    
    print(f"\n✓ Detailed results saved to: {results_file}")
    
    # Generate thesis-style report
    print(f"\n{'=' * 80}")
    print("THESIS REPORT FORMAT (Section 5.5.3)")
    print(f"{'=' * 80}\n")
    
    stats = results['stats']
    metrics = results['metrics']
    
    print("Test Results:")
    print(f"Overall Detection Rate: {metrics['overall_detection_rate'] * 100:.1f}% " +
          f"(detected {stats['overall']['detected']} out of {stats['overall']['total']} ground-truth themes)")
    print()
    print("By Category:")
    print(f"  Common Themes ({stats['common']['total']} total):")
    print(f"    ├─ Detected: {stats['common']['detected']} ({metrics['common_detection_rate'] * 100:.1f}%)")
    print(f"    └─ False Positives: {stats['common']['false_positives']} " +
          f"({metrics['common_fp_rate'] * 100:.1f}% FP rate)")
    print()
    print(f"  Critical Themes ({stats['critical']['total']} total):")
    print(f"    ├─ Detected: {stats['critical']['detected']} ({metrics['critical_detection_rate'] * 100:.1f}%)")
    print(f"    └─ False Positives: {stats['critical']['false_positives']} " +
          f"({metrics['critical_fp_rate'] * 100:.1f}% FP rate)")
    
    # Compare with thesis claim
    claimed_rate = 47.5
    actual_rate = metrics['overall_detection_rate'] * 100
    difference = abs(actual_rate - claimed_rate)
    
    print(f"\n{'=' * 80}")
    print("VERIFICATION")
    print(f"{'=' * 80}\n")
    print(f"Claimed detection rate (Thesis 5.5.3): {claimed_rate:.1f}%")
    print(f"Actual detection rate (This test):     {actual_rate:.1f}%")
    print(f"Difference:                             {difference:.1f} percentage points")
    
    if difference < 5:
        print("\n✓ VERIFIED: Detection rate matches thesis claim (within 5 percentage points)")
    else:
        print(f"\n⚠️  WARNING: Detection rate differs by more than 5 percentage points")
        print("   This may be due to:")
        print("   - Different random sampling of positions")
        print("   - Model variations")
        print("   - Different test set composition")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"\n❌ Error: {str(e)}")
        print("\nFull traceback:")
        print(traceback.format_exc())
        
        error_file = project_root / "scripts" / "detection_rate_error.txt"
        with open(error_file, 'w') as f:
            f.write(f"Error: {str(e)}\n\n")
            f.write(traceback.format_exc())
        print(f"\nError details saved to: {error_file}")
