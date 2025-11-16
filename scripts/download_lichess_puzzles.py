"""
Download REAL puzzle data from Lichess database
"""
import json
import csv
import requests
from pathlib import Path
from typing import List, Dict
import io

def download_lichess_puzzles(max_puzzles: int = 10000) -> List[Dict]:
    """
    Download real puzzles from Lichess database
    Using the CSV database available at database.lichess.org
    """
    print("\n" + "="*80)
    print("DOWNLOADING REAL LICHESS PUZZLE DATABASE")
    print("="*80)
    
    # Lichess provides puzzle database in CSV format
    # URL: https://database.lichess.org/lichess_db_puzzle.csv.zst
    # But we can also use the uncompressed version or their API
    
    # Try API first (easier, no decompression needed)
    print("\n[METHOD 1] Trying Lichess API...")
    try:
        puzzles = download_via_api(max_puzzles)
        if puzzles:
            return puzzles
    except Exception as e:
        print(f"[INFO] API method failed: {e}")
    
    # Try downloading CSV sample
    print("\n[METHOD 2] Downloading from database export...")
    try:
        puzzles = download_csv_sample(max_puzzles)
        if puzzles:
            return puzzles
    except Exception as e:
        print(f"[INFO] CSV method failed: {e}")
    
    print("\n[ERROR] Could not download real data")
    print("[INFO] You may need to manually download from:")
    print("       https://database.lichess.org/")
    return []


def download_via_api(max_puzzles: int) -> List[Dict]:
    """
    Try to download puzzles using Lichess API or endpoints
    """
    # Lichess has a puzzle API but it's limited
    # We'll fetch puzzle data from their public endpoints
    
    base_url = "https://lichess.org/api/puzzle/daily"
    puzzles = []
    
    print("Fetching daily puzzle as sample...")
    response = requests.get(base_url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Successfully fetched puzzle data: {data.get('puzzle', {}).get('id', 'unknown')}")
        
        # Convert to our format
        puzzle_data = data.get('puzzle', {})
        game_data = data.get('game', {})
        
        puzzle = {
            'puzzleId': puzzle_data.get('id', ''),
            'fen': puzzle_data.get('initialPly', ''),
            'moves': puzzle_data.get('solution', []),
            'rating': puzzle_data.get('rating', 1500),
            'ratingDeviation': 100,
            'popularity': 90,
            'nbPlays': 1000,
            'themes': puzzle_data.get('themes', ['unknown']),
            'gameUrl': game_data.get('url', '')
        }
        
        print(f"[INFO] API only provides limited access")
        print(f"[INFO] Switching to bulk download method...")
        return []  # API not suitable for bulk download
    
    return []


def download_csv_sample(max_puzzles: int) -> List[Dict]:
    """
    Download puzzles from Lichess CSV database
    Note: The full database is large and zstd-compressed
    """
    print(f"\nDownloading {max_puzzles} puzzles from Lichess database...")
    print("Note: Full database is ~200MB compressed, ~500MB uncompressed")
    print("      This will take a few minutes...")
    
    # For now, we'll use a smaller dataset approach
    # Full URL: https://database.lichess.org/lichess_db_puzzle.csv.zst
    
    # Since the file is zstd compressed, we need the zstandard library
    try:
        import zstandard as zstd
        print("[OK] zstandard library available")
    except ImportError:
        print("[ERROR] zstandard library not installed")
        print("[FIX] Run: pip install zstandard")
        print("\n[ALTERNATIVE] Manually download and extract:")
        print("1. Download: https://database.lichess.org/lichess_db_puzzle.csv.zst")
        print("2. Extract using zstd or 7-zip")
        print("3. Place CSV in backend/data/raw/lichess_puzzles.csv")
        raise
    
    # Download the compressed file
    url = "https://database.lichess.org/lichess_db_puzzle.csv.zst"
    
    print(f"\n[DOWNLOADING] Fetching from {url}")
    print("This may take several minutes...")
    
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    
    # Get file size
    total_size = int(response.headers.get('content-length', 0))
    print(f"[SIZE] {total_size / (1024*1024):.1f} MB")
    
    # Download with progress
    compressed_data = bytearray()
    downloaded = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    for chunk in response.iter_content(chunk_size=chunk_size):
        if chunk:
            compressed_data.extend(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                print(f"\rDownloading: {percent:.1f}% ({downloaded/(1024*1024):.1f}MB)", end='', flush=True)
    
    print("\n[OK] Download complete!")
    
    # Decompress using streaming
    print("[DECOMPRESSING]...")
    dctx = zstd.ZstdDecompressor()
    try:
        # Try max_window_size parameter for large files
        decompressed_data = dctx.decompress(bytes(compressed_data), max_output_size=10*1024*1024*1024)  # 10GB max
    except:
        # Alternative: decompress with different settings
        dctx = zstd.ZstdDecompressor(max_window_size=2**31)
        decompressed_data = dctx.decompress(bytes(compressed_data))
    
    print("[PARSING] Reading CSV data...")
    csv_text = decompressed_data.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_text))
    
    # Parse puzzles
    puzzles = []
    for i, row in enumerate(csv_reader):
        if i >= max_puzzles:
            break
        
        # CSV format: PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl
        puzzle = {
            'puzzleId': row.get('PuzzleId', ''),
            'fen': row.get('FEN', ''),
            'moves': row.get('Moves', '').split(),
            'rating': int(row.get('Rating', 1500)),
            'ratingDeviation': int(row.get('RatingDeviation', 100)),
            'popularity': int(row.get('Popularity', 50)),
            'nbPlays': int(row.get('NbPlays', 0)),
            'themes': row.get('Themes', '').split(),
            'gameUrl': row.get('GameUrl', '')
        }
        puzzles.append(puzzle)
        
        if (i + 1) % 1000 == 0:
            print(f"\rParsed {i+1} puzzles...", end='', flush=True)
    
    print(f"\n[OK] Parsed {len(puzzles)} real Lichess puzzles!")
    return puzzles


def main():
    import sys
    
    max_puzzles = 10000
    if len(sys.argv) > 1:
        max_puzzles = int(sys.argv[1])
    
    # Download real data
    puzzles = download_lichess_puzzles(max_puzzles)
    
    if not puzzles:
        print("\n[FAILED] Could not download real puzzle data")
        print("\nMANUAL DOWNLOAD INSTRUCTIONS:")
        print("="*80)
        print("1. Install zstandard: pip install zstandard")
        print("2. Download: https://database.lichess.org/lichess_db_puzzle.csv.zst")
        print("3. Run this script again, or manually extract the CSV")
        print("="*80)
        return 1
    
    # Save to file
    output_file = Path(__file__).parent.parent / "backend" / "data" / "raw" / "lichess_puzzles.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(puzzles, f, indent=2)
    
    # Statistics
    unique_fens = len(set(p['fen'] for p in puzzles))
    all_themes = set()
    for p in puzzles:
        all_themes.update(p['themes'])
    
    print("\n" + "="*80)
    print("DOWNLOAD COMPLETE!")
    print("="*80)
    print(f"Total puzzles:    {len(puzzles)}")
    print(f"Unique positions: {unique_fens}")
    print(f"Unique themes:    {len(all_themes)}")
    print(f"Saved to:         {output_file}")
    print("="*80)
    
    return 0


if __name__ == "__main__":
    exit(main())

