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
            '/analysis',
            '/live/',
            '/daily/',
            '/daily'
        ];
        
        const isValidUrl = validContexts.some(context => pathname.includes(context));
        // Try multiple selectors to find the board
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
        const isPuzzlePage = pathname.includes('/puzzles/') || pathname.includes('/daily/') || pathname.includes('/daily');
        const isAnalysisPage = pathname.includes('/analysis/') || pathname.includes('/analysis');
        const isGamePage = pathname.includes('/game/') || pathname.includes('/play/') || pathname.includes('/live/');
        let hasGameUI = false;
        
        if (isPuzzlePage) {
            // For puzzles, just check for puzzle-specific elements
            hasGameUI = document.querySelector('.puzzle-controls, .puzzle-info, .instructions, .puzzle-details, .puzzle-ui, [class*="puzzle"], .daily-puzzle, [class*="daily"]');
        } else if (isAnalysisPage) {
            // For analysis pages, check for analysis-specific elements
            hasGameUI = document.querySelector('.analysis-controls, .analysis-info, [class*="analysis"], .move-list, .pgn-editor');
        } else if (isGamePage) {
            // For games, check for standard game UI elements
            hasGameUI = document.querySelector('.clock, .player-info, .move-list, .game-controls');
        } else {
            // For other pages, check for any chess-related UI
            hasGameUI = document.querySelector('.clock, .player-info, .move-list, .game-controls, .analysis-controls, .puzzle-controls');
        }
        
        // If we have a valid URL and board, and either game UI or it's a special page, it's valid
        let isValid = isValidUrl && hasActiveBoard && (hasGameUI || isPuzzlePage || isAnalysisPage || isGamePage);
        
        // For special pages, be even more permissive - if we're on a valid URL, allow it
        if (!isValid && (isPuzzlePage || isAnalysisPage || isGamePage) && isValidUrl) {
            console.log('[Chess AI] Special page detected, allowing context even without board detection');
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

    detectBoardOrientation() {
        try {
            console.log('[Chess AI] Detecting board orientation...');
            
            // Method 1: Check for board flip indicators in CSS classes
            const boardElement = document.querySelector('wc-chess-board.board, wc-chess-board, .board');
            if (boardElement) {
                const classes = Array.from(boardElement.classList);
                console.log('[Chess AI] Board classes:', classes);
                
                if (classes.some(cls => cls.includes('flipped') || cls.includes('black-perspective') || cls.includes('black-view'))) {
                    console.log('[Chess AI] Board orientation: Flipped (from CSS classes)');
                    return true;
                }
            }
            
            // Method 2: Check for player perspective indicators
            const playerElements = document.querySelectorAll('.player-info, .player-name, [class*="player"]');
            for (const element of playerElements) {
                const text = element.textContent.toLowerCase();
                const classes = Array.from(element.classList);
                
                // Look for indicators that user is playing as Black
                if (text.includes('you are black') || text.includes('playing as black') || 
                    classes.some(cls => cls.includes('black-player') || cls.includes('player-black'))) {
                    console.log('[Chess AI] Board orientation: Flipped (user playing as Black)');
                    return true;
                }
            }
            
            // Method 3: Enhanced piece position analysis
            const pieces = document.querySelectorAll('.piece, [class*="piece"]');
            if (pieces.length > 0) {
                let whitePiecesInTopHalf = 0;
                let whitePiecesInBottomHalf = 0;
                let blackPiecesInTopHalf = 0;
                let blackPiecesInBottomHalf = 0;
                
                const boardElement = document.querySelector('wc-chess-board.board, wc-chess-board, .board');
                if (boardElement) {
                    const boardRect = boardElement.getBoundingClientRect();
                    const boardHeight = boardRect.height;
                    const boardWidth = boardRect.width;
                    
                    pieces.forEach(piece => {
                        const classes = Array.from(piece.classList);
                        const pieceRect = piece.getBoundingClientRect();
                        
                        // Calculate relative position within the board
                        const relativeY = pieceRect.top - boardRect.top;
                        const relativeX = pieceRect.left - boardRect.left;
                        
                        // Check if piece is in top or bottom half
                        const isInTopHalf = relativeY < boardHeight / 2;
                        const isInLeftHalf = relativeX < boardWidth / 2;
                        
                        // Check piece color
                        if (classes.some(cls => cls.match(/^w[prnbqk]$/))) {
                            if (isInTopHalf) whitePiecesInTopHalf++;
                            else whitePiecesInBottomHalf++;
                        } else if (classes.some(cls => cls.match(/^b[prnbqk]$/))) {
                            if (isInTopHalf) blackPiecesInTopHalf++;
                            else blackPiecesInBottomHalf++;
                        }
                    });
                    
                    console.log(`[Chess AI] Piece distribution: White(${whitePiecesInTopHalf}↑, ${whitePiecesInBottomHalf}↓), Black(${blackPiecesInTopHalf}↑, ${blackPiecesInBottomHalf}↓)`);
                    
                    // In a normal board: White pieces should be in bottom half (ranks 1-2)
                    // In a flipped board: White pieces should be in top half (ranks 7-8)
                    if (whitePiecesInTopHalf > whitePiecesInBottomHalf && whitePiecesInTopHalf > 0) {
                        console.log('[Chess AI] Board orientation: Flipped (white pieces predominantly in top half)');
                        return true;
                    } else if (whitePiecesInBottomHalf > whitePiecesInTopHalf && whitePiecesInBottomHalf > 0) {
                        console.log('[Chess AI] Board orientation: Normal (white pieces predominantly in bottom half)');
                        return false;
                    }
                }
            }
            
            // Method 4: Check for game state indicators
            const gameStateElements = document.querySelectorAll('.game-info, .game-status, [class*="game"]');
            for (const element of gameStateElements) {
                const text = element.textContent.toLowerCase();
                if (text.includes('black to move') || text.includes('black\'s turn')) {
                    // This might indicate user is playing as Black
                    console.log('[Chess AI] Board orientation: Possibly flipped (Black to move)');
                    return true;
                }
            }
            
            // Method 5: Check URL patterns for game type
            const url = window.location.href;
            if (url.includes('/game/') || url.includes('/play/')) {
                // For live games, try to detect if user is playing as Black
                const gameInfo = document.querySelector('.game-info, .game-header, [class*="game"]');
                if (gameInfo) {
                    const gameText = gameInfo.textContent.toLowerCase();
                    if (gameText.includes('you are black') || gameText.includes('playing as black')) {
                        console.log('[Chess AI] Board orientation: Flipped (detected from game info)');
                        return true;
                    }
                }
            }
            
            console.log('[Chess AI] Board orientation: Normal (default)');
            return false;
            
        } catch (error) {
            console.log('[Chess AI] Board orientation detection failed:', error);
            return false; // Default to normal orientation
        }
    }

    detectCurrentTurn() {
        try {
            // Method 1: Check for turn indicators in clocks and player info
            const whiteActive = document.querySelector('.clock-player-turn.clock-white, .player-white.player-turn, [class*="white"][class*="turn"], .player-turn-white, .turn-white');
            const blackActive = document.querySelector('.clock-player-turn.clock-black, .player-black.player-turn, [class*="black"][class*="turn"], .player-turn-black, .turn-black');
            
            if (whiteActive && !blackActive) {
                console.log('[Chess AI] Turn detected: White (from turn indicators)');
                return 'w';
            }
            if (blackActive && !whiteActive) {
                console.log('[Chess AI] Turn detected: Black (from turn indicators)');
                return 'b';
            }
            
            // Method 2: Check puzzle/analysis text content
            const textElements = document.querySelectorAll('.puzzle-info, .instructions, .puzzle-details, .analysis-info, [class*="turn"], [class*="move"], .move-list, .moves, [class*="analysis"]');
            for (const element of textElements) {
                const text = element.textContent.toLowerCase();
                if (text.includes('white to move') || text.includes('white to play') || text.includes('white\'s turn')) {
                    console.log('[Chess AI] Turn detected: White (from text content)');
                    return 'w';
                }
                if (text.includes('black to move') || text.includes('black to play') || text.includes('black\'s turn')) {
                    console.log('[Chess AI] Turn detected: Black (from text content)');
                    return 'b';
                }
            }
            
            // Method 2.5: Check for analysis board turn indicators
            const analysisTurnElements = document.querySelectorAll('.analysis-turn, .board-turn, [class*="turn-indicator"], [class*="current-turn"]');
            for (const element of analysisTurnElements) {
                const text = element.textContent.toLowerCase();
                const classes = Array.from(element.classList);
                
                if (text.includes('white') || classes.some(cls => cls.includes('white'))) {
                    console.log('[Chess AI] Turn detected: White (from analysis turn indicator)');
                    return 'w';
                }
                if (text.includes('black') || classes.some(cls => cls.includes('black'))) {
                    console.log('[Chess AI] Turn detected: Black (from analysis turn indicator)');
                    return 'b';
                }
            }
            
            // Method 3: Check for active/highlighted player elements
            const activePlayer = document.querySelector('.player-active, .player-current, .active-player, [class*="active"][class*="player"]');
            if (activePlayer) {
                const classes = Array.from(activePlayer.classList);
                if (classes.some(cls => cls.includes('white'))) {
                    console.log('[Chess AI] Turn detected: White (from active player)');
                    return 'w';
                }
                if (classes.some(cls => cls.includes('black'))) {
                    console.log('[Chess AI] Turn detected: Black (from active player)');
                    return 'b';
                }
            }
            
            // Method 4: Check move list for last move color
            const lastMove = document.querySelector('.move-list .move:last-child, .moves .move:last-child, [class*="move"]:last-child');
            if (lastMove) {
                const classes = Array.from(lastMove.classList);
                if (classes.some(cls => cls.includes('white'))) {
                    console.log('[Chess AI] Turn detected: Black (last move was white)');
                    return 'b';
                }
                if (classes.some(cls => cls.includes('black'))) {
                    console.log('[Chess AI] Turn detected: White (last move was black)');
                    return 'w';
                }
            }
            
            // Method 5: Use a different approach for analysis boards
            // Instead of counting moves, try to detect from the board's visual state
            const boardElement = document.querySelector('wc-chess-board.board, wc-chess-board, .board');
            if (boardElement) {
                // Check for any visual indicators of whose turn it is
                const boardClasses = Array.from(boardElement.classList);
                const boardStyle = window.getComputedStyle(boardElement);
                
                // Look for turn-related classes or styles
                if (boardClasses.some(cls => cls.includes('white-turn') || cls.includes('white-to-move'))) {
                    console.log('[Chess AI] Turn detected: White (from board classes)');
                    return 'w';
                }
                if (boardClasses.some(cls => cls.includes('black-turn') || cls.includes('black-to-move'))) {
                    console.log('[Chess AI] Turn detected: Black (from board classes)');
                    return 'b';
                }
                
                // Check for any data attributes that might indicate turn
                const turnAttr = boardElement.getAttribute('data-turn') || 
                               boardElement.getAttribute('data-active-color') ||
                               boardElement.getAttribute('data-current-player') ||
                               boardElement.getAttribute('data-to-move');
                
                if (turnAttr) {
                    const turn = turnAttr.toLowerCase().includes('black') || turnAttr === 'b' ? 'b' : 'w';
                    console.log(`[Chess AI] Turn detected: ${turn === 'w' ? 'White' : 'Black'} (from board attribute: ${turnAttr})`);
                    return turn;
                }
            }
            
            // Method 6: Check for highlighted/selected squares (analysis board specific)
            const highlightedSquares = document.querySelectorAll('[class*="highlight"], [class*="selected"], [class*="active"]');
            for (const square of highlightedSquares) {
                const classes = Array.from(square.classList);
                const text = square.textContent.toLowerCase();
                
                if (classes.some(cls => cls.includes('white')) || text.includes('white')) {
                    console.log('[Chess AI] Turn detected: White (from highlighted square)');
                    return 'w';
                }
                if (classes.some(cls => cls.includes('black')) || text.includes('black')) {
                    console.log('[Chess AI] Turn detected: Black (from highlighted square)');
                    return 'b';
                }
            }
            
            // Method 7: Try to detect turn from the board's internal JavaScript state
            try {
                // Check if the board element has any internal properties
                const boardElement = document.querySelector('wc-chess-board.board, wc-chess-board, .board');
                if (boardElement) {
                    // Try to access internal properties (this might work for some chess board implementations)
                    const possibleProps = ['turn', 'activeColor', 'currentPlayer', 'toMove', 'sideToMove'];
                    
                    for (const prop of possibleProps) {
                        if (boardElement[prop] !== undefined) {
                            const value = boardElement[prop];
                            const turn = (value === 'black' || value === 'b' || value === 1) ? 'b' : 'w';
                            console.log(`[Chess AI] Turn detected: ${turn === 'w' ? 'White' : 'Black'} (from board.${prop}: ${value})`);
                            return turn;
                        }
                    }
                    
                    // Try to access shadow DOM or internal state
                    if (boardElement.shadowRoot) {
                        const shadowContent = boardElement.shadowRoot.textContent || boardElement.shadowRoot.innerHTML;
                        if (shadowContent.includes('white to move') || shadowContent.includes('white\'s turn')) {
                            console.log('[Chess AI] Turn detected: White (from shadow DOM)');
                            return 'w';
                        }
                        if (shadowContent.includes('black to move') || shadowContent.includes('black\'s turn')) {
                            console.log('[Chess AI] Turn detected: Black (from shadow DOM)');
                            return 'b';
                        }
                    }
                }
                
                // Check for any global chess state variables
                const globalChessVars = ['chessBoard', 'gameBoard', 'analysisBoard', 'currentBoard'];
                for (const varName of globalChessVars) {
                    if (window[varName] && window[varName].turn !== undefined) {
                        const value = window[varName].turn;
                        const turn = (value === 'black' || value === 'b' || value === 1) ? 'b' : 'w';
                        console.log(`[Chess AI] Turn detected: ${turn === 'w' ? 'White' : 'Black'} (from window.${varName}.turn: ${value})`);
                        return turn;
                    }
                }
                
            } catch (error) {
                console.log('[Chess AI] Board state analysis failed:', error);
            }
            
            // Method 8: Fallback - use a simple heuristic based on position analysis
            // This is a last resort when all other methods fail
            try {
                const pieces = document.querySelectorAll('.piece, [class*="piece"]');
                if (pieces.length > 0) {
                    // Count pieces to get a rough idea of the position
                    let whitePieces = 0;
                    let blackPieces = 0;
                    
                    pieces.forEach(piece => {
                        const classes = Array.from(piece.classList);
                        for (const cls of classes) {
                            if (cls.match(/^w[prnbqk]$/)) {
                                whitePieces++;
                                break;
                            } else if (cls.match(/^b[prnbqk]$/)) {
                                blackPieces++;
                                break;
                            }
                        }
                    });
                    
                    // Simple heuristic: if we have a reasonable number of pieces, 
                    // assume it's a normal position and default to white
                    // If it looks like an endgame, try to be more careful
                    if (whitePieces + blackPieces >= 16) {
                        console.log('[Chess AI] Turn detection: Defaulting to White (normal position, no clear indicator)');
                        return 'w';
                    } else {
                        console.log('[Chess AI] Turn detection: Defaulting to White (endgame position, no clear indicator)');
                        return 'w';
                    }
                }
            } catch (error) {
                console.log('[Chess AI] Fallback analysis failed:', error);
            }
            
            console.log('[Chess AI] Turn detection: Defaulting to White (no clear indicator found)');
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

            // Find all pieces - use specific selectors to avoid false positives
            let pieces = document.querySelectorAll(
                '.piece[class*="wp"], .piece[class*="bp"], .piece[class*="wr"], .piece[class*="br"], ' +
                '.piece[class*="wn"], .piece[class*="bn"], .piece[class*="wb"], .piece[class*="bb"], ' +
                '.piece[class*="wq"], .piece[class*="bq"], .piece[class*="wk"], .piece[class*="bk"]'
            );
            
            // Fallback to broader selectors if specific ones don't work
            if (pieces.length === 0) {
                pieces = document.querySelectorAll('.piece');
            }
            if (pieces.length === 0) {
                pieces = document.querySelectorAll('[class*="piece"], .chess-piece, [class*="chess-piece"]');
            }
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
                        // Detect board orientation based on user's perspective
                        // Check for manual override first (for testing)
                        let isBoardFlipped = window.chessAIManualOrientation;
                        if (isBoardFlipped === undefined) {
                            isBoardFlipped = this.detectBoardOrientation();
                        } else {
                            console.log(`[Chess AI] Using manual board orientation: ${isBoardFlipped ? 'Flipped' : 'Normal'}`);
                        }
                        
                        let fenRank, fenFile;
                        
                        // Coordinate mapping based on board orientation
                        // DOM coordinates: 0,0 = top-left, 7,7 = bottom-right
                        // FEN coordinates: 0,0 = a8 (top-left), 7,7 = h1 (bottom-right)
                        
                        if (isBoardFlipped) {
                            // For flipped boards (playing as Black), invert both coordinates
                            // DOM coordinates when Black on bottom: rank 0 = rank 1, rank 7 = rank 8
                            fenRank = 7 - rank; // Invert rank coordinates
                            fenFile = 7 - file; // Invert file coordinates
                        } else {
                            // For normal boards (playing as White, White on bottom)
                            // DOM coordinates: rank 0 = rank 8 (top), rank 7 = rank 1 (bottom)
                            // FEN array: index 0 = rank 8, index 7 = rank 1
                            fenRank = rank;     // Direct rank mapping
                            fenFile = file;     // Direct file mapping
                        }

                        // Convert piece notation (wp -> P, bp -> p, etc.)
                        const pieceChar = pieceType[0] === 'w' ? pieceType[1].toUpperCase() : pieceType[1].toLowerCase();
                        boardArray[fenRank][fenFile] = pieceChar;
                        console.log(`[Chess AI] Placed ${pieceChar} at file ${file}, rank ${rank} (FEN: ${String.fromCharCode(97 + fenFile)}${8 - fenRank}) [${isBoardFlipped ? 'flipped' : 'normal'} board]`);
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

            // Use enhanced turn detection
            let activeColor = this.detectCurrentTurn();
            console.log(`[Chess AI] Detected turn: ${activeColor === 'w' ? 'White' : 'Black'}`);
            
            // Method 8: Try to extract turn from the board's internal state
            // This is the most reliable method for analysis boards
            try {
                // Check if the board element has any data attributes or properties that indicate turn
                const boardElement = document.querySelector('wc-chess-board.board, wc-chess-board, .board');
                if (boardElement) {
                    // Check for data attributes
                    const turnData = boardElement.getAttribute('data-turn') || 
                                   boardElement.getAttribute('data-active-color') ||
                                   boardElement.getAttribute('data-current-player');
                    
                    if (turnData) {
                        const turn = turnData.toLowerCase().includes('black') || turnData === 'b' ? 'b' : 'w';
                        console.log(`[Chess AI] Turn detected: ${turn === 'w' ? 'White' : 'Black'} (from board data attribute: ${turnData})`);
                        activeColor = turn;
                    }
                    
                    // Check for any JavaScript properties (if accessible)
                    if (boardElement._turn !== undefined) {
                        const turn = boardElement._turn === 'black' || boardElement._turn === 'b' ? 'b' : 'w';
                        console.log(`[Chess AI] Turn detected: ${turn === 'w' ? 'White' : 'Black'} (from board property: ${boardElement._turn})`);
                        activeColor = turn;
                    }
                }
                
                // Check window variables for turn information
                if (window.chesscom && window.chesscom.board) {
                    const boardState = window.chesscom.board;
                    if (boardState.turn !== undefined) {
                        const turn = boardState.turn === 'black' || boardState.turn === 'b' ? 'b' : 'w';
                        console.log(`[Chess AI] Turn detected: ${turn === 'w' ? 'White' : 'Black'} (from window.chesscom.board.turn: ${boardState.turn})`);
                        activeColor = turn;
                    }
                }
                
            } catch (error) {
                console.log('[Chess AI] Board state analysis failed:', error);
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
