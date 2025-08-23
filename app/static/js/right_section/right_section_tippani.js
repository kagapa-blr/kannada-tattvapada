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

    // Render DataTable
    const table = new DataTable("#right_section_tippaniTable", {
        processing: true,
        serverSide: true,
        ajax: async (data, callback) => {
            const offset = data.start || 0;
            const limit = data.length || 50;
            const search = data.search.value || "";

            try {
                const res = await apiClient.get(`${apiEndpoints.rightSection.tippaniApi}?offset=${offset}&limit=${limit}&search=${encodeURIComponent(search)}`);

                callback({
                    recordsTotal: res.total || 0,
                    recordsFiltered: res.total || 0,
                    data: res.results || []
                });
            } catch (err) {
                console.error("Error loading Tippani list:", err);
                callback({ recordsTotal: 0, recordsFiltered: 0, data: [] });
            }
        },
        columns: [
            { data: "samputa_sankhye" },
            { data: "tatvapadakarara_hesaru" },
            { data: "tippani_id" },
            { data: "tippani_title" },
            { data: "tatvapada_author_id", visible: false }
        ],
        language: { search: "🔍 ಹುಡುಕಿ:" },
        pageLength: 50,
        stripeClasses: ["odd-row", "even-row"]
    });

    // Row click → fetch Tippani details
    document.querySelector("#right_section_tippaniTable tbody").addEventListener("click", async (event) => {
        const tr = event.target.closest("tr");
        if (!tr) return;
        const rowData = table.row(tr).data();
        if (!rowData) return;

        try {
            const url = `${apiEndpoints.rightSection.tippaniApi}/${rowData.tippani_id}?samputa=${rowData.samputa_sankhye}&author_id=${rowData.tatvapada_author_id}`;
            const res = await apiClient.get(url);
            if (res.success && res.data) {
                const tippani = res.data;
                document.getElementById("right_section_modalSamputa").textContent = tippani.samputa;
                document.getElementById("right_section_modalAuthor").textContent = rowData.tatvapadakarara_hesaru;
                document.getElementById("right_section_modalId").textContent = tippani.id;
                document.getElementById("right_section_modalTitle").textContent = tippani.title || "—";
                document.getElementById("right_section_modalContent").textContent = tippani.content || "—";

                new bootstrap.Modal(document.getElementById("right_section_tippaniModal")).show();
            }
        } catch (err) {
            console.error("Error fetching Tippani:", err);
        }
    });

    // Kannada letters grid → append to DataTable search
    const lettersGrid = document.getElementById("letters-grid");
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

    // Clear search button
    document.getElementById("clearSearch").addEventListener("click", () => {
        table.search("").draw();
    });
});
