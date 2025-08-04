// DealFlow Analytics - Simple Background Service Worker
console.log('DealFlow Analytics background service worker started');

// Keep service worker alive
self.addEventListener('activate', event => {
    console.log('Service worker activated');
});

// Handle extension installation
chrome.runtime.onInstalled.addListener(() => {
    console.log('DealFlow Analytics installed');
});

// Message handling (if needed)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Background received message:', request);
    if (request.action === 'contentScriptReady') {
        sendResponse({ status: 'acknowledged' });
    }
    return true;
});