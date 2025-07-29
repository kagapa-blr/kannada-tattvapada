// static/js/apiClient.js

export const BASE_URL = "http://127.0.0.1:5000";

const defaultHeaders = {
    "Content-Type": "application/json"
};

const buildUrlWithParams = (endpoint, params = {}) => {
    const url = new URL(`${BASE_URL}${endpoint}`);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
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
            throw new Error(`${method.toUpperCase()} ${endpoint} failed: ${errorText}`);
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
