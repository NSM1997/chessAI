/**
 * Test the corrected FEN
 */

function testCorrectedFEN() {
    // Original problematic FEN
    const problematicFen = '8/2q2k1/2b1Q1p1/P5N1/3R4/7P/5PP1/7K b - - 0 1';
    
    // Corrected FEN (fixing rank 7: "2q2k1" -> "2q2k2")
    const correctedFen = '8/2q2k2/2b1Q1p1/P5N1/3R4/7P/5PP1/7K b - - 0 1';
    
    console.log('🔍 Testing corrected FEN...');
    console.log('Original FEN:', problematicFen);
    console.log('Corrected FEN:', correctedFen);
    
    // Test the corrected FEN
    const isValid = isValidFEN(correctedFen);
    console.log('\n🎯 Corrected FEN validation:', isValid ? '✅ VALID' : '❌ INVALID');
    
    if (isValid) {
        console.log('\n✅ SUCCESS! The corrected FEN is valid.');
        console.log('You can now use this FEN for testing:');
        console.log(correctedFen);
        
        // Test with the server
        testWithServer(correctedFen);
    }
    
    return isValid;
}

function testWithServer(fen) {
    console.log('\n🌐 Testing corrected FEN with server...');
    
    fetch('http://localhost:8001/analyze-position', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            fen: fen,
            depth: 15,
            user_skill_level: 'intermediate',
            explanation_type: 'comprehensive'
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Server response:', data);
        if (data.fen) {
            console.log('🎯 Server successfully analyzed the corrected FEN!');
            console.log('Best move:', data.best_moves[0]?.san);
            console.log('Explanation:', data.explanations[0]?.explanation);
        }
    })
    .catch(error => {
        console.error('❌ Server test failed:', error);
    });
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
console.log('🧪 Corrected FEN Tester loaded');
console.log('Testing the corrected FEN...');
testCorrectedFEN();

// Make functions globally available
window.testCorrectedFEN = testCorrectedFEN;
window.testWithServer = testWithServer;
