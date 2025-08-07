// static/js/loader.js

export function showLoader() {
    const loader = document.getElementById('global-loader');
    if (loader) loader.classList.remove('d-none');
}

export function hideLoader() {
    const loader = document.getElementById('global-loader');
    if (loader) loader.classList.add('d-none');
}

// 👇 Optional: expose globally for inline testing if needed
window.showLoader = showLoader;
window.hideLoader = hideLoader;
