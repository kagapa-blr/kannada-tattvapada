// static/js/tabs/add.js
import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

let currentTatvapadaData = [];
let initialized = false; // prevent double init

export function initAddTab() {
    if (initialized) {
        return;
    }
    initialized = true;

    initializeModeSwitching();
    initializeDropdownHandlers();
    loadSamputas();
    initializeFormSubmitHandler();

    initializeBulkUploadHandler();
    // Accessibility fix for bootstrap modals
    document.addEventListener("hide.bs.modal", function () {
        if (document.activeElement) {
            document.activeElement.blur();
        }
    });
}

// --------------------- Mode Switching --------------------- //
function initializeModeSwitching() {
    const modeNew = document.getElementById("add_tatvapada_modeNew");
    const modeExisting = document.getElementById("add_tatvapada_modeExisting");
    const inputsContainer = document.getElementById("add_tatvapada_inputs_container");
    const cascadingSection = document.getElementById("add_tatvapada_cascading_section");

    function updateModeUI() {
        if (modeNew.checked) {
            inputsContainer.style.display = "";
            cascadingSection.style.display = "none";
            resetDropdown(document.getElementById("add_tatvapada_samputa"), "ತತ್ವಪದಕೋಶ ಸಂಪುಟ ಆಯ್ಕೆಮಾಡಿ", true);
            resetDropdown(document.getElementById("add_tatvapada_tatvapadakarara_hesaru"), "ತತ್ವಪದಕಾರರ ಹೆಸರು", true);
            resetDropdown(document.getElementById("add_tatvapada_tatvapada_sankhye"), "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
            removeInlineNewAuthorInput();
            removeInlineNewSankhyeInput();
        } else {
            inputsContainer.style.display = "none";
            cascadingSection.style.display = "";
        }
    }

    modeNew.addEventListener("change", updateModeUI);
    modeExisting.addEventListener("change", updateModeUI);
    updateModeUI();
}

// --------------------- Dropdown Handlers --------------------- //
function initializeDropdownHandlers() {
    const samputaDropdown = document.getElementById("add_tatvapada_samputa");
    const authorDropdown = document.getElementById("add_tatvapada_tatvapadakarara_hesaru");
    const sankhyeDropdown = document.getElementById("add_tatvapada_tatvapada_sankhye");

    samputaDropdown.addEventListener("change", () => {
        const samputa = samputaDropdown.value;
        if (samputa) {
            fetchAuthorsAndSankhyas(samputa);
        } else {
            resetDropdown(authorDropdown, "ತತ್ವಪದಕಾರರ ಹೆಸರು", true);
            resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
            removeInlineNewAuthorInput();
            removeInlineNewSankhyeInput();
        }
    });

    authorDropdown.addEventListener("change", () => {
        const authorId = authorDropdown.value;
        if (authorId === "__add_new__") {
            showInlineNewAuthorInput();
            sankhyeDropdown.disabled = false;
            resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", false);
            appendAddNewSankhyeOption();
        } else {
            removeInlineNewAuthorInput();
            if (authorId) {
                populateTatvapadaSankhyes(authorId);
                sankhyeDropdown.disabled = false;
            } else {
                resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
                removeInlineNewSankhyeInput();
            }
        }
    });

    sankhyeDropdown.addEventListener("change", () => {
        const sankhye = sankhyeDropdown.value;
        const samputa = document.getElementById("add_tatvapada_samputa").value;
        const authorId = document.getElementById("add_tatvapada_tatvapadakarara_hesaru").value;

        if (sankhye === "__add_new_sankhye__") {
            showInlineNewSankhyeInput();
            return;
        } else {
            removeInlineNewSankhyeInput();
        }

        if (sankhye && samputa && authorId && authorId !== "__add_new__") {
            fetchSpecificTatvapada(samputa, authorId, sankhye).then((data) => {
                if (data) populateTatvapadaForm(data);
            });
        }
    });
}

// --------------------- Load Samputas --------------------- //
function loadSamputas() {
    showLoader();
    apiClient
        .get(apiEndpoints.tatvapada.getSamputas)
        .then((samputas) => {
            const list = Array.isArray(samputas)
                ? samputas
                : samputas && typeof samputas === "object"
                    ? Object.keys(samputas)
                    : [];

            const samputaSuggestionValue = document.getElementById("add_tatvapada_samputa_suggestion_value");
            const sortedList = list.slice().sort((a, b) => a - b);
            samputaSuggestionValue.textContent = `[${sortedList.join(", ")}]`;

            const dropdown = document.getElementById("add_tatvapada_samputa");
            resetDropdown(dropdown, "ತತ್ವಪದಕೋಶ ಸಂಪುಟ ಆಯ್ಕೆಮಾಡಿ", true);
            dropdown.innerHTML = `<option value="" disabled selected>ತತ್ವಪದಕೋಶ ಸಂಪುಟ ಆಯ್ಕೆಮಾಡಿ</option>`;

            list.forEach((sankhye) => {
                const option = document.createElement("option");
                option.value = sankhye;
                option.textContent = `ಸಂಪುಟ ${sankhye}`;
                dropdown.appendChild(option);
            });

            dropdown.disabled = false;
        })
        .catch((error) => {
            console.error("[AddTab] Error loading Samputas:", error);
        })
        .finally(() => {
            hideLoader();
        });
}

// --------------------- Fetch Authors & Sankhyas --------------------- //
function fetchAuthorsAndSankhyas(samputaSankhye) {
    const endpoint = apiEndpoints.tatvapada.getAuthorSankhyasBySamputa(samputaSankhye);

    showLoader();
    apiClient
        .get(endpoint)
        .then((data) => {
            currentTatvapadaData = data || [];

            const authorDropdown = document.getElementById("add_tatvapada_tatvapadakarara_hesaru");
            const sankhyeDropdown = document.getElementById("add_tatvapada_tatvapada_sankhye");

            resetDropdown(authorDropdown, "ತತ್ವಪದಕಾರರ ಹೆಸರು", false);
            resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
            removeInlineNewAuthorInput();
            removeInlineNewSankhyeInput();

            const seen = new Set();
            currentTatvapadaData.forEach((item) => {
                if (!seen.has(item.tatvapadakarara_id)) {
                    const option = document.createElement("option");
                    option.value = item.tatvapadakarara_id;
                    option.textContent = item.tatvapadakarara_hesaru;
                    authorDropdown.appendChild(option);
                    seen.add(item.tatvapadakarara_id);
                }
            });

            const addNew = document.createElement("option");
            addNew.value = "__add_new__";
            addNew.textContent = "Add new ತತ್ವಪದಕಾರರ ಹೆಸರು";
            authorDropdown.appendChild(addNew);
        })
        .catch((error) => {
            console.error("[AddTab] Error fetching authors for samputa:", error);
        })
        .finally(() => {
            hideLoader();
        });
}


// --------------------- Populate Sankhyes --------------------- //
function populateTatvapadaSankhyes(authorId) {
    const sankhyeDropdown = document.getElementById("add_tatvapada_tatvapada_sankhye");
    resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", false);
    removeInlineNewSankhyeInput();

    const filtered = currentTatvapadaData.filter(
        (item) => item.tatvapadakarara_id.toString() === authorId.toString()
    );

    filtered.forEach((item) => {
        const option = document.createElement("option");
        option.value = item.tatvapada_sankhye;
        option.textContent = `ತತ್ವಪದ ${item.tatvapada_sankhye}`;
        sankhyeDropdown.appendChild(option);
    });

    appendAddNewSankhyeOption();
}

// --------------------- Fetch & Populate Form --------------------- //
function fetchSpecificTatvapada(samputa, authorId, sankhye) {
    const endpoint = apiEndpoints.tatvapada.getSpecificTatvapada(samputa, authorId, sankhye);

    showLoader();
    return apiClient
        .get(endpoint)
        .then((data) => data)
        .catch((error) => {
            console.error("[AddTab] Error fetching specific Tatvapada:", error);
        })
        .finally(() => {
            hideLoader();
        });
}


function populateTatvapadaForm(data) {
    if (!data) return;
    document.getElementById("add_tatvapada_tatvapadakosha_sheershike").value = data.tatvapadakosha_sheershike || "";
    document.getElementById("add_tatvapada_tatvapada_sheershike").value = data.tatvapada_sheershike || "";
    document.getElementById("add_tatvapada_first_line").value = data.tatvapada_first_line || "";
    document.getElementById("add_tatvapada_tatvapada").value = data.tatvapada || "";
    document.getElementById("add_tatvapada_klishta_padagalu_artha").value = data.klishta_padagalu_artha || "";
    document.getElementById("add_tatvapada_tippani").value = data.tippani || "";
    document.getElementById("add_tatvapada_samputa_input").value = data.samputa_sankhye || "";
    document.getElementById("add_tatvapada_bhavanuvada").value = data.bhavanuvada || "";
    document.getElementById("add_tatvapada_vibhag").value = data.vibhag || "";
}

// --------------------- Inline Add-New Helpers --------------------- //
function showInlineNewAuthorInput() {
    const container = document.getElementById("add_tatvapada_inline_author_container");
    if (document.getElementById("add_tatvapada_inline_new_author")) return;

    container.innerHTML = "";
    const input = document.createElement("input");
    input.type = "text";
    input.id = "add_tatvapada_inline_new_author";
    input.placeholder = "ಹೊಸ ತತ್ವಪದಕಾರರ ಹೆಸರು";
    input.className = "form-control";
    container.appendChild(input);
}

function removeInlineNewAuthorInput() {
    const container = document.getElementById("add_tatvapada_inline_author_container");
    container.innerHTML = "";
}

function appendAddNewSankhyeOption() {
    const sankhyeDropdown = document.getElementById("add_tatvapada_tatvapada_sankhye");
    if ([...sankhyeDropdown.options].some(o => o.value === "__add_new_sankhye__")) return;
    const addNew = document.createElement("option");
    addNew.value = "__add_new_sankhye__";
    addNew.textContent = "Add new ತತ್ವಪದ ಸಂಖ್ಯೆ";
    sankhyeDropdown.appendChild(addNew);
}

function showInlineNewSankhyeInput() {
    const container = document.getElementById("add_tatvapada_inline_sankhye_container");
    if (document.getElementById("add_tatvapada_inline_new_sankhye")) return;

    container.innerHTML = "";
    const input = document.createElement("input");
    input.type = "number";
    input.id = "add_tatvapada_inline_new_sankhye";
    input.placeholder = "ಹೊಸ ತತ್ವಪದ ಸಂಖ್ಯೆ";
    input.className = "form-control";
    container.appendChild(input);
}

function removeInlineNewSankhyeInput() {
    const container = document.getElementById("add_tatvapada_inline_sankhye_container");
    container.innerHTML = "";
}

// --------------------- Submit Handler --------------------- //
function initializeFormSubmitHandler() {
    const form = document.getElementById("add_tatvapada_form");

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const isNewMode = document.getElementById("add_tatvapada_modeNew").checked;
        const formData = new FormData(form);
        const jsonData = Object.fromEntries(formData.entries());

        showLoader(); // 🚀 Show loader before hitting API

        if (isNewMode) {
            const samputa = document.getElementById("add_tatvapada_samputa_input").value.trim();
            const authorName = document.getElementById("add_tatvapada_tatvapadakarara_hesaru_input_modeNew").value.trim();
            const sankhye = document.getElementById("add_tatvapada_tatvapada_sankhye_input")?.value.trim();

            if (!authorName) {
                hideLoader();
                alert("ತತ್ವಪದಕಾರರ ಹೆಸರು ಅಗತ್ಯವಿದೆ");
                return;
            }

            jsonData.samputa_sankhye = samputa || null;
            jsonData.tatvapadakarara_hesaru = authorName;
            if (sankhye) jsonData.tatvapada_sankhye = sankhye;

            apiClient
                .post(apiEndpoints.tatvapada.addTatvapada, jsonData)
                .then((response) => {
                    showSuccessModal(null, response?.message || "ಸೇರಿಸಲಾಗಿದೆ.");
                    if (response?.created_entry) {
                        populateTatvapadaForm(response.created_entry);
                    }
                })
                .catch((error) => {
                    console.error("[AddTab] Add API Error:", error);
                    handleErrorModal(error);
                })
                .finally(() => {
                    hideLoader(); // ✅ always hide loader
                });

        } else {
            const samputa = document.getElementById("add_tatvapada_samputa").value;
            const sankhyeSelect = document.getElementById("add_tatvapada_tatvapada_sankhye");
            const authorDropdown = document.getElementById("add_tatvapada_tatvapadakarara_hesaru");
            const authorId = authorDropdown.value;
            const sankhyeValue = sankhyeSelect.value;

            if (!samputa) {
                hideLoader();
                alert("ಸಂಪುಟ ಆಯ್ಕೆ ಮಾಡಬೇಕು");
                return;
            }
            jsonData.samputa_sankhye = samputa;

            if (authorId === "__add_new__") {
                const inlineAuthorInput = document.getElementById("add_tatvapada_inline_new_author");
                if (!inlineAuthorInput || !inlineAuthorInput.value.trim()) {
                    hideLoader();
                    alert("ಹೊಸ ತತ್ವಪದಕಾರರ ಹೆಸರು ನೀಡಿರಿ");
                    return;
                }
                jsonData.tatvapadakarara_hesaru = inlineAuthorInput.value.trim();
            } else if (authorId) {
                jsonData.tatvapada_author_id = authorId;
            } else {
                hideLoader();
                alert("ತತ್ವಪದಕಾರರ ಹೆಸರು ಆಯ್ಕೆ ಅಗತ್ಯವಿದೆ");
                return;
            }

            if (sankhyeValue === "__add_new_sankhye__") {
                const inlineSankhyeInput = document.getElementById("add_tatvapada_inline_new_sankhye");
                if (!inlineSankhyeInput || !inlineSankhyeInput.value.trim()) {
                    hideLoader();
                    alert("ಹೊಸ ತತ್ವಪದ ಸಂಖ್ಯೆ ನೀಡಿ");
                    return;
                }
                jsonData.tatvapada_sankhye = inlineSankhyeInput.value.trim();
            } else if (sankhyeValue) {
                jsonData.tatvapada_sankhye = sankhyeValue;
            } else {
                hideLoader();
                alert("ತತ್ವಪದ ಸಂಖ್ಯೆ ಆಯ್ಕೆ ಮಾಡಬೇಕು");
                return;
            }

            apiClient
                .post(apiEndpoints.tatvapada.addTatvapada, jsonData)
                .then((response) => {
                    showSuccessModal(null, response?.message || "ಅಪ್ಡೇಟ್ ಯಶಸ್ವಿಯಾಗಿದೆ.");
                    if (response?.created_entry) {
                        populateTatvapadaForm(response.created_entry);
                    }
                })
                .catch((error) => {
                    console.error("[AddTab] Update API Error:", error);
                    handleErrorModal(error);
                })
                .finally(() => {
                    hideLoader(); // ✅ always hide loader
                });
        }
    });
}


// --------------------- Modal Helpers --------------------- //
function showSuccessModal(callback, message = "ಯಶಸ್ವಿಯಾಗಿದೆ.") {
    const modalElement = document.getElementById("add_tatvapada_successModal");
    if (!modalElement) return;

    const serverMessageElement = modalElement.querySelector("#add_tatvapada_successMessage");
    if (serverMessageElement) {
        serverMessageElement.textContent = message;
    }

    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    modalElement.addEventListener(
        "hidden.bs.modal",
        () => {
            callback?.();
        },
        { once: true }
    );
}

function handleErrorModal(error) {
    const messageEl = document.getElementById("add_tatvapada_errorMessage");
    const defaultText = "ತತ್ವಪದವನ್ನು ಸೇರಿಸಲು ಸಾಧ್ಯವಾದಿಲ್ಲ.";
    if (messageEl) {
        messageEl.textContent = error?.message || defaultText;
    }
    const modal = new bootstrap.Modal(document.getElementById("add_tatvapada_errorModal"));
    modal.show();
}

// --------------------- Utility --------------------- //
function resetDropdown(dropdown, placeholder, disable = false) {
    dropdown.innerHTML = `<option value="">${placeholder}</option>`;
    dropdown.disabled = disable;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function initializeBulkUploadHandler() {
    const bulkForm = document.getElementById('bulk_upload_form');
    if (!bulkForm) return;

    if (bulkForm.dataset.bound === "1") return;
    bulkForm.dataset.bound = "1";

    const confirmModalEl = document.getElementById('bulk_upload_confirmModal');
    const confirmModal = new bootstrap.Modal(confirmModalEl);
    const confirmListEl = document.getElementById('bulk_upload_confirmFileList');
    const confirmEmptyEl = document.getElementById('bulk_upload_confirmEmpty');
    const confirmBtn = document.getElementById('bulk_upload_confirmBtn');

    let selectedFiles = [];

    bulkForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const fileInput = document.getElementById('bulk_upload_file');

        if (!fileInput.files || !fileInput.files.length) {
            alert("CSV ಫೈಲ್ ಆಯ್ಕೆಮಾಡಿ");
            return;
        }

        selectedFiles = Array.from(fileInput.files);
        renderConfirmList();
        confirmModal.show();
    });

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
            li.className = "list-group-item d-flex justify-content-between align-items-center";
            li.innerHTML = `
                <span>${file.name}</span>
                <button type="button" class="btn btn-sm btn-outline-danger">Remove</button>
            `;

            li.querySelector("button").addEventListener("click", function () {
                selectedFiles.splice(index, 1);
                renderConfirmList();
            });

            confirmListEl.appendChild(li);
        });
    }

    confirmBtn.addEventListener('click', async function () {
        if (!selectedFiles.length) {
            alert("No files selected for upload.");
            return;
        }

        confirmModal.hide();
        await startBulkUpload();
    });

    async function startBulkUpload() {
        const progressEl = document.getElementById('bulk_upload_progress');
        const progressBar = document.getElementById('bulk_upload_progressbar');
        const submitBtn = bulkForm.querySelector("button[type='submit']");

        const files = selectedFiles.slice();
        const total = files.length;

        if (!total) return;

        submitBtn.disabled = true;

        progressEl.textContent = `Total files: ${total}. Upload started.`;
        progressBar.style.width = "0%";
        progressBar.textContent = `0 / ${total}`;

        const finalMessages = [];

        for (let i = 0; i < files.length; i++) {
            const file = files[i];

            progressEl.textContent = `Uploading file ${i + 1} of ${total}: ${file.name}`;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch(apiEndpoints.tatvapada.bulkUploadUsingCSV, {
                    method: 'POST',
                    body: formData
                });

                const clonedResponse = response.clone();
                let data;
                try {
                    data = await response.json();
                } catch {
                    data = { success: false, message: await clonedResponse.text() };
                }

                if (response.ok && data.success) {
                    let msg = `<strong>${file.name}</strong> uploaded successfully.`;

                    if (Array.isArray(data.errors) && data.errors.length > 0) {
                        msg += `<br>Row errors:<ul>${data.errors.map(e => `<li>${e}</li>`).join('')}</ul>`;
                    }

                    finalMessages.push(msg);
                } else {
                    let errMsg = `<strong>${file.name}</strong> upload failed.`;

                    if (Array.isArray(data.errors) && data.errors.length > 0) {
                        errMsg += `<ul>${data.errors.map(e => `<li>${e}</li>`).join('')}</ul>`;
                    } else {
                        errMsg += `<br>${data.message || data.error || "Upload failed due to server error."}`;
                    }

                    finalMessages.push(errMsg);
                }
            } catch (err) {
                finalMessages.push(
                    `<strong>${file.name}</strong> upload failed due to network error: ${err.message || ""}`
                );
            }

            const percent = Math.round(((i + 1) / total) * 100);
            progressBar.style.width = percent + "%";
            progressBar.textContent = `${i + 1} / ${total}`;

            if (i < files.length - 1) {
                progressEl.textContent = "Waiting 5 seconds before uploading the next file...";
                await sleep(5000);
            }
        }

        submitBtn.disabled = false;
        bulkForm.reset();
        selectedFiles = [];

        progressEl.textContent = `Upload completed. ${total} file(s) processed.`;

        document.getElementById('bulk_upload_successMessage').innerHTML = finalMessages.join("<hr>");
        new bootstrap.Modal(document.getElementById('bulk_upload_successModal')).show();
    }
}
