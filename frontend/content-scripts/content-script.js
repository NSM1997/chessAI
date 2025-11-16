/**
 * Chess AI Content Script - Clean Working Version
 */
class ChessAIOverlay {
    constructor() {
        // Try to get API URL from storage, fallback to localhost
        this.apiBaseUrl = 'http://localhost:8001';
        this.overlay = null;
        this.currentFEN = null;
        this.previousFEN = null;
        this.lastUpdateTime = 0;
        this.isAnalyzing = false;
        this.isActive = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.autoAnalyzeEnabled = false;
        this.lastMoveAnalysis = null;
        
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
        // Try to activate immediately
        if (this.shouldBeActive()) {
            this.activate();
            return;
        }
        
        // If not active, wait for page to load and try again
        console.log('[Chess AI] Page not ready, waiting for load...');
        
        // Try again after a short delay
        setTimeout(() => {
            if (this.shouldBeActive()) {
                this.activate();
            } else {
                console.log('[Chess AI] Still not ready, trying one more time...');
                // Try one more time after a longer delay
                setTimeout(() => {
                    if (this.shouldBeActive()) {
                        this.activate();
                    } else {
                        console.log('[Chess AI] Not activating on this page after retries');
                    }
                }, 2000);
            }
        }, 1000);
    }
    
    activate() {
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
        const validPaths = ['/play/', '/game/', '/puzzles/', '/analysis/', '/live/', '/daily/', '/daily', '/analysis'];
        
        const validUrl = window.location.hostname.includes('chess.com') && 
                         validPaths.some(path => pathname.includes(path));
        
        // Try multiple board selectors
        const boardSelectors = [
            'wc-chess-board.board',
            'wc-chess-board',
            '.board',
            '#board-vs-personalities-board',
            '[id*="board-"]',
            '.chess-board',
            '.puzzle-board',
            '[class*="board"]',
            '[class*="chess"]',
            '.game-board',
            '#game-board',
            '.board-layout-main',
            '.board-layout-chessboard',
            'canvas',
            'svg'
        ];
        
        let hasBoard = false;
        let foundBoard = null;
        
        for (const selector of boardSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                hasBoard = true;
                foundBoard = element;
                console.log('[Chess AI] Found board with selector:', selector);
                break;
            }
        }
        
        // For special pages, also check for pieces as a fallback
        if (!hasBoard && (pathname.includes('/daily/') || pathname.includes('/daily') || pathname.includes('/game/') || pathname.includes('/analysis'))) {
            const pieces = document.querySelectorAll('.piece, [class*="piece"], .chess-piece, [class*="chess-piece"]');
            if (pieces.length > 0) {
                hasBoard = true;
                console.log('[Chess AI] Found pieces on special page:', pieces.length);
            }
        }
        
        // Debug logging
        console.log('[Chess AI] shouldBeActive check:', {
            hostname: window.location.hostname,
            pathname: pathname,
            validUrl: validUrl,
            hasBoard: hasBoard,
            boardElement: foundBoard ? `${foundBoard.tagName}.${foundBoard.className}` : 'none',
            pieceCount: document.querySelectorAll('.piece').length
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
                    <h4>📊 Best Move</h4>
                    <div class="best-moves">
                        <h5>Recommended:</h5>
                        <ul class="moves-list">
                            <li>Click Quick Analysis to start</li>
                        </ul>
                    </div>
                    <div class="explanation">
                        <p class="explanation-text">Ready to analyze position...</p>
                    </div>
                </div>
                
                <div class="your-move-section" id="your-move-section" style="display: none;">
                    <h4>🎯 Your Move Analysis</h4>
                    <div class="move-quality-badge" id="move-quality-badge">GOOD MOVE!</div>
                    <div class="your-move-details" id="your-move-details">
                        <p class="move-name">Your move: <strong>...</strong></p>
                        <p class="move-evaluation">Score: ...</p>
                    </div>
                    <div class="move-explanation" id="move-explanation">
                        <p>Analyzing your move...</p>
                    </div>
                </div>
                
                <div class="chess-ai-actions">
                    <button class="action-btn" id="quick-analysis">Show Best Move</button>
                    <button class="action-btn toggle-btn" id="toggle-auto-analysis">Enable Auto-Analyze</button>
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
                width: 350px;
                max-height: 90vh;
                overflow-y: auto;
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
            
            .toggle-btn {
                margin-top: 5px;
                font-size: 12px;
            }
            
            .your-move-section {
                margin-top: 20px;
                padding-top: 15px;
                border-top: 1px solid rgba(255,255,255,0.2);
            }
            
            .move-quality-badge {
                display: inline-block;
                padding: 5px 12px;
                border-radius: 15px;
                font-size: 11px;
                font-weight: bold;
                margin-bottom: 10px;
                color: white;
            }
            
            .quality-best { background: #10b981; }
            .quality-excellent { background: #06b6d4; }
            .quality-good { background: #3b82f6; }
            .quality-inaccuracy { background: #f59e0b; }
            .quality-mistake { background: #f97316; }
            .quality-blunder { background: #ef4444; }
            
            .your-move-details p {
                margin: 5px 0;
                font-size: 12px;
            }
            
            .move-explanation {
                margin-top: 10px;
                font-size: 12px;
                line-height: 1.4;
                opacity: 0.9;
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    attachEventListeners() {
        const closeBtn = this.overlay.querySelector('#chess-ai-close');
        const quickAnalysisBtn = this.overlay.querySelector('#quick-analysis');
        const toggleAutoBtn = this.overlay.querySelector('#toggle-auto-analysis');
        
        if (closeBtn) closeBtn.addEventListener('click', () => this.hideOverlay());
        if (quickAnalysisBtn) quickAnalysisBtn.addEventListener('click', () => this.quickAnalyze());
        if (toggleAutoBtn) toggleAutoBtn.addEventListener('click', () => this.toggleAutoAnalyze());
    }
    
    startPositionMonitoring() {
        if (!this.isActive) return;
        
        setInterval(() => this.checkBoardChange(), 5000);
        setTimeout(() => this.checkBoardChange(), 2000);
    }
    
    async checkBoardChange() {
        if (!this.isActive || !this.extractor) {
            console.log('[Chess AI] Not active or no extractor');
            return;
        }
        
        const newFEN = this.extractor.extractCurrentFEN();
        
        console.log('[Chess AI] Board check:', {
            newFEN: newFEN,
            currentFEN: this.currentFEN,
            previousFEN: this.previousFEN,
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
            
            // Check if this is a move (not just initial position)
            if (this.currentFEN && this.autoAnalyzeEnabled) {
                // A move was made! Analyze it
                await this.analyzeMoveAsync(this.currentFEN, newFEN);
            }
            
            this.previousFEN = this.currentFEN;
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
                    depth: 20,
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
    
    toggleAutoAnalyze() {
        this.autoAnalyzeEnabled = !this.autoAnalyzeEnabled;
        const toggleBtn = this.overlay.querySelector('#toggle-auto-analysis');
        
        if (toggleBtn) {
            if (this.autoAnalyzeEnabled) {
                toggleBtn.textContent = '✓ Auto-Analyze ON';
                toggleBtn.style.background = 'rgba(16, 185, 129, 0.3)';
            } else {
                toggleBtn.textContent = 'Enable Auto-Analyze';
                toggleBtn.style.background = 'rgba(255,255,255,0.2)';
            }
        }
        
        console.log('[Chess AI] Auto-analyze:', this.autoAnalyzeEnabled ? 'enabled' : 'disabled');
    }
    
    async analyzeMoveAsync(fenBefore, fenAfter) {
        if (!fenBefore || !fenAfter || fenBefore === fenAfter) {
            return;
        }
        
        console.log('[Chess AI] Analyzing move from', fenBefore, 'to', fenAfter);
        
        try {
            const response = await fetch(this.apiBaseUrl + '/analyze-move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fen_before: fenBefore,
                    fen_after: fenAfter
                })
            });
            
            if (!response.ok) {
                throw new Error(`API error ${response.status}`);
            }
            
            const analysis = await response.json();
            this.displayMoveAnalysis(analysis);
            
        } catch (error) {
            console.error('[Chess AI] Move analysis error:', error);
        }
    }
    
    displayMoveAnalysis(analysis) {
        if (!analysis || analysis.error) {
            console.error('[Chess AI] Move analysis error:', analysis);
            return;
        }
        
        const moveSection = this.overlay.querySelector('#your-move-section');
        const qualityBadge = this.overlay.querySelector('#move-quality-badge');
        const moveDetails = this.overlay.querySelector('#your-move-details');
        const moveExplanation = this.overlay.querySelector('#move-explanation');
        
        if (!moveSection) return;
        
        // Show the section
        moveSection.style.display = 'block';
        
        // Update quality badge
        if (qualityBadge && analysis.comparison) {
            const display = analysis.comparison.quality_display;
            qualityBadge.textContent = display.emoji + ' ' + display.label;
            qualityBadge.className = 'move-quality-badge quality-' + analysis.comparison.quality;
            qualityBadge.style.background = display.badge_color;
        }
        
        // Update move details
        if (moveDetails && analysis.user_move) {
            const userMove = analysis.user_move;
            const score = userMove.evaluation;
            moveDetails.innerHTML = `
                <p class="move-name">Your move: <strong>${userMove.san}</strong></p>
                <p class="move-evaluation">Evaluation: ${score.display || '0.00'}</p>
            `;
            
            if (analysis.comparison && !analysis.comparison.is_best_move) {
                moveDetails.innerHTML += `
                    <p class="move-evaluation">Best was: <strong>${analysis.best_move.san}</strong></p>
                `;
            }
        }
        
        // Update explanation
        if (moveExplanation && analysis.explanation) {
            moveExplanation.innerHTML = '<p>' + analysis.explanation + '</p>';
        }
        
        this.lastMoveAnalysis = analysis;
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
