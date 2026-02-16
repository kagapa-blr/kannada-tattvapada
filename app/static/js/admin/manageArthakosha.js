import apiClient from "../apiClient.js";
import { showLoader, hideLoader } from "../loader.js";
import apiEndpoints from "../apiEndpoints.js";

const SAMPUTA_AUTHOR_API = apiEndpoints.admin.samputaAuthor;
const ARTHAKOSHAS_API = apiEndpoints.admin.manageArthakosha;

export async function initArthakoshaManageTab() {
    // ---------------- Modals ----------------
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

    // ---------------- Manage / Add Elements ----------------
    const manageSamputa = document.getElementById("manage_arthakosha_samputaSelect");
    const manageAuthor = document.getElementById("manage_arthakosha_authorSelect");
    const manageArthakosha = document.getElementById("manage_arthakoshaSelect");
    const manageForm = document.getElementById("manage_arthakosha_form");
    const manageId = document.getElementById("manage_arthakosha_id");
    const manageWord = document.getElementById("manage_arthakosha_word");
    const manageMeaning = document.getElementById("manage_arthakosha_meaning");
    const manageNotes = document.getElementById("manage_arthakosha_notes");

    const addSamputa = document.getElementById("add_arthakosha_samputaSelect");
    const addAuthor = document.getElementById("add_arthakosha_authorSelect");
    const addForm = document.getElementById("add_arthakosha_form");
    const addWord = document.getElementById("add_arthakosha_word");
    const addMeaning = document.getElementById("add_arthakosha_meaning");
    const addNotes = document.getElementById("add_arthakosha_notes");

    let samputaAuthors = [];
    let currentEntries = [];

    // ---------------- Load Samputa & Authors ----------------
    async function loadSamputaAuthors() {
        try {
            showLoader();
            const resp = await apiClient.get(SAMPUTA_AUTHOR_API);
            if (resp.success) {
                samputaAuthors = resp.data;
                samputaAuthors.forEach(s => {
                    manageSamputa.appendChild(new Option(s.samputa, s.samputa));
                    addSamputa.appendChild(new Option(s.samputa, s.samputa));
                });
            }
        } catch (err) {
            console.error(err);
            showInfo("Failed to load Samputa & Authors.");
        } finally {
            hideLoader();
        }
    }

    // ---------------- Cascading Dropdowns ----------------
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
        try {
            showLoader();
            const resp = await apiClient.get(`${ARTHAKOSHAS_API}/${manageSamputa.value}/${manageAuthor.value}`);
            if (resp.success && resp.results?.length) {
                currentEntries = resp.results;
                resp.results.forEach(e => {
                    manageArthakosha.appendChild(new Option(`ID:${e.id} - ${e.word}`, e.id));
                });
                manageArthakosha.disabled = false;
            } else {
                showInfo("No Arthakosha entries found.");
            }
        } catch (err) {
            console.error(err);
            showInfo("Failed to load Arthakosha entries.");
        } finally {
            hideLoader();
        }
    });

    manageArthakosha.addEventListener("change", async () => {
        if (!manageArthakosha.value) return;
        const entryId = manageArthakosha.value;
        try {
            showLoader();
            const resp = await apiClient.get(`${ARTHAKOSHAS_API}/${manageSamputa.value}/${manageAuthor.value}/${entryId}`);
            if (resp.success && resp.entry) {
                const entry = resp.entry;
                manageId.value = entry.id;
                manageWord.value = entry.word || "";
                manageMeaning.value = entry.meaning || "";
                manageNotes.value = entry.notes || "";
                manageForm.style.display = "block";
            }
        } catch (err) {
            console.error(err);
            showInfo("Failed to load entry details.");
        } finally {
            hideLoader();
        }
    });

    // ---------------- Update ----------------
    document.getElementById("manage_arthakosha_saveBtn").addEventListener("click", async () => {
        if (!manageId.value) return;
        try {
            showLoader();
            const resp = await apiClient.put(`${ARTHAKOSHAS_API}/${manageSamputa.value}/${manageAuthor.value}/${manageId.value}`, {
                word: manageWord.value,
                meaning: manageMeaning.value,
                notes: manageNotes.value
            });
            showInfo(resp.message || (resp.success ? "Updated successfully!" : "Failed to update."));
            manageAuthor.dispatchEvent(new Event("change"));
        } catch (err) {
            console.error(err);
            showInfo(err?.response?.data?.error || "Failed to update.");
        } finally {
            hideLoader();
        }
    });

    // ---------------- Delete ----------------
    document.getElementById("manage_arthakosha_deleteBtn").addEventListener("click", () => {
        if (!manageId.value) return;
        deleteModal.show();
    });

    confirmDeleteBtn.addEventListener("click", async () => {
        if (!manageId.value) return;
        try {
            showLoader();
            const resp = await apiClient.delete(`${ARTHAKOSHAS_API}/${manageSamputa.value}/${manageAuthor.value}/${manageId.value}`);
            deleteModal.hide();
            showInfo(resp.message || (resp.success ? "Deleted successfully!" : "Failed to delete."));
            manageArthakosha.value = "";
            manageForm.style.display = "none";
            manageAuthor.dispatchEvent(new Event("change"));
        } catch (err) {
            console.error(err);
            showInfo(err?.response?.data?.error || "Failed to delete.");
        } finally {
            hideLoader();
        }
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
            showLoader();
            const resp = await apiClient.post(`${ARTHAKOSHAS_API}`, {
                samputa: addSamputa.value,
                author_id: addAuthor.value,
                word: addWord.value,
                meaning: addMeaning.value,
                notes: addNotes.value
            });
            console.log("Add response:", resp);
            showInfo(resp.success ? "Created successfully!" : resp.message || "Failed to create.");

            addWord.value = "";
            addMeaning.value = "";
            addNotes.value = "";
            addForm.style.display = "none";

            if (manageSamputa.value === addSamputa.value && manageAuthor.value === addAuthor.value) {
                manageAuthor.dispatchEvent(new Event("change"));
            }
        } catch (err) {
            console.log(err.json ? err.json() : err);
            showInfo(err.message || "Failed to create.");
        } finally {
            hideLoader();
        }
    });

    // ---------------- Bulk CSV Upload ----------------
    function initializeArthakoshaCsvBulkUpload() {
        const form = document.getElementById("arthakosha_upload_form");
        if (!form) return;
        if (form.dataset.bound === "1") return;
        form.dataset.bound = "1";

        const fileInput = document.getElementById("arthakosha_csv");
        const successEl = document.getElementById("arthakosha_upload_success");
        const errorEl = document.getElementById("arthakosha_upload_error");
        const warningsEl = document.getElementById("arthakosha_upload_warnings");

        const confirmModalEl = document.getElementById("arthakosha_upload_confirmModal");
        const confirmModal = new bootstrap.Modal(confirmModalEl);
        const confirmListEl = document.getElementById("arthakosha_upload_confirmFileList");
        const confirmEmptyEl = document.getElementById("arthakosha_upload_confirmEmpty");
        const confirmBtn = document.getElementById("arthakosha_upload_confirmBtn");

        let selectedFiles = [];

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            resetMessages();
            if (!fileInput.files || !fileInput.files.length) {
                errorEl.textContent = "Please select one or more CSV files.";
                errorEl.style.display = "block";
                return;
            }
            selectedFiles = Array.from(fileInput.files);
            renderConfirmList();
            confirmModal.show();
        });

        function resetMessages() {
            successEl.style.display = "none";
            errorEl.style.display = "none";
            warningsEl.style.display = "none";
            warningsEl.innerHTML = "";
        }

        function renderConfirmList() {
            confirmListEl.innerHTML = "";

            if (!selectedFiles.length) {
                confirmEmptyEl.classList.remove("d-none");
                confirmBtn.disabled = true;
                return;
            }

            confirmEmptyEl.classList.add("d-none");
            confirmBtn.disabled = false;

            selectedFiles.forEach((file, index) => {
                const li = document.createElement("li");
                li.className = "list-group-item";
                li.dataset.index = index;
                li.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <strong>${file.name}</strong>
                    <div class="text-muted small">${(file.size / 1024).toFixed(2)} KB</div>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger" data-action="remove">Remove</button>
            </div>
            <div class="progress d-none">
                <div class="progress-bar" role="progressbar" style="width: 0%">0%</div>
            </div>
            <div class="text-muted small upload-status"></div>
        `;
                confirmListEl.appendChild(li);
            });
        }


        confirmListEl.addEventListener("click", function (e) {
            const btn = e.target.closest("button[data-action='remove']");
            if (!btn) return;
            const li = btn.closest("li");
            const index = parseInt(li.dataset.index, 10);
            selectedFiles.splice(index, 1);
            renderConfirmList();
        });

        confirmBtn.addEventListener("click", async () => {
            confirmModal.hide();
            await startBulkUpload();
        });

        async function startBulkUpload() {
            resetMessages();
            showLoader();
            const finalWarnings = [];

            for (let i = 0; i < selectedFiles.length; i++) {
                const file = selectedFiles[i];
                const listItem = confirmListEl.querySelector(`li[data-index="${i}"]`);
                if (!listItem) continue;

                const progressContainer = listItem.querySelector(".progress");
                const progressBar = listItem.querySelector(".progress-bar");
                const statusEl = listItem.querySelector(".upload-status");

                if (!file.name.toLowerCase().endsWith(".csv")) {
                    finalWarnings.push(`${file.name} skipped: not a CSV file.`);
                    continue;
                }

                progressContainer.classList.remove("d-none");
                progressBar.style.width = "0%";
                progressBar.textContent = "0%";
                statusEl.textContent = "Uploading...";

                try {
                    const resp = await uploadWithProgress(file, progressBar);
                    if (!resp?.success) {
                        finalWarnings.push(`${file.name} failed: ${resp?.message || "Server error"}`);
                        statusEl.textContent = "Upload failed.";
                    } else {
                        statusEl.textContent = resp.message || "Uploaded successfully.";
                    }

                    if (Array.isArray(resp?.errors)) resp.errors.forEach(e => finalWarnings.push(`${file.name}: ${e}`));

                } catch (err) {
                    console.error("Upload error:", err);
                    finalWarnings.push(`${file.name} failed due to network/server error.`);
                    statusEl.textContent = "Upload failed due to network/server error.";
                }

                if (i < selectedFiles.length - 1) await sleep(1000);
            }

            if (finalWarnings.length) {
                warningsEl.innerHTML = finalWarnings.map(e => `<li>${e}</li>`).join("");
                warningsEl.style.display = "block";
            }

            successEl.textContent = "Bulk upload completed.";
            successEl.style.display = "block";
            hideLoader();
            form.reset();
        }

        function uploadWithProgress(file, progressBar) {
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                const formData = new FormData();
                formData.append("file", file);

                xhr.open("POST", apiEndpoints.rightSection.arthakoshaApiUpload, true);

                xhr.upload.onprogress = e => {
                    if (e.lengthComputable) {
                        const percent = Math.round((e.loaded / e.total) * 100);
                        progressBar.style.width = percent + "%";
                        progressBar.textContent = percent + "%";
                    }
                };

                xhr.onload = () => {
                    try {
                        const resp = JSON.parse(xhr.responseText);
                        resolve(resp);
                    } catch {
                        reject(new Error("Invalid server response"));
                    }
                };

                xhr.onerror = () => reject(new Error("Network error"));
                xhr.send(formData);
            });
        }
    }

    // ---------------- CSV Template ----------------
    function downloadArthakoshaTemplateCSV() {
        if (!samputaAuthors.length) {
            showInfo("No samputa-author data loaded yet. Please reload the page.");
            return;
        }

        const rows = [["author_id", "author_name", "samputa", "word", "meaning", "notes"]];
        samputaAuthors.forEach(item => {
            item.authors.forEach(author => {
                rows.push([`"${author.id}"`, `"${author.name}"`, `"${item.samputa}"`, "", "", ""]);
            });
        });

        const csv = "\uFEFF" + rows.map(r => r.join(",")).join("\n");
        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "arthakosha_template.csv";
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    }

    // ---------------- Init ----------------
    await loadSamputaAuthors();
    initializeArthakoshaCsvBulkUpload();

    document.getElementById("arthakosha_download_template_btn")
        .addEventListener("click", downloadArthakoshaTemplateCSV);

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
