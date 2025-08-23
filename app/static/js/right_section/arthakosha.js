import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";

document.addEventListener("DOMContentLoaded", async () => {
    const letters = [
        "ಅ", "ಆ", "ಇ", "ಈ", "ಉ", "ಊ", "ಋ", "ೠ", "ಎ", "ಏ", "ಐ", "ಒ", "ಓ", "ಔ",
        "ಕ", "ಖ", "ಗ", "ಘ", "ಙ", "ಚ", "ಛ", "ಜ", "ಝ", "ಞ",
        "ಟ", "ಠ", "ಡ", "ಢ", "ಣ", "ತ", "ಥ", "ದ", "ಧ", "ನ",
        "ಪ", "ಫ", "ಬ", "ಭ", "ಮ", "ಯ", "ರ", "ಲ", "ವ",
        "ಶ", "ಷ", "ಸ", "ಹ", "ಳ"
    ];

    // Initialize DataTable for Arthakosha
    const table = new DataTable("#arthakoshaTable", {
        processing: true,
        serverSide: true,
        ajax: async (data, callback) => {
            const offset = data.start || 0;
            const limit = data.length || 50;
            const search = data.search.value || "";

            try {
                const res = await apiClient.get(
                    `${apiEndpoints.rightSection.arthakoshaApi}?offset=${offset}&limit=${limit}&search=${encodeURIComponent(search)}`
                );

                callback({
                    recordsTotal: res.total || 0,
                    recordsFiltered: res.total || 0,
                    data: res.results || []
                });
            } catch (err) {
                console.error("Error loading Arthakosha list:", err);
                callback({ recordsTotal: 0, recordsFiltered: 0, data: [] });
            }
        },
        columns: [
            { data: "samputa" },
            { data: "author_name" },
            { data: "word" },
            { data: "meaning" },
            { data: "title" },
            { data: "id", visible: false },
            { data: "author_id", visible: false }
        ],
        language: {
            search: "🔍 ಹುಡುಕಿ:",
            lengthMenu: "_MENU_ ದಾಖಲೆಗಳನ್ನು ತೋರಿಸು",
            info: "ಒಟ್ಟು _TOTAL_ ದಾಖಲೆಗಳಿಂದ _START_ ರಿಂದ _END_ ಸಂಕ್ಲಿಷ್ಟಿಸಲಾಗಿದೆ",
            infoEmpty: "ಯಾವುದೇ ದಾಖಲೆಗಳಿಲ್ಲ",
            infoFiltered: "(ಮೊತ್ತದಲ್ಲಿ _MAX_ ದಾಖಲೆಗಳಲ್ಲಿ ಫಿಲ್ಟರ್ ಆಗಿವೆ)",
            paginate: {
                first: "ಮೊದಲ",
                last: "ಕೊನೆಯ",
                next: "ಮುಂದೆ",
                previous: "ಹಿಂದೆ"
            }
        },
        pageLength: 50,
        stripeClasses: ["odd-row", "even-row"],
        paging: true,
        info: true
    });

    // Row click → fetch Arthakosha details
    document.querySelector("#arthakoshaTable tbody").addEventListener("click", async (event) => {
        const tr = event.target.closest("tr");
        if (!tr) return;
        const rowData = table.row(tr).data();
        if (!rowData) return;

        try {
            const url = `${apiEndpoints.rightSection.arthakoshaApi}/${rowData.samputa}/${rowData.author_id}/${rowData.id}`;
            const res = await apiClient.get(url);

            if (res) {
                const entry = res;
                document.getElementById("arthakosha_modalSamputa").textContent = entry.samputa;
                document.getElementById("arthakosha_modalAuthor").textContent = entry.author_name;
                document.getElementById("arthakosha_modalId").textContent = entry.id;
                document.getElementById("arthakosha_modalTitle").textContent = entry.title || "—";
                document.getElementById("arthakosha_modalWord").textContent = entry.word || "—";
                document.getElementById("arthakosha_modalMeaning").textContent = entry.meaning || "—";
                document.getElementById("arthakosha_modalNotes").textContent = entry.notes || "—";

                new bootstrap.Modal(document.getElementById("arthakoshaModal")).show();
            }
        } catch (err) {
            console.error("Error fetching Arthakosha entry:", err);
        }
    });

    // Kannada letters grid → append to DataTable search
    const lettersGrid = document.getElementById("arthakosha-letters-grid");
    if (lettersGrid) {
        letters.forEach(ch => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "btn btn-outline-secondary btn-sm letter-box m-1";
            btn.textContent = ch;

            btn.addEventListener("click", () => {
                const dtSearch = table.search() || "";
                table.search(dtSearch + ch).draw();
            });

            lettersGrid.appendChild(btn);
        });
    }

    // Clear search button
    const clearBtn = document.getElementById("arthakosha-clearSearch");
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            table.search("").draw();
        });
    }
});
