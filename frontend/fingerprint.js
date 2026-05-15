/**
 * Enterprise Fingerprinting Utility
 * Generates a unique device signature based on the browser environment.
 */
function getDeviceFingerprint() {
    const components = [
        navigator.userAgent,
        navigator.language,
        screen.width + 'x' + screen.height,
        screen.colorDepth,
        new Date().getTimezoneOffset(),
        // Simple string concat for hashing (or just the string itself)
        // In a real app, we'd use a hashing library like CryptoJS or Web Crypto API
    ];
    return btoa(components.join('|'));
}

// Global fetch wrapper to include fingerprint
async function secureFetch(url, options = {}) {
    const fingerprint = getDeviceFingerprint();
    const headers = {
        ...options.headers,
        'X-Device-Fingerprint': fingerprint
    };
    
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    return fetch(url, { ...options, headers });
}
