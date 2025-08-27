// static/js/tabs/update.js
import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

let currentTatvapadaData = [];
let initialized = false;

export function initUpdateTab() {
    if (initialized) {
        console.log("[UpdateTab] Already initialized");
        return;
    }
    initialized = true;

    console.log("[UpdateTab] Initialization...");

    initializeFormSubmitHandler();
    initializeDropdownHandlers();
    loadSamputas();
}

function initializeDropdownHandlers() {
    const samputaDropdown = document.getElementById("update_tatvapada_samputa");
    const authorDropdown = document.getElementById("update_tatvapada_author");
    const sankhyeDropdown = document.getElementById("update_tatvapada_sankhye");

    samputaDropdown.addEventListener("change", () => {
        const samputa = samputaDropdown.value;
        console.log("[UpdateTab] Samputa selected:", samputa);
        if (samputa) fetchAuthorsAndSankhyas(samputa);
        else {
            resetDropdown(authorDropdown, "ತತ್ವಪದಕಾರರ ಹೆಸರು", true);
            resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
        }
    });

    authorDropdown.addEventListener("change", () => {
        const authorId = authorDropdown.value;
        console.log("[UpdateTab] Author selected:", authorId);
        if (authorId) {
            populateTatvapadaSankhyes(authorId);
            sankhyeDropdown.disabled = false;
        } else {
            resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
        }
    });

    sankhyeDropdown.addEventListener("change", () => {
        const sankhye = sankhyeDropdown.value;
        const samputa = samputaDropdown.value;
        const authorId = authorDropdown.value;
        console.log("[UpdateTab] Sankhye selected:", sankhye);

        if (sankhye && samputa && authorId) {
            fetchSpecificTatvapada(samputa, authorId, sankhye);
        }
    });
}

function loadSamputas() {
    console.log("[UpdateTab] Loading Samputas...");
    showLoader();
    apiClient.get(apiEndpoints.tatvapada.getSamputas)
        .then(samputas => {
            const dropdown = document.getElementById("update_tatvapada_samputa");
            resetDropdown(dropdown, "ಸಂಪುಟ ಆಯ್ಕೆಮಾಡಿ", false);
            samputas.forEach(sankhye => {
                const option = document.createElement("option");
                option.value = sankhye;
                option.textContent = `ಸಂಪುಟ ${sankhye}`;
                dropdown.appendChild(option);
            });
            dropdown.disabled = false;
        })
        .catch(err => console.error("[UpdateTab] Error loading Samputas:", err))
        .finally(() => hideLoader());
}

function fetchAuthorsAndSankhyas(samputaSankhye) {
    console.log("[UpdateTab] Fetching authors for Samputa:", samputaSankhye);
    const endpoint = apiEndpoints.tatvapada.getAuthorSankhyasBySamputa(samputaSankhye);
    showLoader();
    apiClient.get(endpoint)
        .then(data => {
            currentTatvapadaData = data || [];
            const authorDropdown = document.getElementById("update_tatvapada_author");
            const sankhyeDropdown = document.getElementById("update_tatvapada_sankhye");

            resetDropdown(authorDropdown, "ತತ್ವಪದಕಾರರ ಹೆಸರು", false);
            resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);

            const seen = new Set();
            data.forEach(item => {
                if (!seen.has(item.tatvapadakarara_id)) {
                    const option = document.createElement("option");
                    option.value = item.tatvapadakarara_id;
                    option.textContent = item.tatvapadakarara_hesaru;
                    authorDropdown.appendChild(option);
                    seen.add(item.tatvapadakarara_id);
                }
            });
        })
        .catch(err => console.error("[UpdateTab] Error fetching authors:", err))
        .finally(() => hideLoader());
}

function populateTatvapadaSankhyes(authorId) {
    console.log("[UpdateTab] Populating tatvapadas for author:", authorId);
    const sankhyeDropdown = document.getElementById("update_tatvapada_sankhye");
    resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", false);

    const filtered = currentTatvapadaData.filter(
        item => item.tatvapadakarara_id.toString() === authorId
    );

    filtered.forEach(item => {
        const option = document.createElement("option");
        option.value = item.tatvapada_sankhye;
        option.textContent = `ತತ್ವಪದ ${item.tatvapada_sankhye}`;
        sankhyeDropdown.appendChild(option);
    });
}

function fetchSpecificTatvapada(samputa, authorId, sankhye) {
    console.log("[UpdateTab] Fetching specific tatvapada:", { samputa, authorId, sankhye });
    const endpoint = apiEndpoints.tatvapada.getSpecificTatvapada(samputa, authorId, sankhye);
    showLoader();
    return apiClient.get(endpoint)
        .then(data => {
            console.log("[UpdateTab] Tatvapada fetched:", data);
            populateTatvapadaForm(data);
        })
        .catch(err => console.error("[UpdateTab] Error fetching tatvapada:", err))
        .finally(() => hideLoader());
}

function populateTatvapadaForm(data) {
    if (!data) return;
    console.log("[UpdateTab] Populating form:", data.tatvapada_sheershike);
    document.getElementById("update_tatvapadakosha_sheershike").value = data.tatvapadakosha_sheershike || "";
    document.getElementById("update_tatvapada_sheershike").value = data.tatvapada_sheershike || "";
    document.getElementById("update_vibhag").value = data.vibhag || "";
    document.getElementById("update_author_name").value = data.tatvapadakarara_hesaru || "";
    document.getElementById("update_first_line").value = data.tatvapada_first_line || "";
    document.getElementById("update_tatvapada_text").value = data.tatvapada || "";
    document.getElementById("update_bhavanuvada").value = data.bhavanuvada || "";
    document.getElementById("update_klishta").value = data.klishta_padagalu_artha || "";
    document.getElementById("update_tippani").value = data.tippani || "";
}

function initializeFormSubmitHandler() {
    const form = document.getElementById("update_tatvapada_form");
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const jsonData = Object.fromEntries(formData.entries());

        const samputa = document.getElementById("update_tatvapada_samputa").value;
        const sankhye = document.getElementById("update_tatvapada_sankhye").value;
        const authorId = document.getElementById("update_tatvapada_author").value;

        if (!samputa || !sankhye || !authorId) {
            alert("ಸಂಪುಟ, ತತ್ವಪದ ಸಂಖ್ಯೆ ಮತ್ತು ತತ್ವಪದಕಾರರ ಆಯ್ಕೆ ಅಗತ್ಯವಿದೆ");
            return;
        }

        jsonData.samputa_sankhye = samputa;
        jsonData.tatvapada_sankhye = sankhye;
        jsonData.tatvapada_author_id = authorId;

        console.log("[UpdateTab] Submitting payload:", jsonData);

        showLoader();
        apiClient.put(apiEndpoints.tatvapada.updateTatvapada, jsonData)
            .then(response => {
                console.log("[UpdateTab] Update success:", response);
                populateTatvapadaForm(response.updated_entry);
                showSuccessModal(null, response?.message || "ಅಪ್ಡೇಟ್ ಯಶಸ್ವಿಯಾಗಿದೆ.");
            })
            .catch(err => {
                console.error("[UpdateTab] Update error:", err);
                handleErrorModal(err);
            })
            .finally(() => hideLoader());
    });
}

// ============== Modals ==============
function showSuccessModal(callback, message) {
    const modalEl = document.getElementById("update_tatvapada_successModal");
    if (!modalEl) return;
    const msgEl = modalEl.querySelector("#update_tatvapada_successMessage");
    if (msgEl) msgEl.textContent = message;

    new bootstrap.Modal(modalEl).show();
}

function handleErrorModal(error) {
    const msgEl = document.getElementById("update_tatvapada_errorMessage");
    if (msgEl) msgEl.textContent = error?.message || "ತತ್ವಪದವನ್ನು ಉಳಿಸಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ.";
    new bootstrap.Modal(document.getElementById("update_tatvapada_errorModal")).show();
}

// Helpers
function resetDropdown(dropdown, placeholder, disable = false) {
    dropdown.innerHTML = `<option value="">${placeholder}</option>`;
    dropdown.disabled = disable;
}
