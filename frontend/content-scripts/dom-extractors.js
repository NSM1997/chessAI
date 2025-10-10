/**
 * Chess DOM Extractor - Clean Working Version
 */
class ChessDOMExtractor {
    constructor() {
        this.lastFEN = null;
        this.lastUpdateTime = 0;
        console.log('[Chess AI] DOM Extractor initialized');
    }

    isValidChessContext() {
        const url = window.location.href;
        const pathname = window.location.pathname;
        
        const validContexts = [
            '/play/',
            '/game/',
            '/puzzles/',
            '/analysis/',
            '/live/',
            '/daily/'
        ];
        
        const isValidUrl = validContexts.some(context => pathname.includes(context));
        // Try multiple selectors to find the board
        const boardSelectors = [
            '.board',
            '#board-vs-personalities-board',
            '[id*="board-"]',
            '.chess-board',
            '.puzzle-board',
            '[class*="board"]',
            '[class*="chess"]',
            'canvas',
            'svg'
        ];
        
        let hasActiveBoard = false;
        for (const selector of boardSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                hasActiveBoard = true;
                console.log('[Chess AI] Found board with selector:', selector);
                break;
            }
        }
        
        // For puzzle pages, we don't need all game UI elements
        const isPuzzlePage = pathname.includes('/puzzles/');
        let hasGameUI = false;
        
        if (isPuzzlePage) {
            // For puzzles, just check for puzzle-specific elements
            hasGameUI = document.querySelector('.puzzle-controls, .puzzle-info, .instructions, .puzzle-details, .puzzle-ui, [class*="puzzle"]');
        } else {
            // For games, check for standard game UI elements
            hasGameUI = document.querySelector('.clock, .player-info, .move-list, .game-controls');
        }
        
        // If we have a valid URL and board, and either game UI or it's a puzzle page, it's valid
        let isValid = isValidUrl && hasActiveBoard && (hasGameUI || isPuzzlePage);
        
        // For puzzle pages, be even more permissive - if we're on a puzzle URL, allow it
        if (!isValid && isPuzzlePage && isValidUrl) {
            console.log('[Chess AI] Puzzle page detected, allowing context even without board detection');
            isValid = true;
        }
        
        console.log('[Chess AI] Context check:', { 
            isValidUrl, 
            hasActiveBoard: !!hasActiveBoard, 
            hasGameUI: !!hasGameUI, 
            isPuzzlePage,
            isValid 
        });
        return isValid;
    }

    detectCurrentTurn() {
        try {
            const whiteActive = document.querySelector('.clock-player-turn.clock-white, .player-white.player-turn, [class*="white"][class*="turn"]');
            const blackActive = document.querySelector('.clock-player-turn.clock-black, .player-black.player-turn, [class*="black"][class*="turn"]');
            
            if (whiteActive && !blackActive) return 'w';
            if (blackActive && !whiteActive) return 'b';
            
            const puzzleText = document.querySelector('.puzzle-info, .instructions, .puzzle-details');
            if (puzzleText) {
                const text = puzzleText.textContent.toLowerCase();
                if (text.includes('white to move') || text.includes('white to play')) return 'w';
                if (text.includes('black to move') || text.includes('black to play')) return 'b';
            }
            
            return 'w';
        } catch (error) {
            console.log('[Chess AI] Turn detection failed:', error);
            return 'w';
        }
    }

    extractCurrentFEN() {
        if (!this.isValidChessContext()) {
            console.log('[Chess AI] Not in valid chess context');
            return null;
        }
        
        if (window.location.hostname.includes('chess.com')) {
            // Try multiple extraction methods
            let fen = this.extractChessComPuzzleFEN();
            if (!fen) {
                fen = this.extractChessComAlternative();
            }
            if (!fen) {
                fen = this.extractFromChessComData();
            }
            if (!fen) {
                fen = this.extractFromJavaScriptVariables();
            }
            if (!fen) {
                fen = this.extractFromPageSource();
            }
            console.log('[Chess AI] Extracted FEN:', fen);
            return fen;
        }
        return null;
    }

    extractChessComPuzzleFEN() {
        console.log('[Chess AI] Using specialized Chess.com puzzle extractor');
        
        // Use the working Chess.com puzzle extraction method
        return this.extractChessComPuzzlePosition();
    }

    extractChessComPuzzlePosition() {
        console.log('[Chess AI] Extracting puzzle FEN using DOM positioning...');
        
        try {
            // Find the main board - try multiple selectors
            let board = document.querySelector('wc-chess-board.board');
            if (!board) {
                board = document.querySelector('wc-chess-board');
            }
            if (!board) {
                board = document.querySelector('.board');
            }
            if (!board) {
                board = document.querySelector('[id*="board"]');
            }
            if (!board) {
                board = document.querySelector('[class*="board"]');
            }
            
            if (!board) {
                console.log('[Chess AI] No board found with any selector');
                // Try to find any element that might contain pieces
                const pieces = document.querySelectorAll('.piece');
                if (pieces.length > 0) {
                    console.log(`[Chess AI] Found ${pieces.length} pieces but no board element. Using document body as reference.`);
                    board = document.body;
                } else {
                    console.log('[Chess AI] No pieces found either');
                    return null;
                }
            }

            // Get board dimensions and position
            const boardRect = board.getBoundingClientRect();
            console.log(`[Chess AI] Board element: ${board.tagName} with class "${board.className}"`);
            console.log(`[Chess AI] Board dimensions: ${boardRect.width}x${boardRect.height} at (${boardRect.left}, ${boardRect.top})`);

            // Find all pieces
            const pieces = document.querySelectorAll('.piece');
            console.log(`[Chess AI] Found ${pieces.length} pieces`);

            if (pieces.length === 0) {
                console.log('[Chess AI] No pieces found');
                return null;
            }

            // Create 8x8 board array
            const boardArray = Array(8).fill().map(() => Array(8).fill(''));

            // Calculate square size - if board has no dimensions, estimate from pieces
            let squareWidth, squareHeight;
            if (boardRect.width > 0 && boardRect.height > 0) {
                squareWidth = boardRect.width / 8;
                squareHeight = boardRect.height / 8;
            } else {
                // Estimate square size from piece positions
                const piecePositions = Array.from(pieces).map(p => p.getBoundingClientRect());
                const minX = Math.min(...piecePositions.map(p => p.left));
                const maxX = Math.max(...piecePositions.map(p => p.right));
                const minY = Math.min(...piecePositions.map(p => p.top));
                const maxY = Math.max(...piecePositions.map(p => p.bottom));
                
                squareWidth = (maxX - minX) / 8;
                squareHeight = (maxY - minY) / 8;
                
                console.log(`[Chess AI] Estimated board from pieces: ${maxX - minX}x${maxY - minY}`);
            }

            console.log(`[Chess AI] Square size: ${squareWidth}x${squareHeight}`);

            // Parse each piece
            pieces.forEach((piece, index) => {
                const classes = Array.from(piece.classList);
                console.log(`[Chess AI] Piece ${index}:`, classes);

                // Find piece type
                let pieceType = null;
                for (const cls of classes) {
                    if (cls.match(/^[wb][prnbqk]$/)) {
                        pieceType = cls;
                        break;
                    }
                }

                if (pieceType) {
                    // Get piece position relative to board
                    const pieceRect = piece.getBoundingClientRect();
                    const relativeX = pieceRect.left - boardRect.left;
                    const relativeY = pieceRect.top - boardRect.top;

                    // Calculate which square this piece is in
                    let file = Math.floor(relativeX / squareWidth);
                    let rank = Math.floor(relativeY / squareHeight);

                    // If using document.body as reference, we need to normalize coordinates
                    if (board === document.body) {
                        // Find the actual board area by looking at piece distribution
                        const allPieceRects = Array.from(pieces).map(p => p.getBoundingClientRect());
                        const minX = Math.min(...allPieceRects.map(p => p.left));
                        const maxX = Math.max(...allPieceRects.map(p => p.right));
                        const minY = Math.min(...allPieceRects.map(p => p.top));
                        const maxY = Math.max(...allPieceRects.map(p => p.bottom));
                        
                        // Normalize to 0-7 range
                        file = Math.floor((pieceRect.left - minX) / ((maxX - minX) / 8));
                        rank = Math.floor((pieceRect.top - minY) / ((maxY - minY) / 8));
                    }

                    // Ensure coordinates are within bounds
                    if (file >= 0 && file < 8 && rank >= 0 && rank < 8) {
                        // Convert to FEN coordinates (rank 0 = rank 8 in FEN)
                        const fenRank = rank; // FEN ranks go from 8 to 1
                        const fenFile = file;     // FEN files go from a to h

                        // Convert piece notation (wp -> P, bp -> p, etc.)
                        const pieceChar = pieceType[0] === 'w' ? pieceType[1].toUpperCase() : pieceType[1].toLowerCase();
                        boardArray[fenRank][fenFile] = pieceChar;
                        console.log(`[Chess AI] Placed ${pieceChar} at file ${file}, rank ${rank} (FEN: ${String.fromCharCode(97 + fenFile)}${8 - fenRank})`);
                    } else {
                        console.log(`[Chess AI] Piece ${pieceType} at invalid coordinates: file ${file}, rank ${rank}`, 'warn');
                    }
                }
            });

            // Convert board array to FEN
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

            // Try to infer active color (turn)
            let activeColor = 'w'; // Default to white
            const turnIndicator = document.querySelector('.puzzle-turn-indicator, .player-turn-bottom, .player-turn-top');
            if (turnIndicator) {
                if (turnIndicator.classList.contains('player-turn-bottom') || turnIndicator.classList.contains('player-turn-white')) {
                    activeColor = 'w';
                } else if (turnIndicator.classList.contains('player-turn-top') || turnIndicator.classList.contains('player-turn-black')) {
                    activeColor = 'b';
                }
            }

            // For puzzles, use default values for other FEN components
            const castling = 'KQkq';
            const enPassant = '-';
            const halfmoveClock = 0;
            const fullmoveNumber = 1;

            const finalFen = `${fenBoard} ${activeColor} ${castling} ${enPassant} ${halfmoveClock} ${fullmoveNumber}`;
            console.log('[Chess AI] Generated FEN:', finalFen);
            
            // Visual representation for debugging
            this.drawBoardInConsole(boardArray);
            
            return finalFen;
        } catch (error) {
            console.error('[Chess AI] Error extracting puzzle position:', error);
            return null;
        }
    }

    drawBoardInConsole(boardArray) {
        console.log('[Chess AI] Board visualization:');
        console.log('[Chess AI]    a b c d e f g h');
        for (let i = 0; i < 8; i++) {
            let row = `${8 - i} `;
            for (let j = 0; j < 8; j++) {
                const piece = boardArray[i][j];
                row += piece === '' ? '. ' : piece + ' ';
            }
            row += `${8 - i}`;
            console.log('[Chess AI] ' + row);
        }
        console.log('[Chess AI]    a b c d e f g h');
    }

    extractRealChessComPosition() {
        const board = {};
        
        // Try multiple selectors for pieces
        const pieceSelectors = [
            '[class*="piece"]',
            '.piece',
            '[class*="chess-piece"]',
            '.chess-piece'
        ];
        
        let pieces = [];
        for (const selector of pieceSelectors) {
            pieces = document.querySelectorAll(selector);
            if (pieces.length > 0) break;
        }
        
        console.log('[Chess AI] Extracting from', pieces.length, 'pieces');
        
        pieces.forEach((piece, index) => {
            const list = Array.from(piece.classList);
            let pieceType = '', pieceColor = '', squareClass = '';
            
            // Try different class patterns
            list.forEach(cls => {
                // Standard pattern: wP, bK, etc.
                if (cls.match(/^[wb][prnbqk]$/)) {
                    pieceColor = cls[0];
                    pieceType = cls[1];
                }
                // Alternative pattern: piece-wP, piece-bK, etc.
                else if (cls.match(/^piece-[wb][prnbqk]$/)) {
                    const match = cls.match(/^piece-([wb])([prnbqk])$/);
                    if (match) {
                        pieceColor = match[1];
                        pieceType = match[2];
                    }
                }
                // Square position
                if (cls.startsWith('square-')) {
                    squareClass = cls.replace('square-', '');
                }
            });
            
            // Try to get position from parent element or data attributes
            if (!squareClass) {
                const parent = piece.parentElement;
                if (parent) {
                    const parentClasses = Array.from(parent.classList);
                    parentClasses.forEach(cls => {
                        if (cls.startsWith('square-')) {
                            squareClass = cls.replace('square-', '');
                        }
                    });
                }
            }
            
            // Try data attributes
            if (!squareClass && piece.dataset.square) {
                squareClass = piece.dataset.square;
            }
            
            console.log(`[Chess AI] Piece ${index}:`, {
                classes: list,
                pieceType,
                pieceColor,
                squareClass,
                element: piece
            });
            
            if (pieceType && pieceColor && squareClass) {
                const square = this.decodeSquare(squareClass);
                if (square) {
                    board[square] = pieceColor === 'w' ? pieceType.toUpperCase() : pieceType;
                    console.log(`[Chess AI] Mapped ${pieceColor}${pieceType} to ${square}`);
                }
            }
        });
        
        console.log('[Chess AI] Extracted board:', board);
        
        if (Object.keys(board).length < 2) {
            console.log('[Chess AI] Too few pieces extracted, trying alternative method');
            return this.tryAlternativeExtraction();
        }
        
        return this.boardToFEN(board);
    }

    tryAlternativeExtraction() {
        console.log('[Chess AI] Trying alternative extraction method');
        
        // Look for any elements that might contain piece information
        const allElements = document.querySelectorAll('*');
        const board = {};
        
        allElements.forEach((element, index) => {
            if (index > 1000) return; // Limit search to avoid performance issues
            
            const classes = Array.from(element.classList);
            const hasPieceClass = classes.some(cls => 
                cls.includes('piece') || 
                cls.match(/^[wb][prnbqk]$/) ||
                cls.match(/^piece-[wb][prnbqk]$/)
            );
            
            if (hasPieceClass) {
                console.log('[Chess AI] Found potential piece element:', {
                    tagName: element.tagName,
                    classes: classes,
                    id: element.id,
                    parentClasses: element.parentElement ? Array.from(element.parentElement.classList) : []
                });
            }
        });
        
        return null; // Return null if alternative method fails
    }

    extractChessComAlternative() {
        console.log('[Chess AI] Trying Chess.com alternative extraction');
        
        // Look for any div with piece classes
        const allDivs = document.querySelectorAll('div');
        const board = {};
        
        allDivs.forEach(div => {
            const classes = Array.from(div.classList);
            let pieceType = '', pieceColor = '', squareClass = '';
            
            // Check for piece classes
            classes.forEach(cls => {
                // Standard piece classes: wP, bK, etc.
                if (cls.match(/^[wb][prnbqk]$/)) {
                    pieceColor = cls[0];
                    pieceType = cls[1];
                }
                // Square classes
                if (cls.startsWith('square-')) {
                    squareClass = cls.replace('square-', '');
                }
            });
            
            if (pieceType && pieceColor && squareClass) {
                const square = this.decodeSquare(squareClass);
                if (square) {
                    board[square] = pieceColor === 'w' ? pieceType.toUpperCase() : pieceType;
                }
            }
        });
        
        if (Object.keys(board).length >= 2) {
            return this.boardToFEN(board);
        }
        
        return null;
    }

    extractFromChessComData() {
        console.log('[Chess AI] Trying to extract from Chess.com data attributes');
        
        // Look for data attributes that might contain position info
        const possibleElements = [
            document.querySelector('[data-fen]'),
            document.querySelector('[data-position]'),
            document.querySelector('[data-board]'),
            document.querySelector('.board'),
            document.querySelector('#board-vs-personalities-board')
        ];
        
        for (const element of possibleElements) {
            if (element) {
                // Check data attributes
                const fen = element.dataset.fen || element.dataset.position || element.dataset.board;
                if (fen && fen.includes('/')) {
                    console.log('[Chess AI] Found FEN in data attribute:', fen);
                    return fen.trim();
                }
                
                // Check if element has position info in its structure
                const children = element.querySelectorAll('*');
                for (const child of children) {
                    const classes = Array.from(child.classList);
                    if (classes.some(cls => cls.match(/^[wb][prnbqk]$/))) {
                        console.log('[Chess AI] Found piece element, trying to extract position');
                        return this.extractRealChessComPosition();
                    }
                }
            }
        }
        
        return null;
    }

    extractFromJavaScriptVariables() {
        console.log('[Chess AI] Trying to extract from JavaScript variables');
        
        try {
            // Chess.com often stores position data in global variables
            const possibleVariables = [
                'window.chessBoard',
                'window.board',
                'window.game',
                'window.puzzle',
                'window.position',
                'window.fen',
                'window.chess',
                'window.chesscom',
                'window.puzzleData',
                'window.gameData'
            ];
            
            for (const varName of possibleVariables) {
                try {
                    const obj = eval(varName);
                    if (obj) {
                        console.log('[Chess AI] Checking variable:', varName, obj);
                        
                        // Look for FEN in the object
                        if (obj.fen && typeof obj.fen === 'string') {
                            console.log('[Chess AI] Found FEN in variable:', varName, obj.fen);
                            return obj.fen;
                        }
                        if (obj.position && typeof obj.position === 'string') {
                            console.log('[Chess AI] Found position in variable:', varName, obj.position);
                            return obj.position;
                        }
                        if (obj.board && obj.board.fen) {
                            console.log('[Chess AI] Found board.fen in variable:', varName, obj.board.fen);
                            return obj.board.fen;
                        }
                        if (obj.currentFen) {
                            console.log('[Chess AI] Found currentFen in variable:', varName, obj.currentFen);
                            return obj.currentFen;
                        }
                        if (obj.fenString) {
                            console.log('[Chess AI] Found fenString in variable:', varName, obj.fenString);
                            return obj.fenString;
                        }
                    }
                } catch (e) {
                    // Variable doesn't exist, continue
                }
            }
            
            // Try to find any global variable that contains FEN-like data
            for (const key in window) {
                try {
                    const value = window[key];
                    if (typeof value === 'string' && value.includes('/') && value.includes(' ')) {
                        // Check if it looks like a FEN
                        const parts = value.split(' ');
                        if (parts.length >= 2 && parts[0].includes('/')) {
                            console.log('[Chess AI] Found potential FEN in window variable:', key, value);
                            return value;
                        }
                    }
                } catch (e) {
                    // Skip this variable
                }
            }
            
            // Try to access Chess.com's internal data structures
            try {
                // Look for React component data
                const reactRoot = document.querySelector('#root, #app, [data-reactroot]');
                if (reactRoot) {
                    console.log('[Chess AI] Found React root, checking for internal data');
                    // This is a more aggressive approach to find Chess.com's internal state
                    const allProps = Object.getOwnPropertyNames(window);
                    for (const prop of allProps) {
                        if (prop.includes('chess') || prop.includes('puzzle') || prop.includes('game')) {
                            try {
                                const obj = window[prop];
                                if (obj && typeof obj === 'object') {
                                    console.log('[Chess AI] Checking property:', prop, obj);
                                    if (obj.fen || obj.position || obj.currentFen) {
                                        const fen = obj.fen || obj.position || obj.currentFen;
                                        if (typeof fen === 'string' && fen.includes('/')) {
                                            console.log('[Chess AI] Found FEN in property:', prop, fen);
                                            return fen;
                                        }
                                    }
                                }
                            } catch (e) {
                                // Skip this property
                            }
                        }
                    }
                }
            } catch (error) {
                console.log('[Chess AI] Error accessing React data:', error);
            }
            
        } catch (error) {
            console.log('[Chess AI] Error accessing JavaScript variables:', error);
        }
        
            return null;
    }

    extractFromPageSource() {
        console.log('[Chess AI] Trying to extract from page source and hidden elements');
        
        try {
            // Look for FEN in script tags
            const scripts = document.querySelectorAll('script');
            for (const script of scripts) {
                const content = script.textContent || script.innerHTML;
                if (content && content.includes('/')) {
                    // Look for FEN patterns in script content
                    const fenMatches = content.match(/["']([rnbqkpRNBQKP1-8\/\s]+)["']/g);
                    if (fenMatches) {
                        for (const match of fenMatches) {
                            const potentialFen = match.replace(/["']/g, '').trim();
                            if (this.isValidFEN(potentialFen)) {
                                console.log('[Chess AI] Found FEN in script:', potentialFen);
                                return potentialFen;
                            }
                        }
                    }
                }
            }
            
            // Look for FEN in data attributes of all elements
            const allElements = document.querySelectorAll('*');
            for (const element of allElements) {
                const attributes = element.attributes;
                for (const attr of attributes) {
                    if (attr.value && attr.value.includes('/') && this.isValidFEN(attr.value)) {
                        console.log('[Chess AI] Found FEN in attribute:', attr.name, attr.value);
                        return attr.value;
                    }
                }
            }
            
            // Look for FEN in hidden input fields
            const hiddenInputs = document.querySelectorAll('input[type="hidden"]');
            for (const input of hiddenInputs) {
                if (input.value && this.isValidFEN(input.value)) {
                    console.log('[Chess AI] Found FEN in hidden input:', input.name, input.value);
                    return input.value;
                }
            }
            
        } catch (error) {
            console.log('[Chess AI] Error extracting from page source:', error);
        }
        
        return null;
    }

    isValidFEN(fen) {
        if (!fen || typeof fen !== 'string') return false;
        
        const parts = fen.trim().split(' ');
        if (parts.length < 2) return false;
        
        const boardPart = parts[0];
        const turnPart = parts[1];
        
        // Check if board part looks like a FEN board
        if (!boardPart.includes('/')) return false;
        if (boardPart.length < 10) return false; // Minimum FEN length
        
        // Check if turn part is valid
        if (turnPart !== 'w' && turnPart !== 'b') return false;
        
        return true;
    }

    decodeSquare(squareNum) {
        const num = parseInt(squareNum);
        if (num < 11 || num > 88) return null;
        
        const y = (num % 10);
        const x = Math.floor(num / 10);
        
        const file = 8 - y;
        const rank = x;
        
        if (file < 0 || file > 7 || rank < 1 || rank > 8) return null;
        
        const fileChar = String.fromCharCode(97 + file);
        return fileChar + rank;
    }

    boardToFEN(board) {
        let fen = '';
        
        for (let rank = 8; rank >= 1; rank--) {
            let row = '';
            let empty = 0;
            
            for (let file = 0; file < 8; file++) {
                const sq = String.fromCharCode(97 + file) + rank;
                if (board[sq]) {
                    if (empty) { row += empty; empty = 0; }
                    row += board[sq];
                } else {
                    empty++;
                }
            }
            if (empty) row += empty;
            fen += row + (rank > 1 ? '/' : '');
        }
        
        const currentTurn = this.detectCurrentTurn();
        fen += ' ' + currentTurn + ' KQkq - 0 1';
        
        console.log('[Chess AI] Generated FEN:', fen);
        return fen;
    }

    getPositionInfo(fen) {
        if (!fen) return { isWhiteTurn: true, moveNumber: 1, toMove: 'White' };
        
        const parts = fen.split(' ');
        const isWhiteTurn = parts[1] === 'w';
        const moveNumber = parseInt(parts[5]) || 1;
        
        return {
            isWhiteTurn: isWhiteTurn,
            moveNumber: moveNumber,
            toMove: isWhiteTurn ? 'White' : 'Black'
        };
    }

    getSiteInfo() {
        const hostname = window.location.hostname;
        const pathname = window.location.pathname;
        
        let context = 'unknown';
        if (pathname.includes('puzzle')) context = 'puzzle';
        else if (pathname.includes('play') || pathname.includes('game')) context = 'game';
        else if (pathname.includes('analysis')) context = 'analysis';
        
        return {
            hostname: hostname,
            context: context,
            url: window.location.href,
            supported: hostname.includes('chess.com') && this.isValidChessContext()
        };
    }
}

// Make available globally
if (typeof window !== 'undefined') {
    window.ChessDOMExtractor = ChessDOMExtractor;
}

console.log('[Chess AI] DOM Extractor loaded');
