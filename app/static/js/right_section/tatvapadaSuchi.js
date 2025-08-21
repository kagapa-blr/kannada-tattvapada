import apiClient from '../apiClient.js';
import apiEndpoints from '../apiEndpoints.js';

document.addEventListener("DOMContentLoaded", () => {
    const letters = [
        "ಅ", "ಆ", "ಇ", "ಈ", "ಉ", "ಊ", "ಋ", "ೠ", "ಎ", "ಏ", "ಐ", "ಒ", "ಓ", "ಔ",
        "ಕ", "ಖ", "ಗ", "ಘ", "ಙ",
        "ಚ", "ಛ", "ಜ", "ಝ", "ಞ",
        "ಟ", "ಠ", "ಡ", "ಢ", "ಣ",
        "ತ", "ಥ", "ದ", "ಧ", "ನ",
        "ಪ", "ಫ", "ಬ", "ಭ", "ಮ",
        "ಯ", "ರ", "ಲ", "ವ",
        "ಶ", "ಷ", "ಸ", "ಹ", "ಳ"
    ];

    // Initialize DataTable with server-side processing
    function initializeTable() {
        return new DataTable("#tatvapadaTable", {
            processing: true,
            serverSide: true,
            ajax: (data, callback) => {
                const offset = data.start || 0;
                const limit = data.length || 10;
                const search = data.search.value || "";

                apiClient.get(
                    `${apiEndpoints.rightSection.tatvapadaSuchi}?offset=${offset}&limit=${limit}&search=${encodeURIComponent(search)}`
                )
                    .then(res => {
                        callback({
                            recordsTotal: res.total,
                            recordsFiltered: res.total,
                            data: res.data.map(item => ({
                                samputa: item.samputa_sankhye,
                                number: item.tatvapada_sankhye,
                                firstLine: item.tatvapada_first_line,
                                authorId: item.tatvapada_author_id,
                                authorName: item.tatvapadakarara_hesaru
                            }))
                        });
                    })
                    .catch(err => {
                        console.error("Error loading data:", err);
                        callback({ recordsTotal: 0, recordsFiltered: 0, data: [] });
                    });
            },
            pageLength: 10,
            columns: [
                { data: "samputa", title: "ಸಂಪುಟ ಸಂಖ್ಯೆ" },
                { data: "number", title: "ತತ್ವಪದ ಸಂಖ್ಯೆ" },
                { data: "firstLine", title: "ಮೊದಲ ಸಾಲು" },
                { data: "authorName", title: "ತತ್ವಪದಕಾರರ ಹೆಸರು" }
            ],
            language: {
                search: "🔍 ಹುಡುಕಿ:",
                lengthMenu: "_MENU_ ದಾಖಲೆಗಳನ್ನು ತೋರಿಸಿ",
                info: "ಒಟ್ಟು _TOTAL_ ದಾಖಲೆಗಳಲ್ಲಿ _START_ ರಿಂದ _END_ ತೋರಿಸಲಾಗುತ್ತಿದೆ",
                infoEmpty: "ಯಾವುದೇ ದಾಖಲೆಗಳಿಲ್ಲ",
                paginate: {
                    first: "ಮೊದಲ",
                    last: "ಕೊನೆಯ",
                    next: "ಮುಂದೆ",
                    previous: "ಹಿಂದೆ"
                }
            }
        });
    }

    // Show tatvapada details in modal
    function showTatvapadaModal(tatvapadaData) {
        document.getElementById("modalSamputa").textContent = tatvapadaData.samputa_sankhye;
        document.getElementById("modalTatvapadaNumber").textContent = tatvapadaData.tatvapada_sankhye;
        document.getElementById("modalAuthor").textContent = tatvapadaData.tatvapadakarara_hesaru;
        document.getElementById("modalFirstLine").textContent = tatvapadaData.tatvapada_first_line;
        document.getElementById("modalTatvapada").textContent = tatvapadaData.tatvapada || "";
        document.getElementById("modalBhavanuvada").textContent = tatvapadaData.bhavanuvada || "";
        document.getElementById("modalKlishta").textContent = tatvapadaData.klishta_padagalu_artha || "";
        document.getElementById("modalTippani").textContent = tatvapadaData.tippani || "";

        const modal = new bootstrap.Modal(document.getElementById("tatvapadaModal"));
        modal.show();
    }

    // Fetch tatvapada details by keys
    function fetchTatvapadaDetails(samputa, authorId, number) {
        return apiClient.get(apiEndpoints.rightSection.getTatvapada(samputa, authorId, number));
    }

    // Handle row click to fetch and show details
    function attachRowClickListener(table) {
        document.querySelector("#tatvapadaTable tbody").addEventListener("click", (event) => {
            const tr = event.target.closest("tr");
            if (!tr) return;

            const rowData = table.row(tr).data();
            if (!rowData) return;

            fetchTatvapadaDetails(rowData.samputa, rowData.authorId, rowData.number)
                .then(showTatvapadaModal)
                .catch(() => alert("Tatvapada details not found!"));
        });
    }

    // Create Kannada letters grid for search input
    function createLettersGrid(table) {
        const grid = document.getElementById("letters-grid");
        letters.forEach(ch => {
            const btn = document.createElement("button");
            btn.className = "letter-box";
            btn.textContent = ch;
            btn.addEventListener("click", () => {
                const currentSearch = table.search();
                table.search(currentSearch + ch).draw();
            });
            grid.appendChild(btn);
        });
    }

    // Attach clear search button event
    function attachClearSearchListener(table) {
        document.getElementById("clearSearch").addEventListener("click", () => {
            table.search("").draw();
        });
    }

    // Initialization
    const tatvapadaTable = initializeTable();
    attachRowClickListener(tatvapadaTable);
    createLettersGrid(tatvapadaTable);
    attachClearSearchListener(tatvapadaTable);
});
