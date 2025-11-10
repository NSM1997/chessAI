# Explainable Chess AI - Visual Flow Diagram

## 🎯 Complete End-to-End Flow

This diagram shows exactly what happens from the moment you make a move on Chess.com to when you see the AI explanation.

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#e3f2fd','primaryTextColor':'#000','primaryBorderColor':'#1976d2','lineColor':'#1976d2','secondaryColor':'#fff3e0','tertiaryColor':'#e8f5e9'}}}%%

flowchart TD
    Start([👤 User Makes Move on Chess.com]) --> Step1

    Step1[🌐 DOM Changes Detected<br/>Content script monitoring every 5s] --> Step2
    
    Step2[📊 Extract Board Position<br/>Parse pieces from DOM<br/>Convert to FEN string] --> Step3
    
    Step3{Position<br/>Changed?}
    Step3 -->|No| Wait[⏳ Keep Monitoring]
    Wait --> Step1
    Step3 -->|Yes| Step4
    
    Step4[📤 Send to Backend<br/>POST /analyze-position<br/>localhost:8001] --> Parallel
    
    Parallel{⚡ Parallel Processing}
    
    %% Branch 1: Stockfish
    Parallel --> Branch1[🏆 Stockfish Analysis]
    Branch1 --> B1_1[Parse FEN position]
    B1_1 --> B1_2[Set depth 20]
    B1_2 --> B1_3[Calculate best moves]
    B1_3 --> B1_4[Evaluate position<br/>+0.45, -1.23, mate in 5]
    B1_4 --> Merge
    
    %% Branch 2: Board Analysis
    Parallel --> Branch2[🔍 Board Analysis]
    Branch2 --> B2_1[Find all attacks<br/>White attacks e4, d5]
    B2_1 --> B2_2[Find hanging pieces<br/>Undefended pieces]
    B2_2 --> B2_3[Check king safety<br/>Castled? Under attack?]
    B2_3 --> B2_4[Calculate piece activity<br/>Mobility score]
    B2_4 --> Merge
    
    %% Branch 3: ML Tactics
    Parallel --> Branch3[🧠 ML Tactical Detection]
    Branch3 --> B3_1[Encode board to tensor<br/>12 × 8 × 8]
    B3_1 --> B3_2[Run CNN inference<br/>PyTorch model]
    B3_2 --> B3_3[Classify themes<br/>fork: 85%, pin: 72%]
    B3_3 --> Merge
    
    Merge[📦 Combine Results<br/>All analysis ready] --> LLM
    
    LLM[💬 Generate Explanation]
    LLM --> LLM_Check{Which<br/>Provider?}
    
    LLM_Check -->|Ollama| LLM1[🦙 llama3.2<br/>Local inference<br/>5-10 seconds]
    LLM_Check -->|OpenAI| LLM2[🤖 GPT-4o<br/>API call<br/>1-2 seconds]
    LLM_Check -->|Fallback| LLM3[📝 Rule-based<br/>Templates<br/>< 0.1 seconds]
    
    LLM1 --> Response
    LLM2 --> Response
    LLM3 --> Response
    
    Response[📋 Build JSON Response<br/>Best moves + Explanation<br/>Themes + Evaluation] --> Send
    
    Send[📥 Send to Browser<br/>HTTP Response] --> Display
    
    Display[🎨 Update Overlay UI<br/>Show on Chess.com] --> User
    
    User[👀 User Sees:<br/>✓ Best move: Nf3<br/>✓ Evaluation: +0.45<br/>✓ Explanation: Develops knight<br/>to central square...<br/>✓ Themes: fork, center control] --> End
    
    End([✨ Analysis Complete!])
    
    %% Styling
    style Start fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style Step4 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style Parallel fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style Branch1 fill:#ffebee,stroke:#c62828,stroke-width:2px
    style Branch2 fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style Branch3 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style LLM fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    style User fill:#e0f2f1,stroke:#00897b,stroke-width:3px
    style End fill:#c8e6c9,stroke:#388e3c,stroke-width:3px
```

## ⏱️ Timing Breakdown

```mermaid
gantt
    title Request Processing Timeline (6-7 seconds typical)
    dateFormat X
    axisFormat %Ls
    
    section Browser
    Detect board change       :milestone, 0, 0
    Extract FEN              :active, 0, 50
    Send HTTP request        :active, 50, 10
    Receive response         :milestone, 6500, 0
    Update UI                :active, 6500, 50
    
    section Backend Processing
    Parse request            :60, 20
    Start parallel tasks     :80, 10
    Wait for completion      :90, 6400
    Build response           :6490, 20
    
    section Stockfish (parallel)
    Initialize position      :crit, 90, 50
    Deep analysis (depth 20) :crit, 140, 750
    Parse results            :crit, 890, 20
    
    section Board Analysis (parallel)
    Analyze attacks          :done, 90, 40
    Find hanging pieces      :done, 130, 30
    King safety check        :done, 160, 20
    Piece activity           :done, 180, 30
    
    section ML Inference (parallel)
    Encode board tensor      :active, 90, 50
    CNN forward pass         :active, 140, 100
    Classify themes          :active, 240, 50
    
    section LLM Generation
    Build prompt             :90, 100
    Wait for parallel        :190, 810
    Generate explanation     :1000, 5000
    Parse response           :6000, 50
```

## 🔄 State Transitions

```mermaid
stateDiagram-v2
    [*] --> Idle: Extension loaded
    
    Idle --> Monitoring: User visits Chess.com
    
    Monitoring --> Analyzing: Board position changed
    Monitoring --> Monitoring: No change (check every 5s)
    
    Analyzing --> CallingAPI: FEN extracted
    
    CallingAPI --> Processing: Request sent
    
    Processing --> EngineAnalysis: Parallel start
    Processing --> BoardAnalysis: Parallel start
    Processing --> MLInference: Parallel start
    
    EngineAnalysis --> WaitingLLM: Stockfish done
    BoardAnalysis --> WaitingLLM: Analysis done
    MLInference --> WaitingLLM: ML done
    
    WaitingLLM --> GeneratingText: All ready
    
    GeneratingText --> Responding: Explanation ready
    
    Responding --> Displaying: JSON sent to browser
    
    Displaying --> Monitoring: UI updated, continue monitoring
    
    Monitoring --> [*]: User leaves Chess.com
    
    note right of Processing
        Parallel execution:
        - Stockfish: ~800ms
        - Board Analysis: ~100ms
        - ML Inference: ~200ms
        Total: ~1s (not 1.1s!)
    end note
    
    note right of GeneratingText
        Bottleneck:
        - Ollama: 5-10s
        - GPT-4: 1-2s
        - Fallback: <0.1s
    end note
```

## 📊 Component Interaction Matrix

| Component | Talks To | Receives From | Data Format | Latency |
|-----------|----------|---------------|-------------|---------|
| **Content Script** | Backend API | Backend API | HTTP JSON | 50ms |
| **Backend API** | All services | Content Script | FEN string, JSON | 20ms |
| **Stockfish** | Backend | Backend | UCI text protocol | 800ms |
| **Board Analyzer** | Backend | Backend | chess.Board object | 100ms |
| **ML Classifier** | Backend | Backend | NumPy tensor | 200ms |
| **LLM Service** | Ollama/OpenAI | Backend | Text prompts | 1-10s |
| **Overlay UI** | None | Content Script | JSON | 50ms |

## 🎯 Data Transformations

```mermaid
graph LR
    A[HTML DOM<br/>Chess.com board] -->|Extract| B[FEN String<br/>rnbqkbnr/...]
    
    B -->|Parse| C[chess.Board Object<br/>Python chess library]
    
    C -->|Encode| D[12×8×8 Tensor<br/>NumPy array]
    
    C -->|Stockfish| E[UCI Commands<br/>position fen ...<br/>go depth 20]
    
    E -->|Engine Output| F[Move List<br/>e2e4, d2d4<br/>with scores]
    
    C -->|Analyze| G[Analysis Dict<br/>attacks, threats,<br/>king safety]
    
    D -->|CNN| H[Theme Probabilities<br/>fork: 0.85<br/>pin: 0.72]
    
    F -->|Combine| I[Context Bundle]
    G -->|Combine| I
    H -->|Combine| I
    
    I -->|Format| J[LLM Prompt<br/>Explain why Nf3...]
    
    J -->|Generate| K[Natural Language<br/>Nf3 develops the<br/>knight to...]
    
    F -->|JSON| L[API Response]
    K -->|JSON| L
    H -->|JSON| L
    G -->|JSON| L
    
    L -->|Display| M[Overlay UI<br/>Visual display]
    
    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#e8f5e9
    style D fill:#f3e5f5
    style K fill:#fff9c4
    style M fill:#e0f2f1
```

## 🚦 Error Handling Flow

```mermaid
graph TB
    Request[Incoming Request] --> Validate{Valid FEN?}
    
    Validate -->|Yes| Process[Process Request]
    Validate -->|No| Error1[Return 400<br/>Invalid FEN]
    
    Process --> Stockfish{Stockfish<br/>Available?}
    Stockfish -->|No| Error2[Return 500<br/>Engine not initialized]
    Stockfish -->|Yes| Analyze[Analyze Position]
    
    Analyze --> CheckTimeout{Timeout?}
    CheckTimeout -->|Yes| Error3[Return 504<br/>Analysis timeout]
    CheckTimeout -->|No| MLCheck{ML Model<br/>Available?}
    
    MLCheck -->|No| Skip1[Skip tactical analysis<br/>Continue with engine only]
    MLCheck -->|Yes| MLAnalyze[Run ML inference]
    
    MLAnalyze --> LLMCheck{LLM<br/>Available?}
    Skip1 --> LLMCheck
    
    LLMCheck -->|Ollama down| Fallback1[Use GPT-4]
    LLMCheck -->|GPT-4 fails| Fallback2[Use rule-based]
    LLMCheck -->|All fail| Fallback3[Return basic explanation]
    LLMCheck -->|Success| Generate[Generate explanation]
    
    Fallback1 --> Generate
    Fallback2 --> Generate
    Fallback3 --> Success
    Generate --> Success[Return 200<br/>Full analysis]
    
    Error1 --> Log[Log Error]
    Error2 --> Log
    Error3 --> Log
    Log --> End[Return Error Response]
    
    Success --> End2[Return Success Response]
    
    style Error1 fill:#ffebee,stroke:#c62828
    style Error2 fill:#ffebee,stroke:#c62828
    style Error3 fill:#ffebee,stroke:#c62828
    style Success fill:#c8e6c9,stroke:#388e3c
    style Fallback1 fill:#fff9c4,stroke:#f9a825
    style Fallback2 fill:#fff9c4,stroke:#f9a825
    style Fallback3 fill:#fff9c4,stroke:#f9a825
```

## 💡 Key Insights

### Why is it fast despite many components?

**Parallel Processing**: Stockfish, Board Analysis, and ML all run simultaneously!

```
Sequential (bad):  800ms + 100ms + 200ms + 5000ms = 6100ms
Parallel (actual): max(800, 100, 200) + 5000 = 5800ms
```

### Where does the time go?

1. **LLM Generation**: 85% of time (5-10s with Ollama)
2. **Stockfish**: 14% of time (~800ms)
3. **Everything else**: 1% of time (~200ms)

### How to make it faster?

1. **Use GPT-4 instead of Ollama**: 6s → 2s (3x faster)
2. **Use fallback instead of LLM**: 6s → 1s (6x faster, but worse quality)
3. **Reduce Stockfish depth**: 20 → 15 (saves ~300ms)
4. **Use smaller Ollama model**: qwen2.5:1.5b (saves ~2s, but worse quality)

### What happens during waiting?

```mermaid
pie title Time Distribution (with Ollama)
    "LLM Generation" : 5000
    "Stockfish Analysis" : 800
    "ML Inference" : 200
    "Board Analysis" : 100
    "Network/Parsing" : 100
```

---

## 📱 Real Example Walkthrough

Let's trace a real request through the system:

### Step 1: User makes move
```
User plays: e4
Chess.com updates DOM
Content script detects change
```

### Step 2: Extract position
```javascript
// Frontend extracts FEN
fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
```

### Step 3: Send to backend
```bash
POST http://localhost:8001/analyze-position
{
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "depth": 20
}
```

### Step 4: Parallel analysis
```python
# Stockfish (800ms)
best_moves = ["e7e5", "c7c5", "e7e6"]
evaluation = {"value": -34, "display": "-0.34"}

# Board Analysis (100ms)
threats = []  # No immediate threats
hanging = []  # No hanging pieces
king_safety = {"white": 7, "black": 7}

# ML (200ms)
themes = [
    {"theme": "opening", "confidence": 0.89},
    {"theme": "center_control", "confidence": 0.76}
]
```

### Step 5: Generate explanation (5s)
```python
# Ollama prompt
prompt = """
Explain why e5 is the best move in this opening position.
Move: e5 advances the pawn
Evaluation: -0.34
"""

# Response
"e5 controls the center and equalizes the position. 
This move opens lines for the bishop and challenges 
White's central pawn."
```

### Step 6: Return to browser
```json
{
  "best_moves": [{"san": "e5", "score": {"display": "-0.34"}}],
  "explanation": "e5 controls the center...",
  "tactical_motifs": ["center_control", "opening"],
  "analysis_time": 6.2
}
```

### Step 7: Display to user
```
╔═══════════════════════╗
║ Chess AI Analysis     ║
╠═══════════════════════╣
║ Best Move: e5         ║
║ Score: -0.34          ║
║                       ║
║ e5 controls the       ║
║ center and equalizes  ║
║ the position.         ║
║                       ║
║ Themes:               ║
║ • center_control      ║
║ • opening             ║
╚═══════════════════════╝
```

---

*For more details, see [ARCHITECTURE.md](ARCHITECTURE.md) and [ARCHITECTURE_OVERVIEW.md](ARCHITECTURE_OVERVIEW.md)*

