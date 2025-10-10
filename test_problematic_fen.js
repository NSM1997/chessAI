/**
 * Test the problematic FEN that's causing issues
 */

function testProblematicFEN() {
    const problematicFen = '8/2q2k1/2b1Q1p1/P5N1/3R4/7P/5PP1/7K b - - 0 1';
    
    console.log('🔍 Testing problematic FEN:', problematicFen);
    
    // Split into parts
    const parts = problematicFen.split(' ');
    console.log('FEN parts:', parts);
    
    // Check each rank
    const boardPart = parts[0];
    const ranks = boardPart.split('/');
    console.log('Board ranks:', ranks);
    
    console.log('\n📊 Rank Analysis:');
    ranks.forEach((rank, index) => {
        let sum = 0;
        let pieces = 0;
        let empty = 0;
        
        for (const char of rank) {
            if (char >= '1' && char <= '8') {
                const emptySquares = parseInt(char);
                empty += emptySquares;
                sum += emptySquares;
            } else if ('rnbqkpRNBQKP'.includes(char)) {
                pieces++;
                sum += 1;
            }
        }
        
        console.log(`Rank ${8 - index}: "${rank}" - Pieces: ${pieces}, Empty: ${empty}, Total: ${sum}`);
        
        if (sum !== 8) {
            console.error(`❌ Rank ${8 - index} is INVALID! Expected 8 squares, got ${sum}`);
        } else {
            console.log(`✅ Rank ${8 - index} is valid`);
        }
    });
    
    // Check if it's a valid FEN
    const isValid = isValidFEN(problematicFen);
    console.log('\n🎯 Overall FEN validation:', isValid ? '✅ VALID' : '❌ INVALID');
    
    return isValid;
}

function isValidFEN(fen) {
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

// Auto-run the test
console.log('🧪 FEN Validation Tester loaded');
console.log('Testing the problematic FEN...');
testProblematicFEN();

// Make functions globally available
window.testProblematicFEN = testProblematicFEN;
window.isValidFEN = isValidFEN;
