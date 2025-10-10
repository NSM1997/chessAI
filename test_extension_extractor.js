// Test script to verify the extension's FEN extraction
// Run this in the browser console on a Chess.com puzzle page

console.log('🧪 Testing Extension FEN Extraction...');

// Test 1: Check if ChessDOMExtractor is available
if (typeof ChessDOMExtractor !== 'undefined') {
    console.log('✅ ChessDOMExtractor is available');
    
    const extractor = new ChessDOMExtractor();
    
    // Test 2: Check if the new method exists
    if (typeof extractor.extractChessComPuzzlePosition === 'function') {
        console.log('✅ extractChessComPuzzlePosition method exists');
        
        // Test 3: Try to extract FEN
        const fen = extractor.extractCurrentFEN();
        console.log('🎯 Extracted FEN:', fen);
        
        if (fen) {
            console.log('✅ FEN extraction successful!');
            
            // Test 4: Validate the FEN
            const isValid = extractor.isValidFEN ? extractor.isValidFEN(fen) : 'No validation method';
            console.log('🔍 FEN validation:', isValid);
        } else {
            console.log('❌ FEN extraction failed');
            
            // Debug: Check what's happening
            console.log('🔍 Debugging extraction...');
            const puzzleFen = extractor.extractChessComPuzzleFEN();
            console.log('Puzzle FEN result:', puzzleFen);
        }
    } else {
        console.log('❌ extractChessComPuzzlePosition method not found');
    }
} else {
    console.log('❌ ChessDOMExtractor not available');
    console.log('Available globals:', Object.keys(window).filter(k => k.includes('Chess') || k.includes('Extractor')));
}

// Test 5: Direct piece detection
console.log('🔍 Direct piece detection test...');
const pieces = document.querySelectorAll('.piece');
console.log(`Found ${pieces.length} pieces`);

if (pieces.length > 0) {
    console.log('First few pieces:');
    Array.from(pieces).slice(0, 5).forEach((piece, i) => {
        console.log(`Piece ${i}:`, Array.from(piece.classList));
    });
} else {
    console.log('❌ No pieces found with .piece selector');
    
    // Try alternative selectors
    const altPieces = document.querySelectorAll('[class*="piece"], [class*="wp"], [class*="bp"]');
    console.log(`Found ${altPieces.length} pieces with alternative selectors`);
}

// Test 6: Board detection
console.log('🔍 Board detection test...');
const boards = document.querySelectorAll('wc-chess-board, .board, [id*="board"]');
console.log(`Found ${boards.length} board elements`);

boards.forEach((board, i) => {
    console.log(`Board ${i}:`, board.tagName, board.className, board.id);
});
