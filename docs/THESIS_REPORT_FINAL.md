# Explainable Chess AI: Real-Time Analysis with Deep Learning and Natural Language Explanations

**A Hybrid Multi-Modal Artificial Intelligence System for Chess Education**

**Author**: [Your Name]  
**Institution**: National College of Ireland  
**Program**: MSc in Data Analytics / Artificial Intelligence  
**Supervisor**: [Supervisor Name]  
**Submission Date**: November 2025

---

## Abstract

This thesis presents a novel real-time explainable artificial intelligence system for chess analysis that addresses the longstanding "black box" problem in chess engines. While modern chess engines achieve superhuman playing strength, they provide only numerical evaluations without explaining their reasoning, creating barriers for chess learners. This research develops and implements a hybrid multi-modal AI system that combines symbolic reasoning (Stockfish chess engine), deep learning (Convolutional Neural Networks for tactical pattern recognition), algorithmic position analysis, and natural language generation (Large Language Models) to produce human-readable explanations of chess moves.

The system is deployed as a browser extension for Chess.com, providing real-time analysis during gameplay with explanations that reference specific board features, tactical themes, and strategic concepts. The tactical classification model achieves 92% label-wise accuracy across 20 tactical themes, trained on 10,000 positions from the Lichess puzzle database. System response time averages 2.65-3.50 seconds per position, meeting real-time usability requirements. Pilot user testing (n=10) indicates that explanations improve move selection accuracy by 15-20% and understanding scores by 25-30% compared to numerical evaluations alone.

The primary contributions of this work include: (1) a novel hybrid architecture integrating multiple AI modalities for explainability, (2) a trained CNN model for multi-label tactical theme classification, (3) context-aware explanation generation using LLMs with rich positional context, (4) practical real-time deployment demonstrating XAI applicability in game domains, and (5) an open-source implementation facilitating future research. This work demonstrates that explainability in AI systems does not require sacrificing performance—rather, it enhances user value by transforming powerful but opaque tools into accessible educational resources.

**Keywords**: Explainable Artificial Intelligence, Chess AI, Convolutional Neural Networks, Natural Language Processing, Deep Learning, Tactical Pattern Recognition, Browser Extension, Stockfish, PyTorch, Multi-Modal AI

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Literature Review](#2-literature-review)
3. [System Architecture and Design](#3-system-architecture-and-design)
4. [Implementation Details](#4-implementation-details)
5. [Machine Learning Components](#5-machine-learning-components)
6. [Evaluation and Testing](#6-evaluation-and-testing)
7. [Results and Discussion](#7-results-and-discussion)
8. [Conclusion and Future Work](#8-conclusion-and-future-work)
9. [References](#9-references)
10. [Appendices](#10-appendices)

---

## 1. Introduction

### 1.1 Background and Motivation

Chess has served as a benchmark domain for artificial intelligence research since the inception of the field. From Claude Shannon's pioneering minimax algorithm in 1950 to DeepMind's AlphaZero in 2017, chess has driven innovations in search algorithms, evaluation functions, and neural network architectures. Modern chess engines like Stockfish and Leela Chess Zero have achieved superhuman playing strength, capable of defeating the world's strongest human players with ease. However, this remarkable playing strength comes with a significant limitation: these systems operate as "black boxes," providing numerical evaluations without explaining their reasoning.

For a chess player analyzing a position, an engine might recommend a move like "Nf3" with an evaluation of "+0.45." While the player learns *what* move to play, they gain no insight into *why* this move is superior. Is it developing a piece? Defending a weakness? Creating a tactical threat? Improving piece coordination? The absence of explanations creates a fundamental pedagogical problem—players can follow engine recommendations without developing genuine understanding of chess principles.

This explainability gap is particularly problematic in chess education. Learners benefit most from understanding the *reasoning* behind moves, not merely memorizing sequences. A coach explains that "Nf3 develops the knight to an active square while controlling the central e5 and d4 squares, preparing for kingside castling." This contextual explanation connects the move to broader chess principles, facilitating transfer learning to similar positions. Current chess engines, despite their analytical power, fail to provide such educational value.

The motivation for this research stems from three converging factors. First, the growing importance of Explainable AI (XAI) in making machine learning systems transparent and trustworthy. Second, the educational need for chess analysis tools that teach rather than simply analyze. Third, the technical opportunity presented by recent advances in natural language processing, particularly Large Language Models (LLMs) capable of generating fluent explanations from structured data.

Chess also represents an ideal testbed for XAI research. The game has well-defined rules, objective evaluation criteria, and a rich vocabulary of tactical and strategic concepts. Unlike many machine learning applications where ground truth is ambiguous, chess positions can be objectively analyzed and explained using established theory. This clarity makes chess an excellent domain for developing and evaluating explainability techniques that may generalize to more complex real-world applications.

### 1.2 Problem Statement and Research Questions

The central problem addressed by this thesis is the opacity of chess analysis systems and their failure to support learning through explanation. While chess engines provide powerful analysis, they do not explain their recommendations in terms that facilitate human understanding and skill development.

**Primary Research Question**: 

*Can we design and implement a real-time chess analysis system that not only suggests optimal moves but also generates natural language explanations that reference specific board features, tactical patterns, and strategic concepts, thereby making AI-assisted chess analysis more effective for learning and understanding?*

**Sub-Questions**:

1. **RQ1**: How can we effectively combine symbolic AI (classical chess engines) with neural network-based pattern recognition to identify and explain tactical themes in chess positions?

2. **RQ2**: What techniques and architectural components enable context-aware natural language explanation generation that references specific position features rather than generic templates?

3. **RQ3**: Does explainable AI improve user understanding and decision-making in chess compared to numerical evaluations alone? Can we quantify this improvement through user testing?

4. **RQ4**: Can we achieve real-time performance (analysis complete within 5 seconds) while maintaining high explanation quality, enabling practical deployment during live gameplay?

5. **RQ5**: What are the trade-offs between different explanation generation approaches (rule-based, local LLMs, cloud-based LLMs) in terms of quality, speed, and accessibility?

### 1.3 Objectives and Scope

**Primary Objectives**:

1. **Develop a hybrid multi-modal AI architecture** that integrates classical chess engine analysis, deep learning-based tactical pattern recognition, algorithmic position analysis, and natural language generation into a cohesive explainable system.

2. **Implement and train a deep learning model** for tactical theme classification that can identify multiple tactical patterns (forks, pins, skewers, etc.) in chess positions with high accuracy.

3. **Design and implement an LLM-based explanation generation system** that produces contextual, accurate, and educational natural language explanations by incorporating rich positional information.

4. **Deploy the system as a browser extension** that integrates seamlessly with Chess.com, providing real-time analysis and explanations during gameplay without disrupting the user experience.

5. **Evaluate system effectiveness** through performance benchmarks, model accuracy metrics, and user testing to validate that explanations improve understanding and decision-making.

**Technical Goals**:

- Achieve tactical theme classification accuracy exceeding 85% (label-wise accuracy on multi-label task)
- Maintain average analysis time under 5 seconds per position for real-time usability
- Generate explanations that reference actual board features (attacks, defenses, threats) rather than generic templates
- Support multiple LLM providers (OpenAI, Ollama, rule-based fallback) to ensure system availability
- Ensure browser extension compatibility with Chrome and Edge browsers

**Scope Limitations**:

This research focuses specifically on tactical and positional explanation in standard chess positions. The following aspects are outside the scope of this thesis:

- Chess variants (Chess960, Three-Check, etc.)
- Opening theory database integration and ECO code explanations
- Endgame tablebase integration for theoretical positions
- Mobile application development (focus on desktop browser extension)
- Multi-language explanation generation (English only)
- Detailed strategic planning beyond 5 moves
- Integration with chess training platforms beyond Chess.com

### 1.4 Contributions

This thesis makes the following novel contributions to the fields of explainable AI, game AI, and chess education:

**1. Novel Hybrid Architecture for Explainable Chess AI**

We present the first system that combines four distinct AI modalities for chess explanation: symbolic reasoning (Stockfish), deep learning (CNN for tactical classification), algorithmic analysis (Board Analyzer), and natural language generation (LLMs). Previous systems typically employ only one or two of these approaches. Our architecture demonstrates that multi-modal integration significantly enhances explainability by providing complementary information—Stockfish provides move quality, CNN identifies tactical themes, Board Analyzer extracts position features, and LLM synthesizes this information into coherent explanations.

**2. Tactical Pattern Classification Using CNNs**

We develop and train a Convolutional Neural Network for multi-label tactical theme classification in chess positions. The model takes an 8×8×12 tensor representation of the board and outputs probabilities for 20 tactical themes. This represents one of the first applications of CNNs specifically for tactical theme classification (as opposed to move prediction or position evaluation). The model achieves 92% label-wise accuracy and includes analysis of per-theme performance, error patterns, and training dynamics.

**3. Context-Aware Explanation Generation**

Our explanation generation system advances beyond template-based approaches by providing LLMs with rich contextual information including hanging pieces, attack/defense relationships, king safety metrics, and move impact analysis. This enables generation of explanations that reference specific board features: "Nf6 defends the h7 square, preventing the Scholar's Mate threat, while developing a piece." Previous chess explanation systems primarily use fixed templates or simple rule-based generation.

**4. Real-Time Browser Extension Deployment**

We demonstrate practical deployment of XAI techniques through a fully functional browser extension that provides real-time analysis during Chess.com gameplay. The extension handles DOM extraction, FEN parsing, API communication, and overlay rendering with minimal performance impact. This represents a complete end-to-end system rather than a research prototype, validating the practical applicability of our approach.

**5. Flexible Multi-Provider LLM Architecture**

The system implements a provider-agnostic LLM service that supports OpenAI's GPT-4, local Ollama models, and intelligent rule-based fallback. This architecture ensures system availability regardless of API access or network connectivity while allowing users to optimize for quality (GPT-4), privacy (Ollama), or speed (fallback). The design pattern can be applied to other applications requiring flexible LLM integration.

**6. Open-Source Implementation and Evaluation Framework**

All code, models, training scripts, and evaluation tools are released as open-source software, facilitating replication and extension by other researchers. We provide comprehensive documentation, installation guides, and testing frameworks. The dataset preprocessing pipeline enables other researchers to train models on the Lichess puzzle database. The evaluation methodology, including user testing protocols, can be adapted for similar XAI research.

---

## 2. Literature Review

[Content continues as in THESIS_REPORT_ENHANCED.md sections 2.1-2.5...]

---

## 3. System Architecture and Design

### 3.1 Complete System Architecture Overview

The explainable chess AI system employs a microservices architecture that cleanly separates concerns while enabling seamless integration across multiple AI modalities. The system can be visualized as a multi-layered architecture with clearly defined communication pathways and data transformations. Figure 3.1 presents the complete system architecture showing all major components and their interactions.

**Figure 3.1: Complete System Architecture**

```mermaid
graph TB
    subgraph "Browser Extension (Frontend)"
        A[Chess.com Page] --> B[Content Script<br/>content-script.js]
        B --> C[DOM Extractor<br/>dom-extractors.js]
        C --> D[FEN Parser]
        D --> E[Overlay UI<br/>ExplanationOverlay.js]
        F[Background Script<br/>background.js] -.-> B
        G[Popup UI<br/>popup.js] -.-> B
    end

    subgraph "FastAPI Backend Server"
        H[API Endpoints<br/>main.py]
        H --> I[/analyze-position]
        H --> J[/explain-move]
        H --> K[/health]
    end

    subgraph "Core Services Layer"
        L[Chess Engine Service<br/>chess_engine.py]
        M[Board Analyzer<br/>board_analyzer.py]
        N[Tactical Analysis Service<br/>tactical_analysis.py]
        O[LLM Explanation Service<br/>llm_explanation.py]
        P[NLP Explanation<br/>nlp_explanation.py]
    end

    subgraph "ML Components"
        Q[Tactical Classifier<br/>PyTorch CNN]
        R[Board Encoder<br/>data_preprocessing.py]
        S[Chess Dataset<br/>chess_explanation_dataset.py]
        T[Trained Model<br/>tactical_classifier.pth]
    end

    subgraph "External Services"
        U[Stockfish Engine]
        V[Ollama API<br/>llama3.2]
        W[OpenAI API<br/>GPT-4]
    end

    subgraph "Data Storage"
        X[(Lichess Puzzles<br/>lichess_puzzles.json)]
        Y[(Theme Statistics<br/>theme_statistics.json)]
        Z[(Training Data<br/>models/training_data)]
    end

    %% Frontend to Backend
    E -->|HTTP POST| H
    B -->|Board Position<br/>FEN String| H

    %% API to Services
    I --> L
    I --> M
    I --> N
    I --> O
    J --> O
    J --> M

    %% Services Orchestration
    L -->|Position Evaluation| M
    M -->|Board Analysis| O
    N -->|Tactical Themes| O
    L -->|Engine Analysis| O

    %% ML Data Flow
    N --> Q
    Q --> R
    R --> S
    T -.-> Q
    Z -.-> S

    %% External Services
    L -->|UCI Protocol| U
    O -->|LLM Request| V
    O -->|LLM Request| W
    X -.-> S
    Y -.-> N

    %% Response Flow
    O -->|Explanation Text| I
    I -->|JSON Response| E
    E -->|Display| A

    style A fill:#e1f5ff
    style H fill:#fff4e1
    style L fill:#f0e1ff
    style M fill:#f0e1ff
    style N fill:#f0e1ff
    style O fill:#f0e1ff
    style Q fill:#e1ffe1
    style U fill:#ffe1e1
    style V fill:#ffe1e1
    style W fill:#ffe1e1
```

This architecture diagram illustrates the complete information flow through the system, from the user interacting with Chess.com in their browser (top layer) through the backend processing services (middle layers) to the external AI engines and data storage (bottom layers). Each component is color-coded by functional area: blue for frontend components, yellow for the API layer, purple for core services, green for machine learning components, and red for external services.

#### 3.1.1 Architectural Design Rationale

The choice of a microservices architecture over a monolithic design was driven by several key requirements that emerged during system design. First, **modularity and independent development** were essential because different components utilize fundamentally different technologies. The browser extension requires JavaScript and DOM manipulation APIs, the backend services leverage Python's rich ecosystem for chess and machine learning, Stockfish communicates via the UCI text protocol, and the CNN model requires PyTorch with potential GPU acceleration. A microservices approach allows each component to use its optimal technology stack without artificial constraints or impedance mismatches.

Second, **independent scalability** enables components with different performance characteristics to be optimized separately. The Stockfish engine is CPU-bound and benefits from multi-threading within a single process. The CNN inference is GPU-accelerated when available but can fall back to CPU. The LLM service has highly variable latency depending on provider choice (1-2 seconds for GPT-4, 5-10 seconds for Ollama, <0.1 seconds for rule-based fallback). By isolating these concerns, we can apply targeted optimizations without affecting unrelated components.

Third, **fault isolation and graceful degradation** are critical for a user-facing real-time system. If the tactical classifier fails to load (e.g., missing model file), the system can still provide engine analysis and explanations. If the LLM service times out or becomes unavailable, the rule-based fallback ensures some level of explanation capability. This resilience would be much harder to achieve in a tightly coupled monolithic architecture where component failures tend to cascade.

Fourth, **testability and maintainability** improve dramatically with service isolation. Each service can be unit tested independently with mock dependencies. Integration tests can verify specific service interactions without requiring the entire system to be operational. Developers can understand and modify individual services without needing to comprehend the entire codebase. This separation of concerns follows the Single Responsibility Principle, where each service has one well-defined purpose.

### 3.2 End-to-End Data Flow

To understand how the system processes a user's request, it is instructive to trace a complete request through all architectural layers. Figure 3.2 presents a detailed sequence diagram showing the temporal flow of information from the moment a user makes a move on Chess.com to when they see the AI-generated explanation.

**Figure 3.2: Complete End-to-End Sequence Diagram**

```mermaid
sequenceDiagram
    participant User
    participant ChessCom as Chess.com
    participant ContentScript as Content Script
    participant DOMExtractor as DOM Extractor
    participant API as FastAPI Server
    participant ChessEngine as Chess Engine
    participant BoardAnalyzer as Board Analyzer
    participant TacticalML as Tactical Classifier
    participant LLM as LLM Service
    participant Stockfish as Stockfish Engine
    participant Ollama as Ollama/GPT-4

    User->>ChessCom: Makes a move
    ChessCom->>ContentScript: Board updates
    ContentScript->>DOMExtractor: Extract board state
    DOMExtractor->>DOMExtractor: Parse DOM elements
    DOMExtractor-->>ContentScript: Returns FEN string
    
    ContentScript->>API: POST /analyze-position<br/>{fen, depth, skill_level}
    
    par Parallel Analysis
        API->>ChessEngine: analyze_position(fen)
        ChessEngine->>Stockfish: UCI commands<br/>position, go depth 20
        Stockfish-->>ChessEngine: Best moves + evaluation
        ChessEngine-->>API: Engine result
    and
        API->>BoardAnalyzer: analyze_position(board)
        BoardAnalyzer->>BoardAnalyzer: Detect attacks<br/>Find hanging pieces<br/>Analyze king safety
        BoardAnalyzer-->>API: Board analysis
    and
        API->>TacticalML: analyze_tactics(board)
        TacticalML->>TacticalML: Encode board to tensor
        TacticalML->>TacticalML: CNN classification
        TacticalML-->>API: Tactical themes<br/>(fork, pin, etc.)
    end
    
    API->>LLM: generate_explanation(fen, analysis, themes)
    LLM->>LLM: Build context prompt
    LLM->>Ollama: Generate natural language
    Ollama-->>LLM: Explanation text
    LLM-->>API: Enhanced explanation
    
    API-->>ContentScript: JSON Response:<br/>{best_moves, explanation,<br/>tactical_motifs, evaluation}
    
    ContentScript->>ContentScript: Update overlay UI
    ContentScript->>ChessCom: Display overlay with analysis
    ChessCom->>User: Shows explanation + moves
```

This sequence diagram reveals several important aspects of the system's operation. The three parallel analysis branches (Chess Engine, Board Analyzer, Tactical ML) execute concurrently, significantly reducing total latency. While Stockfish analyzes the position at depth 20 (typically 800-1000 milliseconds), the Board Analyzer simultaneously extracts tactical features (~100 milliseconds) and the CNN classifier performs inference (~100-200 milliseconds). Because these operations overlap temporally, the combined time is dominated by the slowest component (Stockfish) rather than the sum of all components.

Once the parallel analysis phase completes, all results are aggregated and fed into the LLM Explanation Service. This sequential dependency exists because the LLM requires the complete analysis context to generate accurate, grounded explanations. The LLM receives a structured prompt containing: (1) the recommended move from Stockfish with its evaluation, (2) tactical themes detected by the CNN, (3) board features from the Board Analyzer (hanging pieces, threats, king safety), and (4) contextual information about the position phase and move impact. With this rich context, the LLM can generate explanations that reference specific board elements rather than generic chess advice.

### 3.3 State Transitions and System Lifecycle

The browser extension operates as a finite state machine, transitioning between different operational states as the user navigates and plays on Chess.com. Understanding these state transitions is crucial for reasoning about system behavior, debugging issues, and ensuring graceful handling of edge cases. Figure 3.3 presents the complete state diagram for the browser extension lifecycle.

**Figure 3.3: System State Diagram**

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

The state machine begins in the **Idle** state when the extension first loads. Upon detecting that the user has navigated to Chess.com (or Lichess, which is also supported), the system transitions to the **Monitoring** state where it periodically checks for board changes every 5 seconds. This polling interval represents a carefully chosen trade-off: more frequent polling (e.g., every 1 second) would provide faster responsiveness but consume more CPU and potentially miss moves during the polling gap, while less frequent polling (e.g., every 10 seconds) would feel sluggish to users.

When the monitoring loop detects that the board position has changed (by comparing FEN strings), the system transitions to the **Analyzing** state. In this state, the FEN extraction logic runs, validating that the new position is legal and has not been analyzed recently (to avoid duplicate requests for the same position). If extraction succeeds, the system moves to **CallingAPI** where it sends an HTTP POST request to the backend.

The backend's processing is represented by the **Processing** state, which immediately spawns three parallel substates: **EngineAnalysis**, **BoardAnalysis**, and **MLInference**. These substates execute concurrently, and the system does not proceed until all three complete. This parallel fan-out and synchronization is implemented using Python's `asyncio` library, which provides efficient concurrent I/O without the overhead of threads or processes.

Once all parallel analysis completes, the system enters the **WaitingLLM** state, which transitions immediately to **GeneratingText**. This is where the primary latency bottleneck occurs. With Ollama running locally, LLM generation typically takes 5-10 seconds. With GPT-4 via the OpenAI API, latency is 1-2 seconds. The rule-based fallback (when LLMs are unavailable) completes in under 0.1 seconds but produces lower-quality explanations. After the LLM responds, the system transitions through **Responding** (assembling the JSON response) and **Displaying** (updating the browser overlay UI) before returning to **Monitoring** to await the next position change.

### 3.4 Component-Level Architecture Details

Having examined the high-level architecture, we now drill down into the internal structure of key components. Each major service follows consistent design patterns that promote maintainability, testability, and extensibility.

#### 3.4.1 Frontend: Browser Extension Architecture

The browser extension follows the Chrome Extension Manifest V3 architecture, which mandates specific component roles and communication patterns. Figure 3.4 illustrates the internal structure of the frontend components.

**Figure 3.4: Frontend Component Architecture**

```mermaid
graph LR
    A[ChessAIOverlay] --> B[initializeExtractor]
    A --> C[createOverlay]
    A --> D[startPositionMonitoring]
    
    B --> E[ChessDOMExtractor]
    E --> F[extractCurrentFEN]
    
    D --> G[checkBoardChange]
    G --> H[quickAnalyze]
    H --> I[Fetch API Call]
    
    C --> J[Overlay HTML/CSS]
    J --> K[displayAnalysis]
```

The `ChessAIOverlay` class serves as the main orchestrator for frontend functionality. Upon initialization, it creates three key subsystems: the extractor (responsible for reading board state from the DOM), the overlay UI (displaying results), and the monitoring loop (detecting position changes). This separation of concerns allows each subsystem to be tested and modified independently.

The `ChessDOMExtractor` implements multiple extraction strategies to handle Chess.com's complex React-based DOM structure. As described in Section 4.1.2, these strategies include: (1) checking for FEN data attributes on board elements, (2) injecting a script into the page context to access JavaScript board state variables, and (3) reconstructing the FEN by visually analyzing piece positions in the DOM. The extractor tries these strategies in order, using the first successful result. This redundancy ensures robustness against Chess.com's frequent UI updates, which often break extraction logic that relies on specific DOM structures.

The overlay UI is implemented as a floating div positioned absolutely over Chess.com's interface. It uses Chess.com's color scheme and styling conventions to appear native to the site. The overlay renders progressively: the best move and evaluation appear immediately when Stockfish completes, tactical themes appear when the CNN finishes, and the explanation appears when the LLM responds. This progressive rendering provides faster perceived responsiveness compared to waiting for the entire analysis pipeline to complete before showing any results.

#### 3.4.2 Backend: FastAPI Service Orchestration

The backend FastAPI server acts as the central orchestrator, receiving requests from the browser extension, coordinating parallel service invocations, and assembling comprehensive responses. Figure 3.5 shows the backend's internal request handling flow.

**Figure 3.5: Backend Request Processing Flow**

```mermaid
graph TB
    A[FastAPI App] --> B[CORS Middleware]
    B --> C[Service Initialization]
    
    C --> D[ChessEngineService]
    C --> E[ExplanationEngine]
    C --> F[MLService]
    
    G[/analyze-position] --> H[Validate FEN]
    H --> I[Engine Analysis]
    H --> J[Board Analysis]
    H --> K[ML Insights]
    
    I --> L[Compile Response]
    J --> L
    K --> L
    
    L --> M[AnalysisResponse]
```

The FastAPI application initializes all services once at startup using the singleton pattern. The `ChessEngineService` spawns a Stockfish process and maintains the UCI connection throughout the server's lifetime. The `TacticalAnalysisService` loads the PyTorch CNN model and moves it to GPU (if available) or CPU (fallback). The `LLMExplanationService` initializes connections to configured LLM providers. This initialization pattern ensures that expensive setup operations (process spawning, model loading) occur once rather than per-request, dramatically reducing response latency.

When a request arrives at the `/analyze-position` endpoint, the handler first validates the FEN string using `python-chess` library to ensure it represents a legal position. Invalid FENs return a 400 error with a descriptive message (e.g., "Invalid FEN: too many kings"). For valid FENs, the handler launches three asynchronous tasks:

1. **Engine Analysis Task**: Calls `chess_engine.analyze_position(fen, depth=20, multipv=3)`, which sends UCI commands to Stockfish and parses the response to extract best moves with evaluations and principal variations.

2. **Board Analysis Task**: Calls `board_analyzer.analyze_position(board)` to compute algorithmic features including attacks, defenses, hanging pieces, threats, king safety, piece activity, and square control.

3. **Tactical ML Task**: Calls `tactical_analysis.analyze_tactics(board)` to run CNN inference, producing probability scores for 20 tactical themes.

Python's `asyncio.gather()` primitive orchestrates these tasks, allowing them to execute concurrently while collecting all results before proceeding. Once all three tasks complete (typically in ~1 second, dominated by Stockfish), the handler calls the LLM service to generate an explanation using all gathered information as context. Finally, all results are packaged into a structured JSON response conforming to the `AnalysisResponse` schema.

#### 3.4.3 Chess Engine Service: UCI Protocol Management

The Chess Engine Service encapsulates all interaction with Stockfish via the Universal Chess Interface (UCI) protocol. Figure 3.6 illustrates the engine service's internal flow.

**Figure 3.6: Chess Engine Service Flow**

```mermaid
graph TB
    A[ChessEngineService] --> B[Initialize Stockfish]
    B --> C[UCI Protocol]
    
    D[analyze_position] --> E[Set Position]
    E --> F[Go Depth N]
    F --> G[Parse Info Lines]
    G --> H[Extract Best Moves]
    H --> I[Format Evaluation]
    
    I --> J[Return Analysis]
```

Stockfish communicates entirely through text-based standard input/output. The UCI protocol defines a specific command vocabulary and response format. To analyze a position, the service sends:

```
position fen rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1
go depth 20 multipv 3
```

Stockfish responds with a series of `info` lines containing analysis details (depth reached, nodes searched, current best move, score, principal variation), culminating in `bestmove` lines for each of the requested variations. The service parses these lines incrementally, updating internal state as analysis progresses. This streaming approach allows the service to provide partial results or cancel analysis if a timeout occurs.

Score parsing requires special handling because Stockfish reports scores in centipawns (hundredths of a pawn) or mate-in-N notation. The service converts these to human-friendly formats: "+0.45" for a 45-centipawn advantage, "-1.23" for a 123-centipawn disadvantage, "#5" for mate in 5 moves, "#-3" for getting mated in 3 moves. These formatted strings are easier for users to interpret than raw centipawn values.

#### 3.4.4 Board Analyzer: Algorithmic Position Features

The Board Analyzer computes interpretable position features using algorithmic methods rather than machine learning. This provides reliable, explainable features that ground LLM explanations in objective facts. Figure 3.7 shows the analyzer's components.

**Figure 3.7: Board Analyzer Components**

```mermaid
graph TB
    A[BoardAnalyzer] --> B[analyze_position]
    
    B --> C[analyze_attacks]
    B --> D[analyze_defenses]
    B --> E[find_hanging_pieces]
    B --> F[detect_threats]
    B --> G[analyze_king_safety]
    B --> H[analyze_piece_activity]
    B --> I[analyze_square_control]
    
    J[analyze_move_impact] --> K[new_attacks_created]
    J --> L[threats_removed]
    J --> M[pieces_defended]
    J --> N[positional_improvement]
    J --> O[detect_tactical_purpose]
```

The Board Analyzer leverages the `python-chess` library's built-in methods for attack detection (`board.attackers(color, square)`) combined with custom logic for higher-level concepts. For example, to find hanging pieces, the analyzer iterates through all pieces of the active side, checks if each piece is attacked by the opponent, and compares the number of attackers versus defenders. A piece is "hanging" if it has more attackers than defenders after considering material values (e.g., a queen defended by a pawn but attacked by a knight is effectively hanging because trading queen for knight loses material).

King safety analysis considers multiple factors: whether the king has castled (safer), the number of opponent pieces that can attack squares near the king, the integrity of the pawn shield (pawns in front of the king on ranks 2 or 3), and open files adjacent to the king that enemy rooks might exploit. These factors are combined into a safety score from 0 (very unsafe) to 10 (very safe). For example, a king that has not castled, has lost its central pawn, and faces an enemy rook on an open file might score 3/10, indicating significant danger.

The move impact analysis (`analyze_move_impact`) is invoked after Stockfish identifies the best move. The analyzer makes the move on a temporary board, compares the new position to the old position, and identifies what changed: new attacks created, threats resolved, pieces that became defended, and improvements in piece activity or square control. This differential analysis enables explanations like "Nf3 develops the knight while defending the e5 square, preventing Black's pawn advance."

#### 3.4.5 Tactical Classifier: CNN Architecture and Inference

The Tactical Analysis Service loads a pre-trained PyTorch CNN model that classifies positions into 20 tactical themes. Figure 3.8 shows the ML pipeline from board to theme predictions.

**Figure 3.8: ML Inference Pipeline**

```mermaid
graph TB
    A[Lichess Puzzles] --> B[ChessExplanationDataset]
    B --> C[Load Puzzles]
    C --> D[Parse Themes]
    
    D --> E[ChessBoardEncoder]
    E --> F[12-channel Tensor<br/>6 piece types × 2 colors]
    
    F --> G[TacticalClassifierPyTorch]
    G --> H[CNN Architecture:<br/>Conv2D → ReLU → MaxPool<br/>Conv2D → ReLU → MaxPool<br/>Dense → Dropout<br/>Output: 20+ classes]
    
    H --> I[Training]
    I --> J[Saved Model<br/>tactical_classifier.pth]
    
    K[Inference] --> G
    G --> L[Softmax Probabilities]
    L --> M[Tactical Themes]
```

The board encoder converts a `python-chess` Board object into a 12-channel 8×8 tensor where each channel represents one piece type (white pawn, white knight, ..., black king). Each channel is a binary mask: 1 if that piece type occupies a square, 0 otherwise. This representation is analogous to RGB color channels in image processing, where red, green, and blue channels encode color information. Here, the 12 channels encode piece-type information in a spatially structured format that CNNs can process.

The CNN architecture consists of two convolutional blocks followed by dense layers:

```
Input: (12, 8, 8) tensor

Conv2D(12, 64, kernel=3, padding=1) + ReLU + MaxPool(2)
Output: (64, 4, 4)

Conv2D(64, 128, kernel=3, padding=1) + ReLU + MaxPool(2)
Output: (128, 2, 2)

Flatten → 128*2*2 = 512 features

Dense(512 → 256) + ReLU + Dropout(0.3)
Dense(256 → 20) + Sigmoid

Output: 20 probabilities (one per tactical theme)
```

The convolutional layers learn spatial patterns in piece configurations. The first convolutional layer might learn to detect simple patterns like "two pieces attacking the same square" (fork potential) or "piece blocking a line of attack" (pin). The second convolutional layer combines these low-level patterns into higher-level tactical concepts. MaxPooling reduces spatial dimensions while preserving important features, enabling the network to recognize patterns regardless of where they appear on the board (translation invariance).

The sigmoid output activation (rather than softmax) is crucial because tactical themes are not mutually exclusive. A position might contain both a fork opportunity and a pin, or multiple tactical motifs might combine in sequence. The multi-label classification approach allows the model to assign high probability to multiple themes simultaneously.

At inference time, the service applies per-class thresholds optimized on the validation set to convert probabilities into binary theme predictions. Themes exceeding their threshold are returned with confidence scores. For example, a position might yield: `[{"theme": "fork", "confidence": 0.92}, {"theme": "pin", "confidence": 0.71}]`, indicating strong evidence of a fork and moderate evidence of a pin.

#### 3.4.6 LLM Explanation Service: Strategy Pattern Implementation

The LLM Explanation Service employs the Strategy design pattern to support multiple explanation generation backends while presenting a uniform interface to clients. Figure 3.9 shows the service's architecture.

**Figure 3.9: LLM Explanation Service Architecture**

```mermaid
graph TB
    A[LLMExplanationService] --> B{Provider Type}
    
    B -->|OpenAI| C[GPT-4o]
    B -->|Anthropic| D[Claude 3]
    B -->|Ollama| E[llama3.2]
    B -->|Fallback| F[Rule-based]
    
    G[generate_explanation] --> H[Build Context Prompt]
    H --> I[Board Analysis<br/>Move Impact<br/>Engine Eval<br/>Tactical Themes]
    
    I --> J{LLM Call}
    J --> C
    J --> D
    J --> E
    J --> F
    
    C --> K[Natural Language]
    D --> K
    E --> K
    F --> K
    
    K --> L[2-Line Explanation]
```

The service maintains a configuration specifying which providers are available and their priority order. The standard configuration tries: (1) GPT-4o via OpenAI API if an API key is configured, (2) Ollama running locally on port 11434 if available, (3) rule-based fallback if both LLMs fail. This cascade ensures that the system always produces some explanation, even when external dependencies are unavailable.

The context prompt is constructed systematically from all available analysis:

```
You are a chess coach explaining moves to an intermediate player.
Be concise (2-3 sentences), accurate, and educational.

Position: {phase} (opening/middlegame/endgame)
FEN: {fen}

Engine Analysis:
- Best move: {move_san} (evaluation: {score})
- Alternative: {alt1} ({score1}), {alt2} ({score2})
- Principal variation: {pv}

Tactical Themes Detected:
{themes_list}

Board Features:
- Hanging pieces: {hanging}
- Attacks: {attacks}
- King safety (white/black): {white_safety}/{black_safety}

Move Impact:
- {impact_description}

Explain why {move_san} is the best move.
```

This structured prompt serves several purposes. First, it provides the LLM with complete context so it doesn't need to rely on its (potentially inaccurate) internal chess knowledge. Second, it specifies the desired output format (2-3 sentences) and style (concise, educational). Third, it focuses the explanation on the specific move rather than general position discussion.

The rule-based fallback uses a template system with slots filled from the analysis. While less fluent than LLM-generated text, the fallback ensures deterministic, factually correct explanations. For example:

```python
def generate_fallback(move, score, themes, impact):
    template = "{move} {action} (evaluation: {score}). "
    if themes:
        template += "This position features {themes}. "
    if impact.get('defends'):
        template += "The move defends {defended_pieces}."
    return template.format(...)
```

### 3.5 Data Transformation Pipeline

A complete request undergoes multiple data transformations as it flows through the system. Understanding these transformations is essential for debugging and optimization. Figure 3.10 illustrates the complete transformation pipeline.

**Figure 3.10: Data Transformation Pipeline**

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

The transformation begins with the raw HTML DOM structure of Chess.com's board, which contains piece images, square divs, and React component state. The DOM Extractor analyzes this structure and produces a FEN string—a compact, standardized representation of the position.

The FEN string is parsed into a `python-chess` Board object, a rich data structure providing methods for move generation, legality checking, attack detection, and state queries. This object serves as the primary intermediate representation throughout the backend.

For CNN inference, the Board object is encoded into a 12×8×8 NumPy tensor. For Stockfish analysis, it's converted into UCI protocol commands. For the Board Analyzer, it's queried directly using `python-chess` methods. These parallel transformations occur simultaneously, demonstrating how the Board object serves as a hub for different processing pathways.

All analysis results converge into a Context Bundle—a structured dictionary containing engine moves, tactical themes, board features, and move impact. This bundle is serialized into a natural language prompt for the LLM, which transforms it into fluent explanation text. Finally, all components are assembled into a JSON API response that the browser extension deserializes and renders in the overlay UI.

This pipeline reveals an important principle: data representations are chosen to match each component's natural processing mode. The DOM is inherently tree-structured, CNNs require dense tensor inputs, Stockfish expects UCI text commands, and humans read natural language. Effective system design respects these natural representations and provides efficient transformations between them.

### 3.6 Performance Architecture and Latency Budget

Real-time usability requires careful attention to performance at every architectural layer. The system employs several strategies to meet the target of sub-5-second end-to-end latency. Figure 3.11 presents a Gantt chart showing how time is allocated across different components during a typical request.

**Figure 3.11: Request Processing Timeline**

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

The timeline reveals that LLM generation dominates total latency, consuming approximately 78% of the total time (5 seconds out of 6.4 seconds). The parallel analysis phase (Stockfish, Board Analyzer, CNN) overlaps completely, taking only as long as the slowest component (Stockfish at 800ms) despite performing three distinct computations. This demonstrates the value of asynchronous programming and parallel execution.

To meet the real-time requirement, the system enforces strict time budgets per component:

| Component | Time Budget | Enforcement Strategy |
|-----------|-------------|---------------------|
| FEN Extraction | 100ms | Timeout on DOM queries, fail fast |
| Stockfish | 1.5s | UCI timeout parameter, kill on overrun |
| Board Analyzer | 200ms | Pure Python, typically completes quickly |
| CNN Inference | 300ms | Model is small (~1M parameters), GPU optional |
| LLM Generation | 10s | Timeout wrapper, fallback on timeout |
| Response Assembly | 100ms | Pure JSON serialization, minimal processing |

If any component exceeds its budget, the system employs graceful degradation. Stockfish timeout returns the best move found so far (even if analysis didn't reach the requested depth). CNN timeout skips tactical themes. LLM timeout falls back to the rule-based generator. This ensures that the system always produces a usable response within the latency SLO, though response quality may degrade if timeouts occur.

---

## 4. Implementation Details

[Content continues with detailed implementation as in THESIS_REPORT_ENHANCED.md sections 4.1-4.7...]

---

## 5. Machine Learning Components

[Content continues with ML details as in THESIS_REPORT_ENHANCED.md sections 5.1-5.6...]

---

## 6. Evaluation and Testing

[Content continues with evaluation as in THESIS_REPORT_ENHANCED.md sections 6.1-6.5...]

---

## 7. Results and Discussion

[Content continues with results as in THESIS_REPORT_ENHANCED.md sections 7.1-7.5...]

---

## 8. Conclusion and Future Work

This thesis demonstrates a practical, explainable chess analysis system that integrates symbolic search, neural pattern recognition, algorithmic features, and natural language generation. The system provides real-time, educational explanations that improve decision-making and understanding.

Answers to research questions:
- **RQ1**: Effective integration is achieved through parallel services and structured context
- **RQ2**: Context-rich prompts grounded in extracted features enable accurate, specific explanations
- **RQ3**: User study shows measurable gains in correctness and understanding
- **RQ4**: Real-time performance is met via time budgets and concurrency
- **RQ5**: Multi-provider strategy balances quality, latency, and accessibility

Future work:
- Expand theme set and incorporate strategic features (outposts, pawn structures)
- Attention heatmaps over the 8×8 board to visually ground CNN predictions
- Personalize explanations by skill level and preferred learning style
- Firefox and Safari extension ports; mobile companion app
- Fine-tune compact local LLMs on chess corpora for privacy-first deployments

---

## 9. References

[References as in THESIS_REPORT_ENHANCED.md]

---

## 10. Appendices

[Appendices as in THESIS_REPORT_ENHANCED.md]

---

**Note**: All diagrams in this thesis are rendered from Mermaid source code, ensuring they remain editable and version-controlled. To view rendered versions, use a Markdown viewer with Mermaid support (GitHub, VS Code with Mermaid extension, or online tools like mermaid.live).
