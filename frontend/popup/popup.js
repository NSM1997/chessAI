document.addEventListener('DOMContentLoaded', function() {
    const statusDiv = document.getElementById('status');
    
    // Test FEN extraction
    document.getElementById('test-extraction').addEventListener('click', async () => {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        chrome.tabs.sendMessage(tab.id, { type: 'GET_CURRENT_FEN' }, (response) => {
            if (response && response.fen) {
                statusDiv.className = 'status success';
                statusDiv.textContent = '✅ FEN: ' + response.fen.substring(0, 30) + '...';
            } else {
                statusDiv.className = 'status error';
                statusDiv.textContent = '❌ No FEN found';
            }
        });
    });
    
    // Toggle overlay
    document.getElementById('toggle-overlay').addEventListener('click', async () => {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        chrome.tabs.sendMessage(tab.id, { type: 'TOGGLE_OVERLAY' });
    });
    
    // Analyze position
    document.getElementById('analyze-position').addEventListener('click', async () => {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        chrome.tabs.sendMessage(tab.id, { type: 'ANALYZE_CURRENT' });
    });
});