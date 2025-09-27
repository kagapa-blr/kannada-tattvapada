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

// ---------- Error Handling ----------
function showShoppingError(message) {
    const container = document.getElementById("shopping-error-container");
    if (container) {
        container.innerHTML = `<div class="alert alert-danger mt-2 rounded-3 shadow-sm">${message}</div>`;
        setTimeout(() => container.innerHTML = "", 5000);
    }
}

function clearShoppingError() {
    const container = document.getElementById("shopping-error-container");
    if (container) container.innerHTML = "";
}

// ---------- Modal ----------
export function openShoppingModal(product = null) {
    const modalLabel = document.getElementById("shopping_productModalLabel");
    const form = document.getElementById("shopping_productForm");
    form.reset();

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
        document.getElementById("shopping_productIdDisplay").setAttribute("readonly", true);
        document.getElementById("shopping_productAuthor").setAttribute("readonly", true);
        document.getElementById("shopping_productSamputa").setAttribute("readonly", true);
        document.getElementById("shopping_productAuthorId").setAttribute("readonly", true);

        modalLabel.innerHTML = `<i class="bi bi-pencil-square me-2"></i> Edit Product`;
    } else {
        modalLabel.innerHTML = `<i class="bi bi-journal-plus me-2"></i> Add Product`;
    }

    new bootstrap.Modal(document.getElementById("shopping_productModal")).show();
}

// ---------- Save ----------
export async function saveShoppingProduct() {
    const id = document.getElementById("shopping_productId").value;
    const payload = {
        id: parseInt(id),
        tatvapada_author_id: parseInt(document.getElementById("shopping_productAuthorId").value),
        samputa_sankhye: document.getElementById("shopping_productSamputa").value.trim(),
        tatvapadakosha_sheershike: document.getElementById("shopping_productTitle").value.trim(),
        price: parseFloat(document.getElementById("shopping_productPrice").value)
    };

    if (!payload.id || !payload.samputa_sankhye || !payload.tatvapadakosha_sheershike || isNaN(payload.price)) {
        showShoppingError("ID, Samputa, Book Title and Price are required, and price must be a number.");
        return;
    }

    showLoader();
    clearShoppingError();

    try {
        await apiClient.put(ShoppingAPI.update(payload.id), payload);
        bootstrap.Modal.getInstance(document.getElementById("shopping_productModal")).hide();
        shoppingTable.ajax.reload();
    } catch (err) {
        console.error(err);
        showShoppingError(err?.response?.data?.message || "Error saving product");
    } finally {
        hideLoader();
    }
}

// ---------- Delete ----------
export async function deleteShoppingProduct(id) {
    if (!confirm("Are you sure you want to delete this product?")) return;
    showLoader();
    clearShoppingError();

    try {
        await apiClient.delete(ShoppingAPI.delete(id));
        shoppingTable.ajax.reload();
    } catch (err) {
        console.error(err);
        showShoppingError(err?.response?.data?.message || "Error deleting product");
    } finally {
        hideLoader();
    }
}

// ---------- Sync ----------
export async function syncShoppingCatalog() {
    showLoader();
    clearShoppingError();

    try {
        await apiClient.get(ShoppingAPI.sync());
        shoppingTable.ajax.reload();
        alert("Catalog synced successfully!");
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
        pageLength: 10,
        lengthMenu: [10, 25, 50],

        ajax: async (data, callback) => {
            showLoader();
            try {
                const searchValue = data.search.value || "";
                const res = await apiClient.get(ShoppingAPI.list(data.start, data.length, searchValue.trim()));
                const items = res.data.items || [];

                // store items in productsMap
                productsMap = {};
                items.forEach(item => {
                    productsMap[item.id] = item;
                });

                const formattedData = items.map((item, index) => [
                    data.start + index + 1,                 // Row #
                    item.samputa_sankhye ?? "--",
                    item.author_name ?? "--",
                    item.tatvapadakosha_sheershike ?? "--",
                    `₹${parseFloat(item.price ?? 0).toFixed(2)}`,
                    // Buttons with data-id directly on buttons
                    `<button class="btn btn-sm btn-outline-primary shopping_edit-btn" data-id="${item.id}" title="Edit Product">
                        <i class="bi bi-pencil-square"></i>
                     </button>
                     <button class="btn btn-sm btn-outline-danger shopping_delete-btn" data-id="${item.id}" title="Delete Product">
                        <i class="bi bi-trash"></i>
                     </button>`
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
            { orderable: false, targets: 5 } // Disable ordering for actions
        ]
    });

    // Edit/Delete handlers
    $("#shopping_catalogTable tbody").off("click").on("click", ".shopping_edit-btn, .shopping_delete-btn", async function () {
        const id = parseInt($(this).attr("data-id"));
        if (!id || !productsMap[id]) return;

        const product = productsMap[id];

        if (this.classList.contains("shopping_edit-btn")) {
            openShoppingModal(product);
        } else if (this.classList.contains("shopping_delete-btn")) {
            await deleteShoppingProduct(product.id);
        }
    });
}

// ---------- Initialize Tab ----------
export function initShoppingCatalogTab() {
    initShoppingCatalogTable();
    document.getElementById("shopping_addProductBtn").addEventListener("click", () => openShoppingModal());
    document.getElementById("shopping_saveProductBtn").addEventListener("click", saveShoppingProduct);
    document.getElementById("shopping_syncCatalogBtn").addEventListener("click", syncShoppingCatalog);
}
