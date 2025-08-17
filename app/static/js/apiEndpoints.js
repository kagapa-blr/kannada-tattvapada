const apiEndpoints = {
    tatvapada: {
        // 🔹 Existing
        getSamputas: "/api/tatvapada/samputas",
        getAuthorSankhyasBySamputa: (samputaSankhye) =>
            `/api/tatvapada/author-sankhyes-by-samputa/${samputaSankhye}`,
        getSpecificTatvapada: (samputa, authorId, sankhye) =>
            `/api/tatvapada/${samputa}/${authorId}/${sankhye}`,
        updateTatvapada: "/api/tatvapada/update",
        addTatvapada: "/api/tatvapada/add",
        searchByWord: "/api/tatvapada/search",

        // 🔹 New delete endpoints
        deleteKeys: "/api/tatvapada/delete-keys",
        deleteByComposite: (samputa, sankhya, authorId) =>
            `/delete/${samputa}/${sankhya}/${authorId}`,
        deleteByAuthor: (authorName) =>
            `/delete-by-author/${encodeURIComponent(authorName)}`,
        deleteBySamputa: (samputa) =>
            `/delete-by-samputa/${samputa}`,
        deleteBySamputaAuthor: (samputa, authorName) =>
            `/delete-by-samputa-author/${samputa}/${encodeURIComponent(authorName)}`,
        bulkDelete: "/bulk-delete",
        bulkUploadUsingCSV: "/bulk-upload"
    },

    auth: {
        signup: "/signup",
        login: "/login"
    },

    admin: {
        users: "/admin/users",            // GET all users / POST new user if needed
        userById: (id) => `/admin/users/${id}`,  // GET, PUT, DELETE specific user
        overview: "/admin/overview"
    }
};

export default apiEndpoints;
