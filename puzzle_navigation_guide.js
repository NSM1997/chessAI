/**
 * Chess.com Puzzle Navigation Guide
 * This script helps you navigate to an actual puzzle for FEN extraction testing
 */

function navigateToPuzzle() {
    console.log('🎯 Chess.com Puzzle Navigation Guide');
    console.log('=====================================');
    
    console.log('\n📍 Current Page Analysis:');
    console.log('URL:', window.location.href);
    console.log('Page Type:', getPageType());
    
    console.log('\n🔧 How to Navigate to a Puzzle:');
    console.log('1. Look for puzzle links on this page');
    console.log('2. Click on any puzzle to go to the puzzle page');
    console.log('3. The puzzle page URL should look like: /puzzles/12345');
    
    // Find puzzle links
    const puzzleLinks = findPuzzleLinks();
    console.log('\n🔗 Found Puzzle Links:');
    if (puzzleLinks.length > 0) {
        puzzleLinks.forEach((link, index) => {
            console.log(`${index + 1}. ${link.text} - ${link.href}`);
        });
        console.log('\n💡 Click on any of these links to go to a puzzle!');
    } else {
        console.log('No puzzle links found on this page.');
        console.log('Try refreshing the page or navigating to /puzzles');
    }
    
    console.log('\n🎯 What to Look For:');
    console.log('- Puzzle page should have a chess board');
    console.log('- URL should contain /puzzles/[number]');
    console.log('- Page should show puzzle instructions');
    console.log('- Board should be interactive');
    
    return puzzleLinks;
}

function getPageType() {
    const url = window.location.href;
    const pathname = window.location.pathname;
    
    if (pathname.includes('/puzzles/rated')) {
        return 'Puzzle List Page (Rated)';
    } else if (pathname.includes('/puzzles/')) {
        return 'Individual Puzzle Page';
    } else if (pathname.includes('/puzzles')) {
        return 'Puzzle Hub Page';
    } else {
        return 'Other Page';
    }
}

function findPuzzleLinks() {
    const links = [];
    
    // Look for common puzzle link patterns
    const selectors = [
        'a[href*="/puzzles/"]',
        'a[href*="/tactics/"]',
        '.puzzle-link',
        '.tactics-link',
        '[data-puzzle-id]',
        '.puzzle-item a',
        '.tactics-item a'
    ];
    
    selectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            if (element.href && element.href.includes('/puzzles/')) {
                links.push({
                    text: element.textContent?.trim() || 'Puzzle Link',
                    href: element.href,
                    element: element
                });
            }
        });
    });
    
    // Remove duplicates
    const uniqueLinks = links.filter((link, index, self) => 
        index === self.findIndex(l => l.href === link.href)
    );
    
    return uniqueLinks.slice(0, 10); // Limit to first 10
}

function testPuzzlePage() {
    console.log('\n🧪 Testing Current Page for Puzzle Elements:');
    
    const hasBoard = document.querySelector('.board, [class*="board"], [id*="board"]');
    const hasPieces = document.querySelector('[class*="piece"], .piece');
    const hasPuzzleUI = document.querySelector('[class*="puzzle"], .puzzle-controls, .puzzle-info');
    
    console.log('Has Board:', !!hasBoard);
    console.log('Has Pieces:', !!hasPieces);
    console.log('Has Puzzle UI:', !!hasPuzzleUI);
    
    if (hasBoard && hasPieces && hasPuzzleUI) {
        console.log('✅ This looks like a puzzle page!');
        console.log('You can now test FEN extraction.');
    } else {
        console.log('❌ This doesn\'t look like a puzzle page.');
        console.log('Navigate to an individual puzzle first.');
    }
}

// Auto-run the guide
console.log('🧭 Puzzle Navigation Guide loaded');
navigateToPuzzle();

// Make functions globally available
window.navigateToPuzzle = navigateToPuzzle;
window.testPuzzlePage = testPuzzlePage;
