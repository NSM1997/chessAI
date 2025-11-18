"""
Create presplit train/val/test datasets from downloaded Lichess puzzles
Ensures no data leakage by splitting before any processing
"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.ml.data_preprocessing import ChessDataset

print("=" * 80)
print("CREATING PRESPLIT DATASETS (No Data Leakage)")
print("=" * 80)

# Load raw puzzles
raw_file = Path("backend/data/raw/lichess_puzzles.json")
print(f"\nLoading puzzles from: {raw_file}")

with open(raw_file, 'r') as f:
    all_puzzles = json.load(f)

print(f"Loaded {len(all_puzzles)} puzzles")

# Deduplicate by FEN
print("\nDeduplicating by FEN...")
seen_fens = set()
unique_puzzles = []

for puzzle in all_puzzles:
    fen = puzzle.get('fen', '')
    if fen and fen not in seen_fens:
        seen_fens.add(fen)
        unique_puzzles.append(puzzle)

print(f"Unique puzzles: {len(unique_puzzles)} (removed {len(all_puzzles) - len(unique_puzzles)} duplicates)")

# Split: 70% train, 15% val, 15% test
import random
random.seed(42)
random.shuffle(unique_puzzles)

n = len(unique_puzzles)
train_size = int(0.7 * n)
val_size = int(0.15 * n)

train_puzzles = unique_puzzles[:train_size]
val_puzzles = unique_puzzles[train_size:train_size + val_size]
test_puzzles = unique_puzzles[train_size + val_size:]

print(f"\nSplit sizes:")
print(f"  Train: {len(train_puzzles)}")
print(f"  Val:   {len(val_puzzles)}")
print(f"  Test:  {len(test_puzzles)}")

# Verify no overlap
train_fens = set(p['fen'] for p in train_puzzles)
val_fens = set(p['fen'] for p in val_puzzles)
test_fens = set(p['fen'] for p in test_puzzles)

overlap_train_val = train_fens & val_fens
overlap_train_test = train_fens & test_fens
overlap_val_test = val_fens & test_fens

if overlap_train_val or overlap_train_test or overlap_val_test:
    print("\n[ERROR] Data leakage detected!")
    print(f"  Train-Val overlap: {len(overlap_train_val)}")
    print(f"  Train-Test overlap: {len(overlap_train_test)}")
    print(f"  Val-Test overlap: {len(overlap_val_test)}")
    sys.exit(1)
else:
    print("\n[OK] No overlap detected - clean split!")

# Save splits
output_dir = Path("backend/data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

files = [
    (train_puzzles, output_dir / "train_puzzles.json"),
    (val_puzzles, output_dir / "val_puzzles.json"),
    (test_puzzles, output_dir / "test_puzzles.json")
]

for puzzles, filepath in files:
    with open(filepath, 'w') as f:
        json.dump(puzzles, f, indent=2)
    print(f"Saved: {filepath} ({len(puzzles)} puzzles)")

# Theme statistics
all_themes = set()
theme_counts = {}

for puzzle in unique_puzzles:
    themes = puzzle.get('themes', puzzle.get('Themes', '').split())
    for theme in themes:
        all_themes.add(theme)
        theme_counts[theme] = theme_counts.get(theme, 0) + 1

print(f"\n{'='*80}")
print(f"DATASET STATISTICS")
print(f"{'='*80}")
print(f"Total unique puzzles: {len(unique_puzzles)}")
print(f"Unique tactical themes: {len(all_themes)}")
print(f"\nTop 20 most common themes:")
sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:20]
for theme, count in sorted_themes:
    print(f"  {theme:<25} {count:>6} ({count/len(unique_puzzles)*100:.1f}%)")

print(f"\n{'='*80}")
print("PRESPLIT DATASETS CREATED SUCCESSFULLY!")
print("="*80)
print("\nYou can now train models using:")
print("  python scripts/retrain_for_recall.py")
print("="*80)

