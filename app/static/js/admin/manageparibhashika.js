import apiClient from "../apiClient.js";
import { showLoader, hideLoader } from "../loader.js";
import apiEndpoints from "../apiEndpoints.js";

// ----------------- API Endpoints ----------------- //
const SAMPUTA_AUTHOR_API = apiEndpoints.admin.samputaAuthor;     // [{ samputa, authors:[{id,name}] }]
const PARIBHASHIKAS_API = apiEndpoints.admin.manageParibhashika; // list & single CRUD base
const PARIBHASHIKA_API = PARIBHASHIKAS_API;                    // alias for clarity

export async function initParibhashikaPadavivaranaManageTab() {
    // Guard: run only if this tab is present
    const root = document.querySelector("#admin-paribhashika .paribhashika_manage_management");
    if (!root) return;

    // ---------- Modal helpers ----------
    const infoModalEl = document.getElementById("paribhashika_infoModal");
    const infoModalBody = document.getElementById("paribhashika_infoModalBody");
    const infoModal = infoModalEl ? new bootstrap.Modal(infoModalEl) : null;

    const showInfo = (msg) => {
        if (infoModal && infoModalBody) {
            infoModalBody.textContent = msg;
            infoModal.show();
        } else {
            alert(msg);
        }
    };

    // ---------- Elements (Manage) ----------
    const manageSamputa = document.getElementById("paribhashika_manage_samputaSelect");
    const manageAuthor = document.getElementById("paribhashika_manage_authorSelect");
    const managePadavivarana = document.getElementById("paribhashika_manage_padavivaranaSelect");
    const manageForm = document.getElementById("paribhashika_manage_form");
    const manageId = document.getElementById("paribhashika_manage_padavivarana_id");
    const manageTitle = document.getElementById("paribhashika_manage_padavivarana_title");
    const manageContent = document.getElementById("paribhashika_manage_padavivarana_content");
    const manageSaveBtn = document.getElementById("paribhashika_manage_saveBtn");
    const manageDeleteBtn = document.getElementById("paribhashika_manage_deleteBtn");

    // ---------- Elements (Add) ----------
    const addSamputa = document.getElementById("paribhashika_add_samputaSelect");
    const addAuthor = document.getElementById("paribhashika_add_authorSelect");
    const addForm = document.getElementById("paribhashika_add_form");
    const addTitle = document.getElementById("paribhashika_add_padavivarana_title");
    const addContent = document.getElementById("paribhashika_add_padavivarana_content");
    const addSaveBtn = document.getElementById("paribhashika_add_saveBtn");

    // ---------- Elements (Upload) ----------
    const uploadForm = document.getElementById("paribhashika_upload_form");
    const uploadFile = document.getElementById("paribhashika_csv");
    const downloadTemplateBtn = document.getElementById("paribhashika_download_template_btn");
    const uploadSuccess = document.getElementById("paribhashika_upload_success");
    const uploadError = document.getElementById("paribhashika_upload_error");
    const uploadWarnings = document.getElementById("paribhashika_upload_warnings");

    // Safety: ensure all critical elements exist
    const requiredEls = [
        manageSamputa, manageAuthor, managePadavivarana, manageForm,
        manageId, manageTitle, manageContent, manageSaveBtn, manageDeleteBtn,
        addSamputa, addAuthor, addForm, addTitle, addContent, addSaveBtn,
        uploadForm, uploadFile, downloadTemplateBtn, uploadSuccess, uploadError, uploadWarnings
    ];
    if (requiredEls.some(el => !el)) {
        console.warn("[Paribhashika] Missing DOM elements; check IDs in HTML.");
    }

    // ---------- Utilities ----------
    function resetSelect(select, placeholder) {
        select.innerHTML = `<option value="">${placeholder}</option>`;
        select.disabled = true;
    }

    function fillSelect(select, items, valueKey, textKey, placeholder) {
        resetSelect(select, placeholder);
        items.forEach(item => {
            select.appendChild(new Option(item[textKey], item[valueKey]));
        });
        select.disabled = false;
    }

    function clearManageForm() {
        manageId.value = "";
        manageTitle.value = "";
        manageContent.value = "";
        manageForm.style.display = "none";
    }

    // ---------- Load samputa & authors ----------
    let samputaAuthors = [];
    async function loadSamputaAuthors() {
        try {
            showLoader();
            const resp = await apiClient.get(SAMPUTA_AUTHOR_API);
            if (resp?.success && Array.isArray(resp.data)) {
                samputaAuthors = resp.data;

                // Populate both manage & add samputa
                const samputas = samputaAuthors.map(s => ({ value: s.samputa, text: s.samputa }));
                fillSelect(manageSamputa, samputas, "value", "text", "-- Select Samputa --");
                fillSelect(addSamputa, samputas, "value", "text", "-- Select Samputa --");

                // Disable downstream selects initially
                resetSelect(manageAuthor, "-- Select Author --");
                resetSelect(managePadavivarana, "-- Select Padavivarana --");
                resetSelect(addAuthor, "-- Select Author --");

                manageForm.style.display = "none";
                addForm.style.display = "none";
            } else {
                showInfo("Failed to load samputa/author list.");
            }
        } catch (e) {
            console.error(e);
            showInfo("Error loading samputa/author list.");
        } finally {
            hideLoader();
        }
    }

    // ---------- Cascades: Manage section ----------
    //Edit / Delete Padavivarana
    //Select Samputa
    manageSamputa.addEventListener("change", () => {

        clearManageForm();
        resetSelect(managePadavivarana, "-- Select Padavivarana --");
        resetSelect(manageAuthor, "-- Select Author --");

        const s = samputaAuthors.find(x => x.samputa === manageSamputa.value);
        if (!s) return;

        fillSelect(
            manageAuthor,
            s.authors.map(a => ({ value: a.id, text: a.name })),
            "value",
            "text",
            "-- Select Author --"
        );
    });

    // 🔹 Select Author → load Padavivarana IDs
    manageAuthor.addEventListener("change", async () => {
        clearManageForm();
        resetSelect(managePadavivarana, "-- Select Padavivarana --");
        if (!manageSamputa.value || !manageAuthor.value) return;

        try {
            showLoader();
            const resp = await apiClient.get(
                `${PARIBHASHIKA_API}/${encodeURIComponent(manageSamputa.value)}/${encodeURIComponent(manageAuthor.value)}`
            );

            if (resp?.success && Array.isArray(resp.data) && resp.data.length) {
                const items = resp.data.map(e => ({
                    value: e.padavivarana_id ?? e.id,  // fallback if backend uses id
                    text: e.paribhashika_padavivarana_title
                        || e.title
                        || `Padavivarana ${e.padavivarana_id ?? e.id}`
                })).filter(x => x.value != null);

                fillSelect(managePadavivarana, items, "value", "text", "-- Select Padavivarana --");
            } else {
                resetSelect(managePadavivarana, "-- No Padavivarana found --");
            }
        } catch (err) {
            console.error(err);
            resetSelect(managePadavivarana, "-- Failed to load --");
        } finally {
            hideLoader();
        }
    });

    // 🔹 Select Padavivarana → load its details
    managePadavivarana.addEventListener("change", async () => {
        clearManageForm();
        if (!managePadavivarana.value) return;

        try {
            showLoader();

            // ✅ Call backend with correct path
            const resp = await apiClient.get(
                `${PARIBHASHIKA_API}/${encodeURIComponent(manageSamputa.value)}/${encodeURIComponent(manageAuthor.value)}/${encodeURIComponent(managePadavivarana.value)}`
            );

            if (resp && resp.id) {
                manageId.value = resp.id;
                manageTitle.value = resp.title ?? "";
                manageContent.value = resp.content ?? "";
                manageForm.style.display = "block";
            } else {
                showInfo("Failed to load selected Padavivarana.");
            }
        } catch (err) {
            console.error(err);
            showInfo("Error fetching Padavivarana details.");
        } finally {
            hideLoader();
        }
    });

    // 🔹 Update
    manageSaveBtn.addEventListener("click", async () => {
        if (!manageId.value) return showInfo("Please select a Padavivarana first.");

        try {
            showLoader();
            const resp = await apiClient.put(
                `${PARIBHASHIKA_API}/${encodeURIComponent(manageSamputa.value)}/${encodeURIComponent(manageAuthor.value)}/${encodeURIComponent(manageId.value)}`,
                {
                    title: manageTitle.value,
                    content: manageContent.value
                }
            );
            showInfo(resp?.success ? "Updated successfully!" : (resp?.message || "Failed to update."));
        } catch (err) {
            console.error(err);
            showInfo("Error while updating.");
        } finally {
            hideLoader();
        }
    });
    // 🔹 Delete (with confirm modal)
    manageDeleteBtn.addEventListener("click", () => {
        if (!manageId.value) return showInfo("Please select a Padavivarana first.");
        const delEl = document.getElementById("paribhashika_deleteModal");
        if (!delEl) return showInfo("Delete modal not found.");
        const delModal = new bootstrap.Modal(delEl);
        delModal.show();

        const confirmBtn = document.getElementById("paribhashika_confirmDeleteBtn");

        // Attach once
        const handler = async () => {
            confirmBtn.removeEventListener("click", handler);
            try {
                showLoader();
                const resp = await apiClient.delete(
                    `${PARIBHASHIKA_API}/${encodeURIComponent(manageSamputa.value)}/${encodeURIComponent(manageAuthor.value)}/${encodeURIComponent(manageId.value)}`
                );
                delModal.hide();
                if (resp?.success) {
                    showInfo("Deleted successfully!");
                    // Reset UI
                    manageForm.style.display = "none";
                    managePadavivarana.value = "";
                    manageId.value = "";
                    manageTitle.value = "";
                    manageContent.value = "";
                    // Refresh list for current samputa/author
                    manageAuthor.dispatchEvent(new Event("change"));
                } else {
                    showInfo(resp?.message || "Failed to delete.");
                }
            } catch (err) {
                console.error(err);
                showInfo("Error while deleting.");
            } finally {
                hideLoader();
            }
        };

        confirmBtn.addEventListener("click", handler);
    });


    // Add New Tatvapada
    // Cascading dropdowns
    addSamputa.addEventListener("change", () => {
        addForm.style.display = "none";
        resetSelect(addAuthor, "-- Select Author --");

        const s = samputaAuthors.find(x => x.samputa === addSamputa.value);
        if (!s) return;

        fillSelect(
            addAuthor,
            s.authors.map(a => ({ value: a.id, text: a.name })),
            "value",
            "text",
            "-- Select Author --"
        );
    });

    addAuthor.addEventListener("change", () => {
        addForm.style.display = addAuthor.value ? "block" : "none";
    });

    // Create new Padavivarana
    addSaveBtn.addEventListener("click", async () => {
        if (!addSamputa.value || !addAuthor.value) {
            return showInfo("Please select Samputa and Author first.");
        }
        if (!addTitle.value.trim() || !addContent.value.trim()) {
            return showInfo("Title and Content are required.");
        }

        try {
            showLoader();
            const resp = await apiClient.post(PARIBHASHIKA_API, {
                samputa: addSamputa.value,
                author_id: addAuthor.value,
                title: addTitle.value.trim(),
                content: addContent.value.trim()
            });

            if (resp?.success) {
                showInfo("Created successfully!");
                addTitle.value = "";
                addContent.value = "";

                // Refresh Manage list if same samputa/author selected
                if (manageSamputa.value === addSamputa.value && manageAuthor.value === addAuthor.value) {
                    manageAuthor.dispatchEvent(new Event("change"));
                }
            } else {
                // Only show the backend error message
                showInfo(resp?.error || "Failed to create.");
            }
        } catch (err) {
            // Try to extract backend error message
            const backendError = err?.response?.data?.error;
            showInfo(backendError || "Error while creating. " + err);
            //console.error(err); // optional: keep for debugging
        } finally {
            hideLoader();
        }
    });






    // ---------- CSV Template ----------
    function downloadParibhashikaTemplateCSV() {
        if (!samputaAuthors.length) {
            showInfo("No samputa-author data loaded yet. Please reload the page.");
            return;
        }

        const rows = [
            [
                "tatvapada_author_id",
                "tatvapadakarara_hesaru",
                "samputa_sankhye",
                "paribhashika_padavivarana_title",
                "paribhashika_padavivarana_content"
            ]
        ];

        samputaAuthors.forEach(item => {
            item.authors.forEach(author => {
                rows.push([
                    `"${author.id}"`,
                    `"${author.name}"`,
                    `"${item.samputa}"`,
                    "",
                    ""
                ]);
            });
        });

        const csv = "\uFEFF" + rows.map(r => r.join(",")).join("\n");
        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "paribhashika_template.csv";
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    }

    downloadTemplateBtn.addEventListener("click", downloadParibhashikaTemplateCSV);


    // ---------- Init ----------
    await loadSamputaAuthors();




    // ---------- Multiple CSV Upload ----------
    const csvInput = document.getElementById("paribhashika_csv");
    const fileListEl = document.getElementById("paribhashika_file_list");
    const uploadBtn = document.getElementById("paribhashika_upload_btn");
    const progressEl = document.querySelector("#paribhashika_fileModal .progress");
    const progressBarEl = document.querySelector("#paribhashika_fileModal .progress-bar");

    let selectedFiles = [];

    // Update file review list
    csvInput.addEventListener("change", () => {
        selectedFiles = Array.from(csvInput.files);
        fileListEl.innerHTML = "";

        if (!selectedFiles.length) {
            fileListEl.innerHTML = "<li class='list-group-item'>No files selected</li>";
            return;
        }

        selectedFiles.forEach((file, idx) => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";
            li.textContent = file.name;
            const removeBtn = document.createElement("button");
            removeBtn.className = "btn btn-sm btn-outline-danger";
            removeBtn.textContent = "Remove";
            removeBtn.addEventListener("click", () => {
                selectedFiles.splice(idx, 1);
                const dt = new DataTransfer();
                selectedFiles.forEach(f => dt.items.add(f));
                csvInput.files = dt.files;
                li.remove();
            });
            li.appendChild(removeBtn);
            fileListEl.appendChild(li);
        });
    });

    // Sequential upload
    uploadBtn.addEventListener("click", async () => {
        if (!selectedFiles.length) return alert("No files selected.");

        progressEl.style.display = "block";
        progressBarEl.style.width = "0%";
        progressBarEl.textContent = "0%";

        const successEl = document.getElementById("paribhashika_upload_success");
        const errorEl = document.getElementById("paribhashika_upload_error");
        const warningsEl = document.getElementById("paribhashika_upload_warnings");

        successEl.style.display = "none";
        errorEl.style.display = "none";
        warningsEl.style.display = "none";
        warningsEl.innerHTML = "";

        let uploadedCount = 0;

        for (const file of selectedFiles) {
            const formData = new FormData();
            formData.append("file", file);

            try {
                const resp = await apiClient.request({
                    method: "POST",
                    endpoint: apiEndpoints.rightSection.padavivaranaApiUpload,
                    body: formData,
                    headers: {}
                });

                uploadedCount++;

                progressBarEl.style.width = `${Math.round((uploadedCount / selectedFiles.length) * 100)}%`;
                progressBarEl.textContent = `${Math.round((uploadedCount / selectedFiles.length) * 100)}%`;

                if (resp.success) {
                    if (resp.errors?.length) {
                        resp.errors.forEach(e => {
                            const li = document.createElement("li");
                            li.textContent = e;
                            warningsEl.appendChild(li);
                        });
                    }
                } else {
                    const li = document.createElement("li");
                    li.textContent = resp.message || "Upload failed";
                    warningsEl.appendChild(li);
                }

            } catch (err) {
                console.error(err);
                const li = document.createElement("li");
                li.textContent = `Error uploading ${file.name}`;
                warningsEl.appendChild(li);
            }
        }

        progressEl.style.display = "none";
        if (warningsEl.children.length) warningsEl.style.display = "block";
        successEl.textContent = `Uploaded ${uploadedCount} / ${selectedFiles.length} file(s)`;
        successEl.style.display = "block";

        // Reset input
        csvInput.value = "";
        selectedFiles = [];
        fileListEl.innerHTML = "<li class='list-group-item'>No files selected</li>";
    });



    // Bind upload form submit
    document.getElementById("paribhashika_upload_form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const file = document.getElementById("paribhashika_csv").files[0];
        await uploadParibhashikaCSV(file);
    });



}
