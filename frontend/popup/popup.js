class ChessAIPopup {
    constructor() {
        this.init();
    }
    
    async init() {
        console.log('[Chess AI Popup] Initializing...');
        
        this.setupUI();
        await this.loadStatus();
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
                    depth: 10,
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
            
            let message = `Analysis successful!\n\n`;
            message += `Turn: ${insights[0]}\n`;
            message += `Position: ${insights[1]}\n`;
            message += `Best move: ${bestMove.san} (${bestMove.move})\n`;
            message += `Score: ${bestMove.score.display}\n\n`;
            message += `Explanation: ${explanation.explanation}`;
            
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
                    depth: 10,
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
            
            let message = `Analysis successful!\n\n`;
            message += `Turn: ${insights[0]}\n`;
            message += `Position: ${insights[1]}\n`;
            message += `Best move: ${bestMove.san} (${bestMove.move})\n`;
            message += `Score: ${bestMove.score.display}\n\n`;
            message += `Explanation: ${explanation.explanation}`;
            
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
            
            // Inject comprehensive debug script
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: () => {
                    try {
                        // Helper function for FEN validation
                        function isValidChessFEN(fen) {
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
                            const turnPart = parts[1];
                            if (turnPart !== 'w' && turnPart !== 'b') return false;
                            
                            return true;
                        }
                        
                        const debugInfo = {
                            url: window.location.href,
                            foundFens: [],
                            windowVariables: [],
                            scriptContent: [],
                            dataAttributes: []
                        };
                    
                    // Check window variables
                    const possibleVars = [
                        'window.puzzle', 'window.game', 'window.board', 'window.chess',
                        'window.chesscom', 'window.puzzleData', 'window.gameData',
                        'window.position', 'window.fen'
                    ];
                    
                    possibleVars.forEach(varName => {
                        try {
                            const obj = eval(varName);
                            if (obj) {
                                debugInfo.windowVariables.push({
                                    name: varName,
                                    type: typeof obj,
                                    hasFen: !!obj.fen,
                                    hasPosition: !!obj.position,
                                    hasCurrentFen: !!obj.currentFen,
                                    fenValue: obj.fen || obj.position || obj.currentFen || 'N/A'
                                });
                                
                                if (obj.fen || obj.position || obj.currentFen) {
                                    const fen = obj.fen || obj.position || obj.currentFen;
                                    if (typeof fen === 'string' && fen.includes('/')) {
                                        debugInfo.foundFens.push({
                                            source: varName,
                                            fen: fen
                                        });
                                    }
                                }
                            }
                        } catch (e) {
                            // Variable doesn't exist
                        }
                    });
                    
                    // Check script tags for FEN patterns
                    const scripts = document.querySelectorAll('script');
                    scripts.forEach((script, index) => {
                        const content = script.textContent || script.innerHTML;
                        if (content && content.includes('/')) {
                            const fenMatches = content.match(/["']([rnbqkpRNBQKP1-8\/\s]+)["']/g);
                            if (fenMatches) {
                                fenMatches.forEach(match => {
                                    const potentialFen = match.replace(/["']/g, '').trim();
                                    if (potentialFen.includes('/') && potentialFen.includes(' ') && 
                                        (potentialFen.includes('w') || potentialFen.includes('b'))) {
                                        debugInfo.scriptContent.push({
                                            scriptIndex: index,
                                            fen: potentialFen
                                        });
                                        debugInfo.foundFens.push({
                                            source: `script[${index}]`,
                                            fen: potentialFen
                                        });
                                    }
                                });
                            }
                        }
                    });
                    
                    // Check data attributes
                    const allElements = document.querySelectorAll('*');
                    allElements.forEach((element, index) => {
                        if (index > 100) return; // Limit search
                        const attributes = element.attributes;
                        for (const attr of attributes) {
                            if (attr.value && attr.value.includes('/') && attr.value.includes(' ')) {
                                // Validate that this looks like a chess FEN
                                const potentialFen = attr.value.trim();
                                if (isValidChessFEN(potentialFen)) {
                                    debugInfo.dataAttributes.push({
                                        element: element.tagName,
                                        attribute: attr.name,
                                        value: attr.value
                                    });
                                    debugInfo.foundFens.push({
                                        source: `${element.tagName}[${attr.name}]`,
                                        fen: attr.value
                                    });
                                }
                            }
                        }
                    });
                    
                        return debugInfo;
                    } catch (error) {
                        return {
                            error: error.message,
                            url: window.location.href,
                            foundFens: [],
                            windowVariables: [],
                            scriptContent: [],
                            dataAttributes: []
                        };
                    }
                }
            });
            
            const debugInfo = results[0]?.result;
            
            // Check if there was an error in the debug script
            if (debugInfo && debugInfo.error) {
                this.showError(`Debug script error: ${debugInfo.error}`);
                return;
            }
            
            if (debugInfo && debugInfo.foundFens.length > 0) {
                let message = 'Found FEN strings:\n\n';
                debugInfo.foundFens.forEach((fen, index) => {
                    message += `${index + 1}. ${fen.source}: ${fen.fen}\n`;
                });
                
                // Auto-fill the first valid FEN
                if (debugInfo.foundFens.length > 0) {
                    this.manualFenInput.value = debugInfo.foundFens[0].fen;
                }
                
                this.showMessage(message, 'success');
            } else {
                let message = 'No FEN strings found. Debug info:\n\n';
                if (debugInfo) {
                    message += `Window variables checked: ${debugInfo.windowVariables?.length || 0}\n`;
                    message += `Scripts checked: ${debugInfo.scriptContent?.length || 0}\n`;
                    message += `Data attributes checked: ${debugInfo.dataAttributes?.length || 0}\n\n`;
                } else {
                    message += 'Debug script failed to execute properly.\n\n';
                }
                message += 'Try using Method 1 or 2 from the instructions.';
                
                this.showMessage(message, 'error');
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
