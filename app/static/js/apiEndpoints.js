// apiEndpoints.js
import { BASE_URL } from "./apiClient.js";

const apiEndpoints = {
    tatvapada: {
        getSamputas: `${BASE_URL}/api/tatvapada/samputas`,
        getAuthorSankhyasBySamputa: (samputaSankhye) =>
            `${BASE_URL}/api/tatvapada/author-sankhyes-by-samputa/${samputaSankhye}`,
        getSpecificTatvapada: (samputa, authorId, sankhye) =>
            `${BASE_URL}/api/tatvapada/${samputa}/${authorId}/${sankhye}`,
        updateTatvapada: `${BASE_URL}/api/tatvapada/update`,
        addTatvapada: `${BASE_URL}/api/tatvapada/add`,
        searchByWord: `${BASE_URL}/api/tatvapada/search`,

        deleteKeys: `${BASE_URL}/api/tatvapada/delete-keys`,
        deleteByComposite: (samputa, sankhya, authorId) =>
            `${BASE_URL}/tatvapada/delete/${samputa}/${sankhya}/${authorId}`,
        deleteByAuthor: (authorName) =>
            `${BASE_URL}/tatvapada/delete-by-author/${encodeURIComponent(authorName)}`,
        deleteBySamputa: (samputa) =>
            `${BASE_URL}/tatvapada/delete-by-samputa/${samputa}`,
        deleteBySamputaAuthor: (samputa, authorName) =>
            `${BASE_URL}/tatvapada/delete-by-samputa-author/${samputa}/${encodeURIComponent(authorName)}`,
        bulkDelete: `${BASE_URL}/bulk-delete`,
        bulkUploadUsingCSV: `${BASE_URL}/tatvapada/bulk-upload`
    },

    auth: {
        signup: `${BASE_URL}/signup`,
        login: `${BASE_URL}/login`,
        logout: `${BASE_URL}/logout`,
        me: `${BASE_URL}/me`
    },

    admin: {
        users: `${BASE_URL}/admin/users`,
        userById: (id) => `${BASE_URL}/admin/users/${id}`,
        overview: `${BASE_URL}/admin/overview`,
        resetPassword: (id) => `${BASE_URL}/admin/users/${id}/reset-password`
    }
};

export default apiEndpoints;
