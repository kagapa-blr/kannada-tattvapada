import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

export async function initOverviewTab() {
    showLoader();
    try {
        const data = await apiClient.get(apiEndpoints.admin.overview);

        // Update stats
        document.getElementById("admin-overview-totalSamputa").textContent = data.total_samputa ?? "--";
        document.getElementById("admin-overview-totalTatvapada").textContent = data.total_tatvapada ?? "--";
        document.getElementById("admin-overview-totalAuthors").textContent = data.total_authors ?? "--";
        document.getElementById("admin-overview-totalAdmins").textContent = data.total_admins ?? "--";

        // Populate samputa table
        const tbody = document.getElementById("admin-overview-samputaTableBody");
        tbody.innerHTML = "";

        (data.tatvapada_per_samputa || []).forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td class="px-3 py-2">${item.samputa_sankhye}</td>
                <td class="px-3 py-2">${item.count}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("initOverviewTab: Error fetching overview data:", err);
    } finally {
        hideLoader();
    }
}
