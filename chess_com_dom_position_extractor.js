// Chess.com DOM Position Extractor - Uses actual DOM positioning instead of square numbers
// This approach uses the piece elements' actual position on the page to determine coordinates

class ChessComDOMPositionExtractor {
    constructor() {
        this.log('ChessComDOMPositionExtractor initialized');
        this.pieceMap = {
            'wp': 'P', 'wr': 'R', 'wn': 'N', 'wb': 'B', 'wq': 'Q', 'wk': 'K',
            'bp': 'p', 'br': 'r', 'bn': 'n', 'bb': 'b', 'bq': 'q', 'bk': 'k'
        };
    }

    log(message, type = 'info') {
        console.log(`[ChessComDOMPositionExtractor][${type.toString().toUpperCase()}] ${message}`);
    }

    extractPuzzleFEN() {
        this.log('Extracting puzzle FEN using DOM positioning...');
        
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
                this.log('No board found with any selector', 'error');
                // Try to find any element that might contain pieces
                const pieces = document.querySelectorAll('.piece');
                if (pieces.length > 0) {
                    this.log(`Found ${pieces.length} pieces but no board element. Using document body as reference.`);
                    board = document.body;
                } else {
                    this.log('No pieces found either', 'error');
                    return null;
                }
            }

            // Get board dimensions and position
            const boardRect = board.getBoundingClientRect();
            this.log(`Board element: ${board.tagName} with class "${board.className}"`);
            this.log(`Board dimensions: ${boardRect.width}x${boardRect.height} at (${boardRect.left}, ${boardRect.top})`);

            // Find all pieces
            const pieces = document.querySelectorAll('.piece');
            this.log(`Found ${pieces.length} pieces`);

            if (pieces.length === 0) {
                this.log('No pieces found', 'error');
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
                
                this.log(`Estimated board from pieces: ${maxX - minX}x${maxY - minY}`);
            }

            this.log(`Square size: ${squareWidth}x${squareHeight}`);

            // Parse each piece
            pieces.forEach((piece, index) => {
                const classes = Array.from(piece.classList);
                this.log(`Piece ${index}:`, classes);

                // Find piece type
                let pieceType = null;
                for (const cls of classes) {
                    if (this.pieceMap[cls]) {
                        pieceType = this.pieceMap[cls];
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

                        boardArray[fenRank][fenFile] = pieceType;
                        this.log(`Placed ${pieceType} at file ${file}, rank ${rank} (FEN: ${String.fromCharCode(97 + fenFile)}${8 - fenRank})`);
                    } else {
                        this.log(`Piece ${pieceType} at invalid coordinates: file ${file}, rank ${rank}`, 'warn');
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
            this.log('Generated FEN:', finalFen);
            
            // Visual representation for debugging
            this.drawBoardInConsole(boardArray);
            
            return finalFen;
        } catch (error) {
            this.log('Error extracting puzzle position: ' + error.message, 'error');
            return null;
        }
    }

    drawBoardInConsole(boardArray) {
        this.log('Board visualization:');
        this.log('   a b c d e f g h');
        for (let i = 0; i < 8; i++) {
            let row = `${8 - i} `;
            for (let j = 0; j < 8; j++) {
                const piece = boardArray[i][j];
                row += piece === '' ? '. ' : piece + ' ';
            }
            row += `${8 - i}`;
            this.log(row);
        }
        this.log('   a b c d e f g h');
    }

    isValidFEN(fen) {
        if (!fen || typeof fen !== 'string') return false;
        const parts = fen.trim().split(' ');
        if (parts.length !== 6) {
            this.log(`Invalid FEN: Expected 6 parts, got ${parts.length}.`, 'error');
            return false;
        }

        const [boardPart, turnPart, castlingPart, enPassantPart, halfmoveClockPart, fullmoveNumberPart] = parts;

        // 1. Validate board part
        const ranks = boardPart.split('/');
        if (ranks.length !== 8) {
            this.log(`Invalid FEN board: Expected 8 ranks, got ${ranks.length}.`, 'error');
            return false;
        }

        for (const rank of ranks) {
            let sumSquares = 0;
            for (const char of rank) {
                if (char >= '1' && char <= '8') {
                    sumSquares += parseInt(char);
                } else if ('rnbqkpRNBQKP'.includes(char)) {
                    sumSquares += 1;
                } else {
                    this.log(`Invalid FEN board: Invalid character '${char}' in rank '${rank}'.`, 'error');
                    return false;
                }
            }
            if (sumSquares !== 8) {
                this.log(`Invalid FEN board: Rank '${rank}' sums to ${sumSquares} squares, expected 8.`, 'error');
                return false;
            }
        }

        // 2. Validate turn part
        if (turnPart !== 'w' && turnPart !== 'b') {
            this.log(`Invalid FEN turn: Expected 'w' or 'b', got '${turnPart}'.`, 'error');
            return false;
        }

        // 3. Validate castling availability
        if (!/^(-|[KQkq]{1,4})$/.test(castlingPart)) {
            this.log(`Invalid FEN castling: '${castlingPart}'.`, 'error');
            return false;
        }

        // 4. Validate en passant target square
        if (!/^(-|[a-h][36])$/.test(enPassantPart)) {
            this.log(`Invalid FEN en passant: '${enPassantPart}'.`, 'error');
            return false;
        }

        // 5. Validate halfmove clock
        if (isNaN(parseInt(halfmoveClockPart, 10)) || parseInt(halfmoveClockPart, 10) < 0) {
            this.log(`Invalid FEN halfmove clock: '${halfmoveClockPart}'.`, 'error');
            return false;
        }

        // 6. Validate fullmove number
        if (isNaN(parseInt(fullmoveNumberPart, 10)) || parseInt(fullmoveNumberPart, 10) < 1) {
            this.log(`Invalid FEN fullmove number: '${fullmoveNumberPart}'.`, 'error');
            return false;
        }

        this.log('FEN is structurally valid.', 'success');
        return true;
    }
}

console.log('🚀 Chess.com DOM Position Extractor loaded');
console.log('Run: new ChessComDOMPositionExtractor().extractPuzzleFEN() to extract FEN');
