import apiClient from "../apiClient.js"; // adjust path if needed
import apiEndpoints from '../apiEndpoints.js';




document.addEventListener("DOMContentLoaded", async () => {
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

    try {
        const data = await apiClient.get(apiEndpoints.rightSection.tippaniApi);

        if (!data.results || data.results.length === 0) {
            console.warn("No Tippanis found");
            return;
        }

        // Initialize DataTable
        const table = new DataTable("#right_section_tippaniTable", {
            data: data.results,
            columns: [
                { data: "samputa_sankhye", title: "ಸಂಪುಟ ಸಂಖ್ಯೆ" },
                { data: "tatvapadakarara_hesaru", title: "ತತ್ವಪದಕಾರರ ಹೆಸರು" },
                { data: "tippani_id", title: "ಟಿಪ್ಪಣಿ ಐಡಿ" },
                { data: "tippani_title", title: "ಟಿಪ್ಪಣಿ ಶೀರ್ಷಿಕೆ" },
                { data: "tatvapada_author_id", visible: false } // hidden
            ],
            paging: true,
            searching: true,
            info: true,
            autoWidth: false,
            language: { emptyTable: "ಟಿಪ್ಪಣಿ ಲಭ್ಯವಿಲ್ಲ" },
            stripeClasses: ["odd-row", "even-row"]
        });

        // Row click → fetch specific Tippani
        document.querySelector("#right_section_tippaniTable tbody").addEventListener("click", async (event) => {
            const tr = event.target.closest("tr");
            if (!tr) return;

            const rowIndex = tr.rowIndex - 1; // account for header row
            const rowData = data.results[rowIndex];
            if (!rowData) return;

            try {
                //const url = `api/v1/right-section/tippani/${rowData.tippani_id}?samputa=${rowData.samputa_sankhye}&author_id=${rowData.tatvapada_author_id}`;
                const url = `${apiEndpoints.rightSection.tippaniApi}/${rowData.tippani_id}?samputa=${rowData.samputa_sankhye}&author_id=${rowData.tatvapada_author_id}`;
                const response = await apiClient.get(url);


                if (response.success && response.data) {
                    const tippani = response.data;
                    document.getElementById("right_section_modalSamputa").textContent = tippani.samputa;
                    document.getElementById("right_section_modalAuthor").textContent = rowData.tatvapadakarara_hesaru;
                    document.getElementById("right_section_modalId").textContent = tippani.id;
                    document.getElementById("right_section_modalTitle").textContent = tippani.title || "—";
                    document.getElementById("right_section_modalContent").textContent = tippani.content || "—";

                    const modal = new bootstrap.Modal(document.getElementById("right_section_tippaniModal"));
                    modal.show();
                } else {
                    console.warn("Tippani not found");
                }
            } catch (err) {
                console.error("Error fetching specific Tippani:", err);
            }
        });

        // ✅ Kannada letters search integration
        const lettersGrid = document.getElementById("letters-grid");
        letters.forEach(ch => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "btn btn-outline-secondary btn-sm letter-box";
            btn.style.margin = "0.1rem";
            btn.textContent = ch;

            btn.addEventListener("click", () => {
                const currentSearch = table.search();
                table.search(currentSearch + ch).draw();
            });

            lettersGrid.appendChild(btn);
        });

        // Clear search button
        const clearBtn = document.getElementById("clearSearch");
        clearBtn.addEventListener("click", () => table.search("").draw());

    } catch (err) {
        console.error("Error loading Tippani list:", err);
    }
});
