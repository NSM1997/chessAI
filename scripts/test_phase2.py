"""
Phase 2 Testing Suite - Tactical Pattern Recognition
Tests all components of the CNN-based tactical classifier
"""

import sys
import os
from pathlib import Path
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

print("=" * 70)
print("🧪 PHASE 2 TESTING SUITE - Tactical Pattern Recognition")
print("=" * 70)


def test_1_imports():
    """Test 1: Check if all required modules can be imported"""
    print("\n📦 TEST 1: Checking imports...")
    
    errors = []
    
    try:
        import numpy as np
        print("  ✅ numpy")
    except ImportError as e:
        errors.append(f"numpy: {e}")
        print(f"  ❌ numpy: {e}")
    
    try:
        import chess
        print("  ✅ python-chess")
    except ImportError as e:
        errors.append(f"python-chess: {e}")
        print(f"  ❌ python-chess: {e}")
    
    try:
        import sklearn
        print("  ✅ scikit-learn")
    except ImportError as e:
        errors.append(f"scikit-learn: {e}")
        print(f"  ❌ scikit-learn: {e}")
    
    try:
        import torch
        print(f"  ✅ pytorch (version {torch.__version__})")
    except ImportError as e:
        errors.append(f"pytorch: {e}")
        print(f"  ❌ pytorch: {e}")
        print("     Install with: pip install torch")
    
    try:
        from backend.app.ml.data_preprocessing import ChessBoardEncoder
        print("  ✅ ChessBoardEncoder")
    except ImportError as e:
        errors.append(f"ChessBoardEncoder: {e}")
        print(f"  ❌ ChessBoardEncoder: {e}")
    
    try:
        from backend.app.ml.tactical_classifier_pytorch import TacticalCNN
        print("  ✅ TacticalCNN (PyTorch)")
    except ImportError as e:
        errors.append(f"TacticalCNN: {e}")
        print(f"  ❌ TacticalCNN: {e}")
    
    try:
        from backend.app.services.tactical_analysis import TacticalAnalysisService
        print("  ✅ TacticalAnalysisService")
    except ImportError as e:
        errors.append(f"TacticalAnalysisService: {e}")
        print(f"  ❌ TacticalAnalysisService: {e}")
    
    if errors:
        print(f"\n  ❌ {len(errors)} import errors found")
        return False
    else:
        print("\n  ✅ All imports successful!")
        return True


def test_2_board_encoding():
    """Test 2: Board encoding and decoding"""
    print("\n🔢 TEST 2: Board Encoding...")
    
    try:
        from backend.app.ml.data_preprocessing import ChessBoardEncoder
        import chess
        import numpy as np
        
        encoder = ChessBoardEncoder()
        
        # Test FEN encoding
        test_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        tensor = encoder.encode_fen(test_fen)
        
        print(f"  Encoded FEN to tensor: {tensor.shape}")
        print(f"  Expected shape: (8, 8, 12)")
        print(f"  Non-zero elements: {np.count_nonzero(tensor)}")
        
        # Test decoding
        decoded_board = encoder.decode_tensor(tensor)
        original_board = chess.Board(test_fen)
        
        # Compare piece positions (ignore turn, castling, etc.)
        match = True
        for square in chess.SQUARES:
            if original_board.piece_at(square) != decoded_board.piece_at(square):
                match = False
                break
        
        if match:
            print("  ✅ Encoding/Decoding successful!")
            print(f"\n  Original FEN:\n    {test_fen}")
            print(f"  Decoded board matches: {match}")
            return True
        else:
            print("  ❌ Encoding/Decoding mismatch")
            return False
            
    except Exception as e:
        print(f"  ❌ Error in board encoding: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_theme_encoding():
    """Test 3: Tactical theme encoding"""
    print("\n🎯 TEST 3: Theme Encoding...")
    
    try:
        from backend.app.ml.data_preprocessing import TacticalThemeEncoder
        import numpy as np
        
        encoder = TacticalThemeEncoder()
        
        print(f"  Number of themes: {encoder.num_classes}")
        print(f"  Sample themes: {', '.join(encoder.themes[:5])}...")
        
        # Test encoding
        test_themes = ['fork', 'pin', 'mate']
        encoded = encoder.encode_themes(test_themes)
        
        print(f"  Encoded themes shape: {encoded.shape}")
        print(f"  Expected: ({encoder.num_classes},)")
        print(f"  Active themes: {np.sum(encoded)}")
        
        # Test decoding
        decoded = encoder.decode_themes(encoded)
        
        print(f"  Decoded themes: {decoded}")
        print(f"  Original themes: {test_themes}")
        
        if set(decoded) == set(test_themes):
            print("  ✅ Theme encoding successful!")
            return True
        else:
            print("  ❌ Theme encoding mismatch")
            return False
            
    except Exception as e:
        print(f"  ❌ Error in theme encoding: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_data_loading():
    """Test 4: Dataset loading"""
    print("\n📂 TEST 4: Dataset Loading...")
    
    try:
        from backend.app.ml.data_preprocessing import ChessDataset
        
        # Check for dataset files
        possible_paths = [
            "backend/data/raw/lichess_puzzles.json",
            "backend/data/raw/lichess_puzzles_sample.json"
        ]
        
        dataset_path = None
        for path in possible_paths:
            if Path(path).exists():
                dataset_path = path
                break
        
        if dataset_path is None:
            print("  ⚠️  No dataset found. Run: python scripts/download_puzzle_dataset.py")
            print("  Generating sample dataset for testing...")
            
            # Generate minimal sample
            import json
            sample_data = [
                {
                    'puzzle_id': 'test_1',
                    'fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',
                    'moves': 'e7e5',
                    'rating': 1500,
                    'rating_deviation': 80,
                    'popularity': 90,
                    'nb_plays': 1000,
                    'themes': ['opening', 'short'],
                    'game_url': 'https://lichess.org/test'
                }
            ]
            
            test_path = Path("backend/data/raw/test_puzzles.json")
            test_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(test_path, 'w') as f:
                json.dump(sample_data, f)
            
            dataset_path = str(test_path)
            print(f"  Created test dataset: {dataset_path}")
        
        # Load dataset
        dataset = ChessDataset(dataset_path)
        
        print(f"  Loaded dataset: {len(dataset)} puzzles")
        print(f"  Dataset path: {dataset_path}")
        
        # Test getting an item
        if len(dataset) > 0:
            board_tensor, theme_label, metadata = dataset[0]
            print(f"  Sample item shape: board={board_tensor.shape}, themes={theme_label.shape}")
            print(f"  Sample metadata: {metadata['puzzle_id']}")
            print("  ✅ Dataset loading successful!")
            return True
        else:
            print("  ❌ Dataset is empty")
            return False
            
    except Exception as e:
        print(f"  ❌ Error loading dataset: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_model_architecture():
    """Test 5: CNN model architecture"""
    print("\n🏗️  TEST 5: CNN Model Architecture...")
    
    try:
        import torch
    except ImportError:
        print("  ⚠️  PyTorch not installed, skipping model test")
        print("  Install with: pip install torch")
        return False
    
    try:
        from backend.app.ml.tactical_classifier_pytorch import TacticalCNN
        
        # Build model
        model = TacticalCNN(num_classes=20)
        
        print(f"  Model input shape: (12, 8, 8)")
        print(f"  Model output shape: (20,)")
        print(f"  Total parameters: {model.count_parameters():,}")
        
        # Test forward pass
        import numpy as np
        test_input = torch.randn(1, 12, 8, 8)  # PyTorch uses (batch, channels, height, width)
        
        model.eval()
        with torch.no_grad():
            output = model(test_input)
        
        output_np = output.numpy()
        
        print(f"  Test output shape: {output.shape}")
        print(f"  Output range: [{output_np.min():.3f}, {output_np.max():.3f}]")
        
        if output.shape == (1, 20) and 0 <= output_np.min() <= output_np.max() <= 1:
            print("  ✅ Model architecture valid!")
            return True
        else:
            print("  ❌ Model output unexpected")
            return False
            
    except Exception as e:
        print(f"  ❌ Error in model architecture: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_6_tactical_service():
    """Test 6: Tactical Analysis Service"""
    print("\n🎮 TEST 6: Tactical Analysis Service...")
    
    try:
        from backend.app.services.tactical_analysis import TacticalAnalysisService
        import chess
        
        # Initialize service
        service = TacticalAnalysisService()
        
        print(f"  Service available: {service.is_available}")
        print(f"  Classifier loaded: {service.classifier is not None}")
        
        if not service.is_available:
            print("  ⚠️  Service not available (PyTorch not installed)")
            return False
        
        if service.classifier is None:
            print("  ⚠️  No trained model found")
            print("  This is expected - model needs to be trained first")
            print("  Run: python scripts/train_tactical_classifier.py")
            return True  # Not an error, just not trained yet
        
        # Test analysis on a simple position
        test_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        board = chess.Board(test_fen)
        
        analysis = await service.analyze_tactics(board, threshold=0.3)
        
        print(f"  Analysis available: {analysis['available']}")
        print(f"  Themes detected: {len(analysis.get('themes', []))}")
        
        if analysis['themes']:
            print("  Detected themes:")
            for theme in analysis['themes'][:3]:
                print(f"    - {theme['theme']}: {theme['confidence']:.2%}")
        
        print("  ✅ Tactical service functional!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error in tactical service: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_7_real_positions():
    """Test 7: Real chess positions"""
    print("\n♟️  TEST 7: Real Chess Positions...")
    
    try:
        from backend.app.ml.data_preprocessing import ChessBoardEncoder
        import chess
        import numpy as np
        
        encoder = ChessBoardEncoder()
        
        # Famous tactical positions
        test_cases = [
            {
                'name': 'Scholar\'s Mate Setup',
                'fen': 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4',
                'expected_pieces': 32
            },
            {
                'name': 'Back Rank Mate',
                'fen': '6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1',
                'expected_pieces': 9
            },
            {
                'name': 'Endgame',
                'fen': '8/5k2/8/5K2/5P2/8/8/8 w - - 0 1',
                'expected_pieces': 3
            }
        ]
        
        all_passed = True
        
        for test in test_cases:
            board = chess.Board(test['fen'])
            tensor = encoder.encode_board(board)
            
            # Count pieces in tensor
            pieces_in_tensor = np.count_nonzero(tensor)
            
            # Count actual pieces
            actual_pieces = len([s for s in chess.SQUARES if board.piece_at(s) is not None])
            
            print(f"\n  {test['name']}:")
            print(f"    FEN: {test['fen']}")
            print(f"    Pieces on board: {actual_pieces}")
            print(f"    Pieces in tensor: {pieces_in_tensor}")
            print(f"    Match: {pieces_in_tensor == actual_pieces}")
            
            if pieces_in_tensor != actual_pieces:
                all_passed = False
                print(f"    ❌ Mismatch!")
        
        if all_passed:
            print("\n  ✅ All positions encoded correctly!")
            return True
        else:
            print("\n  ❌ Some positions had encoding errors")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing positions: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all Phase 2 tests"""
    
    results = {}
    
    # Run tests
    results['imports'] = test_1_imports()
    results['board_encoding'] = test_2_board_encoding()
    results['theme_encoding'] = test_3_theme_encoding()
    results['data_loading'] = test_4_data_loading()
    results['model_architecture'] = test_5_model_architecture()
    results['tactical_service'] = await test_6_tactical_service()
    results['real_positions'] = test_7_real_positions()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\n{passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All Phase 2 components working correctly!")
        print("\n📋 Next Steps:")
        print("  1. Generate dataset: python scripts/download_puzzle_dataset.py --sample-only")
        print("  2. Train model: python scripts/train_tactical_classifier.py --epochs 10")
        print("  3. Test trained model: python scripts/test_phase2.py")
        print("  4. Integrate with server: Update simple_server.py")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        print("\n💡 Common fixes:")
        print("  - Install PyTorch: pip install torch")
        print("  - Install requirements: pip install -r backend/requirements.txt")
        print("  - Check Python version: python --version (need 3.8+, 3.12+ recommended)")
    
    print("=" * 70)


if __name__ == "__main__":
    # Run all tests
    asyncio.run(run_all_tests())

