/**
 * Simple FEN Debug Tool - No Dependencies
 * This script will help debug FEN extraction without relying on extension classes
 */

class SimpleFENDebugger {
    constructor() {
        this.debugInfo = {
            url: window.location.href,
            timestamp: new Date().toISOString(),
            foundFens: [],
            domElements: {},
            windowVariables: {},
            errors: []
        };
    }

    async runSimpleDebug() {
        console.log('🔍 Starting simple FEN extraction debug...');
        
        try {
            // 1. Check basic page info
            this.debugBasicInfo();
            
            // 2. Search for FEN patterns in the page
            this.searchForFENPatterns();
            
            // 3. Check window variables
            this.checkWindowVariables();
            
            // 4. Analyze DOM structure
            this.analyzeDOMStructure();
            
            // 5. Generate report
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

    searchForFENPatterns() {
        console.log('\n🔍 Searching for FEN patterns...');
        
        const foundFens = [];
        
        // Search script tags
        const scripts = document.querySelectorAll('script');
        console.log(`Found ${scripts.length} script tags`);
        
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
        console.log(`Searching ${allElements.length} elements for FEN patterns...`);
        
        allElements.forEach((element, index) => {
            if (index > 1000) return; // Limit search
            
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
        
        // Search hidden inputs
        const hiddenInputs = document.querySelectorAll('input[type="hidden"]');
        console.log(`Found ${hiddenInputs.length} hidden inputs`);
        
        hiddenInputs.forEach((input, index) => {
            if (input.value && this.isValidFEN(input.value)) {
                foundFens.push({
                    source: `hidden input[${index}]`,
                    fen: input.value,
                    element: {
                        name: input.name,
                        id: input.id
                    }
                });
            }
        });
        
        this.debugInfo.foundFens = foundFens;
        console.log(`Found ${foundFens.length} valid FEN strings`);
        foundFens.forEach(fen => console.log('FEN:', fen.fen, 'from:', fen.source));
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
        
        console.log(`Found ${foundVariables.length} specific variables`);
        console.log(`Found ${globalChessVars.length} global chess variables`);
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
        
        this.debugInfo.domElements = {
            boards: foundBoards,
            pieces: foundPieces,
            puzzleElements: foundPuzzleElements
        };
        
        console.log('Found boards:', foundBoards.length);
        console.log('Found piece selectors:', foundPieces.length);
        console.log('Found puzzle elements:', foundPuzzleElements.length);
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
        console.log('\n📊 SIMPLE DEBUG REPORT');
        console.log('======================');
        
        console.log('\n🎯 SUMMARY:');
        console.log('Valid FEN strings found:', this.debugInfo.foundFens.length);
        console.log('Window variables found:', this.debugInfo.windowVariables.specific.length);
        console.log('Global chess variables found:', this.debugInfo.windowVariables.global.length);
        console.log('Board elements found:', this.debugInfo.domElements.boards.length);
        console.log('Piece elements found:', this.debugInfo.domElements.pieces.length);
        console.log('Puzzle elements found:', this.debugInfo.domElements.puzzleElements.length);
        
        console.log('\n📄 FEN STRINGS FOUND:');
        if (this.debugInfo.foundFens.length > 0) {
            this.debugInfo.foundFens.forEach((fen, index) => {
                console.log(`${index + 1}. ${fen.source}: ${fen.fen}`);
            });
        } else {
            console.log('No valid FEN strings found');
        }
        
        console.log('\n🌐 WINDOW VARIABLES:');
        if (this.debugInfo.windowVariables.specific.length > 0) {
            this.debugInfo.windowVariables.specific.forEach(variable => {
                console.log(`${variable.name}: ${variable.type}`);
                if (variable.fenValue) console.log(`  FEN: ${variable.fenValue}`);
                if (variable.positionValue) console.log(`  Position: ${variable.positionValue}`);
                if (variable.currentFenValue) console.log(`  Current FEN: ${variable.currentFenValue}`);
            });
        } else {
            console.log('No chess-related window variables found');
        }
        
        console.log('\n🏗️ DOM STRUCTURE:');
        console.log('Board elements:', this.debugInfo.domElements.boards.map(b => `${b.selector} (${b.count})`));
        console.log('Piece elements:', this.debugInfo.domElements.pieces.map(p => `${p.selector} (${p.count})`));
        console.log('Puzzle elements:', this.debugInfo.domElements.puzzleElements.map(p => `${p.selector} (${p.count})`));
        
        // Save to global variable for easy access
        window.simpleFenDebugReport = this.debugInfo;
        
        console.log('\n💾 Full debug report saved to window.simpleFenDebugReport');
        console.log('You can access it in the console with: window.simpleFenDebugReport');
        
        return this.debugInfo;
    }
}

// Auto-run the debugger
console.log('🚀 Simple FEN Debugger loaded');
console.log('Run: new SimpleFENDebugger().runSimpleDebug() to start debugging');

// Make it globally available
window.SimpleFENDebugger = SimpleFENDebugger;
