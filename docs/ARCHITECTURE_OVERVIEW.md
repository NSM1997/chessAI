# Explainable Chess AI - Architecture Overview

## Complete System Flow

```mermaid
graph TB
    subgraph "🌐 Browser (Chess.com)"
        A[👤 User Playing Chess] --> B[Chess Board DOM]
        B --> C[Content Script<br/>ChessAIOverlay]
        C --> D[DOM Extractor]
        D --> E[FEN Position<br/>e.g., rnbqkbnr/pppppppp...]
        E --> F[Overlay UI<br/>Shows Analysis]
    end

    subgraph "🚀 FastAPI Backend (localhost:8001)"
        G[POST /analyze-position] --> H{Orchestrator}
        
        H --> I[📊 Chess Engine Service]
        H --> J[🔍 Board Analyzer]
        H --> K[🧠 Tactical ML Service]
        
        I --> L[Results Aggregator]
        J --> L
        K --> L
        
        L --> M[💬 LLM Explanation]
        M --> N[Response Builder]
    end

    subgraph "⚙️ Chess Engine Layer"
        I --> O[Stockfish UCI Protocol]
        O --> P[🏆 Stockfish Engine]
        P --> Q[Best Moves:<br/>e4, d4, Nf3]
        Q --> R[Evaluation:<br/>+0.35, mate in 5]
    end

    subgraph "🔍 Position Analysis"
        J --> S[Analyze Attacks<br/>White attacks: e4, d5]
        J --> T[Find Hanging Pieces<br/>Black knight on f6]
        J --> U[King Safety<br/>Not castled]
        J --> V[Piece Activity<br/>White: 20, Black: 18]
    end

    subgraph "🧠 Machine Learning"
        K --> W[Board Encoder<br/>12×8×8 Tensor]
        W --> X[PyTorch CNN<br/>Conv→ReLU→MaxPool]
        X --> Y[Tactical Classifier<br/>tactical_classifier.pth]
        Y --> Z[Themes:<br/>fork: 0.85<br/>pin: 0.72]
    end

    subgraph "💬 LLM Generation"
        M --> AA{Provider?}
        
        AA -->|Local| AB[🦙 Ollama<br/>llama3.2<br/>5-10s]
        AA -->|Cloud| AC[🤖 OpenAI<br/>GPT-4o<br/>1-2s]
        AA -->|Fallback| AD[📝 Rule-based<br/>Templates<br/><0.1s]
        
        AB --> AE[Natural Explanation]
        AC --> AE
        AD --> AE
    end

    subgraph "💾 Data & Models"
        AF[(Lichess Puzzles<br/>2M+ positions)]
        AG[(Trained Model<br/>tactical_classifier.pth)]
        AH[(Theme Metadata<br/>20+ tactical themes)]
    end

    subgraph "📤 Response"
        N --> AI[JSON Response:<br/>✓ Best moves<br/>✓ Explanation<br/>✓ Tactical themes<br/>✓ Evaluation<br/>✓ Learning insights]
    end

    %% Main Flow
    E -->|HTTP POST| G
    R --> L
    S --> L
    T --> L
    U --> L
    V --> L
    Z --> M
    AE --> N
    AI --> F
    F --> A

    %% Data Dependencies
    AF -.Training Data.-> Y
    AG -.Loaded Model.-> Y
    AH -.Theme Names.-> Z

    %% Styling
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style G fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style P fill:#ffebee,stroke:#c62828,stroke-width:2px
    style Y fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style AB fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style AC fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style AI fill:#e0f2f1,stroke:#00897b,stroke-width:3px
```

## Simplified Flow Diagram

```mermaid
sequenceDiagram
    participant 👤 User
    participant 🌐 Browser
    participant 🚀 Backend
    participant 🏆 Stockfish
    participant 🧠 ML Model
    participant 💬 LLM

    👤 User->>🌐 Browser: Makes move on Chess.com
    🌐 Browser->>🌐 Browser: Extract FEN from DOM
    🌐 Browser->>🚀 Backend: POST /analyze-position<br/>{fen, depth, skill_level}
    
    par Parallel Analysis (1-2 seconds)
        🚀 Backend->>🏆 Stockfish: Analyze position depth 20
        🏆 Stockfish-->>🚀 Backend: Best moves + evaluation
    and
        🚀 Backend->>🚀 Backend: Board analysis<br/>(attacks, threats, safety)
    and
        🚀 Backend->>🧠 ML Model: Classify tactical patterns
        🧠 ML Model-->>🚀 Backend: Themes (fork, pin, etc.)
    end
    
    🚀 Backend->>💬 LLM: Generate explanation<br/>(context + analysis)
    
    alt Using Ollama (5-10s)
        💬 LLM->>💬 LLM: Local llama3.2 inference
    else Using GPT-4 (1-2s)
        💬 LLM->>💬 LLM: OpenAI API call
    else Fallback (<0.1s)
        💬 LLM->>💬 LLM: Rule-based generation
    end
    
    💬 LLM-->>🚀 Backend: Natural language explanation
    🚀 Backend-->>🌐 Browser: JSON response with full analysis
    🌐 Browser->>🌐 Browser: Update overlay UI
    🌐 Browser->>👤 User: Display explanation + best moves
```

## Data Flow Example

### Input (from browser)
```json
{
  "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
  "depth": 20,
  "user_skill_level": "intermediate",
  "explanation_type": "comprehensive"
}
```

### Internal Processing

**Step 1: Stockfish Analysis**
```
Best move: d4 (evaluation: +0.45)
Alternative: O-O (evaluation: +0.32)
Alternative: d3 (evaluation: +0.28)
```

**Step 2: Board Analysis**
```
Attacks:
- White attacks: d5, e5, f7
- Black attacks: e4, d4
Hanging pieces: None
Threats: None
King safety: White not castled (score: 7/10)
Center control: White 5, Black 4
```

**Step 3: Tactical ML**
```
Detected themes:
- center_control: 0.89
- development: 0.76
- opening: 0.68
```

**Step 4: LLM Generation**
```
Prompt: "Explain why d4 is the best move in this opening position.
Move: d4 advances the pawn
Evaluation: +0.45
Themes: center_control, development"

Response: "d4 strengthens White's center control and opens lines 
for the dark-squared bishop. This move challenges Black's central 
pawn while maintaining development advantage."
```

### Output (to browser)
```json
{
  "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
  "best_moves": [
    {
      "move": "d2d4",
      "san": "d4",
      "score": {"type": "cp", "value": 45, "display": "+0.45"}
    }
  ],
  "explanations": [
    {
      "explanation": "d4 strengthens White's center control and opens lines for the dark-squared bishop. This move challenges Black's central pawn while maintaining development advantage.",
      "skill_level": "intermediate",
      "confidence": 0.95
    }
  ],
  "position_evaluation": {
    "type": "cp",
    "value": 45,
    "display": "+0.45"
  },
  "tactical_motifs": ["center_control", "development"],
  "strategic_concepts": ["opening", "center_control", "development"],
  "learning_insights": [
    "Position type: opening",
    "Current turn: White",
    "Key concept: Central control is paramount in the opening phase"
  ],
  "analysis_time": 6.42
}
```

## Component Responsibilities

| Component | Responsibility | Input | Output | Time |
|-----------|---------------|-------|--------|------|
| **Content Script** | Extract board position | DOM elements | FEN string | <50ms |
| **Chess Engine** | Calculate best moves | FEN, depth | Moves + eval | 500-1000ms |
| **Board Analyzer** | Analyze tactical features | Board object | Attacks, threats | <100ms |
| **Tactical ML** | Detect patterns | Board tensor | Theme probabilities | 100-200ms |
| **LLM Service** | Generate explanation | All analysis | Natural text | 1-10s |
| **Overlay UI** | Display results | JSON response | Visual overlay | <50ms |

## Technology Summary

```mermaid
mindmap
  root((Explainable<br/>Chess AI))
    Frontend
      Chrome Extension
        Manifest V3
        Content Scripts
        DOM Extraction
      JavaScript ES6+
      CSS3 Styling
    Backend
      FastAPI
        Async/Await
        REST API
        CORS Enabled
      Python 3.8+
      Uvicorn Server
    Chess Engine
      Stockfish 16+
      UCI Protocol
      Depth 20 Analysis
    Machine Learning
      PyTorch
        CNN Architecture
        Multi-label Classification
      NumPy
      Training Data
        Lichess Puzzles
        2M+ Positions
    AI Explanations
      Ollama
        llama3.2
        Local Inference
      OpenAI
        GPT-4o
        Cloud API
      Fallback
        Rule-based
        Templates
```

## Performance Profile

```mermaid
gantt
    title Analysis Timeline (Typical Request)
    dateFormat X
    axisFormat %L ms
    
    section Frontend
    Extract FEN           :0, 50
    Display Results       :6450, 50
    
    section Backend
    Parse Request         :50, 10
    Orchestrate Services  :60, 6390
    Build Response        :6440, 10
    
    section Chess Engine
    Stockfish Analysis    :60, 800
    
    section Board Analysis
    Tactical Analysis     :60, 100
    
    section ML Model
    CNN Inference         :60, 150
    
    section LLM
    Generate Explanation  :1000, 5000
```

**Bottleneck**: LLM generation (5-10s with Ollama, 1-2s with GPT-4)

**Optimization**: All non-LLM components run in parallel (~1s total)

## Deployment Model

```mermaid
graph LR
    A[💻 User's Computer] --> B[Chrome Browser]
    B --> C[Extension]
    
    A --> D[Backend Server]
    D --> E[Stockfish]
    D --> F[Ollama Service]
    
    D -.Optional.-> G[☁️ OpenAI API]
    
    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#fff3e0
    style D fill:#e8f5e9
    style E fill:#ffebee
    style F fill:#f3e5f5
    style G fill:#f3e5f5
```

**Note**: Everything runs locally except optional OpenAI API calls.

---

## Quick Reference

### Start System
```bash
# Terminal 1: Start Ollama (if using)
ollama serve

# Terminal 2: Start Backend
python simple_server.py

# Browser: Load extension
chrome://extensions/ → Load unpacked → frontend/
```

### Test Request
```bash
curl -X POST http://localhost:8001/analyze-position \
  -H "Content-Type: application/json" \
  -d '{"fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"}'
```

### Key Files
- **Frontend Entry**: `frontend/content-scripts/content-script.js`
- **Backend Entry**: `backend/app/main.py` or `simple_server.py`
- **Chess Engine**: `backend/app/services/chess_engine.py`
- **ML Model**: `backend/models/saved_models/tactical_classifier.pth`
- **LLM Service**: `backend/app/services/llm_explanation.py`

---

*For detailed component documentation, see [ARCHITECTURE.md](ARCHITECTURE.md)*

