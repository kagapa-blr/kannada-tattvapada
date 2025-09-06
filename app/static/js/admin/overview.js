import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

// Function to show backend errors in a div at the top
function showOverviewError(message) {
    const container = document.getElementById("admin-overview-error-container");
    if (container) {
        container.innerHTML = `<div class="alert alert-danger mt-2 rounded-3 shadow-sm">${message}</div>`;
    }
}

// Clear error if needed
function clearOverviewError() {
    const container = document.getElementById("admin-overview-error-container");
    if (container) container.innerHTML = "";
}

// Helper to populate tables
function populateTable(tbodyId, items, columns) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    tbody.innerHTML = "";

    (items || [])
        .sort((a, b) => Number(a.samputa_sankhye || 0) - Number(b.samputa_sankhye || 0))
        .forEach((item, index) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `<td>${index + 1}</td>` + columns.map(col => `<td>${item[col] ?? "--"}</td>`).join("");
            tbody.appendChild(tr);
        });
}

export async function initOverviewTab() {
    showLoader();
    clearOverviewError();

    try {
        const response = await apiClient.get(apiEndpoints.admin.overview);

        if (!response.success) {
            showOverviewError(response.error || "Something went wrong while fetching dashboard data.");
            return;
        }

        const data = response.data;

        // Update all cards instantly
        document.getElementById("admin-overview-total-samputa").textContent = data.total_samputa ?? "--";
        document.getElementById("admin-overview-total-tatvapada").textContent = data.total_tatvapada ?? "--";
        document.getElementById("admin-overview-total-authors").textContent = data.total_authors ?? "--";
        document.getElementById("admin-overview-total-admins").textContent = data.total_admins ?? "--";
        document.getElementById("admin-overview-total-paribhashika").textContent = data.total_paribhashika ?? "--";
        document.getElementById("admin-overview-total-arthakosha").textContent = data.total_arthakosha ?? "--";
        document.getElementById("admin-overview-total-documents").textContent = data.total_documents ?? "--";
        document.getElementById("admin-overview-total-author-vivaras").textContent = data.total_author_vivaras ?? "--";

        // Populate tables
        populateTable(
            "admin-overview-samputa-body",
            data.tatvapada_per_samputa,
            ["samputa_sankhye", "total_tatvapada", "total_authors"]
        );

        populateTable(
            "admin-overview-paribhashika-body",
            data.paribhashika_per_samputa,
            ["samputa_sankhye", "count"]
        );

        populateTable(
            "admin-overview-arthakosha-body",
            data.arthakosha_per_samputa,
            ["samputa_sankhye", "count"]
        );

    } catch (err) {
        console.error("Error fetching overview data:", err);
        showOverviewError(`Backend Error: ${err.message || err}`);
    } finally {
        hideLoader();
    }
}
