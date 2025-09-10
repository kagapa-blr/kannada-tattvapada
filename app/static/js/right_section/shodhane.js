import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

let dataTable = null;
let samputaData = [];

// Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"'`=\/]/g, s => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;", "/": "&#x2F;", "`": "&#x60;", "=": "&#x3D;" }[s]));
}

// Highlight keyword
function highlightKeyword(text, keyword) {
    if (!keyword) return escapeHtml(text);
    const escapedKeyword = keyword.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    const trailingCombining = '(?:[\u0CCD\\p{M}])*';
    const regex = new RegExp(`(${escapedKeyword}${trailingCombining})`, 'giu');
    return escapeHtml(text).replace(regex, '<span style="background-color: yellow; color: black; font-weight: bold">$1</span>');
}

// Load Samputa + Authors
async function loadSamputaAuthors() {
    try {
        const resp = await apiClient.get(apiEndpoints.admin.samputaAuthor);
        samputaData = resp.data || [];

        const samputaSelect = document.getElementById("samputaSelect");
        samputaSelect.innerHTML = `<option value="">ಎಲ್ಲಾ ಸಂಪುಟಗಳು</option>`;
        samputaData.forEach(item => {
            const opt = document.createElement("option");
            opt.value = item.samputa;
            opt.textContent = `ಸಂಪುಟ ${item.samputa}`;
            samputaSelect.appendChild(opt);
        });

        populateAuthors(""); // default
    } catch (err) {
        console.error("Samputa/Authors load error:", err);
    }
}

// Populate authors based on selected samputa
function populateAuthors(selectedSamputa) {
    const authorSelect = document.getElementById("authorSelect");
    authorSelect.innerHTML = `<option value="">ಎಲ್ಲಾ ತತ್ವಪದಕಾರರು</option>`;
    if (!selectedSamputa) return;
    const match = samputaData.find(s => s.samputa === selectedSamputa);
    if (match?.authors) {
        match.authors.forEach(a => {
            const opt = document.createElement("option");
            opt.value = a.id;
            opt.textContent = a.name;
            authorSelect.appendChild(opt);
        });
    }
}

// Initialize DataTable
function initDataTable(keyword, samputa, authorId) {
    if (dataTable) {
        dataTable.destroy();
        $('#searchResultsTable').empty();
    }

    dataTable = $('#searchResultsTable').DataTable({
        serverSide: true,
        processing: true,
        searching: false,
        ajax: async (data, callback) => {
            showLoader();
            try {
                const offset = data.start || 0;
                const limit = data.length || 10;

                const response = await apiClient.post(apiEndpoints.tatvapada.searchByWord, {
                    keyword,
                    samputa: samputa || null,
                    author_id: authorId || null,
                    offset,
                    limit
                });

                callback({
                    draw: data.draw,
                    recordsTotal: response.pagination.total,
                    recordsFiltered: response.pagination.total,
                    data: response.results
                });

                document.getElementById("resultCount").innerHTML =
                    `ಒಟ್ಟು ತತ್ವಪದಗಳು: ${response.pagination.total}`;
            } catch (err) {
                document.getElementById("resultCount").innerHTML =
                    `<p class="text-danger">ಶೋಧನೆಯಲ್ಲಿ ದೋಷ: ${escapeHtml(err.message)}</p>`;
                callback({ draw: data.draw, recordsTotal: 0, recordsFiltered: 0, data: [] });
            } finally { hideLoader(); }
        },
        columns: [
            { data: "samputa_sankhye" },
            { data: "tatvapadakarara_hesaru", render: d => highlightKeyword(d, keyword) },
            { data: "tatvapada_sankhye" },
            { data: "tatvapadakosha_sheershike" },
            { data: "tatvapada_sheershike" },
            { data: "tatvapada_first_line" },
            { data: "vibhag" }
        ],
        pageLength: 10,
        language: {
            lengthMenu: "_MENU_ ದಾಖಲೆಗಳು",
            zeroRecords: "ಯಾವುದೇ ಫಲಿತಾಂಶಗಳು ಸಿಕ್ಕಿಲ್ಲ",
            info: "_TOTAL_ ದಾಖಲೆಗಳಲ್ಲಿ _START_ ರಿಂದ _END_ ತೋರಿಸಲಾಗುತ್ತಿದೆ",
            infoEmpty: "ಯಾವುದೇ ದಾಖಲೆಗಳಿಲ್ಲ",
            paginate: { first: "ಮೊದಲ", last: "ಕೊನೆಯ", next: "ಮುಂದೆ", previous: "ಹಿಂದೆ" }
        }
    });

    // Row click → modal
    $('#searchResultsTable tbody').on('click', 'tr', function () {
        const rowData = dataTable.row(this).data();
        if (rowData) showDetailsModal(rowData, keyword);
    });
}

// Show details modal
function showDetailsModal(rowData, keyword) {
    document.getElementById("detail_samputa").innerText = rowData.samputa_sankhye || "";
    document.getElementById("detail_author").innerHTML = highlightKeyword(rowData.tatvapadakarara_hesaru || "", keyword);
    document.getElementById("detail_number").innerText = rowData.tatvapada_sankhye || "";
    document.getElementById("detail_kosha").innerText = rowData.tatvapadakosha_sheershike || "";
    document.getElementById("detail_title").innerText = rowData.tatvapada_sheershike || "";
    document.getElementById("detail_first_line").innerText = rowData.tatvapada_first_line || "";
    document.getElementById("detail_vibhag").innerText = rowData.vibhag || "";
    document.getElementById("detail_tatvapada").innerHTML = highlightKeyword(rowData.tatvapada || "", keyword);
    document.getElementById("detail_bhavanuvada").innerHTML = highlightKeyword(rowData.bhavanuvada || "", keyword);

    new bootstrap.Modal(document.getElementById("detailsModal")).show();
}

// Handle Search
function handleSearchClick() {
    const keyword = document.getElementById("searchKeyword").value.trim();
    const samputa = document.getElementById("samputaSelect").value;
    const authorId = document.getElementById("authorSelect").value;

    if (!keyword) { alert("ಶೋಧನೆಗಾಗಿ ಪದವನ್ನು ನಮೂದಿಸಿ."); return; }

    initDataTable(keyword, samputa, authorId);
}

// DOM Ready
document.addEventListener("DOMContentLoaded", () => {
    loadSamputaAuthors();
    document.getElementById("samputaSelect").addEventListener("change", e => populateAuthors(e.target.value));
    document.getElementById("btnSearch").onclick = handleSearchClick;
});
