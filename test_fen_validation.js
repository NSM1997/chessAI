/**
 * FEN Validation Test Script
 * Test the problematic FEN string to understand why it's invalid
 */

function testFENValidation() {
    console.log('🧪 Testing FEN Validation');
    console.log('========================');
    
    const testFEN = "8/2q2k1/2b1Q1p1/P5N1/3R4/7P/5PP1/7K b - - 0 1";
    
    console.log('Testing FEN:', testFEN);
    
    // Split into parts
    const parts = testFEN.split(' ');
    console.log('FEN parts:', parts);
    
    if (parts.length < 2) {
        console.log('❌ FEN has less than 2 parts');
        return;
    }
    
    const boardPart = parts[0];
    const turnPart = parts[1];
    
    console.log('Board part:', boardPart);
    console.log('Turn part:', turnPart);
    
    // Check if board part has slashes
    if (!boardPart.includes('/')) {
        console.log('❌ Board part does not contain slashes');
        return;
    }
    
    // Split into ranks
    const ranks = boardPart.split('/');
    console.log('Ranks:', ranks);
    console.log('Number of ranks:', ranks.length);
    
    if (ranks.length !== 8) {
        console.log('❌ FEN has', ranks.length, 'ranks, but should have 8');
        return;
    }
    
    // Check each rank
    let allRanksValid = true;
    ranks.forEach((rank, index) => {
        console.log(`\nRank ${8-index}: "${rank}"`);
        
        let sum = 0;
        let pieces = [];
        
        for (const char of rank) {
            if (char >= '1' && char <= '8') {
                const num = parseInt(char);
                sum += num;
                console.log(`  Number ${num} (empty squares)`);
            } else if ('rnbqkpRNBQKP'.includes(char)) {
                sum += 1;
                pieces.push(char);
                console.log(`  Piece ${char}`);
            } else {
                console.log(`  ❌ Invalid character: ${char}`);
                allRanksValid = false;
            }
        }
        
        console.log(`  Total squares: ${sum}`);
        console.log(`  Pieces: [${pieces.join(', ')}]`);
        
        if (sum !== 8) {
            console.log(`  ❌ Rank ${8-index} has ${sum} squares, should have 8`);
            allRanksValid = false;
        } else {
            console.log(`  ✅ Rank ${8-index} is valid`);
        }
    });
    
    // Check turn
    if (turnPart !== 'w' && turnPart !== 'b') {
        console.log('❌ Turn part is invalid:', turnPart);
        return;
    } else {
        console.log('✅ Turn part is valid:', turnPart);
    }
    
    if (allRanksValid) {
        console.log('\n✅ FEN is valid!');
    } else {
        console.log('\n❌ FEN is invalid due to rank issues');
    }
    
    // Try to create a corrected version
    console.log('\n🔧 Attempting to create corrected FEN...');
    
    // The issue might be that we're missing a rank or have incorrect rank counts
    // Let's try to identify what the correct FEN should be
    
    console.log('Current ranks and their square counts:');
    ranks.forEach((rank, index) => {
        let sum = 0;
        for (const char of rank) {
            if (char >= '1' && char <= '8') {
                sum += parseInt(char);
            } else if ('rnbqkpRNBQKP'.includes(char)) {
                sum += 1;
            }
        }
        console.log(`Rank ${8-index}: "${rank}" = ${sum} squares`);
    });
}

// Auto-run the test
testFENValidation();
