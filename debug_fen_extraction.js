/**
 * Comprehensive FEN Extraction Debug Tool
 * This script will help debug why the extension is extracting invalid FEN
 */

class FENDebugger {
    constructor() {
        this.debugInfo = {
            url: window.location.href,
            timestamp: new Date().toISOString(),
            methods: {},
            domStructure: {},
            windowVariables: {},
            errors: []
        };
    }

    async runFullDebug() {
        console.log('🔍 Starting comprehensive FEN extraction debug...');
        
        try {
            // 1. Check basic page info
            this.debugBasicInfo();
            
            // 2. Test each extraction method
            await this.testAllExtractionMethods();
            
            // 3. Analyze DOM structure
            this.analyzeDOMStructure();
            
            // 4. Check window variables
            this.checkWindowVariables();
            
            // 5. Look for FEN patterns in page source
            this.searchPageSource();
            
            // 6. Generate report
            this.generateReport();
            
        } catch (error) {
            console.error('❌ Debug failed:', error);
            this.debugInfo.errors.push(error.message);
        }
    }

    debugBasicInfo() {
        console.log('📋 Basic Page Info:');
        console.log('URL:', window.location.href);
        console.log('Title:', document.title);
        console.log('Hostname:', window.location.hostname);
        console.log('Pathname:', window.location.pathname);
        
        this.debugInfo.basicInfo = {
            url: window.location.href,
            title: document.title,
            hostname: window.location.hostname,
            pathname: window.location.pathname
        };
    }

    async testAllExtractionMethods() {
        console.log('🧪 Testing all extraction methods...');
        
        const extractor = new ChessDOMExtractor();
        
        // Test each method individually
        const methods = [
            { name: 'extractChessComPuzzleFEN', fn: () => extractor.extractChessComPuzzleFEN() },
            { name: 'extractChessComAlternative', fn: () => extractor.extractChessComAlternative() },
            { name: 'extractFromChessComData', fn: () => extractor.extractFromChessComData() },
            { name: 'extractFromJavaScriptVariables', fn: () => extractor.extractFromJavaScriptVariables() },
            { name: 'extractFromPageSource', fn: () => extractor.extractFromPageSource() },
            { name: 'extractCurrentFEN', fn: () => extractor.extractCurrentFEN() }
        ];

        for (const method of methods) {
            try {
                console.log(`\n🔧 Testing method: ${method.name}`);
                const result = method.fn();
                console.log(`Result:`, result);
                
                this.debugInfo.methods[method.name] = {
                    success: true,
                    result: result,
                    isValid: this.isValidFEN(result)
                };
                
                if (result && this.isValidFEN(result)) {
                    console.log(`✅ ${method.name} returned valid FEN!`);
                } else if (result) {
                    console.log(`⚠️ ${method.name} returned invalid FEN:`, result);
                } else {
                    console.log(`❌ ${method.name} returned null/undefined`);
                }
                
            } catch (error) {
                console.error(`❌ ${method.name} failed:`, error);
                this.debugInfo.methods[method.name] = {
                    success: false,
                    error: error.message
                };
            }
        }
    }

    analyzeDOMStructure() {
        console.log('\n🏗️ Analyzing DOM structure...');
        
        // Check for board elements
        const boardSelectors = [
            '.board', '#board-vs-personalities-board', '[id*="board-"]',
            '.chess-board', '.puzzle-board', '[class*="board"]',
            '[class*="chess"]', 'canvas', 'svg'
        ];
        
        const foundBoards = [];
        boardSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                foundBoards.push({
                    selector: selector,
                    count: elements.length,
                    elements: Array.from(elements).map(el => ({
                        tagName: el.tagName,
                        id: el.id,
                        classes: Array.from(el.classList),
                        children: el.children.length
                    }))
                });
            }
        });
        
        // Check for piece elements
        const pieceSelectors = [
            '[class*="piece"]', '.piece', '[class*="chess-piece"]',
            '[data-piece]', '[class*="wP"]', '[class*="bP"]',
            '[class*="wK"]', '[class*="bK"]', '[class*="wQ"]', '[class*="bQ"]',
            '[class*="wR"]', '[class*="bR"]', '[class*="wB"]', '[class*="bB"]',
            '[class*="wN"]', '[class*="bN"]'
        ];
        
        const foundPieces = [];
        pieceSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                foundPieces.push({
                    selector: selector,
                    count: elements.length,
                    sampleClasses: Array.from(elements[0].classList)
                });
            }
        });
        
        // Check for puzzle-specific elements
        const puzzleSelectors = [
            '.puzzle-controls', '.puzzle-info', '.instructions',
            '.puzzle-details', '.puzzle-ui', '[class*="puzzle"]'
        ];
        
        const foundPuzzleElements = [];
        puzzleSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                foundPuzzleElements.push({
                    selector: selector,
                    count: elements.length,
                    text: elements[0].textContent?.substring(0, 100)
                });
            }
        });
        
        this.debugInfo.domStructure = {
            boards: foundBoards,
            pieces: foundPieces,
            puzzleElements: foundPuzzleElements
        };
        
        console.log('Found boards:', foundBoards.length);
        console.log('Found piece selectors:', foundPieces.length);
        console.log('Found puzzle elements:', foundPuzzleElements.length);
    }

    checkWindowVariables() {
        console.log('\n🌐 Checking window variables...');
        
        const possibleVariables = [
            'window.chessBoard', 'window.board', 'window.game', 'window.puzzle',
            'window.position', 'window.fen', 'window.chess', 'window.chesscom',
            'window.puzzleData', 'window.gameData', 'window.chesscomData'
        ];
        
        const foundVariables = [];
        
        possibleVariables.forEach(varName => {
            try {
                const obj = eval(varName);
                if (obj) {
                    const info = {
                        name: varName,
                        type: typeof obj,
                        hasFen: !!obj.fen,
                        hasPosition: !!obj.position,
                        hasCurrentFen: !!obj.currentFen,
                        hasBoard: !!obj.board,
                        keys: Object.keys(obj).slice(0, 10) // First 10 keys
                    };
                    
                    if (obj.fen) info.fenValue = obj.fen;
                    if (obj.position) info.positionValue = obj.position;
                    if (obj.currentFen) info.currentFenValue = obj.currentFen;
                    
                    foundVariables.push(info);
                    console.log(`Found variable: ${varName}`, info);
                }
            } catch (e) {
                // Variable doesn't exist
            }
        });
        
        // Also check for any global variables that might contain chess data
        const globalChessVars = [];
        for (const key in window) {
            if (key.toLowerCase().includes('chess') || 
                key.toLowerCase().includes('puzzle') || 
                key.toLowerCase().includes('game')) {
                try {
                    const value = window[key];
                    if (value && typeof value === 'object') {
                        globalChessVars.push({
                            name: key,
                            type: typeof value,
                            keys: Object.keys(value).slice(0, 5)
                        });
                    }
                } catch (e) {
                    // Skip
                }
            }
        }
        
        this.debugInfo.windowVariables = {
            specific: foundVariables,
            global: globalChessVars
        };
    }

    searchPageSource() {
        console.log('\n📄 Searching page source for FEN patterns...');
        
        const foundFens = [];
        
        // Search script tags
        const scripts = document.querySelectorAll('script');
        scripts.forEach((script, index) => {
            const content = script.textContent || script.innerHTML;
            if (content && content.includes('/')) {
                // Look for FEN-like patterns
                const fenMatches = content.match(/["']([rnbqkpRNBQKP1-8\/\s]+)["']/g);
                if (fenMatches) {
                    fenMatches.forEach(match => {
                        const potentialFen = match.replace(/["']/g, '').trim();
                        if (this.isValidFEN(potentialFen)) {
                            foundFens.push({
                                source: `script[${index}]`,
                                fen: potentialFen,
                                context: content.substring(content.indexOf(match) - 50, content.indexOf(match) + 100)
                            });
                        }
                    });
                }
            }
        });
        
        // Search data attributes
        const allElements = document.querySelectorAll('*');
        allElements.forEach((element, index) => {
            if (index > 500) return; // Limit search
            
            const attributes = element.attributes;
            for (const attr of attributes) {
                if (attr.value && attr.value.includes('/') && this.isValidFEN(attr.value)) {
                    foundFens.push({
                        source: `${element.tagName}[${attr.name}]`,
                        fen: attr.value,
                        element: {
                            tagName: element.tagName,
                            id: element.id,
                            classes: Array.from(element.classList)
                        }
                    });
                }
            }
        });
        
        this.debugInfo.foundFens = foundFens;
        console.log('Found FEN strings:', foundFens.length);
        foundFens.forEach(fen => console.log('FEN:', fen.fen, 'from:', fen.source));
    }

    isValidFEN(fen) {
        if (!fen || typeof fen !== 'string') return false;
        
        const parts = fen.trim().split(' ');
        if (parts.length < 2) return false;
        
        const boardPart = parts[0];
        const turnPart = parts[1];
        
        // Check if board part looks like a FEN board
        if (!boardPart.includes('/')) return false;
        if (boardPart.length < 10) return false;
        
        // Check if turn part is valid
        if (turnPart !== 'w' && turnPart !== 'b') return false;
        
        // Check if it has exactly 8 ranks
        const ranks = boardPart.split('/');
        if (ranks.length !== 8) return false;
        
        // Check each rank sums to 8
        for (const rank of ranks) {
            let sum = 0;
            for (const char of rank) {
                if (char >= '1' && char <= '8') {
                    sum += parseInt(char);
                } else if ('rnbqkpRNBQKP'.includes(char)) {
                    sum += 1;
                } else {
                    return false; // Invalid character
                }
            }
            if (sum !== 8) return false;
        }
        
        return true;
    }

    generateReport() {
        console.log('\n📊 DEBUG REPORT');
        console.log('================');
        
        console.log('\n🎯 SUMMARY:');
        const validMethods = Object.entries(this.debugInfo.methods)
            .filter(([name, info]) => info.success && info.isValid)
            .map(([name]) => name);
        
        const invalidMethods = Object.entries(this.debugInfo.methods)
            .filter(([name, info]) => info.success && info.result && !info.isValid)
            .map(([name, info]) => ({ name, result: info.result }));
        
        console.log('✅ Methods returning valid FEN:', validMethods);
        console.log('⚠️ Methods returning invalid FEN:', invalidMethods);
        console.log('❌ Methods failing:', Object.entries(this.debugInfo.methods)
            .filter(([name, info]) => !info.success)
            .map(([name, info]) => ({ name, error: info.error })));
        
        console.log('\n🏗️ DOM STRUCTURE:');
        console.log('Boards found:', this.debugInfo.domStructure.boards.length);
        console.log('Piece selectors found:', this.debugInfo.domStructure.pieces.length);
        console.log('Puzzle elements found:', this.debugInfo.domStructure.puzzleElements.length);
        
        console.log('\n🌐 WINDOW VARIABLES:');
        console.log('Specific variables found:', this.debugInfo.windowVariables.specific.length);
        console.log('Global chess variables found:', this.debugInfo.windowVariables.global.length);
        
        console.log('\n📄 FEN STRINGS FOUND:');
        console.log('Total FEN strings found:', this.debugInfo.foundFens.length);
        
        // Save to global variable for easy access
        window.fenDebugReport = this.debugInfo;
        
        console.log('\n💾 Full debug report saved to window.fenDebugReport');
        console.log('You can access it in the console with: window.fenDebugReport');
        
        return this.debugInfo;
    }
}

// Auto-run the debugger
console.log('🚀 FEN Extraction Debugger loaded');
console.log('Run: new FENDebugger().runFullDebug() to start debugging');
console.log('Or use: const fenDebug = new FENDebugger(); await fenDebug.runFullDebug();');

// Make it globally available
window.FENDebugger = FENDebugger;
