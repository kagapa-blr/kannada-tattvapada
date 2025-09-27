import apiClient from "../apiClient.js";
import { showLoader, hideLoader } from "../loader.js";

const ShoppingAPI = {
    list: (offset = 0, limit = 10, search = "") => `/shopping/api/v1/orders/catalog?offset=${offset}&limit=${limit}&search=${encodeURIComponent(search)}`,

    add: () => `/shopping/api/v1/orders/catalog`,
    update: (id) => `/shopping/api/v1/orders/catalog/${id}`,
    delete: (id) => `/shopping/api/v1/orders/catalog/${id}`,
    sync: (default_price = 100) => `/shopping/api/v1/orders/catalog/sync?default_price=${default_price}`
};

let shoppingTable;

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
        document.getElementById("shopping_productAuthor").value = product.author_name ?? "";
        document.getElementById("shopping_productSamputa").value = product.samputa_sankhye ?? "";
        document.getElementById("shopping_productTitle").value = product.tatvapadakosha_sheershike ?? "";
        document.getElementById("shopping_productPrice").value = product.price ?? "";
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
        author_name: document.getElementById("shopping_productAuthor").value.trim(),
        samputa_sankhye: document.getElementById("shopping_productSamputa").value.trim(),
        tatvapadakosha_sheershike: document.getElementById("shopping_productTitle").value.trim(),
        price: parseFloat(document.getElementById("shopping_productPrice").value)
    };

    if (!payload.author_name || !payload.samputa_sankhye || !payload.tatvapadakosha_sheershike || isNaN(payload.price)) {
        showShoppingError("All fields are required and price must be a number.");
        return;
    }


    showLoader();
    clearShoppingError();

    try {
        if (id) await apiClient.put(ShoppingAPI.update(id), payload);
        else await apiClient.post(ShoppingAPI.add(), payload);

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
    shoppingTable = $("#shopping_catalogTable").DataTable({
        serverSide: true,
        processing: true,
        responsive: true,
        pageLength: 10,
        lengthMenu: [10, 25, 50],

        ajax: async (data, callback) => {
            showLoader();
            try {
                const searchValue = data.search.value || ""; // DataTables search input value
                const res = await apiClient.get(ShoppingAPI.list(data.start, data.length, searchValue.trim()));
                const items = res.data.items || [];
                const template = document.getElementById("shopping-action-buttons-template").innerHTML;

                const formattedData = items.map((item, index) => [
                    data.start + index + 1,
                    item.samputa_sankhye ?? "--",
                    item.author_name ?? "--",
                    item.tatvapadakosha_sheershike ?? "--",
                    `₹${parseFloat(item.price ?? 0).toFixed(2)}`,
                    template.replace("{{ID}}", item.id)
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


        columnDefs: [{ orderable: false, targets: 5 }]
    });

    // Edit/Delete handlers
    $("#shopping_catalogTable tbody").on("click", ".shopping_edit-btn, .shopping_delete-btn", async function () {
        const row = shoppingTable.row($(this).closest("tr")).data();
        console.log("shopping table : ", row)
        const id = $(this).closest("tr").find("[data-id]").data("id");

        if (this.classList.contains("shopping_edit-btn")) {
            openShoppingModal({
                id,
                samputa_sankhye: row[1],
                author_name: row[2],
                tatvapadakosha_sheershike: row[3],
                price: parseFloat(row[4].replace("₹", ""))
            });
        } else if (this.classList.contains("shopping_delete-btn")) {
            await deleteShoppingProduct(id);
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
