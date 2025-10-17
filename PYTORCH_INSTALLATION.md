# 🚀 PyTorch Installation for Phase 2
## Python 3.12 Compatible Setup

Your system is now using **PyTorch** instead of TensorFlow, which is fully compatible with Python 3.12!

---

## ✅ What Changed

| Before (TensorFlow) | After (PyTorch) |
|---------------------|-----------------|
| ❌ Python 3.9-3.11 only | ✅ Python 3.8-3.12+ |
| `tensorflow>=2.15.0` | `torch>=2.1.0` |
| `.h5` model files | `.pth` model files |
| `tactical_classifier.py` | `tactical_classifier_pytorch.py` |

---

## 📦 Step 1: Install PyTorch

```bash
# Install PyTorch and dependencies
pip install torch>=2.1.0 scikit-learn>=1.3.0 matplotlib>=3.8.0

# Or install all requirements
pip install -r backend/requirements.txt
```

**Verify installation:**

```bash
python -c "import torch; print(f'✅ PyTorch {torch.__version__} installed successfully!')"
```

---

## 🧪 Step 2: Run Tests

```bash
# Test all Phase 2 components
python scripts/test_phase2.py
```

**Expected output:**
```
🧪 PHASE 2 TESTING SUITE - Tactical Pattern Recognition
======================================================================
📦 TEST 1: Checking imports...
  ✅ numpy
  ✅ python-chess
  ✅ scikit-learn
  ✅ pytorch (version 2.x.x)
  ✅ ChessBoardEncoder
  ✅ TacticalCNN (PyTorch)
  ✅ TacticalAnalysisService

🔢 TEST 2: Board Encoding...
  ✅ Encoding/Decoding successful!

... (more tests)

📊 TEST SUMMARY
✅ PASS  imports
✅ PASS  board_encoding
✅ PASS  theme_encoding
✅ PASS  data_loading
✅ PASS  model_architecture
✅ PASS  tactical_service
✅ PASS  real_positions

7/7 tests passed (100.0%)
🎉 All Phase 2 components working correctly!
```

---

## 📥 Step 3: Download Sample Dataset

```bash
# Download 1000 sample puzzles (~1-2 minutes)
python scripts/download_puzzle_dataset.py --sample-only --max-puzzles 1000
```

**Expected output:**
```
📥 Downloading Lichess puzzle database...
Processing: 100%|████████████████| 1000/1000
✅ Saved 1000 puzzles to backend/data/raw/lichess_puzzles_sample.json

📊 Theme Statistics (Top 20):
  1. mate: 150 puzzles
  2. fork: 120 puzzles
  3. pin: 95 puzzles
  ...
```

---

## 🎓 Step 4: Train the Model

**Quick training (10 epochs, ~5-10 minutes):**

```bash
python scripts/train_tactical_classifier.py --epochs 10 --batch-size 32
```

**Expected output:**
```
🚀 TACTICAL PATTERN CLASSIFIER TRAINING
================================================================
📦 Initializing encoders...
Board encoding: (8, 8, 12)
Number of themes: 20

📥 Loading dataset from backend/data/raw/lichess_puzzles_sample.json...
Loaded 1000 puzzles

📦 Creating PyTorch datasets...
Using device: cpu

🏗️  Building CNN model...
Total parameters: 425,556

🎓 Training model...
Epochs: 10
Batch size: 32
Learning rate: 0.001

Epoch 1/10 (2.3s) - train_loss: 0.3245, train_acc: 0.8521, val_loss: 0.2987, val_acc: 0.8654
Epoch 2/10 (2.1s) - train_loss: 0.2654, train_acc: 0.8789, val_loss: 0.2543, val_acc: 0.8876
...
Epoch 10/10 (2.0s) - train_loss: 0.1234, train_acc: 0.9245, val_loss: 0.1876, val_acc: 0.9012

📊 Evaluating on test set...

💾 Saving model...

================================================================
✅ TRAINING COMPLETE!
================================================================
Model saved to: backend\models\saved_models\tactical_classifier.pth
Test Accuracy: 0.8534
Test F1 Score: 0.7821
Test Precision: 0.7912
Test Recall: 0.7734
================================================================
```

---

## 🧪 Step 5: Test Trained Model

```bash
python scripts/train_tactical_classifier.py --test-only
```

**Expected output:**
```
🧪 Testing Tactical Classifier...

========================================
Position: Fork position
FEN: r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4
Detected themes:
  - fork: 78%
  - opening: 65%
  - short: 54%

========================================
Position: Back rank mate
FEN: 6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1
Detected themes:
  - mate: 92%
  - endgame: 68%
  - short: 61%
```

---

## ✅ Verification Checklist

- [ ] **PyTorch installed**: `python -c "import torch; print(torch.__version__)"`
- [ ] **Test suite passes**: `python scripts/test_phase2.py` (7/7 tests)
- [ ] **Dataset downloaded**: Check `backend/data/raw/lichess_puzzles_sample.json`
- [ ] **Model trained**: Check `backend/models/saved_models/tactical_classifier.pth`
- [ ] **Predictions work**: `python scripts/train_tactical_classifier.py --test-only`

---

## 🔧 Troubleshooting

### Issue: "No module named 'torch'"

**Fix:**
```bash
pip install torch
```

### Issue: Training is slow

**Solutions:**
- ✅ Use CPU-optimized PyTorch (already installed by default)
- ✅ Reduce epochs: `--epochs 5`
- ✅ Reduce batch size: `--batch-size 16`
- ✅ Use fewer puzzles: `--max-puzzles 500`

### Issue: Out of memory

**Fix:**
```bash
# Train with smaller batch size
python scripts/train_tactical_classifier.py --epochs 10 --batch-size 16
```

---

## 🎯 Quick Commands Summary

```bash
# 1. Install
pip install torch scikit-learn matplotlib

# 2. Test
python scripts/test_phase2.py

# 3. Download data
python scripts/download_puzzle_dataset.py --sample-only --max-puzzles 1000

# 4. Train
python scripts/train_tactical_classifier.py --epochs 10 --batch-size 32

# 5. Test model
python scripts/train_tactical_classifier.py --test-only
```

---

## 🎉 Success!

Once all steps complete successfully:

✅ Phase 2 is fully operational with PyTorch!  
✅ Python 3.12 compatible!  
✅ Tactical pattern recognition working!  
✅ Ready to integrate with the chess server!  

**Next step:** Test with real game positions in your chess browser extension! 🚀

