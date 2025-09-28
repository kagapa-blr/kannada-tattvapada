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
        sampadakaraNudi: `${BASE_URL}/right-section/sampadakaru_nudi`,
        tatvapadakara_vivarane: `${BASE_URL}/right-section/tatvapadakara_vivarane`,
        tatvapadaShodhane: `${BASE_URL}/right-section/shodhane`,
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
    },


    shopping: {
        // ---------------------------------
        // ShoppingUser APIs
        // ---------------------------------
        createUser: `${BASE_URL}/shopping/api/v1/users`,               // POST
        getUserByEmail: (email) => `${BASE_URL}/shopping/api/v1/users/${email}`,  // GET
        updateUserByEmail: (email) => `${BASE_URL}/shopping/api/v1/users/${email}`,  // PUT
        deleteUserByEmail: (email) => `${BASE_URL}/shopping/api/v1/users/${email}`,  // DELETE
        listUsers: `${BASE_URL}/shopping/api/v1/users`,               // GET, ?limit=100&offset=0

        // ---------------------------------
        // ShoppingUserAddress APIs
        // ---------------------------------
        listAddressesByEmail: (email) => `${BASE_URL}/shopping/api/v1/users/${email}/addresses`, // GET
        createAddress: (email) => `${BASE_URL}/shopping/api/v1/users/${email}/addresses`, // POST
        updateAddress: (id) => `${BASE_URL}/shopping/api/v1/addresses/${id}`,          // PUT
        deleteAddress: (id) => `${BASE_URL}/shopping/api/v1/addresses/${id}`,          // DELETE

        // -----------------------------
        // ShoppingOrder API Endpoints
        // -----------------------------
        listOrdersByEmail: (email, limit = 100, offset = 0) =>
            `${BASE_URL}/shopping/api/v1/users/${email}/orders?limit=${limit}&offset=${offset}`, // GET

        createOrder: (email) =>
            `${BASE_URL}/shopping/api/v1/users/${email}/orders`, // POST

        updateOrder: (orderId) =>
            `${BASE_URL}/shopping/api/v1/orders/${orderId}`, // PUT

        deleteOrder: (orderId) =>
            `${BASE_URL}/shopping/api/v1/orders/${orderId}`, // DELETE



        // Admin Manage shopping
        shoppingList: (offset = 0, limit = 10, search = "") => `${BASE_URL}/shopping/api/v1/orders/catalog?offset=${offset}&limit=${limit}&search=${encodeURIComponent(search)}`,
        shoppingUpdate: (id) => `${BASE_URL}/shopping/api/v1/orders/catalog/${id}`,
        shoppingDelete: (id) => `${BASE_URL}/shopping/api/v1/orders/catalog/${id}`,
        shoppingSync: (default_price = 100) => `${BASE_URL}/shopping/api/v1/orders/catalog/sync?default_price=${default_price}`
    },



};

export default apiEndpoints;
