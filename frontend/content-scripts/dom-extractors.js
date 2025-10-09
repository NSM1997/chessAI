class ChessDOMExtractor {
    extractCurrentFEN() {
        if (window.location.hostname.includes('chess.com')) {
            return this.extractChessComPuzzleFEN();
        }
        return this.getDefaultPosition();
    }

    extractChessComPuzzleFEN() {
        const pieces = document.querySelectorAll('[class*="piece"]');
        if (!pieces.length) return this.getDefaultPosition();
        return this.extractRealChessComPosition();
    }

    extractRealChessComPosition() {
        const board = {};
        const pieces = document.querySelectorAll('[class*="piece"]');
        pieces.forEach((piece) => {
            const list = Array.from(piece.classList);
            let pieceType = '', pieceColor = '', squareClass = '';
            list.forEach(cls => {
                if (cls.match(/^[wb][prnbqk]$/)) {
                    pieceColor = cls[0];
                    pieceType = cls[1];
                }
                if (cls.startsWith('square-')) {
                    squareClass = cls.replace('square-', '');
                }
            });
            if (pieceType && pieceColor && squareClass) {
                const square = this.decodeSquare(squareClass);
                if (square) {
                    board[square] = pieceColor === 'w' ? pieceType.toUpperCase() : pieceType;
                    console.log(`[DEBUG] ${pieceColor}${pieceType.toUpperCase()} on square-${squareClass} -> ${square}`);
                }
            }
        });
        return this.boardToFEN(board);
    }

    // MIRRORED Chess.com coordinate mapping for your board layout
    decodeSquare(squareNum) {
        const num = parseInt(squareNum);
        if (isNaN(num) || num < 11 || num > 88) return null;

        // Chess.com DOM counts top-to-bottom, left-to-right
        // So 11 is a8, 88 is h1
        const file = (num % 10) - 1;     // 1–8 → 0–7
        const rank = Math.floor(num / 10) - 1; // 1–8 → 0–7

        // Flip rank because DOM's rank 1 = top of board (a8)
        const correctedRank = 7 - rank;
        const correctedFile = file; // no need to flip file unless you're seeing left/right swapped

        const fileChar = String.fromCharCode(97 + correctedFile); // a–h
        const rankChar = (correctedRank + 1).toString();          // 1–8

        return fileChar + rankChar;
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
        fen += ' w KQkq - 0 1';
        return fen;
    }
    getDefaultPosition() {
        return 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
    }
    getPositionInfo(fen) {
        // Basic FEN parser to extract who's to move and move number
        try {
            const parts = fen.split(' ');
            const toMove = parts[1] === 'b' ? 'Black' : 'White';
            const moveNumber = parts.length >= 6 ? parseInt(parts[5]) : 1;
            return { toMove, moveNumber };
        } catch (e) {
            console.error('[Chess AI] Error parsing FEN info:', e);
            return { toMove: 'Unknown', moveNumber: 1 };
        }
    }
}
if (typeof module !== 'undefined' && module.exports) module.exports = ChessDOMExtractor;
console.log('[Chess AI] FINAL: Chess.com mirrored coordinate mapping for left=h1, right=a8.');