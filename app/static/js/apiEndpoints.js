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
        deleteBySamputaAuthor: (samputa, authorId) =>
            `${BASE_URL}/delete-by-samputa-author/${samputa}/${authorId}`,
        bulkDelete: `${BASE_URL}/bulk-delete`,
        bulkUploadUsingCSV: `${BASE_URL}/bulk-upload`
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
        resetPassword: (id) => `${BASE_URL}/admin/users/${id}/reset-password`,

        //---------------------
        samputaAuthor: `${BASE_URL}/api/v1/right-section/samputa-authors`,
        manageTippani: `${BASE_URL}/api/v1/right-section/tippani`,
        manageArthakosha: `${BASE_URL}/api/v1/right-section/arthakosha`,
        manageParibhashika: `${BASE_URL}/api/v1/right-section/padavivarana`


    },
    documents: {
        list: `${BASE_URL}/api/documents/`,
        create: `${BASE_URL}/api/documents`,
        getById: (id) => `${BASE_URL}/api/documents/${id}`,
        update: (id) => `${BASE_URL}/api/documents/${id}`,
        delete: (id) => `${BASE_URL}/api/documents/${id}`
    },
    rightSectionUI: {
        tatvapadaSuchi: `${BASE_URL}/right-section/tatvapada_suchi`,
        tippani: `${BASE_URL}/right-section/tippani`,
        arthakosha: `${BASE_URL}/right-section/arthakosha`,
        sampadakaraNudi: `${BASE_URL}/right-section/user_document`,
    },

    rightSection: {
        padavivaranaApi: `${BASE_URL}/api/v1/right-section/padavivarana`,
        tippaniApiUpload: `${BASE_URL}/api/v1/right-section/upload-tippani`,
        padavivaranaApiUpload: `${BASE_URL}/api/v1/right-section/upload-padavivarana`,
        arthakoshaApi: `${BASE_URL}/api/v1/right-section/arthakosha`,
        arthakoshaApiUpload: `${BASE_URL}/api/v1/right-section/upload-arthakosha`,
        tatvapadaSuchi: `${BASE_URL}/api/v1/right-section/tatvapadasuchi`,
        getTatvapada: (samputa, authorId, sankhye) =>
            `${BASE_URL}/api/v1/right-section/tatvapada?samputa_sankhye=${samputa}&tatvapada_author_id=${authorId}&tatvapada_sankhye=${sankhye}`,
        arthakosha: `${BASE_URL}/arthakosha`,
        tippani: `${BASE_URL}/tippani`,
        tatvapadakaraVivarane: `${BASE_URL}/tatvapadakara_vivarane`,
        pradhanaSampadakaruNudi: `${BASE_URL}/pradhana_sampadakaru_nudi`,
        samputaSampadakaruNudi: `${BASE_URL}/user_document`,
        paramarshanaSahitya: `${BASE_URL}/paramarshana_sahitya`
    },

    authors: {
        list: `${BASE_URL}/api/v1/authors`,               // GET all (id + name only)
        create: `${BASE_URL}/api/v1/authors`,             // POST
        getById: (id) => `${BASE_URL}/api/v1/authors/${id}`, // GET single
        update: (id) => `${BASE_URL}/api/v1/authors/${id}`,  // PUT
        delete: (id) => `${BASE_URL}/api/v1/authors/${id}`   // DELETE
    }

};

export default apiEndpoints;
