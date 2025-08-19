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

        // Populate table
        const tbody = document.getElementById("admin-overview-samputaTableBody");
        tbody.innerHTML = "";

        // ✅ Sort by samputa_sankhye (convert to number for correct sorting)
        const sortedSamputas = (data.tatvapada_per_samputa || []).sort(
            (a, b) => Number(a.samputa_sankhye) - Number(b.samputa_sankhye)
        );

        sortedSamputas.forEach((item, index) => {
            const tr = document.createElement("tr");
            tr.style.cursor = "pointer";
            tr.onmouseover = () => (tr.style.backgroundColor = "#f1f5ff");
            tr.onmouseout = () => (tr.style.backgroundColor = "");
            tr.innerHTML = `
                <td class="px-3 py-2">${index + 1}</td>
                <td class="px-3 py-2">ಸಂಪುಟ ${item.samputa_sankhye}</td>
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
