/**
 * Chess AI Content Script - Clean Working Version
 */
class ChessAIOverlay {
    constructor() {
        // Try to get API URL from storage, fallback to localhost
        this.apiBaseUrl = 'http://localhost:8001';
        this.overlay = null;
        this.currentFEN = null;
        this.lastUpdateTime = 0;
        this.isAnalyzing = false;
        this.isActive = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        this.loadConfiguration();
        this.initializeExtractor();
        this.init();
    }
    
    async loadConfiguration() {
        try {
            // Try to get API URL from chrome storage
            if (typeof chrome !== 'undefined' && chrome.storage) {
                const result = await chrome.storage.sync.get(['apiBaseUrl']);
                if (result.apiBaseUrl) {
                    this.apiBaseUrl = result.apiBaseUrl;
                    console.log('[Chess AI] Using API URL from storage:', this.apiBaseUrl);
                }
            }
        } catch (error) {
            console.log('[Chess AI] Could not load configuration, using default:', error);
        }
    }
    
    initializeExtractor() {
        try {
            this.extractor = new ChessDOMExtractor();
            console.log('[Chess AI] DOM extractor initialized');
        } catch (error) {
            console.error('[Chess AI] Failed to initialize DOM extractor:', error);
            this.extractor = null;
        }
    }
    
    init() {
        if (!this.shouldBeActive()) {
            console.log('[Chess AI] Not activating on this page');
            return;
        }
        
        this.createOverlay();
        this.startPositionMonitoring();
        this.isActive = true;
        
        window.chessAI = {
            overlay: this,
            extractor: this.extractor,
            currentFEN: () => this.currentFEN
        };
        
        console.log('[Chess AI] Activated');
    }
    
    shouldBeActive() {
        const pathname = window.location.pathname;
        const validPaths = ['/play/', '/game/', '/puzzles/', '/analysis/', '/live/', '/daily/'];
        
        const validUrl = window.location.hostname.includes('chess.com') && 
                         validPaths.some(path => pathname.includes(path));
        
        const hasBoard = document.querySelector('.board, #board-vs-personalities-board, [id*="board-"]');
        
        // Debug logging
        console.log('[Chess AI] shouldBeActive check:', {
            hostname: window.location.hostname,
            pathname: pathname,
            validUrl: validUrl,
            hasBoard: !!hasBoard,
            boardElement: hasBoard ? hasBoard.className : 'none'
        });
        
        return validUrl && hasBoard;
    }
    
    createOverlay() {
        if (this.overlay) return;
        
        this.overlay = document.createElement('div');
        this.overlay.id = 'chess-ai-overlay';
        this.overlay.innerHTML = `
            <div class="chess-ai-header">
                <span class="chess-ai-title">Chess AI</span>
                <button class="chess-ai-close" id="chess-ai-close">×</button>
            </div>
            <div class="chess-ai-content">
                <div class="chess-ai-position">
                    <h3>Position Analysis</h3>
                    <div class="position-info">
                        <span class="turn-indicator">White to move</span>
                    </div>
                </div>
                
                <div class="chess-ai-analysis">
                    <h4>Analysis</h4>
                    <div class="best-moves">
                        <h5>Best Moves:</h5>
                        <ul class="moves-list">
                            <li>Click Quick Analysis to start</li>
                        </ul>
                    </div>
                    <div class="explanation">
                        <p class="explanation-text">Ready to analyze position...</p>
                    </div>
                </div>
                
                <div class="chess-ai-actions">
                    <button class="action-btn" id="quick-analysis">Quick Analysis</button>
                </div>
            </div>
        `;
        
        this.addStyles();
        document.body.appendChild(this.overlay);
        this.attachEventListeners();
        this.hideOverlay();
    }
    
    addStyles() {
        if (document.getElementById('chess-ai-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'chess-ai-styles';
        styles.textContent = `
            #chess-ai-overlay {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 300px;
                background: #4f46e5;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                z-index: 10000;
                font-family: system-ui, sans-serif;
                color: white;
                display: none;
            }
            
            .chess-ai-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }
            
            .chess-ai-title {
                font-weight: bold;
                font-size: 16px;
            }
            
            .chess-ai-close {
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                padding: 5px;
                border-radius: 3px;
            }
            
            .chess-ai-close:hover {
                background: rgba(255,255,255,0.2);
            }
            
            .chess-ai-content {
                padding: 15px;
            }
            
            .chess-ai-content h3, .chess-ai-content h4, .chess-ai-content h5 {
                margin: 0 0 10px 0;
                font-size: 14px;
            }
            
            .position-info {
                margin-bottom: 15px;
            }
            
            .turn-indicator {
                background: rgba(255,255,255,0.2);
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 12px;
            }
            
            .moves-list {
                list-style: none;
                padding: 0;
                margin: 0 0 15px 0;
            }
            
            .moves-list li {
                background: rgba(255,255,255,0.1);
                margin: 5px 0;
                padding: 8px;
                border-radius: 5px;
                font-size: 13px;
            }
            
            .explanation-text {
                margin: 0;
                font-size: 13px;
                line-height: 1.4;
                opacity: 0.9;
            }
            
            .action-btn {
                width: 100%;
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
                cursor: pointer;
            }
            
            .action-btn:hover {
                background: rgba(255,255,255,0.3);
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    attachEventListeners() {
        const closeBtn = this.overlay.querySelector('#chess-ai-close');
        const quickAnalysisBtn = this.overlay.querySelector('#quick-analysis');
        
        if (closeBtn) closeBtn.addEventListener('click', () => this.hideOverlay());
        if (quickAnalysisBtn) quickAnalysisBtn.addEventListener('click', () => this.quickAnalyze());
    }
    
    startPositionMonitoring() {
        if (!this.isActive) return;
        
        setInterval(() => this.checkBoardChange(), 5000);
        setTimeout(() => this.checkBoardChange(), 2000);
    }
    
    checkBoardChange() {
        if (!this.isActive || !this.extractor) {
            console.log('[Chess AI] Not active or no extractor');
            return;
        }
        
        const newFEN = this.extractor.extractCurrentFEN();
        
        console.log('[Chess AI] Board check:', {
            newFEN: newFEN,
            currentFEN: this.currentFEN,
            isActive: this.isActive,
            hasExtractor: !!this.extractor
        });
        
        if (!newFEN) {
            console.log('[Chess AI] No FEN extracted, hiding overlay');
            this.hideOverlay();
            return;
        }
        
        const now = Date.now();
        const timeSinceLastUpdate = now - this.lastUpdateTime;
        
        if (newFEN && newFEN !== this.currentFEN && timeSinceLastUpdate > 3000) {
            console.log('[Chess AI] Position changed:', newFEN);
            
            this.currentFEN = newFEN;
            this.lastUpdateTime = now;
            
            this.updatePositionDisplay();
            this.showOverlay();
        }
    }
    
    updatePositionDisplay() {
        if (!this.currentFEN || !this.overlay) return;
        
        const positionInfo = this.extractor.getPositionInfo(this.currentFEN);
        const turnIndicatorEl = this.overlay.querySelector('.turn-indicator');
        
        if (turnIndicatorEl) {
            turnIndicatorEl.textContent = positionInfo.toMove + ' to move';
        }
    }
    
    async quickAnalyze() {
        if (this.isAnalyzing || !this.currentFEN) return;
        
        this.isAnalyzing = true;
        this.showAnalysisLoading();
        
        try {
            const response = await fetch(this.apiBaseUrl + '/analyze-position', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fen: this.currentFEN,
                    depth: 10,
                    user_skill_level: 'intermediate',
                    explanation_type: 'comprehensive'
                })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`API error ${response.status}: ${errorText}`);
            }
            
            const analysis = await response.json();
            this.displayAnalysis(analysis);
            this.retryCount = 0; // Reset retry count on success
            
        } catch (error) {
            console.error('[Chess AI] Analysis error:', error);
            
            // Retry logic for network errors
            if (this.retryCount < this.maxRetries && error.message.includes('fetch')) {
                this.retryCount++;
                console.log(`[Chess AI] Retrying analysis (${this.retryCount}/${this.maxRetries})`);
                setTimeout(() => {
                    this.isAnalyzing = false;
                    this.quickAnalyze();
                }, 1000 * this.retryCount);
                return;
            }
            
            this.showError('Analysis failed: ' + error.message);
        } finally {
            this.isAnalyzing = false;
        }
    }
    
    showAnalysisLoading() {
        const movesListEl = this.overlay.querySelector('.moves-list');
        const explanationEl = this.overlay.querySelector('.explanation-text');
        
        if (movesListEl) movesListEl.innerHTML = '<li>Analyzing...</li>';
        if (explanationEl) explanationEl.textContent = 'Analyzing position...';
    }
    
    displayAnalysis(analysis) {
        const movesListEl = this.overlay.querySelector('.moves-list');
        const explanationEl = this.overlay.querySelector('.explanation-text');
        
        if (movesListEl && analysis.best_moves) {
            const movesHTML = analysis.best_moves.slice(0, 3).map(move => 
                '<li><strong>' + move.san + '</strong> (' + (move.score?.display || '0.00') + ') - ' + move.move + '</li>'
            ).join('');
            movesListEl.innerHTML = movesHTML || '<li>No moves available</li>';
        }
        
        if (explanationEl) {
            let explanation = 'Position analyzed successfully.';
            if (analysis.explanations && analysis.explanations.length > 0) {
                // Use the first explanation from the API
                explanation = analysis.explanations[0].explanation;
            } else if (analysis.best_moves && analysis.best_moves.length > 0) {
                explanation = 'Best move: ' + analysis.best_moves[0].san + '. Consider piece development and king safety.';
            }
            
            // Add learning insights if available
            if (analysis.learning_insights && analysis.learning_insights.length > 0) {
                explanation += '\n\nKey insights:\n• ' + analysis.learning_insights.slice(2).join('\n• ');
            }
            
            explanationEl.textContent = explanation;
        }
    }
    
    showError(message) {
        const movesListEl = this.overlay.querySelector('.moves-list');
        const explanationEl = this.overlay.querySelector('.explanation-text');
        
        if (movesListEl) movesListEl.innerHTML = '<li>Error: ' + message + '</li>';
        if (explanationEl) explanationEl.textContent = message;
    }
    
    showOverlay() {
        if (this.overlay && this.isActive) {
            this.overlay.style.display = 'block';
        }
    }
    
    hideOverlay() {
        if (this.overlay) {
            this.overlay.style.display = 'none';
        }
    }
}

function initializeChessAI() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    if (!hostname.includes('chess.com')) return;
    
    const validPaths = ['/play/', '/game/', '/puzzles/', '/analysis/', '/live/', '/daily/'];
    const isValidPath = validPaths.some(path => pathname.includes(path));
    
    if (!isValidPath) return;
    
    const checkBoard = () => {
        const hasBoard = document.querySelector('.board, #board-vs-personalities-board, [id*="board-"]');
        if (hasBoard) {
            new ChessAIOverlay();
            console.log('[Chess AI] Initialized successfully');
        } else {
            setTimeout(checkBoard, 2000);
        }
    };
    
    setTimeout(checkBoard, 1000);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChessAI);
} else {
    initializeChessAI();
}

console.log('[Chess AI] Content script loaded');
