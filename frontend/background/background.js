console.log('[Chess AI] Background script loaded');

chrome.runtime.onInstalled.addListener((details) => {
    console.log('[Chess AI] Extension installed:', details.reason);
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('[Chess AI] Message received:', message);
    
    switch (message.action) {
        case 'getStatus':
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                if (tabs[0]) {
                    const isChessPage = tabs[0].url && tabs[0].url.includes('chess.com');
                    const hasValidPath = isChessPage && (
                        tabs[0].url.includes('/play/') ||
                        tabs[0].url.includes('/game/') ||
                        tabs[0].url.includes('/puzzles/') ||
                        tabs[0].url.includes('/analysis/') ||
                        tabs[0].url.includes('/analysis') ||
                        tabs[0].url.includes('/daily/') ||
                        tabs[0].url.includes('/daily') ||
                        tabs[0].url.includes('/live/')
                    );
                    
                    sendResponse({
                        success: true,
                        data: {
                            isActive: hasValidPath,
                            isChessPage: isChessPage,
                            url: tabs[0].url
                        }
                    });
                } else {
                    sendResponse({ success: false, error: 'No active tab' });
                }
            });
            return true;
            
        case 'ping':
            sendResponse({ success: true, message: 'pong' });
            break;
            
        case 'analyzeMoveInBackground':
            // Perform move analysis in background
            const { fen_before, fen_after } = message;
            
            fetch('http://localhost:8001/analyze-move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fen_before, fen_after })
            })
            .then(response => response.json())
            .then(analysis => {
                // Cache the result for instant popup display
                chrome.storage.local.set({
                    cachedMoveAnalysis: {
                        ...analysis,
                        _cached_at: Date.now(),
                        _fen_before: fen_before,
                        _fen_after: fen_after
                    }
                });
                
                console.log('[Chess AI Background] Analysis complete and cached');
                sendResponse({ success: true, analysis });
            })
            .catch(error => {
                console.error('[Chess AI Background] Analysis failed:', error);
                sendResponse({ success: false, error: error.message });
            });
            
            return true; // Keep channel open for async response
            
        default:
            sendResponse({ success: false, error: 'Unknown action' });
    }
});

console.log('[Chess AI] Background script ready');
