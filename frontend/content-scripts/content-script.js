/**
 * Chess AI Content Script - Real Position Analysis
 * FINAL VERSION with stable position detection
 */

class ChessAIOverlay {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.overlay = null;
        this.currentFEN = null;
        this.lastUpdateTime = 0;
        this.analysisCache = new Map();
        this.isAnalyzing = false;
        this.initializeExtractor();
        this.init();
        
        console.log('[Chess AI] Chess AI Overlay initialized');
    }
    
    initializeExtractor() {
        try {
            this.extractor = new ChessDOMExtractor();
            console.log('[Chess AI] DOM extractor initialized successfully');
        } catch (error) {
            console.error('[Chess AI] Failed to initialize DOM extractor:', error);
            this.extractor = null;
        }
    }
    
    init() {
        this.createOverlay();
        this.startPositionMonitoring();
        
        // Add global reference for debugging
        window.chessAI = {
            overlay: this,
            extractor: this.extractor,
            currentFEN: () => this.currentFEN
        };
    }
    
    createOverlay() {
        if (this.overlay) return;
        
        this.overlay = document.createElement('div');
        this.overlay.id = 'chess-ai-overlay';
        this.overlay.innerHTML = `
            <div class="chess-ai-header">
                <div class="chess-ai-icon">♔</div>
                <span class="chess-ai-title">Chess AI</span>
                <button class="chess-ai-close" id="chess-ai-close">×</button>
            </div>
            <div class="chess-ai-content">
                <div class="chess-ai-position">
                    <h3>Position Analysis</h3>
                    <div class="position-info">
                        <span class="position-type">Loading...</span>
                        <span class="turn-indicator">White to move</span>
                        <span class="move-number">Move 1</span>
                    </div>
                </div>
                
                <div class="chess-ai-analysis">
                    <h4>🧠 Analysis for <span class="analysis-color">White</span></h4>
                    
                    <div class="best-moves">
                        <h5>🎯 Best Moves:</h5>
                        <ul class="moves-list">
                            <li>Loading analysis...</li>
                        </ul>
                    </div>
                    
                    <div class="explanation">
                        <h5>💡 Explanation:</h5>
                        <p class="explanation-text">Analyzing position...</p>
                        <small class="analysis-perspective">Analysis from White's perspective</small>
                    </div>
                </div>
                
                <div class="chess-ai-actions">
                    <button class="action-btn" id="quick-analysis">⚡ Quick Analysis</button>
                </div>
            </div>
        `;
        
        this.addStyles();
        document.body.appendChild(this.overlay);
        this.attachEventListeners();
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                color: white;
                overflow: hidden;
                transition: all 0.3s ease;
            }
            
            .chess-ai-header {
                display: flex;
                align-items: center;
                padding: 12px 16px;
                background: rgba(255,255,255,0.1);
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }
            
            .chess-ai-icon {
                font-size: 20px;
                margin-right: 8px;
            }
            
            .chess-ai-title {
                font-weight: 600;
                font-size: 16px;
                flex-grow: 1;
            }
            
            .chess-ai-close {
                background: none;
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background 0.2s;
            }
            
            .chess-ai-close:hover {
                background: rgba(255,255,255,0.2);
            }
            
            .chess-ai-content {
                padding: 16px;
                max-height: 600px;
                overflow-y: auto;
            }
            
            .chess-ai-position h3 {
                margin: 0 0 8px 0;
                font-size: 16px;
                font-weight: 600;
            }
            
            .position-info {
                display: flex;
                gap: 12px;
                margin-bottom: 16px;
                flex-wrap: wrap;
            }
            
            .position-info span {
                background: rgba(255,255,255,0.2);
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }
            
            .chess-ai-analysis h4 {
                margin: 0 0 12px 0;
                font-size: 15px;
                font-weight: 600;
            }
            
            .best-moves h5, .explanation h5 {
                margin: 0 0 8px 0;
                font-size: 13px;
                font-weight: 600;
                opacity: 0.9;
            }
            
            .moves-list {
                list-style: none;
                padding: 0;
                margin: 0 0 16px 0;
            }
            
            .moves-list li {
                background: rgba(255,255,255,0.15);
                margin: 4px 0;
                padding: 8px 10px;
                border-radius: 6px;
                font-size: 13px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .move-notation {
                font-weight: 600;
                font-family: monospace;
            }
            
            .move-evaluation {
                opacity: 0.8;
                font-size: 12px;
            }
            
            .explanation-text {
                margin: 0 0 8px 0;
                font-size: 13px;
                line-height: 1.4;
                opacity: 0.9;
            }
            
            .analysis-perspective {
                opacity: 0.7;
                font-size: 11px;
            }
            
            .chess-ai-actions {
                margin-top: 16px;
                display: flex;
                gap: 8px;
            }
            
            .action-btn {
                flex: 1;
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                padding: 10px 12px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .action-btn:hover {
                background: rgba(255,255,255,0.3);
                transform: translateY(-1px);
            }
            
            .loading {
                opacity: 0.7;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 0.7; }
                50% { opacity: 1; }
            }
            
            .loading .moves-list li {
                animation: pulse 1.5s infinite;
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    attachEventListeners() {
        const closeBtn = this.overlay.querySelector('#chess-ai-close');
        const quickAnalysisBtn = this.overlay.querySelector('#quick-analysis');
        
        closeBtn?.addEventListener('click', () => this.hideOverlay());
        quickAnalysisBtn?.addEventListener('click', () => this.quickAnalyze());
    }
    
    startPositionMonitoring() {
        // Check for position changes every 3 seconds (reduced frequency)
        setInterval(() => this.checkBoardChange(), 3000);
        
        // Initial check
        setTimeout(() => this.checkBoardChange(), 1000);
    }
    
    checkBoardChange() {
        console.log('[Chess AI] === CHECKING BOARD CHANGE ===');
        
        const newFEN = this.extractor?.extractCurrentFEN();
        console.log('[Chess AI] Extracted FEN:', newFEN?.substring(0, 50));
        
        // Only update if FEN actually changed AND it's been at least 5 seconds
        const now = Date.now();
        const timeSinceLastUpdate = now - this.lastUpdateTime;
        
        const shouldUpdate = newFEN && 
                           newFEN !== this.currentFEN && 
                           timeSinceLastUpdate > 5000; // 5 second minimum between updates
        
        if (shouldUpdate) {
            console.log('[Chess AI] Position change detected or forced update');
            console.log('[Chess AI] Old FEN:', this.currentFEN?.substring(0, 50));
            console.log('[Chess AI] New FEN:', newFEN?.substring(0, 50));
            
            this.currentFEN = newFEN;
            this.lastUpdateTime = now;
            
            this.updatePositionDisplay();
            this.showOverlay();
            
            // Analyze the new position
            setTimeout(() => this.quickAnalyze(), 100);
        } else if (newFEN === this.currentFEN) {
            console.log('[Chess AI] Same position, no update needed');
        } else {
            console.log(`[Chess AI] Too soon for update (${timeSinceLastUpdate}ms < 5000ms)`);
        }
    }
    
    updatePositionDisplay() {
        if (!this.currentFEN || !this.overlay) return;
        
        const positionInfo = this.extractor?.getPositionInfo(this.currentFEN);
        if (!positionInfo) return;
        
        const positionTypeEl = this.overlay.querySelector('.position-type');
        const turnIndicatorEl = this.overlay.querySelector('.turn-indicator');
        const moveNumberEl = this.overlay.querySelector('.move-number');
        const analysisColorEl = this.overlay.querySelector('.analysis-color');
        
        if (positionTypeEl) {
            const pieceCount = (this.currentFEN.match(/[rnbqkpRNBQKP]/g) || []).length;
            let positionType = 'Middle Game';
            if (pieceCount <= 10) positionType = 'Endgame';
            else if (pieceCount >= 28) positionType = 'Opening';
            
            positionTypeEl.textContent = positionType;
        }
        
        if (turnIndicatorEl) {
            turnIndicatorEl.textContent = `${positionInfo.toMove} to move`;
        }
        
        if (moveNumberEl) {
            moveNumberEl.textContent = `Move ${positionInfo.moveNumber}`;
        }
        
        if (analysisColorEl) {
            analysisColorEl.textContent = positionInfo.toMove;
        }
    }
    
    async quickAnalyze() {
        console.log('[Chess AI] quickAnalyze called');
        console.log('[Chess AI] isAnalyzing:', this.isAnalyzing);
        console.log('[Chess AI] currentFEN:', this.currentFEN);
        
        if (this.isAnalyzing) {
            console.log('[Chess AI] Analysis already in progress, skipping');
            return;
        }
        
        if (!this.currentFEN) {
            this.showError('No chess position detected');
            return;
        }
        
        // Check cache first
        if (this.analysisCache.has(this.currentFEN)) {
            console.log('[Chess AI] Using cached analysis');
            const cachedAnalysis = this.analysisCache.get(this.currentFEN);
            this.displayAnalysis(cachedAnalysis);
            return;
        }
        
        this.isAnalyzing = true;
        console.log('[Chess AI] Starting analysis for FEN:', this.currentFEN);
        this.showAnalysisLoading();
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);
        
        try {
            console.log('[Chess AI] Sending API request to:', `${this.apiBaseUrl}/analyze-position`);
            
            const response = await fetch(`${this.apiBaseUrl}/analyze-position`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    fen: this.currentFEN,
                    depth: 10,
                    user_skill_level: 'intermediate'
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            console.log('[Chess AI] Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('[Chess AI] API error response:', response.status, errorText);
                throw new Error(`API error: ${response.status} - ${errorText}`);
            }
            
            const analysis = await response.json();
            console.log('[Chess AI] Analysis received:', analysis);
            
            // Cache the result
            this.analysisCache.set(this.currentFEN, analysis);
            
            this.displayAnalysis(analysis);
            
        } catch (error) {
            clearTimeout(timeoutId);
            
            let errorMessage = 'Analysis failed';
            
            if (error.name === 'AbortError') {
                errorMessage = 'Analysis timed out. The position may be too complex.';
            } else if (error.message && error.message.includes('fetch')) {
                errorMessage = 'Cannot connect to analysis server. Make sure the backend is running.';
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            console.error('[Chess AI] Analysis error:', error);
            this.showError(`Analysis failed: ${errorMessage}`);
        } finally {
            this.isAnalyzing = false;
        }
    }
    
    showAnalysisLoading() {
        if (!this.overlay) return;
        
        const movesListEl = this.overlay.querySelector('.moves-list');
        const explanationEl = this.overlay.querySelector('.explanation-text');
        
        if (movesListEl) {
            movesListEl.innerHTML = `
                <li><span class="move-notation">Analyzing...</span></li>
                <li><span class="move-notation">Please wait...</span></li>
            `;
        }
        
        if (explanationEl) {
            explanationEl.textContent = 'Analyzing position with chess engine...';
        }
        
        this.overlay.classList.add('loading');
    }
    
    displayAnalysis(analysis) {
        if (!this.overlay || !analysis) return;
        
        this.overlay.classList.remove('loading');
        
        const movesListEl = this.overlay.querySelector('.moves-list');
        const explanationEl = this.overlay.querySelector('.explanation-text');
        
        if (movesListEl && analysis.best_moves) {
            const movesHTML = analysis.best_moves.slice(0, 3).map(move => `
                <li>
                    <span class="move-notation">${move.san}</span>
                    <span class="move-evaluation">(${move.score?.display || '0.00'})</span>
                </li>
            `).join('');
            
            movesListEl.innerHTML = movesHTML || '<li>No moves available</li>';
        }
        
        if (explanationEl) {
            let explanation = 'Position analyzed successfully.';
            
            if (analysis.best_moves && analysis.best_moves.length > 0) {
                const bestMove = analysis.best_moves[0];
                explanation = `Moving ${bestMove.san}. `;
                
                if (analysis.evaluation?.position_type) {
                    explanation += `This is a ${analysis.evaluation.position_type} position. `;
                }
                
                if (analysis.is_endgame) {
                    explanation += 'Focus on king activity and pawn promotion.';
                } else {
                    explanation += 'Consider piece development and king safety.';
                }
            }
            
            explanationEl.textContent = explanation;
        }
    }
    
    showError(message) {
        if (!this.overlay) return;
        
        const movesListEl = this.overlay.querySelector('.moves-list');
        const explanationEl = this.overlay.querySelector('.explanation-text');
        
        if (movesListEl) {
            movesListEl.innerHTML = `<li>Error: ${message}</li>`;
        }
        
        if (explanationEl) {
            explanationEl.textContent = message;
        }
        
        this.overlay.classList.remove('loading');
    }
    
    showOverlay() {
        if (this.overlay) {
            this.overlay.style.display = 'block';
        }
    }
    
    hideOverlay() {
        if (this.overlay) {
            this.overlay.style.display = 'none';
        }
    }
}

// Initialize when DOM is ready
function initializeChessAI() {
    console.log('[Chess AI] Initializing Chess AI on:', window.location.href);
    
    // Only run on supported chess sites
    const hostname = window.location.hostname;
    if (hostname.includes('chess.com') || hostname.includes('lichess.org')) {
        new ChessAIOverlay();
        console.log('[Chess AI] Chess AI initialized successfully');
    } else {
        console.log('[Chess AI] Not a supported chess site, skipping initialization');
    }
}

// Wait for DOM and run
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChessAI);
} else {
    initializeChessAI();
}

console.log('[Chess AI] Content script loaded');