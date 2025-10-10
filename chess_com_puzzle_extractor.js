// chess_com_puzzle_extractor.js
class ChessComPuzzleExtractor {
    constructor() {
        this.squareMap = this.createSquareMap();
        this.pieceMap = {
            'wp': 'P', 'bp': 'p',
            'wr': 'R', 'br': 'r', 
            'wn': 'N', 'bn': 'n',
            'wb': 'B', 'bb': 'b',
            'wq': 'Q', 'bq': 'q',
            'wk': 'K', 'bk': 'k'
        };
        console.log('🔧 Chess.com Puzzle Extractor loaded');
    }

    createSquareMap() {
        // Chess.com uses square numbers 0-63 (0=a8, 63=h1)
        const squares = [];
        for (let rank = 8; rank >= 1; rank--) {
            for (let file = 0; file < 8; file++) {
                const squareIndex = (8 - rank) * 8 + file;
                const squareName = String.fromCharCode(97 + file) + rank;
                squares[squareIndex] = squareName;
            }
        }
        return squares;
    }

    extractPuzzleFEN() {
        console.log('🔍 Extracting puzzle FEN from Chess.com format...');
        
        try {
            // Find the main board
            const board = document.querySelector('wc-chess-board.board, .board, [id*="board"]');
            if (!board) {
                console.log('❌ No board found');
                return null;
            }

            // Find all pieces - try both inside board and globally
            let pieces = board.querySelectorAll('.piece');
            if (pieces.length === 0) {
                // If no pieces found inside board, search globally
                pieces = document.querySelectorAll('.piece');
                console.log('No pieces found inside board, searching globally...');
            }
            console.log(`Found ${pieces.length} pieces`);

            if (pieces.length === 0) {
                console.log('❌ No pieces found');
                return null;
            }

            // Create 8x8 board array
            const boardArray = Array(8).fill().map(() => Array(8).fill(''));

            // Parse each piece
            pieces.forEach((piece, index) => {
                const classes = Array.from(piece.classList);
                console.log(`Piece ${index}:`, classes);
                console.log(`Piece ${index} element:`, piece);

                // Find piece type and square
                let pieceType = null;
                let squareIndex = null;

                for (const className of classes) {
                    if (this.pieceMap[className]) {
                        pieceType = this.pieceMap[className];
                    } else if (className.startsWith('square-')) {
                        squareIndex = parseInt(className.replace('square-', ''));
                    }
                }

                if (pieceType && squareIndex !== null) {
                    const squareName = this.squareMap[squareIndex];
                    if (squareName) {
                        const file = squareName.charCodeAt(0) - 97; // a=0, b=1, etc.
                        const rank = 8 - parseInt(squareName[1]); // 8=0, 7=1, etc.
                        boardArray[rank][file] = pieceType;
                        console.log(`Placed ${pieceType} at ${squareName} (${squareIndex}) -> [${rank}][${file}]`);
                    }
                }
            });

            // Convert board array to FEN
            const fenRanks = [];
            for (let rank = 0; rank < 8; rank++) {
                let fenRank = '';
                let emptyCount = 0;

                for (let file = 0; file < 8; file++) {
                    const piece = boardArray[rank][file];
                    if (piece) {
                        if (emptyCount > 0) {
                            fenRank += emptyCount;
                            emptyCount = 0;
                        }
                        fenRank += piece;
                    } else {
                        emptyCount++;
                    }
                }

                if (emptyCount > 0) {
                    fenRank += emptyCount;
                }
                fenRanks.push(fenRank);
            }

            const boardFEN = fenRanks.join('/');

            // Determine active color (this is tricky for puzzles - we'll need to infer it)
            // For now, let's try to find clues in the DOM
            let activeColor = 'w'; // default to white
            
            // Look for turn indicators or puzzle hints
            const turnIndicator = document.querySelector('.turn, .active-color, [class*="turn"], [class*="active"]');
            if (turnIndicator) {
                const text = turnIndicator.textContent.toLowerCase();
                if (text.includes('black') || text.includes('b to move')) {
                    activeColor = 'b';
                }
            }

            // Look for puzzle-specific indicators
            const puzzleHint = document.querySelector('.puzzle-hint, .hint, [class*="hint"]');
            if (puzzleHint) {
                const text = puzzleHint.textContent.toLowerCase();
                if (text.includes('black') || text.includes('b to move')) {
                    activeColor = 'b';
                }
            }

            // Construct full FEN (we'll use default values for castling, en passant, etc.)
            const fen = `${boardFEN} ${activeColor} - - 0 1`;
            
            console.log('✅ Generated FEN:', fen);
            console.log('Board visualization:');
            this.printBoard(boardArray);
            
            return fen;

        } catch (error) {
            console.error('❌ Error extracting puzzle FEN:', error);
            return null;
        }
    }

    printBoard(boardArray) {
        console.log('   a b c d e f g h');
        for (let rank = 0; rank < 8; rank++) {
            let row = `${8 - rank} `;
            for (let file = 0; file < 8; file++) {
                const piece = boardArray[rank][file];
                row += piece ? piece : '.';
                row += ' ';
            }
            row += `${8 - rank}`;
            console.log(row);
        }
        console.log('   a b c d e f g h');
    }

    validateFEN(fen) {
        if (!fen || typeof fen !== 'string') return false;
        const parts = fen.trim().split(' ');
        if (parts.length < 2) return false;
        
        const boardPart = parts[0];
        const turnPart = parts[1];
        
        if (!boardPart.includes('/') || boardPart.length < 10) return false;
        if (turnPart !== 'w' && turnPart !== 'b') return false;
        
        const ranks = boardPart.split('/');
        if (ranks.length !== 8) return false;
        
        for (const rank of ranks) {
            let sumSquares = 0;
            for (const char of rank) {
                if (char >= '1' && char <= '8') {
                    sumSquares += parseInt(char);
                } else if ('rnbqkpRNBQKP'.includes(char)) {
                    sumSquares += 1;
                } else {
                    return false;
                }
            }
            if (sumSquares !== 8) return false;
        }
        return true;
    }
}

console.log('🚀 Chess.com Puzzle Extractor loaded');
console.log('Run: new ChessComPuzzleExtractor().extractPuzzleFEN() to extract FEN');

// Make it globally available
window.ChessComPuzzleExtractor = ChessComPuzzleExtractor;
