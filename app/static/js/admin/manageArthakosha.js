import apiClient from "../apiClient.js";
import { showLoader, hideLoader } from "../loader.js";
import apiEndpoints from "../apiEndpoints.js";

const SAMPUTA_AUTHOR_API = apiEndpoints.admin.samputaAuthor;
const ARTHAKOSHAS_API = apiEndpoints.admin.manageArthakosha;

export async function initArthakoshaManageTab() {
    // Modals
    const infoModalEl = document.getElementById("arthakosha_infoModal");
    const deleteModalEl = document.getElementById("arthakosha_deleteModal");

    const infoModal = new bootstrap.Modal(infoModalEl);
    const deleteModal = new bootstrap.Modal(deleteModalEl);

    const infoModalBody = document.getElementById("arthakosha_infoModalBody");
    const confirmDeleteBtn = document.getElementById("arthakosha_confirmDeleteBtn");

    function showInfo(msg) {
        infoModalBody.textContent = msg;
        infoModal.show();
    }

    // ---------------- Manage Existing ----------------
    const manageSamputa = document.getElementById("manage_arthakosha_samputaSelect");
    const manageAuthor = document.getElementById("manage_arthakosha_authorSelect");
    const manageArthakosha = document.getElementById("manage_arthakoshaSelect");
    const manageForm = document.getElementById("manage_arthakosha_form");

    const manageId = document.getElementById("manage_arthakosha_id");
    const manageTitle = document.getElementById("manage_arthakosha_title");
    const manageWord = document.getElementById("manage_arthakosha_word");
    const manageMeaning = document.getElementById("manage_arthakosha_meaning");
    const manageNotes = document.getElementById("manage_arthakosha_notes");

    // ---------------- Add New ----------------
    const addSamputa = document.getElementById("add_arthakosha_samputaSelect");
    const addAuthor = document.getElementById("add_arthakosha_authorSelect");
    const addForm = document.getElementById("add_arthakosha_form");

    const addTitle = document.getElementById("add_arthakosha_title");
    const addWord = document.getElementById("add_arthakosha_word");
    const addMeaning = document.getElementById("add_arthakosha_meaning");
    const addNotes = document.getElementById("add_arthakosha_notes");

    let samputaAuthors = [];
    let currentEntries = [];

    // Load Samputa & Authors
    async function loadSamputaAuthors() {
        try {
            showLoader();
            const resp = await apiClient.get(SAMPUTA_AUTHOR_API);
            if (resp.success) {
                samputaAuthors = resp.data;
                samputaAuthors.forEach(s => {
                    const opt1 = new Option(s.samputa, s.samputa);
                    const opt2 = new Option(s.samputa, s.samputa);
                    manageSamputa.appendChild(opt1);
                    addSamputa.appendChild(opt2);
                });
            }
        } finally {
            hideLoader();
        }
    }

    // ---------------- Manage Cascading ----------------
    manageSamputa.addEventListener("change", () => {
        manageAuthor.innerHTML = `<option value="">-- Select Author --</option>`;
        manageArthakosha.innerHTML = `<option value="">-- Select Entry --</option>`;
        manageForm.style.display = "none";
        currentEntries = [];

        const samputaObj = samputaAuthors.find(s => s.samputa === manageSamputa.value);
        if (samputaObj) {
            samputaObj.authors.forEach(a => manageAuthor.appendChild(new Option(a.name, a.id)));
            manageAuthor.disabled = false;
        } else manageAuthor.disabled = true;
    });

    manageAuthor.addEventListener("change", async () => {
        manageArthakosha.innerHTML = `<option value="">-- Select Entry --</option>`;
        manageForm.style.display = "none";
        currentEntries = [];

        if (!manageSamputa.value || !manageAuthor.value) return;

        const resp = await apiClient.get(`${ARTHAKOSHAS_API}?samputa=${manageSamputa.value}&author_id=${manageAuthor.value}`);
        if (resp.results?.length) {
            currentEntries = resp.results;
            resp.results.forEach(e => {
                const text = `ID:${e.id} - ${e.title || e.word}`;
                manageArthakosha.appendChild(new Option(text, e.id));
            });
            manageArthakosha.disabled = false;
        }
    });

    manageArthakosha.addEventListener("change", async () => {
        if (!manageArthakosha.value) return;
        const entryId = manageArthakosha.value;
        const resp = await apiClient.get(`${ARTHAKOSHAS_API}/${manageSamputa.value}/${manageAuthor.value}/${entryId}`);
        if (resp) {
            manageId.value = resp.id;
            manageTitle.value = resp.title || "";
            manageWord.value = resp.word || "";
            manageMeaning.value = resp.meaning || "";
            manageNotes.value = resp.notes || "";
            manageForm.style.display = "block";
        }
    });

    document.getElementById("manage_arthakosha_saveBtn").addEventListener("click", async () => {
        const resp = await apiClient.put(`${ARTHAKOSHAS_API}/${manageSamputa.value}/${manageAuthor.value}/${manageId.value}`, {
            title: manageTitle.value,
            word: manageWord.value,
            meaning: manageMeaning.value,
            notes: manageNotes.value
        });
        showInfo(resp.message || (resp.success ? "Updated successfully!" : "Failed to update."));
    });

    document.getElementById("manage_arthakosha_deleteBtn").addEventListener("click", () => {
        if (!manageId.value) return;
        deleteModal.show();
    });

    confirmDeleteBtn.addEventListener("click", async () => {
        const resp = await apiClient.delete(`${ARTHAKOSHAS_API}/${manageSamputa.value}/${manageAuthor.value}/${manageId.value}`);
        deleteModal.hide();
        showInfo(resp.message || (resp.success ? "Deleted successfully!" : "Failed to delete."));
        manageArthakosha.value = "";
        manageForm.style.display = "none";
        manageAuthor.dispatchEvent(new Event("change"));
    });

    // ---------------- Add New Cascading ----------------
    addSamputa.addEventListener("change", () => {
        addAuthor.innerHTML = `<option value="">-- Select Author --</option>`;
        addForm.style.display = "none";

        const samputaObj = samputaAuthors.find(s => s.samputa === addSamputa.value);
        if (samputaObj) {
            samputaObj.authors.forEach(a => addAuthor.appendChild(new Option(a.name, a.id)));
            addAuthor.disabled = false;
        } else addAuthor.disabled = true;
    });

    addAuthor.addEventListener("change", () => {
        addForm.style.display = addAuthor.value ? "block" : "none";
    });


    document.getElementById("add_arthakosha_saveBtn").addEventListener("click", async () => {
        if (!addSamputa.value || !addAuthor.value || !addWord.value || !addMeaning.value) {
            showInfo("Please fill all required fields.");
            return;
        }

        try {
            const resp = await apiClient.post(`${ARTHAKOSHAS_API}`, {
                samputa: addSamputa.value,
                author_id: addAuthor.value,
                title: addTitle.value,
                word: addWord.value,
                meaning: addMeaning.value,
                notes: addNotes.value
            });

            if (resp.id) {  // <-- check if id exists
                showInfo("Created successfully!");
            } else {
                showInfo("Failed to create.");
            }

            // Reset form
            addTitle.value = "";
            addWord.value = "";
            addMeaning.value = "";
            addNotes.value = "";
            addForm.style.display = "none";

            // Refresh Manage dropdown if same Samputa & Author
            if (manageSamputa.value === addSamputa.value && manageAuthor.value === addAuthor.value) {
                manageAuthor.dispatchEvent(new Event("change"));
            }
        } catch (err) {
            console.error(err);
            showInfo("Failed to create.");
        }
    });


    // ---------------- Init ----------------
    await loadSamputaAuthors();
}
