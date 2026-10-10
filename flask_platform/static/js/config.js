/**
 * HydroFlow Central Application Configuration
 * Decoupled client configuration for local and cloud deployments
 */
(function() {
    'use strict';

    const urlParams = new URLSearchParams(window.location.search);
    
    // API Base URL Resolution Priority:
    // 1. Explicit ?api= URL query parameter (for custom proxy/cloud testing)
    // 2. Pre-set window override
    // 3. Localhost / same-origin if backend is co-hosted with frontend
    // 4. Default cloud inference backend
    let resolvedBaseUrl = window.HYDROFLOW_API_BASE || '';
    if (urlParams.has('api')) {
        resolvedBaseUrl = urlParams.get('api').replace(/\/+$/, '');
    } else if (!resolvedBaseUrl) {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            resolvedBaseUrl = window.location.origin;
        } else {
            // By default, same origin relative endpoints
            resolvedBaseUrl = '';
        }
    }

    window.HYDROFLOW_CONFIG = {
        apiBaseUrl: resolvedBaseUrl,
        timeoutMs: 30000,
        maxUploadBytes: 32 * 1024 * 1024, // 32 MB
        supportedExtensions: ['.tif', '.tiff', '.png', '.jpg', '.jpeg'],
        version: 'v2.5.0-mvp',
        
        // Helper method to construct full API URLs
        apiUrl: function(endpoint) {
            const cleanEndpoint = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
            if (!this.apiBaseUrl) return cleanEndpoint;
            return this.apiBaseUrl + cleanEndpoint;
        }
    };
})();
