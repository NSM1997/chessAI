// Background script for Explainable Chess AI
console.log('Chess AI background script loaded');

// Handle extension installation
chrome.runtime.onInstalled.addListener(() => {
    console.log('Chess AI extension installed');
});

// Handle messages from content scripts or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Background received message:', message);
    sendResponse({ received: true });
});