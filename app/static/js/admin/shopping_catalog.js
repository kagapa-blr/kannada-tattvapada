import apiClient from "../apiClient.js";
import { showLoader, hideLoader } from "../loader.js";

const ShoppingAPI = {
    list: (offset = 0, limit = 10, search = "") =>
        `/shopping/api/v1/orders/catalog?offset=${offset}&limit=${limit}&search=${encodeURIComponent(search)}`,
    update: (id) => `/shopping/api/v1/orders/catalog/${id}`,
    delete: (id) => `/shopping/api/v1/orders/catalog/${id}`,
    sync: (default_price = 100) => `/shopping/api/v1/orders/catalog/sync?default_price=${default_price}`
};

let shoppingTable;
let productsMap = {}; // store products keyed by ID


// ---------- Toast ----------
function showToast(message, isSuccess = true) {
    const toastEl = document.getElementById("shopping_toast");
    const toastBody = document.getElementById("shopping_toast_body");

    toastBody.innerText = message;
    toastEl.className = `toast align-items-center text-white border-0 ${isSuccess ? "bg-success" : "bg-danger"}`;
    new bootstrap.Toast(toastEl).show();
}

// ---------- Error Handling ----------
function showShoppingError(message) {
    showToast(message, false);
}

// ---------- Modal ----------
export function openShoppingModal(product = null) {
    const modalLabel = document.getElementById("shopping_productModalLabel");
    const form = document.getElementById("shopping_productForm");
    form.reset();

    const readonlyStyle = "background-color:#f5f5f5; color:#6c757d; cursor:not-allowed;";

    if (product) {
        document.getElementById("shopping_productId").value = product.id;
        document.getElementById("shopping_productIdDisplay").value = product.id;
        document.getElementById("shopping_productAuthorId").value = product.tatvapada_author_id;
        document.getElementById("shopping_productAuthor").value = product.author_name;
        document.getElementById("shopping_productSamputa").value = product.samputa_sankhye;
        document.getElementById("shopping_productTitle").value = product.tatvapadakosha_sheershike;
        document.getElementById("shopping_productPrice").value = product.price;

        // Editable only Book Title & Price
        document.getElementById("shopping_productTitle").removeAttribute("readonly");
        document.getElementById("shopping_productPrice").removeAttribute("readonly");

        // Read-only fields
        ["shopping_productIdDisplay", "shopping_productAuthor", "shopping_productSamputa", "shopping_productAuthorId"]
            .forEach(id => {
                const el = document.getElementById(id);
                el.setAttribute("readonly", true);
                el.style = readonlyStyle;
            });

        modalLabel.innerHTML = `<i class="bi bi-pencil-square me-2"></i> Edit Product`;
    } else {
        modalLabel.innerHTML = `<i class="bi bi-journal-plus me-2"></i> Add Product`;
    }

    new bootstrap.Modal(document.getElementById("shopping_productModal")).show();
}

// ---------- Save ---------- (with confirmation modal)
let pendingSave = null;

export function prepareSaveProduct() {
    const id = document.getElementById("shopping_productId").value;
    pendingSave = {
        id: parseInt(id),
        tatvapada_author_id: parseInt(document.getElementById("shopping_productAuthorId").value),
        samputa_sankhye: document.getElementById("shopping_productSamputa").value.trim(),
        tatvapadakosha_sheershike: document.getElementById("shopping_productTitle").value.trim(),
        price: parseFloat(document.getElementById("shopping_productPrice").value)
    };

    if (!pendingSave.id || !pendingSave.samputa_sankhye || !pendingSave.tatvapadakosha_sheershike || isNaN(pendingSave.price)) {
        showShoppingError("ID, Samputa, Book Title and Price are required, and price must be a number.");
        return;
    }

    new bootstrap.Modal(document.getElementById("shopping_saveConfirmModal")).show();
}

export async function confirmSaveProduct() {
    if (!pendingSave) return;
    bootstrap.Modal.getInstance(document.getElementById("shopping_saveConfirmModal")).hide();
    showLoader();

    try {
        await apiClient.put(ShoppingAPI.update(pendingSave.id), pendingSave);
        bootstrap.Modal.getInstance(document.getElementById("shopping_productModal")).hide();
        shoppingTable.ajax.reload();
        showToast("Product saved successfully!");
    } catch (err) {
        console.error(err);
        showShoppingError(err?.response?.data?.message || "Error saving product");
    } finally {
        hideLoader();
        pendingSave = null;
    }
}

// ---------- Delete ---------- (with confirmation modal)
let deleteProductId = null;

export function prepareDeleteProduct(id) {
    deleteProductId = id;
    new bootstrap.Modal(document.getElementById("shopping_deleteConfirmModal")).show();
}


export async function confirmDeleteProduct() {
    if (!deleteProductId) return;

    // Hide modal safely
    bootstrap.Modal.getOrCreateInstance(document.getElementById("shopping_deleteConfirmModal")).hide();
    showLoader();

    try {
        await apiClient.delete(ShoppingAPI.delete(deleteProductId));
        shoppingTable.ajax.reload();
        showToast("Product deleted successfully!");
    } catch (err) {
        console.error(err);
        showShoppingError(err?.response?.data?.message || "Error deleting product");
    } finally {
        hideLoader();
        deleteProductId = null;
    }
}


// ---------- Sync ----------
export async function syncShoppingCatalog() {
    showLoader();

    try {
        await apiClient.get(ShoppingAPI.sync());
        shoppingTable.ajax.reload();
        showToast("Catalog synced successfully!");
    } catch (err) {
        console.error(err);
        showShoppingError(err?.response?.data?.message || "Error syncing catalog");
    } finally {
        hideLoader();
    }
}

// ---------- Initialize DataTable ----------
export function initShoppingCatalogTable() {
    if ($.fn.DataTable.isDataTable("#shopping_catalogTable")) {
        $("#shopping_catalogTable").DataTable().destroy();
    }

    shoppingTable = $("#shopping_catalogTable").DataTable({
        serverSide: true,
        processing: true,
        responsive: true,
        scrollX: true,
        pageLength: 10,
        lengthMenu: [10, 25, 50],
        ajax: async (data, callback) => {
            showLoader();
            try {
                const searchValue = data.search.value || "";
                const res = await apiClient.get(ShoppingAPI.list(data.start, data.length, searchValue.trim()));
                const items = res.data.items || [];

                productsMap = {};
                items.forEach(item => productsMap[item.id] = item);

                const formattedData = items.map((item, index) => [
                    data.start + index + 1,
                    item.samputa_sankhye ?? "--",
                    item.author_name ?? "--",
                    item.tatvapadakosha_sheershike ?? "--",
                    `₹${parseFloat(item.price ?? 0).toFixed(2)}`,
                    `<div class="d-flex justify-content-center gap-1">
                        <button class="btn btn-sm btn-outline-primary shopping_edit-btn" data-id="${item.id}" title="Edit Product">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger shopping_delete-btn" data-id="${item.id}" title="Delete Product">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>`
                ]);

                callback({
                    draw: data.draw,
                    recordsTotal: res.data.total || 0,
                    recordsFiltered: res.data.total || 0,
                    data: formattedData
                });
            } catch (err) {
                console.error(err);
            } finally {
                hideLoader();
            }
        },
        columnDefs: [
            { orderable: false, targets: 5 },
            { className: "text-center", targets: [0, 5] },
            { className: "text-end", targets: [4] }
        ]
    });

    $("#shopping_catalogTable tbody").off("click").on("click", ".shopping_edit-btn", function () {
        const id = parseInt($(this).attr("data-id"));
        if (!id || !productsMap[id]) return;
        openShoppingModal(productsMap[id]);
    });

    $("#shopping_catalogTable tbody").on("click", ".shopping_delete-btn", function () {
        const id = parseInt($(this).attr("data-id"));
        if (!id || !productsMap[id]) return;
        prepareDeleteProduct(id);
    });
}

// ---------- Initialize Tab ----------
export function initShoppingCatalogTab() {
    initShoppingCatalogTable();
    document.getElementById("shopping_addProductBtn").addEventListener("click", () => openShoppingModal());
    document.getElementById("shopping_saveProductBtn").addEventListener("click", prepareSaveProduct);
    document.getElementById("confirmSaveBtn").addEventListener("click", confirmSaveProduct);
    document.getElementById("shopping_confirmDeleteBtn").addEventListener("click", confirmDeleteProduct);
    document.getElementById("shopping_syncCatalogBtn").addEventListener("click", syncShoppingCatalog);
}
