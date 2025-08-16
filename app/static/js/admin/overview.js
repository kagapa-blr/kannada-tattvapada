export function initOverviewTab() {
    fetch('/admin/overview')
        .then(res => res.json())
        .then(data => {
            document.getElementById("totalSamputa").textContent = data.total_samputa;
            document.getElementById("totalTatvapada").textContent = data.total_tatvapada;
            document.getElementById("totalAuthors").textContent = data.total_authors;
            document.getElementById("totalAdmins").textContent = data.total_admins;

            const tbody = document.getElementById("samputaTableBody");
            tbody.innerHTML = "";

            data.tatvapada_per_samputa.forEach(item => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td style="padding: 10px">${item.samputa_sankhye}</td>
                    <td style="padding: 10px">${item.count}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error fetching overview data:", err));
}
