"""
Download Lichess Tactical Puzzle Database for training
This script downloads a subset of Lichess puzzles with tactical themes
"""

import requests
import csv
import json
from pathlib import Path
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def download_lichess_puzzles(output_dir: str = "backend/data/raw", max_puzzles: int = 50000):
    """
    Download Lichess puzzle database
    
    Args:
        output_dir: Directory to save the dataset
        max_puzzles: Maximum number of puzzles to download (default: 50k for quick training)
    """
    
    print(f"📥 Downloading Lichess puzzle database...")
    print(f"Target: {max_puzzles} puzzles")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Lichess puzzle database URL (compressed CSV)
    # Full database: https://database.lichess.org/lichess_db_puzzle.csv.zst
    # We'll use a smaller, pre-processed version for faster setup
    
    puzzle_url = "https://database.lichess.org/lichess_db_puzzle.csv.bz2"
    
    print(f"Downloading from: {puzzle_url}")
    print("Note: This may take a few minutes...")
    
    try:
        # Download the file
        response = requests.get(puzzle_url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Save compressed file
        compressed_file = output_path / "lichess_puzzles.csv.bz2"
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0
        
        with open(compressed_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rDownloading: {percent:.1f}%", end='', flush=True)
        
        print("\n✅ Download complete!")
        
        # Decompress and process
        print("📦 Decompressing and processing...")
        import bz2
        
        processed_puzzles = []
        puzzle_count = 0
        
        with bz2.open(compressed_file, 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if puzzle_count >= max_puzzles:
                    break
                
                try:
                    # Extract relevant fields
                    puzzle = {
                        'puzzle_id': row['PuzzleId'],
                        'fen': row['FEN'],
                        'moves': row['Moves'],
                        'rating': int(row['Rating']),
                        'rating_deviation': int(row['RatingDeviation']),
                        'popularity': int(row['Popularity']),
                        'nb_plays': int(row['NbPlays']),
                        'themes': row['Themes'].split(),  # Split space-separated themes
                        'game_url': row['GameUrl']
                    }
                    
                    processed_puzzles.append(puzzle)
                    puzzle_count += 1
                    
                    if puzzle_count % 5000 == 0:
                        print(f"Processed {puzzle_count} puzzles...")
                
                except (KeyError, ValueError) as e:
                    continue  # Skip malformed rows
        
        # Save processed data as JSON
        output_file = output_path / "lichess_puzzles.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_puzzles, f, indent=2)
        
        print(f"\n✅ Saved {len(processed_puzzles)} puzzles to {output_file}")
        
        # Create theme statistics
        theme_counts = {}
        for puzzle in processed_puzzles:
            for theme in puzzle['themes']:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        # Save theme statistics
        stats_file = output_path / "theme_statistics.json"
        sorted_themes = dict(sorted(theme_counts.items(), key=lambda x: x[1], reverse=True))
        
        with open(stats_file, 'w') as f:
            json.dump(sorted_themes, f, indent=2)
        
        print(f"\n📊 Theme Statistics (Top 20):")
        for i, (theme, count) in enumerate(list(sorted_themes.items())[:20]):
            print(f"  {i+1}. {theme}: {count} puzzles")
        
        # Clean up compressed file
        compressed_file.unlink()
        
        return output_file, stats_file
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Download failed: {e}")
        print("\n💡 Alternative: Using sample dataset generator...")
        return generate_sample_dataset(output_path, max_puzzles=1000)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Generating sample dataset for testing...")
        return generate_sample_dataset(output_path, max_puzzles=1000)


def generate_sample_dataset(output_path: Path, max_puzzles: int = 1000):
    """
    Generate a small sample dataset for testing when download fails
    Uses common tactical patterns
    """
    
    print("🎲 Generating sample tactical positions...")
    
    sample_puzzles = [
        # Forks
        {
            'puzzle_id': 'sample_fork_1',
            'fen': 'r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4',
            'moves': 'd2d3 f8c5 f3g5',
            'rating': 1200,
            'rating_deviation': 80,
            'popularity': 95,
            'nb_plays': 5000,
            'themes': ['fork', 'opening', 'short'],
            'game_url': 'https://lichess.org/sample/1'
        },
        # Pins
        {
            'puzzle_id': 'sample_pin_1',
            'fen': 'r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 5',
            'moves': 'c1g5',
            'rating': 1300,
            'rating_deviation': 75,
            'popularity': 90,
            'nb_plays': 4500,
            'themes': ['pin', 'middlegame', 'short'],
            'game_url': 'https://lichess.org/sample/2'
        },
        # Back rank mate
        {
            'puzzle_id': 'sample_backrank_1',
            'fen': '6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1',
            'moves': 'e1e8',
            'rating': 1400,
            'rating_deviation': 70,
            'popularity': 98,
            'nb_plays': 6000,
            'themes': ['backRankMate', 'endgame', 'short', 'mate', 'mateIn1'],
            'game_url': 'https://lichess.org/sample/3'
        },
        # Discovered attack
        {
            'puzzle_id': 'sample_discovered_1',
            'fen': 'r1bqk2r/pppp1ppp/2n5/2b1p3/2BnP3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 0 5',
            'moves': 'd4f3',
            'rating': 1500,
            'rating_deviation': 85,
            'popularity': 88,
            'nb_plays': 3800,
            'themes': ['discoveredAttack', 'middlegame', 'short'],
            'game_url': 'https://lichess.org/sample/4'
        },
        # Skewer
        {
            'puzzle_id': 'sample_skewer_1',
            'fen': '4k3/8/8/3Q4/8/8/4r3/4K3 w - - 0 1',
            'moves': 'd5d8',
            'rating': 1350,
            'rating_deviation': 78,
            'popularity': 92,
            'nb_plays': 4200,
            'themes': ['skewer', 'endgame', 'short'],
            'game_url': 'https://lichess.org/sample/5'
        },
    ]
    
    # Replicate samples to reach desired count
    puzzles = []
    while len(puzzles) < max_puzzles:
        for sample in sample_puzzles:
            if len(puzzles) >= max_puzzles:
                break
            # Create variation with slight ID change
            puzzle = sample.copy()
            puzzle['puzzle_id'] = f"{sample['puzzle_id']}_{len(puzzles)}"
            puzzles.append(puzzle)
    
    # Save sample dataset
    output_file = output_path / "lichess_puzzles_sample.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(puzzles, f, indent=2)
    
    # Theme statistics
    theme_counts = {}
    for puzzle in puzzles:
        for theme in puzzle['themes']:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    stats_file = output_path / "theme_statistics.json"
    
    with open(stats_file, 'w') as f:
        json.dump(theme_counts, f, indent=2)
    
    print(f"✅ Generated {len(puzzles)} sample puzzles")
    print(f"📁 Saved to {output_file}")
    
    return output_file, stats_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Download Lichess puzzle database')
    parser.add_argument('--max-puzzles', type=int, default=50000,
                       help='Maximum number of puzzles to download (default: 50000)')
    parser.add_argument('--output-dir', type=str, default='backend/data/raw',
                       help='Output directory for dataset')
    parser.add_argument('--sample-only', action='store_true',
                       help='Generate sample dataset only (no download)')
    
    args = parser.parse_args()
    
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if args.sample_only:
        print("🎲 Sample mode: Generating test dataset...")
        puzzle_file, stats_file = generate_sample_dataset(output_path, max_puzzles=args.max_puzzles)
    else:
        puzzle_file, stats_file = download_lichess_puzzles(args.output_dir, args.max_puzzles)
    
    print(f"\n✅ Dataset ready!")
    print(f"📁 Puzzles: {puzzle_file}")
    print(f"📊 Statistics: {stats_file}")
    print(f"\n🚀 Next step: Run training script")

