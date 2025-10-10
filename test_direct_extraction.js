// Direct test of the working Chess.com puzzle extractor
// Copy and paste this into the browser console on a Chess.com puzzle page

console.log('🚀 Testing Direct Chess.com Puzzle Extraction...');

// Load the working extractor
const extractorCode = `
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
    }

    createSquareMap() {
        const squares = {};
        const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        for (let rank = 8; rank >= 1; rank--) {
            for (let fileIndex = 0; fileIndex < 8; fileIndex++) {
                const squareNum = (8 - rank) * 8 + fileIndex + 1;
                squares[squareNum] = files[fileIndex] + rank;
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
            console.log(\`Found \${pieces.length} pieces\`);

            if (pieces.length === 0) {
                console.log('❌ No pieces found');
                return null;
            }

            // Create 8x8 board array
            const boardArray = Array(8).fill().map(() => Array(8).fill(''));

            // Parse each piece
            pieces.forEach((piece, index) => {
                const classes = Array.from(piece.classList);
                console.log(\`Piece \${index}:\`, classes);

                // Find piece type and square
                let pieceType = null;
                let squareIndex = null;

                // Extract piece type from classes like 'wp', 'bp', 'wr', etc.
                for (const cls of classes) {
                    if (cls.match(/^[wb][prnbqk]$/)) {
                        pieceType = cls;
                        break;
                    }
                }

                // Extract square from classes like 'square-13', 'square-73', etc.
                for (const cls of classes) {
                    if (cls.startsWith('square-')) {
                        const match = cls.match(/square-(\\d+)/);
                        if (match && match[1]) {
                            squareIndex = parseInt(match[1], 10);
                            break;
                        }
                    }
                }

                if (pieceType && squareIndex !== null) {
                    // Convert Chess.com square number to board coordinates
                    const rank = 8 - Math.floor((squareIndex - 1) / 8);
                    const file = (squareIndex - 1) % 8;

                    if (rank >= 0 && rank < 8 && file >= 0 && file < 8) {
                        // Convert piece notation (wp -> P, bp -> p, etc.)
                        const pieceChar = pieceType[0] === 'w' ? pieceType[1].toUpperCase() : pieceType[1].toLowerCase();
                        boardArray[rank][file] = pieceChar;
                        console.log(\`Placed \${pieceChar} at rank \${rank}, file \${file} (square-\${squareIndex})\`);
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

            const finalFen = \`\${fenBoard} \${activeColor} \${castling} \${enPassant} \${halfmoveClock} \${fullmoveNumber}\`;
            console.log('Generated FEN:', finalFen);
            
            // Visual representation for debugging
            this.drawBoardInConsole(boardArray);
            
            return finalFen;
        } catch (error) {
            console.error('Error extracting puzzle position:', error);
            return null;
        }
    }

    drawBoardInConsole(boardArray) {
        console.log('Board visualization:');
        console.log('   a b c d e f g h');
        for (let i = 0; i < 8; i++) {
            let row = \`\${8 - i} \`;
            for (let j = 0; j < 8; j++) {
                const piece = boardArray[i][j];
                row += piece === '' ? '. ' : piece + ' ';
            }
            row += \`\${8 - i}\`;
            console.log(row);
        }
        console.log('   a b c d e f g h');
    }
}
`;

// Execute the extractor code
eval(extractorCode);

// Test the extractor
console.log('🧪 Testing the extractor...');
const extractor = new ChessComPuzzleExtractor();
const fen = extractor.extractPuzzleFEN();

if (fen) {
    console.log('✅ SUCCESS! Extracted FEN:', fen);
    
    // Test with server
    console.log('🌐 Testing with server...');
    fetch('http://localhost:8001/analyze-position', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fen: fen }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Server response:', data);
        console.log('Best move:', data.best_moves[0].san);
        console.log('Explanation:', data.explanations[0].explanation);
    })
    .catch(error => {
        console.error('Server error:', error);
    });
} else {
    console.log('❌ FEN extraction failed');
}
