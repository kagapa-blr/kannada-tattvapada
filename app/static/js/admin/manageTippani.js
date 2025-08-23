import apiClient from "../apiClient.js";
import { showLoader, hideLoader } from "../loader.js";
import apiEndpoints from "../apiEndpoints.js";
// ----------------- API Endpoints ----------------- //
const SAMPUTA_AUTHOR_API = apiEndpoints.admin.samputaAuthor;  // Get samputa & authors
const TIPPANIS_API = apiEndpoints.admin.manageTippani; // Get all tippanis for samputa+author
const TIPPANI_API = TIPPANIS_API             // Specific tippani CRUD

export async function initTippaniManageTab() {
    const infoModalEl = document.getElementById("tippani_infoModal");
    const infoModal = new bootstrap.Modal(infoModalEl);
    const infoModalBody = document.getElementById("tippani_infoModalBody");

    function showInfo(msg) {
        infoModalBody.textContent = msg;
        infoModal.show();
    }

    // ------------ Load Samputa & Authors ------------ //
    let samputaAuthors = [];

    async function loadSamputaAuthors() {
        try {
            showLoader();
            const resp = await apiClient.get(SAMPUTA_AUTHOR_API);
            if (resp.success) {
                samputaAuthors = resp.data;

                // Fill both dropdowns (manage & add)
                samputaAuthors.forEach(s => {
                    const opt1 = new Option(s.samputa, s.samputa);
                    const opt2 = new Option(s.samputa, s.samputa);
                    document.getElementById("manage_samputaSelect").appendChild(opt1);
                    document.getElementById("add_samputaSelect").appendChild(opt2);
                });
            }
        } finally {
            hideLoader();
        }
    }

    // ------------ Manage Existing Tippani ------------ //
    const manageSamputa = document.getElementById("manage_samputaSelect");
    const manageAuthor = document.getElementById("manage_authorSelect");
    const manageTippani = document.getElementById("manage_tippaniSelect");
    const manageForm = document.getElementById("manage_form");

    const manageId = document.getElementById("manage_tippani_id");
    const manageTitle = document.getElementById("manage_tippani_title");
    const manageContent = document.getElementById("manage_tippani_content");

    // On Samputa change → populate authors
    manageSamputa.addEventListener("change", () => {
        manageAuthor.innerHTML = `<option value="">-- Select Author --</option>`;
        manageTippani.innerHTML = `<option value="">-- Select Tippani --</option>`;
        manageForm.style.display = "none";

        const samputaObj = samputaAuthors.find(s => s.samputa === manageSamputa.value);
        if (samputaObj) {
            samputaObj.authors.forEach(a => {
                manageAuthor.appendChild(new Option(a.name, a.id));
            });
            manageAuthor.disabled = false;
        }
    });

    // On Author change → fetch tippanis
    manageAuthor.addEventListener("change", async () => {
        manageTippani.innerHTML = `<option value="">-- Select Tippani --</option>`;
        manageForm.style.display = "none";
        if (!manageSamputa.value || !manageAuthor.value) return;

        const resp = await apiClient.get(`${TIPPANIS_API}?samputa=${manageSamputa.value}&author_id=${manageAuthor.value}`);
        if (resp.success && resp.data.length) {
            resp.data.forEach(t => {
                manageTippani.appendChild(new Option(t.title || `Tippani ${t.tippani_id}`, t.tippani_id));
            });
            manageTippani.disabled = false;
        }
    });

    // On Tippani change → fetch specific tippani
    manageTippani.addEventListener("change", async () => {
        if (!manageTippani.value) return;
        const resp = await apiClient.get(
            `${TIPPANI_API}/${manageTippani.value}?samputa=${manageSamputa.value}&author_id=${manageAuthor.value}`
        );
        if (resp.success && resp.data) {
            manageId.value = resp.data.id;
            manageTitle.value = resp.data.title || "";
            manageContent.value = resp.data.content || "";
            manageForm.style.display = "block";
        }
    });

    // Save (Update Tippani)
    document.getElementById("manage_saveBtn").addEventListener("click", async () => {
        const resp = await apiClient.put(`${TIPPANI_API}/${manageId.value}`, {
            samputa: manageSamputa.value,
            author_id: manageAuthor.value,
            title: manageTitle.value,
            content: manageContent.value
        });
        showInfo(resp.success ? "Updated successfully!" : "Failed to update.");
    });

    // Delete Tippani
    document.getElementById("manage_deleteBtn").addEventListener("click", async () => {
        const resp = await apiClient.delete(`${TIPPANI_API}/${manageId.value}`, {
            samputa: manageSamputa.value,
            author_id: manageAuthor.value
        });
        showInfo(resp.success ? "Deleted successfully!" : "Failed to delete.");
    });

    // ------------ Add New Tippani ------------ //
    const addSamputa = document.getElementById("add_samputaSelect");
    const addAuthor = document.getElementById("add_authorSelect");
    const addForm = document.getElementById("add_form");

    const addTitle = document.getElementById("add_tippani_title");
    const addContent = document.getElementById("add_tippani_content");

    addSamputa.addEventListener("change", () => {
        addAuthor.innerHTML = `<option value="">-- Select Author --</option>`;
        addForm.style.display = "none";
        const samputaObj = samputaAuthors.find(s => s.samputa === addSamputa.value);
        if (samputaObj) {
            samputaObj.authors.forEach(a => addAuthor.appendChild(new Option(a.name, a.id)));
            addAuthor.disabled = false;
        }
    });

    addAuthor.addEventListener("change", () => {
        if (addAuthor.value) addForm.style.display = "block";
    });

    // Save new Tippani
    document.getElementById("add_saveBtn").addEventListener("click", async () => {
        const resp = await apiClient.post(TIPPANI_API, {
            samputa: addSamputa.value,
            author_id: addAuthor.value,
            title: addTitle.value,
            content: addContent.value
        });
        showInfo(resp.success ? "Created successfully!" : "Failed to create.");
    });

    // ------------ Init ------------ //
    await loadSamputaAuthors();
}
