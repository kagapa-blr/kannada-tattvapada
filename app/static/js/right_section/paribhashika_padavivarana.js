import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";

document.addEventListener("DOMContentLoaded", () => {
    const letters = [
        "ಅ", "ಆ", "ಇ", "ಈ", "ಉ", "ಊ", "ಋ", "ೠ", "ಎ", "ಏ", "ಐ", "ಒ", "ಓ", "ಔ",
        "ಕ", "ಖ", "ಗ", "ಘ", "ಙ", "ಚ", "ಛ", "ಜ", "ಝ", "ಞ",
        "ಟ", "ಠ", "ಡ", "ಢ", "ಣ", "ತ", "ಥ", "ದ", "ಧ", "ನ",
        "ಪ", "ಫ", "ಬ", "ಭ", "ಮ", "ಯ", "ರ", "ಲ", "ವ",
        "ಶ", "ಷ", "ಸ", "ಹ", "ಳ"
    ];

    // ✅ Initialize DataTable
    const table = new DataTable("#right_section_padavivaranaTable", {
        processing: true,
        serverSide: true,
        ajax: async (data, callback) => {
            const offset = data.start || 0;
            const limit = data.length || 50;
            const search = data.search.value || "";

            try {
                const res = await apiClient.get(
                    `${apiEndpoints.rightSection.padavivaranaApi}?offset=${offset}&limit=${limit}&search=${encodeURIComponent(search)}`
                );

                callback({
                    recordsTotal: res.total || 0,
                    recordsFiltered: res.total || 0,
                    data: res.results || []
                });
            } catch (err) {
                console.error("Error loading Padavivarana list:", err);
                callback({ recordsTotal: 0, recordsFiltered: 0, data: [] });
            }
        },
        columns: [
            { data: "samputa_sankhye" },
            { data: "tatvapadakarara_hesaru" },
            { data: "id", visible: false },
            { data: "title" },
            { data: "tatvapada_author_id", visible: false }
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

    // ✅ Row click → fetch Padavivarana details
    document.querySelector("#right_section_padavivaranaTable tbody").addEventListener("click", async (event) => {
        const tr = event.target.closest("tr");
        if (!tr) return;
        const rowData = table.row(tr).data();
        if (!rowData) return;

        try {
            const url = `${apiEndpoints.rightSection.padavivaranaApi}/${rowData.samputa_sankhye}/${rowData.tatvapada_author_id}/${rowData.id}`;
            const res = await apiClient.get(url);

            if (res.id) {
                document.getElementById("modalSamputa").textContent = res.samputa;
                document.getElementById("modalAuthor").textContent = rowData.tatvapadakarara_hesaru;
                document.getElementById("modalId").textContent = res.id;
                document.getElementById("modalTitle").textContent = res.title || "—";
                document.getElementById("modalContent").textContent = res.content || "—";

                new bootstrap.Modal(document.getElementById("right_section_padavivaranaModal")).show();
            }
        } catch (err) {
            console.error("Error fetching Padavivarana:", err);
        }
    });

    // ✅ Kannada letters grid → append to DataTable search
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

    // ✅ Clear search button
    document.getElementById("clearSearch").addEventListener("click", () => {
        table.search("").draw();
    });
});
