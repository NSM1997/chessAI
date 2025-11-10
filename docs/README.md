# Documentation Index

Welcome to the Explainable Chess AI documentation! This directory contains comprehensive guides and architecture diagrams for the project.

## 📚 Documentation Structure

### 🏗️ Architecture Documentation

| Document | Description | Best For |
|----------|-------------|----------|
| **[ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)** | High-level overview with complete flow diagrams | Understanding the big picture |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Detailed component-by-component documentation | Deep technical understanding |
| **[FLOW_DIAGRAM.md](FLOW_DIAGRAM.md)** | Visual flow diagrams with timing and examples | Following request lifecycle |

### 📖 Main Documentation

| Document | Description |
|----------|-------------|
| **[../README.md](../README.md)** | Main project README with setup instructions |
| **[THESIS_REPORT_ENHANCED.md](THESIS_REPORT_ENHANCED.md)** | Academic thesis report |

---

## 🎯 Quick Navigation

### New to the Project?
Start here to understand what the system does:
1. Read [Main README](../README.md) - Features and quick start
2. View [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md) - See the complete system flow
3. Try [FLOW_DIAGRAM.md](FLOW_DIAGRAM.md) - Follow a real request through the system

### Want to Understand the Code?
Deep dive into implementation details:
1. Start with [ARCHITECTURE.md](ARCHITECTURE.md) - Component details
2. Refer to [FLOW_DIAGRAM.md](FLOW_DIAGRAM.md) - Data transformations
3. Check source code in `backend/` and `frontend/`

### Setting Up the System?
Follow the installation guide:
1. [Main README - Installation](../README.md#installation-steps) - Step-by-step setup
2. [Main README - Troubleshooting](../README.md#troubleshooting) - Common issues

### Contributing?
Understand the architecture first:
1. [ARCHITECTURE.md](ARCHITECTURE.md) - All components explained
2. [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md) - Technology stack
3. [Main README - Contributing](../README.md#contributing) - Guidelines

---

## 📊 Architecture Diagrams Summary

### Complete System Flow
**File**: [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)

Shows the entire system from browser to backend to external services:
- Frontend (Chrome Extension)
- Backend API (FastAPI)
- Chess Engine (Stockfish)
- ML Components (PyTorch CNN)
- LLM Service (Ollama/GPT-4)

```
Browser Extension → Backend API → Stockfish/ML/LLM → Response → UI
```

### Detailed Sequence Flow
**File**: [FLOW_DIAGRAM.md](FLOW_DIAGRAM.md)

Step-by-step flow from user action to displayed result:
1. User makes move on Chess.com
2. Content script extracts FEN
3. Backend analyzes in parallel
4. LLM generates explanation
5. UI displays result

### Component Details
**File**: [ARCHITECTURE.md](ARCHITECTURE.md)

Individual component architectures:
- Chess Engine Service (UCI protocol, Stockfish)
- Board Analyzer (attacks, threats, king safety)
- Tactical Analysis Service (CNN classification)
- LLM Explanation Service (Ollama/GPT-4/fallback)
- ML Pipeline (training and inference)

---

## 🔑 Key Concepts

### System Architecture Pattern
**Microservices with Orchestrator**

```
┌─────────────┐
│ Orchestrator│ (Backend API)
└──────┬──────┘
       │
   ┌───┴───┬────────┬─────────┐
   │       │        │         │
┌──▼───┐┌──▼──┐┌───▼───┐┌───▼───┐
│Engine││Board││Tactical││  LLM  │
└──────┘└─────┘└────────┘└───────┘
```

### Data Flow Pattern
**Pipeline with Parallel Processing**

```
Input → Parse → Parallel Analysis → Aggregate → Generate → Output
                (Stockfish + Board + ML)
```

### Frontend Pattern
**Content Script with Overlay**

```
Chess.com DOM → Monitor → Extract → API Call → Display
```

---

## 📁 Project Structure Reference

```
explainable-chess-ai/
├── backend/                        # Python backend
│   ├── app/
│   │   ├── main.py                # FastAPI entry point
│   │   ├── services/              # Core services
│   │   │   ├── chess_engine.py   # Stockfish integration
│   │   │   ├── board_analyzer.py # Position analysis
│   │   │   ├── tactical_analysis.py # ML tactics
│   │   │   └── llm_explanation.py # LLM generation
│   │   └── ml/                    # ML models
│   │       ├── tactical_classifier_pytorch.py
│   │       └── data_preprocessing.py
│   ├── models/                    # Trained models
│   │   └── saved_models/
│   │       └── tactical_classifier.pth
│   └── requirements.txt
│
├── frontend/                       # Chrome extension
│   ├── content-scripts/
│   │   ├── content-script.js     # Main content script
│   │   └── dom-extractors.js     # FEN extraction
│   ├── components/
│   │   └── ExplanationOverlay.js # UI overlay
│   ├── background/
│   │   └── background.js         # Background service
│   └── manifest.json
│
├── docs/                          # Documentation (you are here)
│   ├── README.md                  # This file
│   ├── ARCHITECTURE.md            # Detailed architecture
│   ├── ARCHITECTURE_OVERVIEW.md   # Architecture overview
│   ├── FLOW_DIAGRAM.md           # Visual flow diagrams
│   └── THESIS_REPORT_ENHANCED.md # Academic report
│
├── scripts/                       # Utility scripts
│   ├── train_tactical_classifier.py
│   └── test_llm_service.py
│
├── stockfish/                     # Stockfish binaries
├── models/                        # Additional models
└── README.md                      # Main README
```

---

## 🎨 Diagram Legend

### Colors in Mermaid Diagrams

| Color | Meaning |
|-------|---------|
| 🔵 Blue (`#e3f2fd`) | Frontend/User interface |
| 🟠 Orange (`#fff3e0`) | Backend/API |
| 🔴 Red (`#ffebee`) | External services (Stockfish) |
| 🟢 Green (`#e8f5e9`) | ML components |
| 🟣 Purple (`#f3e5f5`) | LLM services |
| 🟡 Yellow (`#fff9c4`) | Processing/Transformation |
| 🔷 Teal (`#e0f2f1`) | Output/Results |

### Diagram Types

- **Flowchart**: Shows process flow and decision points
- **Sequence**: Shows interaction between components over time
- **State Diagram**: Shows system states and transitions
- **Gantt**: Shows timing and parallel execution
- **Mindmap**: Shows hierarchical relationships
- **Graph**: Shows component relationships

---

## 🔍 Common Questions

### How does the extension detect the chess board?
See: [FLOW_DIAGRAM.md - DOM Extraction](FLOW_DIAGRAM.md#-complete-end-to-end-flow)

### What format is used for chess positions?
**FEN (Forsyth-Edwards Notation)**

Example: `rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1`

See: [ARCHITECTURE.md - Data Flow](ARCHITECTURE.md#data-transformations)

### How does the ML model work?
**CNN (Convolutional Neural Network)** with 12-channel input (6 piece types × 2 colors)

See: [ARCHITECTURE.md - ML Pipeline](ARCHITECTURE.md#7-ml-pipeline)

### Why use multiple LLM providers?
**Flexibility and fallback**
- Ollama: Free, local, private
- GPT-4: Fast, high quality
- Fallback: Always works, no dependencies

See: [ARCHITECTURE.md - LLM Service](ARCHITECTURE.md#6-llm-explanation-service)

### What makes the analysis accurate?
**Three-layer validation**:
1. Stockfish (world's strongest engine)
2. Board analysis (tactical rules)
3. ML classifier (pattern recognition)

See: [ARCHITECTURE_OVERVIEW.md - Component Responsibilities](ARCHITECTURE_OVERVIEW.md#component-responsibilities)

---

## 🚀 Performance Reference

| Operation | Time | Optimization |
|-----------|------|--------------|
| DOM extraction | <50ms | Efficient selectors |
| Stockfish (depth 20) | 500-1000ms | Parallel with other tasks |
| Board analysis | <100ms | Pure Python, fast |
| ML inference | 100-200ms | PyTorch on CPU |
| LLM (Ollama) | 5-10s | **Bottleneck** - use GPT-4 |
| LLM (GPT-4) | 1-2s | API call |
| LLM (Fallback) | <0.1s | Rule-based |
| **Total** | **2-12s** | Depends on LLM choice |

See: [FLOW_DIAGRAM.md - Timing Breakdown](FLOW_DIAGRAM.md#️-timing-breakdown)

---

## 🛠️ Technology Stack

### Backend
- Python 3.8+
- FastAPI (web framework)
- python-chess (chess logic)
- PyTorch (deep learning)
- Stockfish (chess engine)

### Frontend
- JavaScript ES6+
- Chrome Extension API
- Vanilla JS (no frameworks)

### AI/ML
- PyTorch (CNN training/inference)
- Ollama (local LLM)
- OpenAI API (GPT-4)

### Data
- Lichess puzzles (2M+ positions)
- JSON (data storage)
- FEN (chess positions)

See: [ARCHITECTURE_OVERVIEW.md - Technology Summary](ARCHITECTURE_OVERVIEW.md#technology-summary)

---

## 📞 Need Help?

1. **Setup Issues**: Check [Main README - Troubleshooting](../README.md#troubleshooting)
2. **Architecture Questions**: Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Flow Understanding**: See [FLOW_DIAGRAM.md](FLOW_DIAGRAM.md)
4. **Code Issues**: Check source files and comments

---

## 📝 Document Changelog

| Date | Update | File |
|------|--------|------|
| Nov 2025 | Initial architecture documentation | All files |
| Nov 2025 | Added flow diagrams | FLOW_DIAGRAM.md |
| Nov 2025 | Created documentation index | This file |

---

*Last updated: November 2025*

