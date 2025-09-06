import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

// Function to toggle table visibility
window.toggleTable = function (id) {
    const tableWrapper = document.getElementById(id);
    if (tableWrapper) {
        tableWrapper.style.display = tableWrapper.style.display === "none" ? "block" : "none";
    }
};

// Function to show backend errors in a div at the top
function showOverviewError(message) {
    let errorDiv = document.getElementById("admin-overview-error");
    if (!errorDiv) {
        errorDiv = document.createElement("div");
        errorDiv.id = "admin-overview-error";
        errorDiv.className = "alert alert-danger mt-2";
        errorDiv.style.borderRadius = "12px";
        errorDiv.style.boxShadow = "0 2px 6px rgba(0,0,0,0.1)";
        const container = document.getElementById("admin-overview-section");
        container.insertBefore(errorDiv, container.firstChild);
    }
    errorDiv.textContent = message;
}

// Clear error if needed
function clearOverviewError() {
    const errorDiv = document.getElementById("admin-overview-error");
    if (errorDiv) errorDiv.remove();
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

        // Update all cards
        document.getElementById("admin-overview-totalSamputa").textContent = data.total_samputa ?? "--";
        document.getElementById("admin-overview-totalTatvapada").textContent = data.total_tatvapada ?? "--";
        document.getElementById("admin-overview-totalAuthors").textContent = data.total_authors ?? "--";
        document.getElementById("admin-overview-totalAdmins").textContent = data.total_admins ?? "--";
        document.getElementById("admin-overview-totalParibhashika").textContent = data.total_paribhashika ?? "--";
        document.getElementById("admin-overview-totalArthakosha").textContent = data.total_arthakosha ?? "--";
        document.getElementById("admin-overview-totalDocuments").textContent = data.total_documents ?? "--";
        document.getElementById("admin-overview-totalAuthorVivaras").textContent = data.total_author_vivaras ?? "--";

        // Helper to populate tables
        const populateTable = (tbodyId, items, columns) => {
            const tbody = document.getElementById(tbodyId);
            tbody.innerHTML = "";
            (items || []).sort((a, b) => Number(a.samputa_sankhye) - Number(b.samputa_sankhye))
                .forEach((item, index) => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = columns.map(col => `<td>${item[col] ?? "--"}</td>`).join("");
                    // prepend row number
                    tr.innerHTML = `<td>${index + 1}</td>` + tr.innerHTML;
                    tbody.appendChild(tr);
                });
        };

        // Tatvapada per Samputa
        populateTable("admin-overview-samputaTableBody", data.tatvapada_per_samputa, ["samputa_sankhye", "total_tatvapada", "total_authors"]);

        // Paribhashika per Samputa
        populateTable("admin-overview-paribhashikaTableBody", data.paribhashika_per_samputa, ["samputa_sankhye", "count"]);

        // Arthakosha per Samputa
        populateTable("admin-overview-arthakoshaTableBody", data.arthakosha_per_samputa, ["samputa_sankhye", "count"]);

    } catch (err) {
        console.error("Error fetching overview data:", err);
        showOverviewError(`Backend Error: ${err.message || err}`);
    } finally {
        hideLoader();
    }
}
