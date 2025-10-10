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
                        tabs[0].url.includes('/analysis/')
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
            
        default:
            sendResponse({ success: false, error: 'Unknown action' });
    }
});

console.log('[Chess AI] Background script ready');
