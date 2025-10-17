# 🚀 Phase 2 Quick Start Guide
## Tactical Pattern Recognition with CNN

This guide will help you set up and test the Phase 2 ML enhancements.

---

## 📋 Prerequisites

### Required Python Packages

**✅ Python 3.12 Compatible!**

```bash
# Core ML packages (PyTorch - Python 3.12+ compatible)
pip install torch>=2.1.0
pip install scikit-learn>=1.3.0
pip install matplotlib>=3.8.0

# Or install all requirements
pip install -r backend/requirements.txt
```

### Check Installation

```bash
python -c "import torch; print(f'PyTorch {torch.__version__} installed')"
python -c "import sklearn; print('scikit-learn installed')"
python --version  # Should show Python 3.8+ (3.12+ works!)
```

---

## 🎯 Step-by-Step Setup

### Step 1: Test Phase 2 Components

Run the comprehensive test suite:

```bash
python scripts/test_phase2.py
```

**Expected Output:**
```
🧪 PHASE 2 TESTING SUITE - Tactical Pattern Recognition
📦 TEST 1: Checking imports...
  ✅ numpy
  ✅ python-chess
  ✅ scikit-learn
  ✅ pytorch (version X.X.X)
  ✅ ChessBoardEncoder
  ✅ TacticalCNN (PyTorch)
  ✅ TacticalAnalysisService
...
```

### Step 2: Generate Training Dataset

**Option A: Sample Dataset (Quick - 1 minute)**
```bash
python scripts/download_puzzle_dataset.py --sample-only --max-puzzles 1000
```

**Option B: Full Lichess Dataset (Slow - 10-30 minutes)**
```bash
python scripts/download_puzzle_dataset.py --max-puzzles 50000
```

**Expected Output:**
```
📥 Downloading Lichess puzzle database...
✅ Saved 1000 puzzles to backend/data/raw/lichess_puzzles_sample.json

📊 Theme Statistics (Top 20):
  1. mate: 150 puzzles
  2. fork: 120 puzzles
  3. pin: 95 puzzles
  ...
```

### Step 3: Train the CNN Model

**Quick Training (10 epochs, ~5-10 minutes on CPU)**
```bash
python scripts/train_tactical_classifier.py --epochs 10 --batch-size 32
```

**Full Training (50 epochs, ~30-60 minutes on CPU)**
```bash
python scripts/train_tactical_classifier.py --epochs 50 --batch-size 32
```

**Expected Output:**
```
🚀 TACTICAL PATTERN CLASSIFIER TRAINING
================================================================
📦 Initializing encoders...
Board encoding: (8, 8, 12)
Number of themes: 20

📥 Loading dataset...
Loaded 1000 puzzles

🏗️  Building CNN model...
Total parameters: 425,556

🎓 Training model...
Epoch 1/10
32/32 [======] - 5s - loss: 0.3245 - accuracy: 0.8521
...

✅ TRAINING COMPLETE!
Model saved to: backend/models/saved_models/tactical_classifier.h5
Test Accuracy: 0.8534
Test F1 Score: 0.7821
```

### Step 4: Test Trained Model

```bash
python scripts/train_tactical_classifier.py --test-only
```

**Expected Output:**
```
🧪 Testing Tactical Classifier...

========================================
Position: Fork position
FEN: r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4
Detected themes:
  - fork: 78%
  - opening: 65%
  - short: 54%
```

---

## 🧪 Testing Individual Components

### Test 1: Board Encoding

```bash
python -c "
from backend.app.ml.data_preprocessing import ChessBoardEncoder
import chess

encoder = ChessBoardEncoder()
fen = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'
tensor = encoder.encode_fen(fen)
print(f'Encoded shape: {tensor.shape}')
print(f'Non-zero elements: {(tensor != 0).sum()}')
"
```

### Test 2: Theme Encoding

```bash
python -c "
from backend.app.ml.data_preprocessing import TacticalThemeEncoder

encoder = TacticalThemeEncoder()
print(f'Themes: {encoder.themes[:5]}...')
encoded = encoder.encode_themes(['fork', 'pin'])
print(f'Encoded: {encoded[:10]}')
"
```

### Test 3: Model Architecture

```bash
python -c "
from backend.app.ml.tactical_classifier import TacticalCNN

model = TacticalCNN(num_classes=20)
model.build_model()
model.summary()
"
```

---

## 🔗 Integration with Chess Engine

### Test Tactical Analysis Service

Create a test file `test_integration.py`:

```python
import asyncio
import chess
from backend.app.services.tactical_analysis import TacticalAnalysisService

async def test():
    service = TacticalAnalysisService()
    
    # Test position (Scholar's Mate setup)
    fen = "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4"
    board = chess.Board(fen)
    
    # Analyze tactics
    analysis = await service.analyze_tactics(board, threshold=0.3)
    
    print(f"Available: {analysis['available']}")
    print(f"Themes: {analysis['themes']}")
    
    # Enhance explanation
    if analysis['themes']:
        base = "This is a strong attacking move."
        enhanced = service.enhance_explanation(base, analysis['themes'])
        print(f"\nBase: {base}")
        print(f"Enhanced: {enhanced}")

asyncio.run(test())
```

Run:
```bash
python test_integration.py
```

---

## 📊 Expected Results

### After Training

| Metric | Expected Value | Good Performance |
|--------|---------------|------------------|
| Accuracy | 70-85% | > 80% |
| Precision | 65-80% | > 75% |
| Recall | 60-75% | > 70% |
| F1 Score | 65-80% | > 75% |

### File Structure After Setup

```
backend/
├── data/
│   └── raw/
│       ├── lichess_puzzles.json (or lichess_puzzles_sample.json)
│       └── theme_statistics.json
├── models/
│   └── saved_models/
│       ├── tactical_classifier.pth  ← Trained PyTorch model
│       ├── theme_names.json
│       └── training_metrics.json
└── app/
    └── ml/
        ├── data_preprocessing.py
        ├── tactical_classifier_pytorch.py
        └── __init__.py
```

---

## 🐛 Troubleshooting

### Issue: PyTorch not found

**Error:**
```
ModuleNotFoundError: No module named 'torch'
```

**Fix:**
```bash
# Install PyTorch (works with Python 3.12+)
pip install torch

# Or CPU-only version (lighter and faster for training):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Issue: Out of Memory during training

**Error:**
```
ResourceExhaustedError: OOM when allocating tensor
```

**Fix:**
```bash
# Reduce batch size
python scripts/train_tactical_classifier.py --batch-size 16 --epochs 20

# Or use fewer puzzles
python scripts/download_puzzle_dataset.py --sample-only --max-puzzles 500
```

### Issue: Model training is slow

**Solution:**
- Use CPU-optimized PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- Reduce epochs: `--epochs 10`
- Reduce batch size: `--batch-size 16`
- Use sample dataset: `--sample-only`
- PyTorch is generally faster than TensorFlow on CPU!

### Issue: No dataset found

**Error:**
```
❌ Data file not found: backend/data/raw/lichess_puzzles.json
```

**Fix:**
```bash
python scripts/download_puzzle_dataset.py --sample-only
```

---

## ✅ Validation Checklist

- [ ] TensorFlow installed and working
- [ ] Test suite passes (at least 5/7 tests)
- [ ] Dataset downloaded (sample or full)
- [ ] Model trained successfully
- [ ] Model saved to `backend/models/saved_models/`
- [ ] Test predictions work on sample positions
- [ ] Tactical service initializes without errors

---

## 🎯 Next Steps

Once Phase 2 is working:

1. **Test with real game positions**
   - Use positions from your games
   - Test on famous tactical puzzles
   - Verify theme detection accuracy

2. **Improve the model**
   - Train on more data (50k+ puzzles)
   - Adjust learning rate
   - Try different architectures

3. **Integrate with server**
   - Add tactical analysis to `/analyze-position` endpoint
   - Update frontend to display detected tactics
   - Create visual indicators for tactical themes

4. **Prepare for Phase 3**
   - Install transformers: `pip install transformers`
   - Test NLP models
   - Create explanation templates

---

## 📚 Additional Resources

### Files Created in Phase 2

1. **`backend/app/ml/data_preprocessing.py`** - Board and theme encoding
2. **`backend/app/ml/tactical_classifier_pytorch.py`** - PyTorch CNN model (Python 3.12+ compatible)
3. **`backend/app/services/tactical_analysis.py`** - Integration service
4. **`scripts/download_puzzle_dataset.py`** - Dataset downloader
5. **`scripts/train_tactical_classifier.py`** - PyTorch training script
6. **`scripts/test_phase2.py`** - Comprehensive testing

### Quick Commands Reference

```bash
# Complete Phase 2 setup (one-time, Python 3.12+ compatible!)
pip install torch scikit-learn matplotlib
python scripts/download_puzzle_dataset.py --sample-only
python scripts/train_tactical_classifier.py --epochs 10

# Test everything
python scripts/test_phase2.py

# Re-train with better settings
python scripts/train_tactical_classifier.py --epochs 50 --batch-size 32

# Test specific component
python scripts/train_tactical_classifier.py --test-only
```

---

## 🎉 Success Indicators

You'll know Phase 2 is working when:

✅ Test suite shows 7/7 tests passing  
✅ Model achieves >75% accuracy  
✅ Tactical themes are detected on test positions  
✅ Service initializes without errors  
✅ Explanations are enhanced with tactical context  

**Ready for Phase 3!** 🚀

