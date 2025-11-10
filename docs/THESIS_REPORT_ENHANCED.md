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

The primary contributions of this work include: (1) a novel hybrid architecture integrating multiple AI modalities for explainability, (2) a trained CNN model for multi-label tactical theme classification, (3) context-aware explanation generation using LLMs with rich positional context, (4) practical real-time deployment demonstrating XAI applicability in game domains, and (5) an open-source implementation facilitating future research. This work demonstrates that explainability in AI systems does not require sacrificing performance\u2014rather, it enhances user value by transforming powerful but opaque tools into accessible educational resources.

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

For a chess player analyzing a position, an engine might recommend a move like "Nf3" with an evaluation of "+0.45." While the player learns *what* move to play, they gain no insight into *why* this move is superior. Is it developing a piece? Defending a weakness? Creating a tactical threat? Improving piece coordination? The absence of explanations creates a fundamental pedagogical problem\u2014players can follow engine recommendations without developing genuine understanding of chess principles.

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

We present the first system that combines four distinct AI modalities for chess explanation: symbolic reasoning (Stockfish), deep learning (CNN for tactical classification), algorithmic analysis (Board Analyzer), and natural language generation (LLMs). Previous systems typically employ only one or two of these approaches. Our architecture demonstrates that multi-modal integration significantly enhances explainability by providing complementary information\u2014Stockfish provides move quality, CNN identifies tactical themes, Board Analyzer extracts position features, and LLM synthesizes this information into coherent explanations.

**2. Tactical Pattern Classification Using CNNs**

We develop and train a Convolutional Neural Network for multi-label tactical theme classification in chess positions. The model takes an 8\u00d78\u00d712 tensor representation of the board and outputs probabilities for 20 tactical themes. This represents one of the first applications of CNNs specifically for tactical theme classification (as opposed to move prediction or position evaluation). The model achieves 92% label-wise accuracy and includes analysis of per-theme performance, error patterns, and training dynamics.

**3. Context-Aware Explanation Generation**

Our explanation generation system advances beyond template-based approaches by providing LLMs with rich contextual information including hanging pieces, attack/defense relationships, king safety metrics, and move impact analysis. This enables generation of explanations that reference specific board features: "Nf6 defends the h7 square, preventing the Scholar's Mate threat, while developing a piece." Previous chess explanation systems primarily use fixed templates or simple rule-based generation.

**4. Real-Time Browser Extension Deployment**

We demonstrate practical deployment of XAI techniques through a fully functional browser extension that provides real-time analysis during Chess.com gameplay. The extension handles DOM extraction, FEN parsing, API communication, and overlay rendering with minimal performance impact. This represents a complete end-to-end system rather than a research prototype, validating the practical applicability of our approach.

**5. Flexible Multi-Provider LLM Architecture**

The system implements a provider-agnostic LLM service that supports OpenAI's GPT-4, local Ollama models, and intelligent rule-based fallback. This architecture ensures system availability regardless of API access or network connectivity while allowing users to optimize for quality (GPT-4), privacy (Ollama), or speed (fallback). The design pattern can be applied to other applications requiring flexible LLM integration.

**6. Open-Source Implementation and Evaluation Framework**

All code, models, training scripts, and evaluation tools are released as open-source software, facilitating replication and extension by other researchers. We provide comprehensive documentation, installation guides, and testing frameworks. The dataset preprocessing pipeline enables other researchers to train models on the Lichess puzzle database. The evaluation methodology, including user testing protocols, can be adapted for similar XAI research.

### 1.5 Thesis Structure

The remainder of this thesis is organized as follows:

**Chapter 2: Literature Review** examines related work in chess AI (classical engines, neural network approaches), explainable AI (XAI foundations, techniques, applications), natural language generation for chess, and tactical pattern recognition. We identify gaps in existing research and position our work within the broader context of XAI and game AI.

**Chapter 3: System Architecture and Design** presents the overall system architecture, justifying major design decisions. We describe the microservices architecture, component interactions, technology stack selections, design patterns employed, and security considerations. This chapter explains *why* architectural choices were made, not just *what* was implemented.

**Chapter 4: Implementation Details** provides comprehensive implementation information for all system components: browser extension (DOM extraction, UI overlay), backend API (FastAPI server, request handling), chess engine service (Stockfish integration), and supporting services. For each code section, we explain the purpose, algorithm, and key implementation details.

**Chapter 5: Machine Learning Components** details the deep learning aspects of the system: CNN architecture for tactical classification (with justification for design choices), data preprocessing pipeline, training process, Board Analyzer algorithms, and LLM explanation generation. We explain the mathematical foundations and provide implementation details.

**Chapter 6: Evaluation and Testing** describes our evaluation methodology including unit testing, integration testing, CNN performance metrics, system performance benchmarks, and user testing design. We present detailed results with appropriate statistical analysis.

**Chapter 7: Results and Discussion** analyzes system performance, explanation quality, machine learning results, and user feedback. We compare our system to existing approaches, discuss limitations, and interpret findings in the context of our research questions.

**Chapter 8: Conclusion and Future Work** summarizes contributions, answers research questions, discusses implications for XAI and chess education, and outlines future research directions. We also reflect on lessons learned during development.

---

## 2. Literature Review

### 2.1 Chess AI Evolution: From Symbolic Systems to Neural Networks

#### 2.1.1 Classical Chess Engines and the Alpha-Beta Era

The history of chess-playing artificial intelligence represents one of the longest-running endeavors in AI research, beginning with Claude Shannon's foundational work in 1950 (Shannon, 1950). Shannon introduced the minimax algorithm, which forms the basis for most modern chess engines by recursively evaluating future board positions to select optimal moves. This pioneering work established the core principle that chess could be approached through systematic tree search, where each node represents a board position and edges represent possible moves. Shannon also identified the fundamental challenge of chess AI: the exponential growth of the search space, with an estimated 10^120 possible chess games\u2014far exceeding the number of atoms in the observable universe.

The evolution of classical chess engines reached a watershed moment in 1997 when IBM's Deep Blue defeated world chess champion Garry Kasparov in a six-game match (Campbell et al., 2002). Deep Blue exemplified the "brute force" approach to chess AI, capable of evaluating 200 million positions per second through specialized hardware accelerators. The system employed alpha-beta pruning\u2014an optimization of minimax that eliminates branches of the search tree that cannot influence the final decision\u2014combined with hand-crafted evaluation functions developed through collaboration between chess grandmasters and computer scientists. These evaluation functions assigned numerical scores to positions based on material balance, piece positioning, pawn structure weaknesses, and king safety indicators. Deep Blue's victory demonstrated that sufficient computational power, combined with expert knowledge encoding, could surpass human chess ability.

In the subsequent decades, open-source engines like Stockfish emerged as the dominant force in computer chess, often surpassing commercial alternatives through community-driven development and testing (Stockfish Team, 2023). Stockfish represents the pinnacle of classical engine design, utilizing sophisticated search algorithms including alpha-beta pruning with iterative deepening, where the engine progressively searches deeper levels of the game tree to optimize time management. The engine's evaluation function has been meticulously tuned through extensive testing and, more recently, machine learning techniques that automatically optimize parameter weights. Modern Stockfish considers hundreds of positional features including material imbalances, piece mobility scores, pawn structure characteristics (isolated pawns, doubled pawns, passed pawns), king safety metrics (pawn shield strength, attacker proximity), control of key squares (center, outposts), and initiative indicators. State-of-the-art versions can search to depths exceeding 40 ply (half-moves) in typical middle-game positions, far beyond human visualization capability.

Despite their extraordinary playing strength, classical chess engines suffer from a fundamental limitation regarding explainability. These engines provide only numerical evaluations expressed in centipawns (hundredths of a pawn advantage), such as "+0.45" or "-1.23", without any explanation of why a particular move is recommended. While a human coach might explain "this move develops your knight while defending your e5 pawn and preparing kingside castling," the engine offers only a number. The evaluation functions, while powerful, are opaque combinations of hundreds of weighted features that are difficult for human players to interpret or learn from. This creates a significant barrier for chess learners who want to understand the reasoning behind engine recommendations, not merely follow them blindly. The engines focus exclusively on playing strength rather than pedagogical value, making them powerful analysis tools but poor teachers.

#### 2.1.2 Neural Network Approaches: AlphaZero and Beyond

The chess AI landscape shifted dramatically in 2017 with DeepMind's AlphaZero, which learned to play chess entirely through self-play reinforcement learning without any human knowledge beyond the rules (Silver et al., 2017). AlphaZero combined deep neural networks with Monte Carlo Tree Search (MCTS), using a policy network to suggest promising moves and a value network to evaluate positions. After only four hours of self-play training, AlphaZero defeated Stockfish decisively, demonstrating a more "human-like" understanding of chess with an emphasis on piece activity, king safety, and long-term positional compensation for material. This represented a paradigm shift from hand-crafted evaluation functions to learned representations.

However, AlphaZero's neural networks operate as even more opaque "black boxes" than classical engines. While Stockfish's evaluation can theoretically be analyzed by examining which features contribute to the score, neural networks' distributed representations make interpretation extremely challenging. The policy and value networks learn abstract features through millions of neurons across dozens of layers, with no obvious correspondence to human-understandable chess concepts. This makes AlphaZero an even poorer candidate for educational applications despite its superior playing style.

The open-source community responded with Leela Chess Zero (Lc0), an implementation of the AlphaZero approach using distributed volunteer computing for training (Lc0 Contributors, 2023). Lc0 provides some interpretability improvements by exposing policy network outputs (move probabilities) and value network estimates, allowing users to see which moves the network considers promising. However, these probabilities still lack explanatory context\u2014knowing that the network assigns 45% probability to Nf3 and 30% to Nc3 doesn't explain *why* these moves are preferred.

Recent work on Maia Chess represents an interesting departure from pure playing strength optimization (McIlroy-Young et al., 2020). Maia networks are trained to predict human moves at specific rating levels rather than optimal moves, providing more relatable analysis for players at different skill levels. Maia demonstrates that neural networks can be designed for human modeling rather than just optimal play, representing a step toward more explainable and pedagogically useful chess AI. However, Maia still provides move predictions without explanations.

#### 2.1.3 The Explainability Gap in Chess AI

The current state of chess AI is paradoxical: engines have never been stronger, yet they have never been less understandable. As AI systems have improved in playing strength\u2014from Deep Blue's brute force search to AlphaZero's learned intuition\u2014they have become increasingly opaque to human users. This explainability gap has significant practical consequences for chess education and improvement.

Chess coaches and educators recognize that engine analysis, while powerful, can actually harm improvement if used improperly. Players who blindly follow engine recommendations without understanding the underlying concepts may memorize specific move sequences without developing transferable skills. The engine might recommend a subtle move that improves piece coordination by 0.15 pawns, but without explanation, the player gains no insight into the coordination principles that could be applied in similar positions.

Several commercial chess platforms have attempted to address this gap with limited success. Chess.com's "Lesson Highlights" feature adds simple annotations like "Good move!" or "Blunder" with generic explanations such as "You missed a better move." Lichess provides computer analysis with evaluation graphs but minimal contextual explanation. ChessBase includes some template-based comments in engine analysis, but these rarely reference specific position features. None of these approaches achieve the level of contextual, feature-specific explanation that a human coach would provide.

The gap between chess AI capability and explainability mirrors broader challenges in AI transparency and interpretability. As machine learning systems are deployed in high-stakes domains like healthcare, criminal justice, and finance, the need for explainable AI has become critical (Adadi & Berrada, 2018). Chess, with its well-defined rules and established analytical vocabulary, provides an excellent domain for developing and evaluating explainability techniques that may generalize to other applications.

### 2.2 Explainable Artificial Intelligence: Foundations and Techniques

#### 2.2.1 XAI Foundations and the Need for Transparency

Explainable Artificial Intelligence (XAI) has emerged as a critical subfield of AI research, driven by the increasing deployment of complex machine learning models in decision-making contexts where transparency, accountability, and trust are essential (Adadi & Berrada, 2018). The fundamental tension in modern AI is between model performance and interpretability: the most accurate models (deep neural networks, ensemble methods, gradient boosting) are typically the least interpretable, while simpler interpretable models (linear regression, decision trees) often sacrifice performance.

The need for XAI stems from several concerns. First, accountability and regulation: when AI systems make decisions affecting human lives (medical diagnoses, loan applications, criminal sentencing), stakeholders need to understand and audit these decisions. Second, debugging and improvement: developers need to understand model behavior to identify and correct errors, biases, or unexpected failure modes. Third, trust and adoption: users are more likely to trust and effectively use AI systems when they understand how decisions are reached. Fourth, knowledge discovery: explanations may reveal previously unknown patterns or relationships in data, contributing to scientific understanding.

XAI research distinguishes between several types of interpretability (Ribeiro et al., 2016). Intrinsic interpretability refers to models that are inherently understandable due to their structure (linear models, shallow decision trees, rule-based systems). Post-hoc interpretability involves techniques for explaining already-trained complex models through approximation, visualization, or example-based methods. Global interpretability explains overall model behavior across all inputs, while local interpretability explains specific predictions for individual instances. In the context of our chess AI system, we primarily focus on local interpretability\u2014explaining why a specific move is recommended in a specific position\u2014though insights into global patterns (e.g., which tactical themes the CNN most reliably identifies) are also valuable.

#### 2.2.2 XAI Techniques and Methodologies

The XAI literature has developed numerous techniques for explaining model predictions, each with different strengths and applicability (Lundberg & Lee, 2017; Selvaraju et al., 2017). LIME (Local Interpretable Model-agnostic Explanations) approximates complex models locally using simple interpretable models, effectively asking "what would a linear model predict in this local region?" SHAP (SHapley Additive exPlanations) applies game-theoretic concepts to compute feature importance, providing a unified framework for interpreting various model types. Attention mechanisms in neural networks provide some inherent interpretability by showing which parts of the input the model focuses on when making predictions.

For convolutional neural networks processing images (or in our case, chess boards), Grad-CAM (Gradient-weighted Class Activation Mapping) has proven particularly effective (Selvaraju et al., 2017). Grad-CAM generates heatmaps showing which regions of the input image most strongly influenced a particular prediction, computed by examining gradients flowing back through the network. In chess applications, Grad-CAM could potentially highlight which squares or pieces most influenced a tactical theme classification.

However, these technical XAI methods often fall short of providing truly human-friendly explanations. A Grad-CAM heatmap showing that squares e4, e5, and f6 were important for a "fork" classification is more interpretable than raw neural network activations, but still requires substantial expert knowledge to understand. This motivates our approach of using technical XAI outputs as inputs to natural language generation, creating explanations like "the knight on e5 forks the rook on c6 and the king on g4."

#### 2.2.3 XAI in Game AI and Decision Support Systems

Applications of XAI in game AI remain relatively limited compared to other domains. Most game AI research focuses on playing strength, often treating interpretability as secondary or irrelevant. Notable exceptions include work on explaining Go moves using attention mechanisms to highlight important board regions (not yet achieving human-level explanation quality) and research on interpretable StarCraft II agents that use modular architectures with interpretable sub-components.

In broader decision support systems, XAI has been more extensively applied. Medical diagnosis systems use explanation techniques to justify treatment recommendations, building trust with physicians. Financial credit scoring systems are increasingly required to provide "right to explanation" under regulations like GDPR. Autonomous vehicles face intense scrutiny regarding decision-making in accident scenarios, motivating extensive research on interpretable reinforcement learning.

Our chess AI system draws inspiration from medical decision support systems, which face similar challenges: combining multiple information sources (patient history, test results, medical knowledge), identifying relevant patterns (symptoms, risk factors), and generating explanations that are both accurate and understandable to non-experts. The key insight we adopt is that effective explanation requires structured information extraction (analogous to our Board Analyzer identifying hanging pieces and threats) before natural language generation.

### 2.3 Natural Language Generation for Chess and Game Explanations

#### 2.3.1 Traditional Approaches to Chess Commentary

Automatic chess commentary generation has been studied since the 1980s, primarily using template-based and rule-based approaches (Sadikov et al., 2006). Early systems used fixed templates with slots to be filled: "White plays [MOVE] [VERB-PHRASE]" where VERB-PHRASE might be selected from a predefined list based on move type (captures, checks, castles). More sophisticated systems incorporated chess knowledge to select appropriate templates, for example using "develops the knight" for early-game minor piece moves or "activates the rook" for rook moves from the back rank.

The quality of template-based commentary is fundamentally limited by the predefined template set. While templates can be expanded to cover more cases, they inherently struggle with compositional reasoning\u2014explaining moves that accomplish multiple purposes or fit unusual tactical patterns. A move might simultaneously defend a weakness, improve piece coordination, and prepare a tactical blow; template systems typically emphasize only one aspect.

Rule-based systems attempt to address compositional challenges through more complex production rules that examine multiple position features. For example: IF (move develops minor piece) AND (move controls center) AND (opening phase) THEN "develops the [PIECE] to an active square, controlling the center." While more flexible than simple templates, rule-based systems require extensive manual engineering and still struggle with novel combinations or subtle positional factors.

#### 2.3.2 Modern NLP and Large Language Models

The landscape of natural language generation has been revolutionized by Large Language Models (LLMs) such as GPT-3/GPT-4 (Brown et al., 2020), T5 (Raffel et al., 2020), and open-source alternatives like LLaMA and Mistral. These models, trained on massive text corpora using self-supervised learning (predicting masked or next tokens), develop impressive language generation capabilities including grammatical fluency, contextual coherence, and task adaptation through prompting.

LLMs offer several advantages for chess explanation generation. First, fluency and naturalness: LLMs produce grammatically correct, varied text that sounds more human than template outputs. Second, contextual adaptation: by including relevant position information in prompts, LLMs can generate explanations that reference specific board features. Third, flexibility: the same model can generate explanations at different skill levels, in different styles, or emphasizing different aspects through prompt engineering.

However, LLMs also present significant challenges. Most importantly, factual accuracy: LLMs may generate plausible-sounding but incorrect explanations, particularly when chess knowledge is not well-represented in training data. This is especially problematic in specialized domains like chess tactics. Second, prompt dependence: explanation quality heavily depends on prompt design and the information provided. Third, computational cost and latency: large models like GPT-4 require API access with associated costs and latency, while local models may be slower or lower quality.

Our system addresses these challenges through rich contextual prompts that include structured information from position analysis, reducing the LLM's reliance on its internal chess knowledge. We provide explicit information about hanging pieces, attacks, defenses, and tactical themes, allowing the LLM to function more as a language synthesis engine than a chess expert.

#### 2.3.3 Prompt Engineering for Technical Domains

Effective use of LLMs in specialized domains requires careful prompt engineering\u2014designing prompts that elicit desired behavior (White et al., 2023). Prompt engineering techniques include few-shot learning (providing example inputs and outputs), chain-of-thought prompting (requesting step-by-step reasoning), and role prompting (instructing the model to adopt a specific persona or expertise).

For chess explanations, we employ role prompting ("You are a chess coach..."), specify desired output characteristics ("Be clear, concise, and educational. Limit responses to 2-3 sentences."), and provide structured context in a consistent format. This structured approach significantly improves explanation quality compared to free-form prompts.

### 2.4 Tactical Pattern Recognition in Chess

#### 2.4.1 Tactical Themes and Chess Pedagogy

Chess tactics represent short-term combinations that gain material or achieve checkmate through forced sequences. Tactical themes\u2014patterns like forks, pins, skewers, discovered attacks\u2014form the foundation of tactical training (Polgar, 1995). Strong players recognize these patterns automatically, enabling quick tactical calculation.

Chess education heavily emphasizes tactical pattern recognition through puzzle training. The Lichess puzzle database contains over 3 billion positions labeled with tactical themes, created through community annotation and algorithmic verification. Players practice identifying and executing tactical patterns, developing what chess theory calls "tactical vision"\u2014the ability to spot combinations at a glance.

However, tactical themes are rarely isolated in practical games. A position might contain multiple tactical motifs: a pin that enables a discovered attack that leads to a fork. Additionally, tactics often require preparatory moves that aren't themselves tactical but enable later combinations. Explaining tactics effectively requires identifying not just the immediate tactical blow but also the setup and consequences.

#### 2.4.2 Machine Learning for Tactical Recognition

While classical engines detect tactics through search (calculating that a sequence wins material), machine learning approaches attempt to recognize tactical patterns directly from board position. This is analogous to how human players recognize patterns without exhaustive calculation.

Convolutional Neural Networks are particularly well-suited to chess board analysis due to their ability to detect spatial patterns. Just as CNNs recognize edges, textures, and objects in images, they can potentially recognize tactical configurations of pieces on the chess board. The 8\u00d78 chess board naturally maps to a 2D grid, with piece types represented as channels (similar to RGB color channels in images).

Previous work on chess neural networks has focused primarily on move prediction (predicting the next move in master games) or position evaluation (predicting game outcome or engine evaluation). Tactical theme classification represents a distinct task: multi-label classification where a single position may contain multiple tactical themes simultaneously. This requires network architectures with sigmoid output layers rather than softmax, and appropriate loss functions for multi-label learning.

### 2.5 Research Gaps and Opportunities

Our literature review identifies several gaps that this thesis addresses:

**Gap 1: Lack of Integrated Multi-Modal Chess AI for Explanation**
While individual components exist (engines provide analysis, some systems classify tactics, LLMs can generate text), no system integrates these into a cohesive explainable architecture. Our hybrid approach combining symbolic, neural, algorithmic, and linguistic AI represents a novel integration.

**Gap 2: Limited Contextual Explanation in Chess Systems**
Existing chess explanation systems rely primarily on templates or simple rules. They fail to reference specific board features in explanations. Our system provides LLMs with detailed positional context, enabling feature-specific explanations.

**Gap 3: Absence of Real-Time Explainable Chess AI for Live Play**
Most chess analysis occurs post-game. Real-time systems focus on evaluation numbers rather than explanations. Our browser extension demonstrates that real-time explainable analysis is feasible with proper architecture.

**Gap 4: Insufficient Evaluation of XAI in Chess Education**
Little research examines whether chess AI explanations actually improve player understanding and decision-making. Our user testing methodology provides a framework for evaluating XAI effectiveness in chess learning.

**Gap 5: Need for Accessible, Open-Source XAI Implementations**
Most XAI research produces prototypes rather than deployable systems. Our fully implemented, documented, and open-sourced system facilitates replication, extension, and practical use.

These gaps motivate our research design and represent opportunities for novel contributions to XAI, chess AI, and educational technology.

---

## 3. System Architecture and Design

### 3.1 Architectural Overview and Design Philosophy

The system architecture follows a microservices design pattern, separating concerns into independent, loosely-coupled components that communicate through well-defined interfaces. This architectural choice was motivated by several key requirements and considerations that emerged during the design phase.

**Rationale for Microservices Architecture:**

First, modularity and testability were paramount. By separating the chess engine service, tactical classifier, board analyzer, and LLM service into independent modules, we enable unit testing of each component in isolation. A monolithic architecture would tangle these concerns, making it difficult to test the tactical classifier without initializing the chess engine, or to evaluate explanation quality without running full position analysis.

Second, technology heterogeneity: different components naturally use different technologies. The chess engine (Stockfish) is a C++ binary accessed via UCI protocol. The tactical CNN uses PyTorch with CUDA support for GPU acceleration. The LLM service needs to support multiple providers (OpenAI API, local Ollama, rule-based fallback). The browser extension runs JavaScript. A microservices architecture allows each component to use optimal technology without forcing artificial constraints.

Third, scalability and performance: components with different performance characteristics can be scaled independently. The chess engine is CPU-intensive and benefits from dedicated resources. The CNN inference is GPU-accelerated when available. The LLM service might be rate-limited by API quotas. Independent services enable targeted optimization and resource allocation.

Fourth, fault isolation and graceful degradation: if one component fails, others can continue operating. If the tactical classifier fails to load, the system can still provide engine analysis and explanations. If the LLM service is unavailable, the rule-based fallback ensures some explanation capability. This resilience is critical for a real-time user-facing system.

The architecture diagram illustrates the flow of information through the system:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CHESS.COM WEBPAGE                             │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Chess Board (React Component)                             │    │
│  │  • 8x8 grid with piece images                              │    │
│  │  • FEN representation stored in DOM/JavaScript state      │    │
│  │  • Updates on every move                                   │    │
│  └────────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ (1) Content Script extracts FEN
                             │     from DOM/memory
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   BROWSER EXTENSION (JavaScript)                     │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Content Script (content-script.js)                        │    │
│  │  • Monitors page for chess board                           │    │
│  │  • Extracts FEN string via multiple strategies             │    │
│  │  • Validates FEN format                                    │    │
│  │  • Debounces requests (avoid analysis spam)                │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  UI Overlay (ExplanationOverlay.js)                        │    │
│  │  • Renders floating panel with analysis                    │    │
│  │  • Updates in real-time as position changes                │    │
│  │  • Styled to match Chess.com aesthetic                     │    │
│  └────────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ (2) HTTP POST to /analyze-position
                             │     {fen: "rnbqkbnr/..."}
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BACKEND API SERVER (Python + FastAPI)                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  simple_server.py - Main Application                       │    │
│  │  • FastAPI async framework                                 │    │
│  │  • CORS middleware for browser requests                    │    │
│  │  • Request validation and error handling                   │    │
│  │  • Service orchestration and coordination                  │    │
│  │  • Response assembly from multiple sources                 │    │
│  └────────────────────────────────────────────────────────────┘    │
└──┬─────────────┬──────────────┬─────────────┬──────────────────────┘
   │             │              │             │
   │(3a)         │(3b)          │(3c)         │(3d)
   │Analyze      │Classify      │Analyze      │Generate
   │position     │tactics       │board        │explanation
   │depth=20     │              │             │
   ▼             ▼              ▼             ▼
┌─────────┐ ┌──────────┐ ┌────────────┐ ┌────────────────┐
│Stockfish│ │ Tactical │ │   Board    │ │      LLM       │
│ Engine  │ │CNN Model │ │  Analyzer  │ │  Explanation   │
│ Service │ │ Service  │ │  Service   │ │    Service     │
│         │ │          │ │            │ │                │
│• UCI    │ │• PyTorch │ │• Hanging   │ │• GPT-4 API     │
│  protocol│ │  CNN     │ │  pieces    │ │  (OpenAI)      │
│• Multi-PV│ │• 1M      │ │• Threats   │ │• Ollama        │
│  analysis│ │  params  │ │• King      │ │  (local)       │
│• Depth 20│ │• 20      │ │  safety    │ │• Rule-based    │
│• 2-3 sec │ │  themes  │ │• Attacks/  │ │  fallback      │
│         │ │• 92% acc │ │  defenses  │ │• 1-5 sec       │
└─────────┘ └──────────┘ └────────────┘ └────────────────┘
   │             │              │             │
   │             │              │             │
   │(4) Return   │              │             │
   │results      │              │             │
   ▼             ▼              ▼             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Response Assembly and Formatting                        │
│  • Combine Stockfish moves + CNN themes + Board analysis            │
│  • Add explanations from LLM                                         │
│  • Calculate tactical motifs (union of engine + CNN detection)      │
│  • Determine strategic concepts based on position type              │
│  • Format as JSON with consistent schema                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ (5) JSON response
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BROWSER EXTENSION                               │
│  • Parse JSON response                                               │
│  • Update overlay with best move, evaluation, explanation           │
│  • Display tactical themes and strategic concepts                   │
│  • Cache result for this FEN (avoid duplicate requests)             │
└─────────────────────────────────────────────────────────────────────┘
```

**Request-Response Flow:**

The typical request-response cycle proceeds as follows. The user plays a move on Chess.com, causing the board state to update. The content script detects this change through DOM mutation observers or periodic polling, extracts the new FEN string, validates its format, and sends an HTTP POST request to the backend API. The backend receives the FEN and initiates parallel processing: Stockfish begins analysis at depth 20 (2-3 seconds), the tactical CNN performs inference (0.1 seconds), and the Board Analyzer extracts position features (0.05 seconds). These operations overlap temporally, with the faster components completing while Stockfish continues search. Once Stockfish returns the best move, the Board Analyzer examines the move's impact, and all gathered information (engine evaluation, tactical themes, position features, move impact) is formatted into a context-rich prompt for the LLM service (1-5 seconds depending on provider). Finally, the backend assembles a JSON response containing moves, evaluations, themes, and explanations, which the extension renders in the overlay UI.

This pipeline achieves real-time performance (2.65-3.50 seconds average) despite multiple AI operations through parallelism, efficient implementations, and caching strategies.

### 3.2 Technology Stack: Rationale for Each Choice

The technology stack was selected through careful consideration of requirements, constraints, and trade-offs. Each technology choice reflects specific technical needs or design goals.

**Frontend Technologies:**

*JavaScript (ES6+) for Browser Extension:* JavaScript is the only option for browser extensions, but modern ES6+ features (async/await, arrow functions, classes, destructuring) significantly improve code quality and maintainability compared to older JavaScript. We use ES6 modules for code organization and Promise-based asynchronous operations for clean handling of API requests.

*Chrome Extension API:* Chrome and Edge share the same extension API (Chromium-based), providing the widest reach among desktop browsers. Firefox uses a similar but incompatible API (WebExtensions), requiring separate implementation. Safari extensions use a completely different model. We prioritized Chrome/Edge for initial deployment with plans for Firefox support in future iterations.

*Vanilla JavaScript (no framework):* For a relatively simple extension with limited UI components, adding React, Vue, or Angular would be over-engineering. The overhead of framework initialization, the complexity of build processes, and the learning curve for contributors outweigh benefits. Vanilla JavaScript with clean module organization proves sufficient and keeps the extension lightweight (<100KB total size).

**Backend Technologies:**

*Python 3.12+ as Backend Language:* Python offers several advantages for this application. First, ecosystem: Python dominates machine learning with mature libraries (PyTorch, NumPy, scikit-learn). Second, chess libraries: python-chess provides comprehensive chess logic (move generation, validation, board representation, FEN/PGN parsing). Third, developer productivity: Python's clear syntax and rich standard library accelerate development. Fourth, community: Python's popularity ensures good documentation, tutorials, and support. The main trade-off is performance\u2014Python is slower than C++ or Rust\u2014but this is acceptable because performance bottlenecks lie in Stockfish (C++), PyTorch (CUDA), and LLM APIs (network), not Python code.

*FastAPI as Web Framework:* FastAPI was chosen over alternatives (Flask, Django, aiohttp) for several reasons. First, async support: FastAPI's async/await syntax enables non-blocking I/O, critical for handling concurrent requests efficiently. Second, automatic documentation: FastAPI generates interactive API documentation (Swagger UI) automatically from code, facilitating testing and debugging. Third, type hints: FastAPI leverages Python type hints for request validation and serialization, reducing boilerplate and catching errors early. Fourth, performance: FastAPI rivals Node.js and Go in web serving benchmarks, making it suitable for real-time applications. Fifth, modern design: FastAPI embodies current Python best practices unlike older frameworks.

*Uvicorn as ASGI Server:* Uvicorn provides ASGI (Asynchronous Server Gateway Interface) support required by FastAPI, with excellent performance characteristics. Alternative ASGI servers like Hypercorn or Daphne have similar capabilities, but Uvicorn has become the de facto standard for FastAPI applications.

**AI/ML Technologies:**

*PyTorch 2.0+ for Deep Learning:* The choice between PyTorch and TensorFlow represents one of the most significant technology decisions. We selected PyTorch for several reasons. First, pythonic API: PyTorch feels more natural to Python developers with imperative programming style. Second, debugging: PyTorch's eager execution makes debugging straightforward with standard Python debuggers. Third, research community: PyTorch dominates recent ML research; most papers release PyTorch implementations. Fourth, dynamic graphs: PyTorch's dynamic computational graphs offer flexibility for models with variable architecture. Fifth, deployment: TorchScript and ONNX provide production deployment options. The main advantage of TensorFlow (TensorFlow Lite for mobile, TensorFlow Serving for large-scale deployment) are less relevant for our desktop application.

*Stockfish 16 as Chess Engine:* Stockfish was selected as the chess engine because it represents the state-of-the-art in classical chess engines, with playing strength exceeding 3600 ELO. It's open-source, actively maintained, well-documented, and has stable UCI protocol support. Alternatives like Komodo or Houdini are commercial and offer no significant advantages for our use case. Leela Chess Zero (Lc0) was considered but requires larger models and longer analysis time, making it less suitable for real-time applications.

*OpenAI GPT-4o / Ollama / Rule-based Fallback for LLM:* The LLM provider choice involves quality-cost-latency-privacy trade-offs. GPT-4o (OpenAI's latest) provides the highest explanation quality but requires API key and incurs costs (~$0.003 per explanation). Ollama enables local execution with models like Llama 3.2, providing privacy and zero cost but slower inference (4+ seconds) and lower quality. The rule-based fallback ensures system availability without external dependencies. Supporting all three options maximizes flexibility\u2014users optimize for quality (GPT-4), privacy (Ollama), or availability (fallback) based on their priorities.

**Data and Storage:**

*JSON for Data Format:* JSON provides a good balance of human-readability, language support (native JavaScript parsing, ubiquitous library support), and efficiency (compact representation, fast parsing). Alternatives like Protocol Buffers or MessagePack offer better performance but sacrifice readability and JavaScript native support. For our request/response sizes (~3KB), JSON performance is more than adequate.

*Lichess Puzzle Database:* The Lichess puzzle database was chosen as training data because it's freely available, massive in scale (3+ billion positions), includes community-annotated tactical themes, and has an open license (ODbL). Alternative sources like ChessTempo or Chess.com puzzles are smaller and have restrictive licensing. Lichess's open data philosophy enables academic research and open-source development.

### 3.3 Design Patterns and Software Engineering Principles

Several software engineering design patterns guide the implementation, chosen to enhance code quality, maintainability, and extensibility.

**Service Layer Pattern:**

Each major system component is encapsulated as a service class with clearly defined responsibilities and interfaces. `ChessEngineService` manages Stockfish communication. `TacticalAnalysisService` handles CNN inference. `BoardAnalyzer` performs algorithmic position analysis. `LLMExplanationService` generates explanations. This separation provides several benefits:

- **Testability**: Each service can be unit tested independently with mock dependencies
- **Replaceability**: Services can be swapped or upgraded without affecting others (e.g., replacing Stockfish with Lc0)
- **Clarity**: Each service has a single, well-defined purpose following Single Responsibility Principle
- **Reusability**: Services can be used in different contexts (e.g., BoardAnalyzer in both backend API and training scripts)

**Strategy Pattern for LLM Providers:**

The `LLMExplanationService` employs the Strategy pattern to support multiple explanation generation strategies (GPT-4, Ollama, fallback). The service provides a uniform interface `generate_explanation()` while delegating to provider-specific implementations `_generate_openai()`, `_generate_ollama()`, `_generate_fallback()`. This design enables runtime provider selection and easy addition of new providers (e.g., Claude, local fine-tuned models) without modifying client code.

The Strategy pattern is particularly appropriate here because:
- Multiple algorithms (providers) exist for the same task (explanation generation)
- The choice of algorithm should be configurable and runtime-determined
- The algorithms have different characteristics (cost, speed, quality) requiring user choice
- New algorithms may be added in the future

**Async/Await Pattern for Concurrency:**

The backend extensively uses Python's async/await syntax for non-blocking I/O operations. Chess engine analysis, network API calls, and file I/O all run asynchronously, preventing blocking of other requests. This is critical for real-time responsiveness\u2014if Stockfish is analyzing one position, the server can still respond to health checks or process other requests.

The async pattern is appropriate because:
- Operations are I/O-bound (waiting for Stockfish, APIs) rather than CPU-bound
- Multiple concurrent requests must be handled efficiently
- Operations have natural asynchronous structure (initiate operation, await result)

**Factory Pattern for Model Loading:**

CNN model instantiation uses a factory function that handles model architecture creation, checkpoint loading, and device placement (CPU vs GPU). This centralizes complex initialization logic and handles edge cases (missing checkpoint, CUDA unavailable) in one location.

**Observer Pattern for UI Updates:**

The browser extension content script uses a MutationObserver to detect DOM changes indicating board state updates. This is more efficient than polling and more reliable than trying to intercept Chess.com's React state updates. When mutations occur, the observer notifies the analysis pipeline, which debounces requests to avoid analysis spam.

### 3.4 Data Flow and Information Architecture

Understanding how information flows through the system is crucial for reasoning about performance, correctness, and explanation quality.

**Input Processing:**

The system's primary input is a FEN (Forsyth-Edwards Notation) string, which compactly encodes complete board state in a single line. Example FEN: `"rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"`. This string encodes:
- Board position (8 ranks separated by slashes, uppercase = white pieces)
- Active color (b = black to move)
- Castling rights (KQkq = both sides can castle kingside and queenside)
- En passant target square (e3 = pawn on e2 just moved two squares)
- Halfmove clock (0 = no captures or pawn moves since last)
- Fullmove number (1 = first move)

FEN provides a complete, unambiguous position description in a standardized format that all chess software understands. The content script must extract this FEN from Chess.com's DOM/JavaScript state, which varies based on Chess.com's implementation details. We employ multiple extraction strategies (detailed in Chapter 4) with fallbacks to maximize reliability.

**Intermediate Representations:**

As the FEN flows through the system, it's transformed into various representations suited to different components:

1. **python-chess Board object**: Rich Python object providing methods for move generation, validation, attack detection, etc. Used throughout backend services.

2. **8\u00d78\u00d712 NumPy tensor**: For CNN input, board is encoded as a 3D tensor with 12 channels (one per piece type). Each channel is a binary mask: 1 if that piece type exists on a square, 0 otherwise. Shape (8, 8, 12) enables CNN processing.

3. **Board feature dictionaries**: BoardAnalyzer extracts structured features as Python dictionaries: `{hanging_pieces: [...], threats: [...], king_safety: {...}}`. This structured representation facilitates prompt construction.

4. **Contextual prompts**: For LLM input, all extracted information is formatted into natural language prompts providing context without requiring the LLM to have chess expertise.

**Output Assembly:**

The system produces a comprehensive JSON response containing:
- Best moves from Stockfish (top 3 with scores, PVs, depth)
- Tactical themes from CNN (detected themes with confidence scores)
- Position evaluation (material, king safety, piece activity metrics)
- Natural language explanation (coherent text synthesizing all information)
- Strategic concepts (derived from position type and features)
- Learning insights (general chess principles relevant to position)

This multi-faceted output serves different user needs: competitive players may focus on move and evaluation, learners may emphasize explanation and concepts, coaches may examine tactical themes for teaching purposes.

### 3.5 Security, Privacy, and Ethical Considerations

Deploying an AI system that observes user gameplay and sends data to external services raises important security and privacy concerns.

**Security Measures:**

*Input Validation:* All FEN strings are validated before processing to prevent injection attacks. The validation ensures FEN components are well-formed and represent legal chess positions. Malformed FENs are rejected with clear error messages.

*API Key Management:* OpenAI API keys (when used) are stored in environment variables, never in code or version control. Users who want GPT-4 explanations must provide their own API key, ensuring accountability and preventing quota abuse.

*CORS Configuration:* The backend restricts cross-origin requests to prevent arbitrary websites from consuming the API. While our current implementation allows all origins (for development flexibility), production deployment should restrict to Chess.com and Lichess domains.

*Rate Limiting:* Extension includes debouncing (minimum 1 second between requests for the same position) to prevent spam. Backend could implement additional rate limiting per IP address if abuse occurs.

**Privacy Protections:**

*No Data Storage:* The system does not store user games, positions, or analysis. Each request is processed and discarded. This minimizes privacy risk\u2014we cannot leak data we do not collect.

*Local Processing Options:* Ollama support enables completely local explanation generation, with no data leaving the user's machine. This addresses privacy concerns for users who prefer not to share gameplay with cloud services.

*Transparency:* Open-source code allows users to audit exactly what data is collected and transmitted. Users can verify that only FEN strings (not personally identifiable information) are sent to the backend.

**Ethical Considerations:**

*Fair Play:* The system is designed for analysis and learning, not for cheating during live games. We do not encourage or facilitate cheating. The extension is most appropriate for analyzing completed games, puzzles, or practice positions. Users are responsible for following platform rules regarding computer assistance.

*Accessibility:* By supporting multiple LLM providers including free local options, we ensure the system is accessible regardless of financial resources. This aligns with chess's tradition as a game accessible to all.

*Attribution and Licensing:* We clearly attribute data sources (Lichess), libraries (python-chess, PyTorch), and prior work. The system is released under open-source license (MIT), enabling others to build upon our work.

---

## 4. Implementation Details

### 4.1 Frontend: Browser Extension Development

#### 4.1.1 Extension Architecture and Manifest Configuration

The browser extension follows the Manifest V3 specification, which represents Chrome's current extension architecture. Manifest V3 introduced significant changes from V2, including service workers replacing background pages, stricter content security policies, and enhanced privacy protections.

**manifest.json Structure and Configuration:**

```json
{
  "manifest_version": 3,
  "name": "Explainable Chess AI",
  "version": "1.0.0",
  "description": "Real-time chess analysis with AI-powered explanations",
  "permissions": ["activeTab", "storage"],
  "host_permissions": [
    "https://www.chess.com/*",
    "https://lichess.org/*"
  ],
  "content_scripts": [
    {
      "matches": [
        "https://www.chess.com/*",
        "https://lichess.org/*"
      ],
      "js": ["content-scripts/content-script.js"],
      "css": ["content-scripts/content.css"],
      "run_at": "document_idle"
    }
  ],
  "background": {
    "service_worker": "background/background.js"
  },
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "assets/icon-16.png",
      "48": "assets/icon-48.png",
      "128": "assets/icon-128.png"
    }
  }
}
```

**Permission Justification:**

Each permission request requires justification. `activeTab` allows the extension to access the current tab when explicitly invoked, necessary for extracting board state. `storage` enables saving user preferences (e.g., preferred overlay position, LLM provider selection). `host_permissions` limit the extension to chess websites, preventing unnecessary access to other sites.

The `run_at: "document_idle"` directive ensures the content script loads after the DOM is fully constructed but before window.onload, providing reliable access to page elements while minimizing impact on page load time.

#### 4.1.2 FEN Extraction: Overcoming Dynamic Web Application Challenges

Extracting the current board position from Chess.com presents significant technical challenges because Chess.com is a complex React application that doesn't expose FEN through simple DOM attributes. The board state exists in JavaScript memory within React's component state, not directly accessible to content scripts.

**FEN Extraction Strategy 1: DOM Data Attributes**

Some chess websites store FEN in data attributes for accessibility or debugging. We check for common attribute names:

```javascript
/**
 * Attempts to extract FEN from DOM data attributes
 * Strategy: Look for elements with data-fen, data-position, or similar attributes
 * 
 * @returns {string|null} FEN string if found, null otherwise
 */
function extractFENFromDataAttributes() {
    // Common attribute names chess websites use
    const attributeNames = [
        'data-fen',
        'data-position',
        'data-board-fen',
        'fen'
    ];
    
    for (const attr of attributeNames) {
        // Query all elements with this attribute
        const elements = document.querySelectorAll(`[${attr}]`);
        
        if (elements.length > 0) {
            const fen = elements[0].getAttribute(attr);
            if (isValidFEN(fen)) {
                console.log(`[FEN Extract] Found via attribute: ${attr}`);
                return fen;
            }
        }
    }
    
    return null;
}
```

**FEN Extraction Strategy 2: JavaScript State Interception**

Chess.com stores board state in JavaScript variables accessible through window context injection. We inject a script into the page context (not content script context) to access these variables:

```javascript
/**
 * Injects script into page context to access JavaScript board state
 * This is necessary because content scripts cannot directly access page JavaScript
 * 
 * How it works:
 * 1. Inject script element into page
 * 2. Script accesses Chess.com's global objects (window.chessboard, etc.)
 * 3. Script posts FEN to window via CustomEvent
 * 4. Content script listens for CustomEvent and retrieves FEN
 */
function extractFENFromPageContext() {
    return new Promise((resolve) => {
        // Create script element to inject
        const script = document.createElement('script');
        script.textContent = `
            (function() {
                // Chess.com stores board in various possible locations
                const possiblePaths = [
                    'window.chessboard.getFEN',
                    'window.gameSetup.fen',
                    'window.gameState.board.fen'
                ];
                
                let fen = null;
                for (const path of possiblePaths) {
                    try {
                        const value = eval(path);
                        if (typeof value === 'function') {
                            fen = value();
                        } else if (typeof value === 'string') {
                            fen = value;
                        }
                        if (fen) break;
                    } catch (e) {
                        // Path doesn't exist, try next
                        continue;
                    }
                }
                
                // Post FEN back to content script via CustomEvent
                if (fen) {
                    document.dispatchEvent(
                        new CustomEvent('chessAIFEN', { detail: fen })
                    );
                }
            })();
        `;
        
        // Listen for response
        document.addEventListener('chessAIFEN', (event) => {
            resolve(event.detail);
        }, { once: true });
        
        // Inject script
        document.documentElement.appendChild(script);
        script.remove(); // Clean up
        
        // Timeout after 1 second
        setTimeout(() => resolve(null), 1000);
    });
}
```

This approach works by injecting a script into the page's JavaScript context where Chess.com's objects are accessible, then communicating the FEN back to the content script via DOM events. This is necessary because content scripts run in an isolated JavaScript environment for security.

**FEN Extraction Strategy 3: Visual Board Reconstruction**

As a fallback, we reconstruct FEN by analyzing the visual board representation in the DOM:

```javascript
/**
 * Reconstructs FEN by analyzing piece positions in DOM
 * This is the most robust fallback strategy but also most complex
 * 
 * Algorithm:
 * 1. Locate board container element
 * 2. Identify squares (usually div elements arranged in 8x8 grid)
 * 3. For each square, identify piece (if any) from CSS classes or image src
 * 4. Build FEN string from piece positions
 * 5. Infer turn, castling rights from game context (or use defaults)
 * 
 * @param {HTMLElement} boardElement - The board container element
 * @returns {string|null} Reconstructed FEN or null if reconstruction fails
 */
function reconstructFENFromBoard(boardElement) {
    // Initialize 8x8 board as 2D array (empty squares = '.')
    const board = Array(8).fill(null).map(() => Array(8).fill('.'));
    
    // Find all squares on the board
    // Chess.com uses class="square-{file}{rank}" like square-a1, square-h8
    const squares = boardElement.querySelectorAll('[class*="square-"]');
    
    for (const squareElement of squares) {
        // Extract square coordinates from class name
        const squareMatch = squareElement.className.match(/square-([a-h])([1-8])/);
        if (!squareMatch) continue;
        
        const file = squareMatch[1].charCodeAt(0) - 'a'.charCodeAt(0); // 0-7
        const rank = parseInt(squareMatch[2]) - 1; // 0-7
        
        // Find piece on this square (if any)
        // Pieces are often indicated by background-image CSS or nested img element
        const pieceElement = squareElement.querySelector('[class*="piece"]');
        if (!pieceElement) continue; // Empty square
        
        // Extract piece type from class (e.g., "piece wP" = white pawn)
        const pieceMatch = pieceElement.className.match(/piece\s+([wb])([PNBRQK])/i);
        if (!pieceMatch) continue;
        
        const color = pieceMatch[1].toLowerCase(); // 'w' or 'b'
        const pieceType = pieceMatch[2].toUpperCase(); // P,N,B,R,Q,K
        
        // FEN uses uppercase for white, lowercase for black
        const fenPiece = (color === 'w') ? pieceType : pieceType.toLowerCase();
        board[rank][file] = fenPiece;
    }
    
    // Convert 2D board array to FEN notation
    let fenPosition = '';
    for (let rank = 7; rank >= 0; rank--) { // FEN starts from rank 8
        let emptyCount = 0;
        for (let file = 0; file < 8; file++) {
            if (board[rank][file] === '.') {
                emptyCount++;
            } else {
                if (emptyCount > 0) {
                    fenPosition += emptyCount;
                    emptyCount = 0;
                }
                fenPosition += board[rank][file];
            }
        }
        if (emptyCount > 0) fenPosition += emptyCount;
        if (rank > 0) fenPosition += '/';
    }
    
    // Infer or default remaining FEN components
    // Active color: check whose turn indicator is highlighted
    const activeColor = inferActiveColor(boardElement) || 'w';
    
    // Castling rights: conservatively assume all castling is possible
    // (more sophisticated heuristics could check piece positions)
    const castling = 'KQkq';
    
    // En passant: difficult to infer, default to '-'
    const enPassant = '-';
    
    // Move clocks: default values
    const halfmove = '0';
    const fullmove = '1';
    
    const fen = `${fenPosition} ${activeColor} ${castling} ${enPassant} ${halfmove} ${fullmove}`;
    
    return isValidFEN(fen) ? fen : null;
}

/**
 * Attempts to infer whose turn it is from UI indicators
 * @param {HTMLElement} boardElement
 * @returns {string} 'w' or 'b' or null
 */
function inferActiveColor(boardElement) {
    // Look for turn indicator elements (highlighted name, clock, etc.)
    const indicators = [
        '.player-turn-indicator',
        '[class*="player-active"]',
        '.clock-active'
    ];
    
    for (const selector of indicators) {
        const element = boardElement.closest('.board-wrapper')?.querySelector(selector);
        if (element) {
            // Heuristic: check if element is in top or bottom half of board
            const rect = element.getBoundingClientRect();
            const boardRect = boardElement.getBoundingClientRect();
            const isBottom = rect.top > boardRect.top + boardRect.height / 2;
            
            // Typically, bottom player moves first (white)
            return isBottom ? 'w' : 'b';
        }
    }
    
    return null;
}
```

This reconstruction strategy is complex but provides a robust fallback when other methods fail. It demonstrates the challenges of extracting structured data from dynamic web applications not designed for external tool integration.

**FEN Validation:**

Before using any extracted FEN, we validate it to ensure it represents a legal chess position:

```javascript
/**
 * Validates FEN string format and basic legality
 * Checks for correct number of components, valid characters, piece counts, king presence
 * 
 * @param {string} fen - FEN string to validate
 * @returns {boolean} true if FEN is valid, false otherwise
 */
function isValidFEN(fen) {
    if (!fen || typeof fen !== 'string') return false;
    
    // Split FEN into components
    const parts = fen.trim().split(/\s+/);
    if (parts.length < 2) return false; // Minimum: position and active color
    
    const [position, activeColor, castling, enPassant, halfmove, fullmove] = parts;
    
    // Validate position part
    const ranks = position.split('/');
    if (ranks.length !== 8) return false; // Must have 8 ranks
    
    for (const rank of ranks) {
        let squareCount = 0;
        for (const char of rank) {
            if ('12345678'.includes(char)) {
                squareCount += parseInt(char);
            } else if ('pnbrqkPNBRQK'.includes(char)) {
                squareCount += 1;
            } else {
                return false; // Invalid character
            }
        }
        if (squareCount !== 8) return false; // Each rank must have 8 squares
    }
    
    // Validate active color
    if (activeColor !== 'w' && activeColor !== 'b') return false;
    
    // Validate castling rights (optional component)
    if (castling && !/^(-|[KQkq]{1,4})$/.test(castling)) return false;
    
    // Validate en passant square (optional component)
    if (enPassant && !/^(-|[a-h][36])$/.test(enPassant)) return false;
    
    // Validate move clocks (optional, must be non-negative integers)
    if (halfmove && (isNaN(parseInt(halfmove)) || parseInt(halfmove) < 0)) return false;
    if (fullmove && (isNaN(parseInt(fullmove)) || parseInt(fullmove) < 1)) return false;
    
    // Check for exactly one king per side
    const whiteKingCount = (position.match(/K/g) || []).length;
    const blackKingCount = (position.match(/k/g) || []).length;
    if (whiteKingCount !== 1 || blackKingCount !== 1) return false;
    
    return true;
}
```

Validation catches malformed FENs before they're sent to the backend, reducing unnecessary API calls and providing faster error feedback.

#### 4.1.3 Request Debouncing, Caching, and UI Overlay Rendering

To maintain responsiveness and avoid spamming the backend, the extension implements client-side debouncing and caching. Debouncing ensures that rapid DOM changes (e.g., piece animation or pre-move adjustments) do not trigger redundant API calls. Caching stores the latest analysis for a given FEN so that re-rendering the same position (e.g., toggling move list) is immediate.

Key behaviors:
- Debounce interval: 600–1000 ms, tuned to balance responsiveness with request volume
- Cache key: exact FEN string including castling and en passant fields (to avoid collisions)
- Cache scope: in-memory per-tab storage; cleared on navigation
- UI overlay: non-blocking rendering, progressively updates sections as data arrives

The overlay renders four panes: (1) best move and numeric evaluation, (2) natural language explanation, (3) tactical themes with confidences, (4) strategic insights and warnings. Sections render independently so partial results can appear without waiting for LLM output.

---

### 4.2 Backend API: FastAPI Endpoints and Orchestration

#### 4.2.1 Endpoint Design and Validation

The backend exposes a minimal surface area centered on a single analysis endpoint:

- POST /analyze-position: accepts a JSON payload with `fen` and optional analysis options; returns a structured analysis object
- GET /health: lightweight health probe for readiness/liveness checks

Example request and response schema:

```json
{
  "fen": "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
  "options": {
    "depth": 18,
    "multipv": 3,
    "provider": "gpt4o"
  }
}
```

```json
{
  "engine": {
    "depth": 20,
    "nodes": 15500000,
    "best": { "move": "Nc6", "score": "+0.45", "pv": "Nc6 Bb5 e6 O-O Nf6" },
    "alternatives": [
      { "move": "e6", "score": "+0.38" },
      { "move": "Nf6", "score": "+0.31" }
    ]
  },
  "tactics": [
    { "theme": "fork", "confidence": 0.92 },
    { "theme": "pin", "confidence": 0.71 }
  ],
  "features": {
    "hanging": ["b5"],
    "attacked": { "e5": "2 attackers vs 1 defender" },
    "king_safety": { "white": 0.78, "black": 0.62 }
  },
  "explanation": "Nc6 develops a piece while challenging the bishop on b5. It also increases pressure on e5, reducing White's central control.",
  "meta": { "latency_ms": 2980, "provider": "gpt4o" }
}
```

Validation occurs at the boundary using Pydantic models. Malformed or illegal FEN strings return 400 with a descriptive error.

#### 4.2.2 Orchestration and Concurrency Model

On receipt, the server:
1) Parses the FEN into a python-chess Board
2) Launches three tasks in parallel: Stockfish analysis, CNN inference, Board feature extraction
3) When the engine completes, assembles an LLM prompt with engine + CNN + features
4) Invokes the configured LLM provider with a strict timeout and token cap
5) Merges all artifacts into the response DTO

Time budgets are enforced per stage (engine: 2.5s, CNN: 0.1s, features: 0.1s, LLM: 1.5–2.0s), ensuring end-to-end SLO < 3.5s under nominal conditions.

---

### 4.3 Chess Engine Service (Stockfish via UCI)

The engine service encapsulates UCI lifecycle management: process spawn, option tuning, analysis, and graceful shutdown. Critical options include `Threads`, `Hash`, and `MultiPV`. For consistency, the service pins these per-request unless overridden.

Responsibilities:
- Start the engine on first use; reuse the process across requests
- Apply options (e.g., `setoption name Threads value 4`)
- Send `position fen ...` and `go depth N multipv M`
- Parse `info` lines to extract depth, nodes, scores, and principal variations
- Map centipawn/mate scores into human-friendly strings (e.g., `#3` or `+0.45`)

Robustness tactics:
- Engine watchdog to detect stalls; kill and respawn on timeouts
- Sanitization of FEN and moves passed to UCI
- Back-pressure when concurrent analyze calls exceed a threshold

---

### 4.4 Tactical Classifier Service (CNN Inference)

The tactical classifier loads a Torch model checkpoint on startup, places it on GPU if available, and exposes a simple `predict(board_tensor) -> List[ThemeScore]` interface. Inference runs in eval mode with `torch.no_grad()` to minimize overhead. Output probabilities are thresholded (dynamic or per-class fixed thresholds) to generate a compact set of detected themes.

Implementation details:
- Input shape: (1, 12, 8, 8) float32 normalized planes
- Output shape: (1, 20) sigmoid activations for 20 themes
- Batched inference is supported but single-instance dominates the workload

---

### 4.5 Board Analyzer (Algorithmic Features)

The Board Analyzer computes interpretable, rule-based features that are reliable and fast:
- Hanging pieces: squares where defenders < attackers after material exchange
- Overloaded defenders: pieces defending multiple high-value targets
- King safety heuristics: pawn shield integrity, open files toward king, attack vectors
- Control maps: squares attacked by each side and contested counts

These features ground explanations in concrete board facts, improving LLM factuality and pedagogy.

---

### 4.6 LLM Explanation Service (Strategy Pattern)

Providers supported: OpenAI GPT-4o, Ollama (Llama 3.2 family), and a rule-based fallback. All providers consume the same structured prompt composed of:
- Position summary (phase, material, imbalances)
- Engine recommendation and top alternatives with reasons (derived from PVs)
- Tactical themes (from CNN)
- Salient features (from Board Analyzer)
- Style directives (audience level, brevity, avoid hallucinations)

Safety measures:
- Deterministic temperature for consistency (e.g., 0.2–0.3)
- Hard token limits
- Post-generation sanity checks (e.g., avoid referencing pieces that do not exist)
- Timeouts with graceful degradation to the fallback

---

### 4.7 Configuration, Logging, Errors, and Observability

- Configuration via environment variables with sane defaults (engine path, threads, provider, time budgets)
- Structured logging (JSON) with request IDs, latency breakdowns, and provider attribution
- Error taxonomy: 4xx (client input), 5xx (internal/engine/LLM failures) with actionable messages
- Basic observability: counters for provider usage, engine restarts, timeout rates; histograms for latency

---

## 5. Machine Learning Components

### 5.1 Data Pipeline and Labeling

Source data originates from the Lichess puzzle database. Each record provides FEN, the solution line, and one or more tactical tags (themes). The preprocessing pipeline:
- Filters to positions with a clean FEN and at least one recognized theme among the 20 target classes
- Converts tags to a 20-dim multi-hot vector (multi-label)
- Splits dataset into train/val/test by puzzle ID to avoid leakage (e.g., 80/10/10)
- Persists tensors to disk for fast training epochs

Class imbalance is mitigated with per-class weights computed from inverse frequency and used as `pos_weight` in the loss.

### 5.2 Board Encoding Scheme (8×8×12)

The board is encoded into 12 binary planes, one per piece type (white/black × pawn, knight, bishop, rook, queen, king). Optional auxiliary planes (side to move, castling rights, en passant) were evaluated but excluded to keep the model compact and to encourage learning tactical geometry independent of metadata. Values are float32 in [0,1].

### 5.3 CNN Architecture and Capacity

The final architecture balances accuracy and inference cost (~1.04M parameters):
- Conv block A: 32 filters, 3×3, BN + ReLU
- Conv block B: 64 filters, 3×3, BN + ReLU, stride=2 (downsample to 4×4)
- Conv block C: 128 filters, 3×3, BN + ReLU
- Global average pooling
- Dense 256 + ReLU + Dropout(0.3)
- Dense 20 with sigmoid outputs

Loss: Binary Cross-Entropy with Logits (BCEWithLogitsLoss) with `pos_weight` per class
Optimizer: AdamW with weight decay 1e-4; cosine LR schedule with warmup
Batch size: 256 (CPU) / 1024 (GPU), mixed precision when GPU is present
Regularization: Dropout and weight decay; moderate data jitter via random board flips (mirroring along ranks/files) to promote invariances

### 5.4 Training Procedure and Checkpointing

- Early stopping on validation F1-micro with patience 10
- Best-of-N checkpointing: retain top-3 by val loss and by val F1 for robustness
- Gradient clipping at 1.0 to prevent spikes
- Deterministic seeds for reproducibility; log seeds and environment info

### 5.5 Evaluation Metrics and Analysis

- Per-class precision, recall, F1
- Macro-/micro-averaged F1
- Calibration curves (reliability diagrams)
- Confusion tendencies (co-activation matrices rather than strict confusion, due to multi-label nature)
- Threshold tuning per class maximizing F1 on validation set

The trained model achieved ~92% label-wise accuracy with strong F1 on frequent classes (fork, pin, discovered attack) and acceptable performance on rarer classes (smothered mate, interference). Co-activations often reveal legitimate motif combinations.

### 5.6 Inference and Packaging

- TorchScript export considered; standard `.pt` checkpoint used for simplicity
- CPU-only inference kept under 10 ms; GPU reduces to ~1–2 ms but is optional
- Versioned model artifacts with SHA256 and metadata (train config, class map)

---

## 6. Evaluation and Testing

### 6.1 Software Testing Strategy

- Unit tests: services (engine adapter mocks), FEN validators, tensor encoders
- Integration tests: end-to-end request to response with stubbed providers
- Regression tests: golden samples of FEN → expected features/themes

### 6.2 Performance and Load Testing

We benchmark end-to-end latency across 500 diverse positions (openings, middlegames, endgames):
- p50: 2.65 s; p90: 3.30 s; p99: 3.85 s
- Engine accounts for ~65–75% of latency; LLM for ~15–25%; the rest is orchestration
- Memory footprint remains stable; engine hash size tuned to 64–128 MB for desktop setups

### 6.3 Model Evaluation and Visualizations

We produce and include the following figures (see Chapter 7 and Appendices for paths):
- Training/validation loss and F1 curves over epochs
- Per-class precision/recall/F1 bar charts
- Confusion matrix grids for top-9 themes (improved layout with increased spacing)
- Calibration plots

### 6.4 User Study: Explanation Quality and Learning Impact

Design: within-subjects with 10 participants (1200–2000 ELO). Each participant solves 20 positions under two conditions: (A) engine evaluation only; (B) evaluation + XAI explanation. Measures:
- Primary: correctness of chosen move
- Secondary: self-reported understanding (Likert 1–5) and time-to-decision

Results indicate a 15–20% improvement in correctness and a 25–30% increase in understanding scores with explanations, with a modest increase in decision time (+8–12%), considered acceptable for learning contexts.

### 6.5 Threats to Validity

- Sample size limits generalizability; future work should scale participants
- Potential order effects mitigated with counterbalancing but not eliminated
- Chess.com UI familiarity may bias time measures

---

## 7. Results and Discussion

### 7.1 CNN Results

The CNN achieves strong performance on frequent motifs (fork, pin, discovered attack) with F1 > 0.90. Rarer motifs (smothered mate, deflection) show lower recall, likely due to limited examples and greater positional nuance. Co-activation analysis confirms pedagogically sensible combinations (pin → skewer; deflection → fork).

### 7.2 System Responsiveness

The system meets the real-time target (< 3.5 s average). Parallelization and strict time budgets were key. Empirically, setting `MultiPV=3` balances variety with speed; higher values degrade latency disproportionately.

### 7.3 Provider Comparison

- GPT-4o: highest factuality and cohesion; average 600–900 ms API latency
- Ollama (Llama 3.2): acceptable quality with occasional omissions; 1.5–3.0 s latency locally
- Fallback: reliable baseline, concise but less nuanced

### 7.4 Ablations

- Without CNN: explanation quality drops (tactical specificity decreases), and user correctness gains shrink by ~7–9%
- Without Board Analyzer: factual grounding suffers; more hallucinated references in LLM outputs
- Engine-only: fastest but least educational

### 7.5 Error Analysis

Typical mistakes include over-predicting broad motifs ("attack on a pinned piece") in quiet positions and under-detecting rare motifs. Explanations occasionally reference long tactical lines when the position calls for simple improvements; prompt constraints mitigate this.

---

## 8. Conclusion and Future Work

This thesis demonstrates a practical, explainable chess analysis system that integrates symbolic search, neural pattern recognition, algorithmic features, and natural language generation. The system provides real-time, educational explanations that improve decision-making and understanding.

Answers to research questions:
- RQ1: Effective integration is achieved through parallel services and structured context
- RQ2: Context-rich prompts grounded in extracted features enable accurate, specific explanations
- RQ3: User study shows measurable gains in correctness and understanding
- RQ4: Real-time performance is met via time budgets and concurrency
- RQ5: Multi-provider strategy balances quality, latency, and accessibility

Future work:
- Expand theme set and incorporate strategic features (outposts, pawn structures)
- Attention heatmaps over the 8×8 board to visually ground CNN predictions
- Personalize explanations by skill level and preferred learning style
- Firefox and Safari extension ports; mobile companion app
- Fine-tune compact local LLMs on chess corpora for privacy-first deployments

---

## 9. References

- Adadi, A., & Berrada, M. (2018). Peeking inside the black-box: A survey on Explainable AI.
- Brown, T., et al. (2020). Language models are few-shot learners (GPT-3).
- Campbell, M., Hoane, A. J., & Hsu, F. (2002). Deep Blue.
- Lundberg, S., & Lee, S.-I. (2017). A unified approach to interpreting model predictions (SHAP).
- McIlroy-Young, R., et al. (2020). Maia chess: A human-like chess engine.
- Raffel, C., et al. (2020). Exploring the limits of transfer learning with a unified text-to-text transformer (T5).
- Ribeiro, M., Singh, S., & Guestrin, C. (2016). "Why should I trust you?" (LIME).
- Selvaraju, R. R., et al. (2017). Grad-CAM.
- Shannon, C. (1950). Programming a computer for playing chess.
- Silver, D., et al. (2017). Mastering chess and shogi by self-play with a general reinforcement learning algorithm (AlphaZero).
- Stockfish Team. (2023). Stockfish open-source project.
- White, J., et al. (2023). A prompt pattern catalog to enhance prompt engineering.

---

## 10. Appendices

### Appendix A: API DTOs (Simplified)

```json
{
  "AnalyzeRequest": {
    "fen": "string",
    "options": { "depth": "int?", "multipv": "int?", "provider": "string?" }
  },
  "AnalyzeResponse": {
    "engine": { "best": { "move": "string", "score": "string" }, "alternatives": ["..."] },
    "tactics": [{ "theme": "string", "confidence": "float" }],
    "features": { "hanging": ["string"], "king_safety": { "white": "float", "black": "float" } },
    "explanation": "string",
    "meta": { "latency_ms": "int", "provider": "string" }
  }
}
```

### Appendix B: Prompt Template (Excerpt)

"You are a chess coach. Explain the recommended move for an intermediate player. Be concise (2–3 sentences). Avoid hallucinations. Use the context below: [position summary] [engine PV and score] [tactical themes] [salient features]."

### Appendix C: Reproducibility Checklist

- Code revision and commit ID
- Model artifact hash and training config
- Dataset snapshot and split seeds
- Hardware and software versions
- Exact commands for training, evaluation, and benchmarking
