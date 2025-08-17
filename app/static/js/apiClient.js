// static/js/apiClient.js

//export const BASE_URL = "https://kagapa.com/kannada-tattvapada/";
export const BASE_URL = "http://127.0.0.1:5000";

const defaultHeaders = {
    "Content-Type": "application/json"
};

// Ensure endpoint is always relative (remove accidental leading slashes or full URLs)
const normalizeEndpoint = (endpoint) => {
    try {
        // Strip full URL if mistakenly passed
        const url = new URL(endpoint);
        return url.pathname + url.search;
    } catch {
        // Not a full URL — ensure no leading slash to avoid double slashes in final URL
        return endpoint.replace(/^\/+/, '');
    }
};

const buildUrlWithParams = (endpoint, params = {}) => {
    const normalizedEndpoint = normalizeEndpoint(endpoint);
    const url = new URL(normalizedEndpoint, BASE_URL);

    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
            url.searchParams.append(key, value);
        }
    });

    return url.toString();
};

const apiClient = {
    request: async ({ method, endpoint, body = null, params = {}, headers = {} }) => {
        const url = buildUrlWithParams(endpoint, params);
        const options = {
            method: method.toUpperCase(),
            headers: { ...defaultHeaders, ...headers }
        };

        if (body && method.toUpperCase() !== "GET") {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`${method.toUpperCase()} ${url} failed: ${errorText}`);
        }

        const contentType = response.headers.get("content-type");
        return contentType && contentType.includes("application/json")
            ? await response.json()
            : await response.text();
    },

    get: (endpoint, params = {}, headers = {}) =>
        apiClient.request({ method: "GET", endpoint, params, headers }),

    post: (endpoint, body = {}, headers = {}) =>
        apiClient.request({ method: "POST", endpoint, body, headers }),

    put: (endpoint, body = {}, headers = {}) =>
        apiClient.request({ method: "PUT", endpoint, body, headers }),

    patch: (endpoint, body = {}, headers = {}) =>
        apiClient.request({ method: "PATCH", endpoint, body, headers }),

    delete: (endpoint, body = {}, headers = {}) =>
        apiClient.request({ method: "DELETE", endpoint, body, headers })
};

export default apiClient;
