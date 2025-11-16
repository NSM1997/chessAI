class ChessAIPopup {
    constructor() {
        this.init();
    }
    
    async init() {
        console.log('[Chess AI Popup] Initializing...');
        
        this.setupUI();
        await this.loadStatus();
        await this.restoreTrackingState();
    }
    
    setupUI() {
        this.statusElement = document.getElementById('status');
        this.urlElement = document.getElementById('current-url');
        this.refreshButton = document.getElementById('refresh-btn');
        this.testAnalysisButton = document.getElementById('test-analysis-btn');
        this.manualFenInput = document.getElementById('manual-fen');
        this.analyzeManualFenButton = document.getElementById('analyze-manual-fen');
        this.debugFenExtractionButton = document.getElementById('debug-fen-extraction');
        this.errorElement = document.getElementById('error-message');
        
        // Move analysis elements
        this.analyzeMyMoveButton = document.getElementById('analyze-my-move-btn');
        this.autoTrackStatus = document.getElementById('auto-track-status');
        this.moveAnalysisSection = document.querySelector('.move-analysis-section');
        this.moveQualityBadge = document.getElementById('move-quality-badge');
        this.moveDetails = document.getElementById('move-details');
        this.moveExplanationText = document.getElementById('move-explanation-text');
        
        // Tracking state
        this.isWaitingForMove = false;
        this.trackingInterval = null;
        this.capturedFEN = null;
        this.capturedTurn = null;
        this.opponentMoved = false;
        this.initialBestMove = null;
        
        if (this.refreshButton) {
            this.refreshButton.addEventListener('click', () => this.loadStatus());
        }
        
        if (this.testAnalysisButton) {
            this.testAnalysisButton.addEventListener('click', () => this.testAnalysis());
        }
        
        if (this.analyzeManualFenButton) {
            this.analyzeManualFenButton.addEventListener('click', () => this.analyzeManualFEN());
        }
        
        if (this.debugFenExtractionButton) {
            this.debugFenExtractionButton.addEventListener('click', () => this.debugFenExtraction());
        }
        
        if (this.analyzeMyMoveButton) {
            this.analyzeMyMoveButton.addEventListener('click', () => this.handleAnalyzeMyMove());
        }
    }
    
    async loadStatus() {
        try {
            this.clearError();
            
            const response = await this.sendMessage({ action: 'getStatus' });
            
            if (response.success) {
                this.updateUI(response.data);
            } else {
                throw new Error(response.error || 'Failed to get status');
            }
        } catch (error) {
            console.error('[Chess AI Popup] Failed to load status:', error);
            this.showError(error.message);
        }
    }
    
    updateUI(data) {
        if (this.statusElement) {
            if (data.isActive) {
                this.statusElement.textContent = 'Active on Chess.com';
                this.statusElement.style.color = '#4ade80';
            } else if (data.isChessPage) {
                this.statusElement.textContent = 'Chess.com detected (inactive page)';
                this.statusElement.style.color = '#fbbf24';
            } else {
                this.statusElement.textContent = 'Not on Chess.com';
                this.statusElement.style.color = '#fbbf24';
            }
        }
        
        if (this.urlElement && data.url) {
            const shortUrl = data.url.length > 40 ? 
                data.url.substring(0, 37) + '...' : 
                data.url;
            this.urlElement.textContent = shortUrl;
        }
    }
    
    showError(message) {
        if (this.errorElement) {
            this.errorElement.textContent = message;
            this.errorElement.style.display = 'block';
            this.errorElement.className = 'message error';
        }
    }
    
    clearError() {
        if (this.errorElement) {
            this.errorElement.style.display = 'none';
        }
    }
    
    async testAnalysis() {
        try {
            this.clearError();
            this.showMessage('Extracting current position...', 'info');
            
            // Get current FEN from the active tab
            const currentFEN = await this.getCurrentFEN();
            if (!currentFEN) {
                this.showError('Could not extract current board position. Make sure you are on a chess game or puzzle.');
                return;
            }
            
            this.showMessage('Analyzing current position...', 'info');
            
            const response = await fetch('http://localhost:8001/analyze-position', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fen: currentFEN,
                    depth: 20,
                    user_skill_level: 'intermediate',
                    explanation_type: 'comprehensive'
                })
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const analysis = await response.json();
            
            // Check if the server returned an error
            if (analysis.error) {
                this.showError(`${analysis.error}: ${analysis.message}`);
                return;
            }
            
            // Display detailed analysis information
            const bestMove = analysis.best_moves[0];
            const explanation = analysis.explanations[0];
            const insights = analysis.learning_insights;
            const positionEval = analysis.position_evaluation;
            
            // Format the message with improved structure
            let message = `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
            message += `BEST MOVE: ${bestMove.san} (${bestMove.move})\n`;
            message += `SCORE: ${bestMove.score.display}\n`;
            message += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
            
            message += `${insights[0]}\n`;
            message += `Position Score: ${positionEval.score.display}\n`;
            message += `Position Type: ${positionEval.position_type}\n`;
            
            // Add Opening Variation if available
            if (analysis.opening_info && analysis.opening_info.name) {
                message += `Opening: ${analysis.opening_info.name}\n`;
            }
            message += `\n`;
            
            // Add Tactical Motifs from explanation
            if (explanation.tactical_motifs && explanation.tactical_motifs.length > 0) {
                message += `Tactical Motifs:\n`;
                explanation.tactical_motifs.forEach(motif => {
                    message += `  • ${motif}\n`;
                });
                message += `\n`;
            }
            
            // Add Strategic Concepts
            if (explanation.strategic_concepts && explanation.strategic_concepts.length > 0) {
                message += `Strategic Concepts:\n`;
                explanation.strategic_concepts.forEach(concept => {
                    message += `  • ${concept}\n`;
                });
                message += `\n`;
            }
            
            message += `Explanation:\n${explanation.explanation}`;
            
            this.showMessage(message, 'success');
            
        } catch (error) {
            console.error('[Chess AI Popup] Test analysis failed:', error);
            this.showError('Test analysis failed: ' + error.message);
        }
    }
    
    showMessage(message, type = 'info') {
        if (this.errorElement) {
            this.errorElement.textContent = message;
            this.errorElement.style.display = 'block';
            this.errorElement.className = `message ${type}`;
        }
    }
    
    async getCurrentFEN() {
        try {
            // Get the active tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab || !tab.url.includes('chess.com')) {
                return null;
            }
            
            // Inject script to extract FEN from the page with detailed debugging
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: () => {
                    // Debug function to analyze the page structure
                    const debugInfo = {
                        url: window.location.href,
                        hasChessDOMExtractor: !!window.ChessDOMExtractor,
                        boardElements: [],
                        pieceElements: [],
                        allElements: []
                    };
                    
                    // Look for board elements
                    const boardSelectors = [
                        '.board',
                        '#board-vs-personalities-board',
                        '[id*="board-"]',
                        '.chess-board',
                        '.puzzle-board'
                    ];
                    
                    boardSelectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            debugInfo.boardElements.push({
                                selector: selector,
                                count: elements.length,
                                classes: Array.from(elements[0].classList)
                            });
                        }
                    });
                    
                    // Look for piece elements
                    const pieceSelectors = [
                        '[class*="piece"]',
                        '.piece',
                        '[class*="chess-piece"]',
                        '.chess-piece',
                        '[data-piece]',
                        '[class*="wP"]',
                        '[class*="bP"]',
                        '[class*="wK"]',
                        '[class*="bK"]'
                    ];
                    
                    pieceSelectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            debugInfo.pieceElements.push({
                                selector: selector,
                                count: elements.length,
                                sampleClasses: Array.from(elements[0].classList)
                            });
                        }
                    });
                    
                    // Try to extract FEN if DOM extractor is available
                    let fen = null;
                    if (window.ChessDOMExtractor) {
                        const extractor = new window.ChessDOMExtractor();
                        fen = extractor.extractCurrentFEN();
                    }
                    
                    return { fen, debugInfo };
                }
            });
            
            const result = results[0]?.result;
            console.log('[Chess AI Popup] Debug info:', result?.debugInfo);
            
            if (!result?.fen) {
                // If FEN extraction failed, try a simpler approach
                const simpleResults = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: () => {
                        // Try to find any element that might contain FEN data
                        const possibleFenSources = [
                            document.querySelector('[data-fen]'),
                            document.querySelector('[data-position]'),
                            document.querySelector('.fen'),
                            document.querySelector('.position')
                        ];
                        
                        for (const element of possibleFenSources) {
                            if (element) {
                                const fen = element.dataset.fen || element.dataset.position || element.textContent;
                                if (fen && fen.includes('/')) {
                                    return fen.trim();
                                }
                            }
                        }
                        
                        // Try to find FEN in JavaScript variables
                        try {
                            const possibleVariables = [
                                'window.chessBoard',
                                'window.board',
                                'window.game',
                                'window.puzzle',
                                'window.position',
                                'window.chess',
                                'window.chesscom',
                                'window.puzzleData',
                                'window.gameData'
                            ];
                            
                            for (const varName of possibleVariables) {
                                try {
                                    const obj = eval(varName);
                                    if (obj && obj.fen && typeof obj.fen === 'string') {
                                        return obj.fen;
                                    }
                                    if (obj && obj.currentFen && typeof obj.currentFen === 'string') {
                                        return obj.currentFen;
                                    }
                                } catch (e) {
                                    // Variable doesn't exist, continue
                                }
                            }
                        } catch (error) {
                            console.log('Error accessing variables:', error);
                        }
                        
                        // Try to find FEN in script tags
                        try {
                            const scripts = document.querySelectorAll('script');
                            for (const script of scripts) {
                                const content = script.textContent || script.innerHTML;
                                if (content && content.includes('/')) {
                                    const fenMatches = content.match(/["']([rnbqkpRNBQKP1-8\/\s]+)["']/g);
                                    if (fenMatches) {
                                        for (const match of fenMatches) {
                                            const potentialFen = match.replace(/["']/g, '').trim();
                                if (isValidChessFEN(potentialFen)) {
                                    return potentialFen;
                                }
                                        }
                                    }
                                }
                            }
                        } catch (error) {
                            console.log('Error searching scripts:', error);
                        }
                        
                        return null;
                    }
                });
                
                return simpleResults[0]?.result || null;
            }
            
            return result.fen;
        } catch (error) {
            console.error('[Chess AI Popup] Failed to extract FEN:', error);
            return null;
        }
    }
    
    async analyzeManualFEN() {
        try {
            this.clearError();
            
            const fen = this.manualFenInput.value.trim();
            if (!fen) {
                this.showError('Please enter a FEN string');
                return;
            }
            
            this.showMessage('Analyzing manual FEN...', 'info');
            
            const response = await fetch('http://localhost:8001/analyze-position', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fen: fen,
                    depth: 20,
                    user_skill_level: 'intermediate',
                    explanation_type: 'comprehensive'
                })
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const analysis = await response.json();
            
            // Check if the server returned an error
            if (analysis.error) {
                this.showError(`${analysis.error}: ${analysis.message}`);
                return;
            }
            
            // Display detailed analysis information
            const bestMove = analysis.best_moves[0];
            const explanation = analysis.explanations[0];
            const insights = analysis.learning_insights;
            const positionEval = analysis.position_evaluation;
            
            // Format the message with improved structure
            let message = `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
            message += `BEST MOVE: ${bestMove.san} (${bestMove.move})\n`;
            message += `SCORE: ${bestMove.score.display}\n`;
            message += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
            
            message += `${insights[0]}\n`;
            message += `Position Score: ${positionEval.score.display}\n`;
            message += `Position Type: ${positionEval.position_type}\n`;
            
            // Add Opening Variation if available
            if (analysis.opening_info && analysis.opening_info.name) {
                message += `Opening: ${analysis.opening_info.name}\n`;
            }
            message += `\n`;
            
            // Add Tactical Motifs from explanation
            if (explanation.tactical_motifs && explanation.tactical_motifs.length > 0) {
                message += `Tactical Motifs:\n`;
                explanation.tactical_motifs.forEach(motif => {
                    message += `  • ${motif}\n`;
                });
                message += `\n`;
            }
            
            // Add Strategic Concepts
            if (explanation.strategic_concepts && explanation.strategic_concepts.length > 0) {
                message += `Strategic Concepts:\n`;
                explanation.strategic_concepts.forEach(concept => {
                    message += `  • ${concept}\n`;
                });
                message += `\n`;
            }
            
            message += `Explanation:\n${explanation.explanation}`;
            
            this.showMessage(message, 'success');
            
        } catch (error) {
            console.error('[Chess AI Popup] Manual FEN analysis failed:', error);
            this.showError('Manual FEN analysis failed: ' + error.message);
        }
    }
    
    async debugFenExtraction() {
        try {
            this.clearError();
            this.showMessage('Debugging FEN extraction...', 'info');
            
            // Get the active tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab || !tab.url.includes('chess.com')) {
                this.showError('Please navigate to a Chess.com puzzle page first');
                return;
            }
            
            // Inject debug script that uses our working extractor
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: () => {
                    try {
                        const debugInfo = {
                            url: window.location.href,
                            timestamp: new Date().toISOString(),
                            boardElements: [],
                            pieceElements: [],
                            extractedFen: null,
                            extractionMethod: null,
                            errors: []
                        };
                        
                        // Check if ChessDOMExtractor is available
                        if (typeof ChessDOMExtractor !== 'undefined') {
                            try {
                                const extractor = new ChessDOMExtractor();
                                debugInfo.extractedFen = extractor.extractCurrentFEN();
                                debugInfo.extractionMethod = 'ChessDOMExtractor';
                            } catch (error) {
                                debugInfo.errors.push(`ChessDOMExtractor error: ${error.message}`);
                            }
                        } else {
                            debugInfo.errors.push('ChessDOMExtractor not available');
                        }
                        
                        // Check board elements
                        const boardSelectors = [
                            'wc-chess-board.board',
                            'wc-chess-board',
                            '.board',
                            '[id*="board"]',
                            '[class*="board"]'
                        ];
                        
                        boardSelectors.forEach(selector => {
                            const elements = document.querySelectorAll(selector);
                            elements.forEach((el, index) => {
                                const rect = el.getBoundingClientRect();
                                debugInfo.boardElements.push({
                                    selector: selector,
                                    index: index,
                                    tagName: el.tagName,
                                    className: el.className,
                                    id: el.id,
                                    dimensions: `${rect.width}x${rect.height}`,
                                    position: `(${rect.left}, ${rect.top})`
                                });
                            });
                        });
                        
                        // Check piece elements
                        const pieceElements = document.querySelectorAll('.piece');
                        debugInfo.pieceElements = Array.from(pieceElements).slice(0, 10).map((el, index) => {
                            const classes = Array.from(el.classList);
                            const rect = el.getBoundingClientRect();
                            return {
                                index: index,
                                classes: classes,
                                position: `(${rect.left}, ${rect.top})`,
                                dimensions: `${rect.width}x${rect.height}`
                            };
                        });
                        
                        // Try direct DOM position extraction as fallback
                        if (!debugInfo.extractedFen) {
                            try {
                                // Use the working DOM position extraction logic
                                let board = document.querySelector('wc-chess-board.board');
                                if (!board) {
                                    board = document.querySelector('wc-chess-board');
                                }
                                if (!board) {
                                    board = document.querySelector('.board');
                                }
                                
                                if (board) {
                                    const boardRect = board.getBoundingClientRect();
                                    const pieces = document.querySelectorAll('.piece');
                                    
                                    if (pieces.length > 0) {
                                        const boardArray = Array(8).fill().map(() => Array(8).fill(''));
                                        const squareWidth = boardRect.width / 8;
                                        const squareHeight = boardRect.height / 8;
                                        
                                        pieces.forEach(piece => {
                                            const classes = Array.from(piece.classList);
                                            let pieceType = null;
                                            for (const cls of classes) {
                                                if (cls.match(/^[wb][prnbqk]$/)) {
                                                    pieceType = cls;
                                                    break;
                                                }
                                            }
                                            
                                            if (pieceType) {
                                                const pieceRect = piece.getBoundingClientRect();
                                                const relativeX = pieceRect.left - boardRect.left;
                                                const relativeY = pieceRect.top - boardRect.top;
                                                
                                                const file = Math.floor(relativeX / squareWidth);
                                                const rank = Math.floor(relativeY / squareHeight);
                                                
                                                if (file >= 0 && file < 8 && rank >= 0 && rank < 8) {
                                                    const pieceChar = pieceType[0] === 'w' ? pieceType[1].toUpperCase() : pieceType[1].toLowerCase();
                                                    boardArray[rank][file] = pieceChar;
                                                }
                                            }
                                        });
                                        
                                        // Convert to FEN
                                        const fenBoard = boardArray.map(rank => {
                                            let rankStr = '';
                                            let emptyCount = 0;
                                            for (const square of rank) {
                                                if (square === '') {
                                                    emptyCount++;
                                                } else {
                                                    if (emptyCount > 0) {
                                                        rankStr += emptyCount;
                                                        emptyCount = 0;
                                                    }
                                                    rankStr += square;
                                                }
                                            }
                                            if (emptyCount > 0) {
                                                rankStr += emptyCount;
                                            }
                                            return rankStr;
                                        }).join('/');
                                        
                                        debugInfo.extractedFen = `${fenBoard} w KQkq - 0 1`;
                                        debugInfo.extractionMethod = 'Direct DOM positioning';
                                    }
                                }
                            } catch (error) {
                                debugInfo.errors.push(`Direct extraction error: ${error.message}`);
                            }
                        }
                        
                        return debugInfo;
                        
                    } catch (error) {
                        return { error: error.message };
                    }
                }
            });
            
            if (results && results[0] && results[0].result) {
                const debugInfo = results[0].result;
                
                if (debugInfo.error) {
                    this.showError(`Debug script error: ${debugInfo.error}`);
                    return;
                }
                
                if (debugInfo.extractedFen) {
                    // Auto-fill the extracted FEN
                    if (this.manualFenInput) {
                        this.manualFenInput.value = debugInfo.extractedFen;
                    }
                    
                    // Create visual board representation
                    const fenParts = debugInfo.extractedFen.split(' ');
                    const boardPart = fenParts[0];
                    const ranks = boardPart.split('/');
                    
                    let message = `FEN Extracted Successfully!\n\n`;
                    message += `FEN: ${debugInfo.extractedFen}\n\n`;
                    message += `Visual Board:\n`;
                    message += `  ┌─────────────────┐\n`;
                    
                    ranks.forEach((rank, index) => {
                        const rankNum = 8 - index;
                        let rankStr = `${rankNum} │ `;
                        
                        for (let char of rank) {
                            if (char >= '1' && char <= '8') {
                                // Empty squares
                                const emptyCount = parseInt(char);
                                rankStr += '. '.repeat(emptyCount);
                            } else {
                                // Piece
                                rankStr += char + ' ';
                            }
                        }
                        
                        message += rankStr + '│\n';
                    });
                    
                    message += `  └─────────────────┘\n`;
                    message += `    a b c d e f g h`;
                    
                    this.showMessage(message, 'success');
                } else {
                    this.showError('Failed to extract FEN from the page.\nPlease make sure you are on an active Chess.com game or puzzle.');
                }
            } else {
                this.showError('Debug failed: No results returned');
            }
            
        } catch (error) {
            console.error('[Chess AI Popup] Debug failed:', error);
            this.showError('Debug failed: ' + error.message);
        }
    }
    
    isValidChessFEN(fen) {
        if (!fen || typeof fen !== 'string') return false;
        
        const parts = fen.trim().split(' ');
        if (parts.length < 2) return false;
        
        // Check board position (first part)
        const boardPart = parts[0];
        if (!boardPart.includes('/')) return false;
        
        // Check if it contains valid chess piece characters
        const validChars = 'rnbqkpRNBQKP12345678/';
        if (!boardPart.split('').every(c => validChars.includes(c))) return false;
        
        // Check active color (second part)
        const activeColor = parts[1];
        if (!['w', 'b'].includes(activeColor)) return false;
        
        // Basic structure check - should have 8 ranks separated by /
        const ranks = boardPart.split('/');
        if (ranks.length !== 8) return false;
        
        // Check each rank has valid content
        for (const rank of ranks) {
            if (!rank || rank.length === 0) return false;
            // Each rank should be a combination of pieces and numbers
            if (!/^[rnbqkpRNBQKP1-8]+$/.test(rank)) return false;
        }
        
        return true;
    }
    
    async analyzeMove() {
        try {
            this.clearError();
            
            const fenBefore = this.fenBeforeInput.value.trim();
            const fenAfter = this.fenAfterInput.value.trim();
            
            if (!fenBefore || !fenAfter) {
                this.showError('Please enter both FEN positions (before and after your move)');
                return;
            }
            
            this.showMessage('Analyzing your move...', 'info');
            
            // Call the /analyze-move API endpoint
            const response = await fetch('http://localhost:8001/analyze-move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fen_before: fenBefore,
                    fen_after: fenAfter
                })
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const analysis = await response.json();
            
            // Check if the server returned an error
            if (analysis.error) {
                this.showError(`${analysis.error}: ${analysis.message}`);
                return;
            }
            
            // Display move analysis
            this.displayMoveAnalysis(analysis);
            
        } catch (error) {
            console.error('[Chess AI Popup] Move analysis failed:', error);
            this.showError('Move analysis failed: ' + error.message);
        }
    }
    
    displayMoveAnalysis(analysis) {
        // Show the move analysis section
        if (this.moveAnalysisSection) {
            this.moveAnalysisSection.style.display = 'block';
        }
        
        // Update quality badge
        if (this.moveQualityBadge && analysis.comparison) {
            const display = analysis.comparison.quality_display;
            const quality = analysis.comparison.quality;
            
            this.moveQualityBadge.textContent = display.emoji + ' ' + display.label;
            this.moveQualityBadge.className = 'quality-badge quality-' + quality;
        }
        
        // Update move details
        if (this.moveDetails && analysis.user_move && analysis.best_move) {
            const userMove = analysis.user_move;
            const bestMove = analysis.best_move;
            const isbestMove = analysis.comparison.is_best_move;
            
            let detailsHTML = `
                <p><strong>Your move:</strong> ${userMove.san}</p>
                <p><strong>Evaluation:</strong> ${userMove.evaluation.display || '0.00'}</p>
            `;
            
            if (!isbestMove) {
                detailsHTML += `
                    <p><strong>Best move:</strong> ${bestMove.san} (${bestMove.score.display})</p>
                    <p><strong>Difference:</strong> ${Math.abs(analysis.comparison.score_difference)} centipawns</p>
                `;
                
                // Show initial hint if different
                if (analysis.initialBestMove && analysis.initialBestMove.san !== bestMove.san) {
                    detailsHTML += `
                        <p style="font-size: 11px; color: #9ca3af; margin-top: 5px;">
                            <em>Note: Initial hint was ${analysis.initialBestMove.san}</em>
                        </p>
                    `;
                }
            }
            
            this.moveDetails.innerHTML = detailsHTML;
        }
        
        // Update explanation
        if (this.moveExplanationText && analysis.explanation) {
            this.moveExplanationText.textContent = analysis.explanation;
        }
        
        // Clear the error message and show success
        this.clearError();
    }
    
    async handleAnalyzeMyMove() {
        if (this.isWaitingForMove) {
            // Cancel waiting
            this.cancelWaiting();
            return;
        }
        
        try {
            this.clearError();
            
            // Clear any old cached analysis
            await chrome.storage.local.remove(['cachedMoveAnalysis']);
            
            // Capture current position
            const currentFEN = await this.getCurrentFEN();
            
            if (!currentFEN) {
                this.showError('Could not extract current position. Make sure you are on a chess game page.');
                return;
            }
            
            this.capturedFEN = currentFEN;
            this.isWaitingForMove = true;
            
            // Determine whose turn it is
            const fenParts = currentFEN.split(' ');
            this.capturedTurn = fenParts[1]; // 'w' or 'b'
            this.opponentMoved = false;
            this.initialBestMove = null; // Don't fetch now, will be in final analysis
            
            // Save state to chrome storage
            await chrome.storage.local.set({
                isWaitingForMove: true,
                capturedFEN: currentFEN,
                capturedTurn: this.capturedTurn,
                opponentMoved: false,
                initialBestMove: this.initialBestMove,
                timestamp: Date.now()
            });
            
            // Update UI
            if (this.analyzeMyMoveButton) {
                this.analyzeMyMoveButton.textContent = 'Waiting for your move... (Click to cancel)';
                this.analyzeMyMoveButton.style.background = 'rgba(251, 191, 36, 0.3)';
            }
            
            if (this.autoTrackStatus) {
                const turnColor = this.capturedTurn === 'w' ? 'White' : 'Black';
                this.autoTrackStatus.textContent = `⏳ Tracking ${turnColor}'s move. Make your move...`;
                this.autoTrackStatus.style.color = '#fbbf24';
            }
            
            // Start checking for move
            this.trackingInterval = setInterval(() => this.checkForMove(), 1500);
            
            console.log('[Chess AI] Waiting for move. Captured FEN:', currentFEN);
            
        } catch (error) {
            console.error('[Chess AI] Failed to start move detection:', error);
            this.showError('Failed to start move detection: ' + error.message);
            this.resetButton();
        }
    }
    
    async checkForMove() {
        if (!this.isWaitingForMove) return;
        
        try {
            const currentFEN = await this.getCurrentFEN();
            
            if (!currentFEN) {
                console.log('[Chess AI] Could not extract FEN during tracking');
                return;
            }
            
            // Check if position changed
            if (currentFEN !== this.capturedFEN) {
                const fenParts = currentFEN.split(' ');
                const currentTurn = fenParts[1]; // 'w' or 'b'
                
                console.log('[Chess AI] Position changed');
                console.log('[Chess AI] Captured turn:', this.capturedTurn);
                console.log('[Chess AI] Current turn:', currentTurn);
                console.log('[Chess AI] Opponent moved:', this.opponentMoved);
                
                // Check if this is the opponent's move or user's move
                if (currentTurn !== this.capturedTurn && !this.opponentMoved) {
                    // Opponent just moved (turn switched)
                    console.log('[Chess AI] Opponent moved, waiting for user move...');
                    this.opponentMoved = true;
                    this.capturedFEN = currentFEN; // Update to opponent's move
                    
                    // Update storage
                    await chrome.storage.local.set({
                        capturedFEN: currentFEN,
                        opponentMoved: true
                    });
                    
                    // Update UI
                    if (this.autoTrackStatus) {
                        this.autoTrackStatus.textContent = '⏳ Opponent moved. Now make YOUR move...';
                    }
                    
                } else if (currentTurn === this.capturedTurn && this.opponentMoved) {
                    // User just moved (turn switched back)
                    console.log('[Chess AI] User move detected!');
                    console.log('[Chess AI] Before user move:', this.capturedFEN);
                    console.log('[Chess AI] After user move:', currentFEN);
                    
                    // Stop tracking
                    this.stopWaiting();
                    
                    // Trigger background analysis (won't block)
                    this.triggerBackgroundAnalysis(this.capturedFEN, currentFEN);
                    
                } else if (currentTurn === this.capturedTurn && !this.opponentMoved) {
                    // User moved without opponent moving first
                    console.log('[Chess AI] User move detected (no opponent move)!');
                    console.log('[Chess AI] Before:', this.capturedFEN);
                    console.log('[Chess AI] After:', currentFEN);
                    
                    // Stop tracking
                    this.stopWaiting();
                    
                    // Trigger background analysis
                    this.triggerBackgroundAnalysis(this.capturedFEN, currentFEN);
                }
            }
            
        } catch (error) {
            console.error('[Chess AI] Error checking for move:', error);
        }
    }
    
    triggerBackgroundAnalysis(fenBefore, fenAfter) {
        // Send to background script for analysis (non-blocking)
        chrome.runtime.sendMessage({
            action: 'analyzeMoveInBackground',
            fen_before: fenBefore,
            fen_after: fenAfter
        }, (response) => {
            if (response && response.success) {
                console.log('[Chess AI] Background analysis triggered successfully');
            } else {
                console.error('[Chess AI] Background analysis failed:', response?.error);
            }
        });
        
        console.log('[Chess AI] Analysis triggered in background, close and reopen popup to see result');
    }
    
    async analyzeDetectedMove(fenBefore, fenAfter) {
        try {
            this.clearError();
            
            if (this.autoTrackStatus) {
                this.autoTrackStatus.textContent = '🔍 Analyzing your move...';
                this.autoTrackStatus.style.color = '#3b82f6';
            }
            
            console.log('[Chess AI] Analyzing move:');
            console.log('[Chess AI] FEN Before:', fenBefore);
            console.log('[Chess AI] FEN After:', fenAfter);
            
            // Call the /analyze-move API endpoint
            const response = await fetch('http://localhost:8001/analyze-move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fen_before: fenBefore,
                    fen_after: fenAfter
                })
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const analysis = await response.json();
            
            // Check if the server returned an error
            if (analysis.error) {
                let errorMsg = `${analysis.error}: ${analysis.message}`;
                
                // Add helpful tips based on error type
                if (analysis.error === 'Could not detect move') {
                    errorMsg += '\n\nPossible reasons:\n';
                    errorMsg += '• Multiple moves were made (you + opponent)\n';
                    errorMsg += '• Try clicking button IMMEDIATELY before YOUR move\n';
                    errorMsg += '• Make sure it\'s your turn when you click the button';
                }
                
                this.showError(errorMsg);
                this.resetButton();
                return;
            }
            
            // Add initial best move info if available
            if (this.initialBestMove) {
                analysis.initialBestMove = this.initialBestMove;
            }
            
            // Cache analysis for instant display on next popup open
            // Include timestamp and FENs to ensure it's for the right move
            await chrome.storage.local.set({
                cachedMoveAnalysis: {
                    ...analysis,
                    _cached_at: Date.now(),
                    _fen_before: fenBefore,
                    _fen_after: fenAfter
                }
            });
            
            // Display move analysis
            this.displayMoveAnalysis(analysis);
            
            // Update status based on quality
            if (this.autoTrackStatus && analysis.comparison) {
                const quality = analysis.comparison.quality;
                const emoji = analysis.comparison.quality_display.emoji;
                const label = analysis.comparison.quality_display.label;
                
                this.autoTrackStatus.textContent = `${emoji} ${label}! Click to analyze another move.`;
                
                if (quality === 'best' || quality === 'excellent') {
                    this.autoTrackStatus.style.color = '#4ade80';
                } else if (quality === 'good') {
                    this.autoTrackStatus.style.color = '#3b82f6';
                } else if (quality === 'inaccuracy') {
                    this.autoTrackStatus.style.color = '#fbbf24';
                } else {
                    this.autoTrackStatus.style.color = '#f87171';
                }
            }
            
            // Reset button
            this.resetButton();
            
        } catch (error) {
            console.error('[Chess AI Popup] Move analysis failed:', error);
            this.showError('Move analysis failed: ' + error.message);
            this.resetButton();
        }
    }
    
    stopWaiting() {
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
            this.trackingInterval = null;
        }
        this.isWaitingForMove = false;
    }
    
    cancelWaiting() {
        this.stopWaiting();
        this.resetButton();
        
        if (this.autoTrackStatus) {
            this.autoTrackStatus.textContent = 'Cancelled. Click to analyze another move.';
            this.autoTrackStatus.style.color = '#9ca3af';
        }
    }
    
    resetButton() {
        if (this.analyzeMyMoveButton) {
            this.analyzeMyMoveButton.textContent = 'Analyze My Move';
            this.analyzeMyMoveButton.style.background = 'rgba(255,255,255,0.2)';
        }
        this.isWaitingForMove = false;
        
        // Clear storage including cached analysis
        chrome.storage.local.remove(['isWaitingForMove', 'capturedFEN', 'capturedTurn', 'opponentMoved', 'initialBestMove', 'cachedMoveAnalysis', 'timestamp']);
    }
    
    async restoreTrackingState() {
        try {
            const data = await chrome.storage.local.get(['isWaitingForMove', 'capturedFEN', 'capturedTurn', 'opponentMoved', 'initialBestMove', 'timestamp']);
            
            if (!data.isWaitingForMove || !data.capturedFEN) {
                return;
            }
            
            // Check if state is not too old (max 5 minutes)
            const age = Date.now() - (data.timestamp || 0);
            if (age > 5 * 60 * 1000) {
                console.log('[Chess AI] Tracking state too old, clearing');
                this.resetButton();
                return;
            }
            
            console.log('[Chess AI] Restoring tracking state');
            this.capturedFEN = data.capturedFEN;
            this.capturedTurn = data.capturedTurn || 'w';
            this.opponentMoved = data.opponentMoved || false;
            this.initialBestMove = data.initialBestMove || null;
            this.isWaitingForMove = true;
            
            // Check if we have cached analysis from previous popup session
            const cachedData = await chrome.storage.local.get(['cachedMoveAnalysis']);
            if (cachedData.cachedMoveAnalysis) {
                const cached = cachedData.cachedMoveAnalysis;
                
                // Check if cache is recent (within last 10 seconds)
                const cacheAge = Date.now() - (cached._cached_at || 0);
                if (cacheAge < 10000) {
                    console.log('[Chess AI] Showing cached analysis');
                    this.displayMoveAnalysis(cached);
                    
                    // Update status to show it's complete
                    if (this.autoTrackStatus && cached.comparison) {
                        const emoji = cached.comparison.quality_display.emoji;
                        const label = cached.comparison.quality_display.label;
                        this.autoTrackStatus.textContent = `${emoji} ${label}! Click button to analyze another move.`;
                    }
                    
                    // Clear tracking state since we showed the result
                    this.resetButton();
                    return;
                } else {
                    // Cache too old, clear it
                    console.log('[Chess AI] Cache too old, clearing');
                    await chrome.storage.local.remove(['cachedMoveAnalysis']);
                }
            }
            
            // Check if move was made while popup was closed
            const currentFEN = await this.getCurrentFEN();
            
            if (currentFEN && currentFEN !== this.capturedFEN) {
                // Move detected!
                console.log('[Chess AI] Move detected while popup was closed');
                
                // Show loading status immediately
                if (this.autoTrackStatus) {
                    this.autoTrackStatus.textContent = '🔍 Analyzing your move...';
                    this.autoTrackStatus.style.color = '#3b82f6';
                }
                
                // Analyze immediately (this is when popup reopens)
                await this.analyzeDetectedMove(this.capturedFEN, currentFEN);
                
                // Reset state
                this.resetButton();
            } else {
                // Still waiting
                if (this.analyzeMyMoveButton) {
                    this.analyzeMyMoveButton.textContent = 'Waiting for your move... (Click to cancel)';
                    this.analyzeMyMoveButton.style.background = 'rgba(251, 191, 36, 0.3)';
                }
                
                if (this.autoTrackStatus) {
                    this.autoTrackStatus.textContent = '⏳ Still waiting for your move...';
                    this.autoTrackStatus.style.color = '#fbbf24';
                }
                
                // Resume checking
                this.trackingInterval = setInterval(() => this.checkForMove(), 1500);
            }
            
        } catch (error) {
            console.error('[Chess AI] Error restoring tracking state:', error);
        }
    }
    
    sendMessage(message) {
        return new Promise((resolve, reject) => {
            chrome.runtime.sendMessage(message, (response) => {
                if (chrome.runtime.lastError) {
                    reject(new Error(chrome.runtime.lastError.message));
                } else {
                    resolve(response || { success: false, error: 'No response' });
                }
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChessAIPopup();
});
