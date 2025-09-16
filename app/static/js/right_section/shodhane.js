import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";

let dataTable = null;
let samputaData = [];

// Escape HTML
const escapeHtml = txt =>
    txt ? txt.replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m])) : "";

// Highlight whole word safely (handles Kannada/Unicode)
const highlight = (txt, keyword) => {
    if (!txt || !keyword) return escapeHtml(txt);

    const escapedKeyword = keyword.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

    // Zero Width Non-Joiner safe regex
    // Match whole word: start of string or whitespace or punctuation, then keyword, then end of string/whitespace/punctuation
    const regex = new RegExp(`(?:(?<=^|\\s|[.,!?;:]))${escapedKeyword}(?=(\\s|$|[.,!?;:]))`, "gu");

    return escapeHtml(txt).replace(regex, m => `<span class="highlight">${m}</span>`);
};


// Load samputa & authors
async function loadSamputaAuthors() {
    try {
        const resp = await apiClient.get(apiEndpoints.admin.samputaAuthor);
        samputaData = resp.data || [];

        const samputaSelect = document.getElementById("samputaSelect");
        samputaSelect.innerHTML = `<option value="">ಎಲ್ಲಾ ಸಂಪುಟಗಳು</option>`;

        samputaData.forEach(s =>
            samputaSelect.insertAdjacentHTML("beforeend", `<option value="${s.samputa}">ಸಂಪುಟ ${s.samputa}</option>`)
        );
    } catch (err) {
        console.error("Samputa load error:", err);
    }
}

// Populate authors dynamically
function populateAuthors(samputa) {
    const authorSelect = document.getElementById("authorSelect");
    authorSelect.innerHTML = `<option value="">ಎಲ್ಲಾ ತತ್ವಪದಕಾರರು</option>`;

    const match = samputaData.find(s => s.samputa === samputa);
    match?.authors?.forEach(a =>
        authorSelect.insertAdjacentHTML("beforeend", `<option value="${a.id}">${a.name}</option>`)
    );
}

// Initialize DataTable
function initDataTable(keyword, samputa, authorId) {
    if (dataTable) {
        dataTable.destroy();
        document.querySelector("#searchResultsTable tbody").innerHTML = "";
    }

    dataTable = $("#searchResultsTable").DataTable({
        serverSide: true,
        processing: true,
        searching: false,
        scrollX: true, // ✅ makes table horizontally scrollable on mobile
        ajax: async (data, cb) => {
            try {
                const { start: offset, length: limit, draw } = data;
                const res = await apiClient.post(apiEndpoints.tatvapada.searchByWord, {
                    keyword,
                    samputa: samputa || null,
                    author_id: authorId || null,
                    offset,
                    limit
                });

                cb({
                    draw,
                    recordsTotal: res.pagination.total,
                    recordsFiltered: res.pagination.total,
                    data: res.results
                });

                document.getElementById("resultCount").textContent = `ಒಟ್ಟು ತತ್ವಪದಗಳು: ${res.pagination.total}`;
            } catch (err) {
                document.getElementById("resultCount").innerHTML = `<span class="text-danger">ದೋಷ: ${escapeHtml(err.message)}</span>`;
                cb({ draw: data.draw, recordsTotal: 0, recordsFiltered: 0, data: [] });
            }
        },
        columns: [
            { data: "samputa_sankhye" },
            //  { data: "tatvapadakarara_hesaru", render: d => highlight(d, keyword) },
            { data: "tatvapadakarara_hesaru" }, // no highlight
            { data: "tatvapada_sankhye" },
            { data: "tatvapadakosha_sheershike" },
            { data: "tatvapada_sheershike" },
            { data: "tatvapada_first_line" },
            { data: "vibhag" }
        ],
        pageLength: 10,
        language: {
            zeroRecords: "ಫಲಿತಾಂಶಗಳಿಲ್ಲ",
            info: "_TOTAL_ ದಾಖಲೆಗಳಲ್ಲಿ _START_ - _END_ ತೋರಿಸಲಾಗುತ್ತಿದೆ",
            paginate: { first: "ಮೊದಲ", last: "ಕೊನೆಯ", next: "ಮುಂದೆ", previous: "ಹಿಂದೆ" }
        }
    });

    // Row click → show details modal
    $("#searchResultsTable tbody").off("click").on("click", "tr", function () {
        const row = dataTable.row(this).data();
        if (row) showDetails(row, keyword);
    });
}

// Show details in modal
function showDetails(row, keyword) {
    document.getElementById("detail_samputa").textContent = row.samputa_sankhye || "";
    //document.getElementById("detail_author").innerHTML = highlight(row.tatvapadakarara_hesaru, keyword);
    document.getElementById("detail_author").textContent = row.tatvapadakarara_hesaru || "";
    document.getElementById("detail_number").textContent = row.tatvapada_sankhye || "";
    document.getElementById("detail_kosha").textContent = row.tatvapadakosha_sheershike || "";
    document.getElementById("detail_title").textContent = row.tatvapada_sheershike || "";
    document.getElementById("detail_first_line").textContent = row.tatvapada_first_line || "";
    document.getElementById("detail_vibhag").textContent = row.vibhag || "";
    document.getElementById("detail_tatvapada").innerHTML = highlight(row.tatvapada, keyword);
    document.getElementById("detail_bhavanuvada").innerHTML = highlight(row.bhavanuvada, keyword);

    new bootstrap.Modal(document.getElementById("detailsModal")).show();
}

// Setup copy buttons
function setupCopy(btnId, targetId) {
    const btn = document.getElementById(btnId);
    btn.onclick = () => {
        const text = document.getElementById(targetId).innerText.trim();
        if (!text) return alert("ಯಾವುದೇ ಪಠ್ಯ ಇಲ್ಲ");

        navigator.clipboard.writeText(text).then(() => {
            btn.textContent = "✅ Copied!";
            setTimeout(() => (btn.textContent = "📋 Copy"), 1500);
        });
    };
}

// Handle search
function handleSearch() {
    const keyword = document.getElementById("searchKeyword").value.trim();
    const samputa = document.getElementById("samputaSelect").value;
    const author = document.getElementById("authorSelect").value;

    if (!keyword) return alert("ಪದವನ್ನು ನಮೂದಿಸಿ");
    initDataTable(keyword, samputa, author);
}

// Init everything
document.addEventListener("DOMContentLoaded", () => {
    loadSamputaAuthors();
    document.getElementById("samputaSelect").onchange = e => populateAuthors(e.target.value);
    document.getElementById("btnSearch").onclick = handleSearch;
    document.getElementById("searchKeyword").addEventListener("keypress", e => {
        if (e.key === "Enter") handleSearch();
    });

    setupCopy("copyTatvapadaBtn", "detail_tatvapada");
    setupCopy("copyBhavanuvadaBtn", "detail_bhavanuvada");

    // Fix backdrop stuck issue
    document.addEventListener("hidden.bs.modal", () => {
        document.querySelectorAll(".modal-backdrop").forEach(el => el.remove());
        document.body.classList.remove("modal-open");
        document.body.style.removeProperty("overflow");
        document.body.style.removeProperty("padding-right");
    });
});
