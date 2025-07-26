// ManageApi.js

const BASE_URL = "http://127.0.0.1:5000/api";

const defaultHeaders = {
    "Content-Type": "application/json",
    // Add any auth headers here if needed
    // "Authorization": "Bearer <token>"
};

const apiClient = {
    get: async (endpoint) => {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method: "GET",
            headers: defaultHeaders,
        });
        if (!response.ok) {
            throw new Error(`GET ${endpoint} failed`);
        }
        return await response.json();
    },

    post: async (endpoint, body) => {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method: "POST",
            headers: defaultHeaders,
            body: JSON.stringify(body),
        });
        if (!response.ok) {
            throw new Error(`POST ${endpoint} failed`);
        }
        return await response.json();
    },

    // Add put/delete if needed later
};

export default apiClient;
