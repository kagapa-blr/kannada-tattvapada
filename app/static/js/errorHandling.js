import { BASE_URL } from './apiClient.js';

/**
 * Redirects to the home page immediately
 */
function goHome() {
    window.location.href = BASE_URL + "/";
}

// Expose globally for onclick
window.goHome = goHome;
