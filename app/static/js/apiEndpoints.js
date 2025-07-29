// static/js/apiEndpoints.js

const apiEndpoints = {
    tatvapada: {
        getSamputas: "/api/tatvapada/samputas",
        getAuthorSankhyasBySamputa: (samputaSankhye) => `/api/tatvapada/author-sankhyes-by-samputa/${samputaSankhye}`,
        getSpecificTatvapada: (samputa, authorId, sankhye) => `/api/tatvapada/${samputa}/${authorId}/${sankhye}`,
        updateTatvapada: "/api/tatvapada/update",
        addTatvapada: "/api/tatvapada/add"
    },
    auth: {
        signup: "/signup",
        login: "/login"
    }
};

export default apiEndpoints;
