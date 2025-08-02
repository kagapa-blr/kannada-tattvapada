import apiClient from "./apiClient.js";
import apiEndpoints from "./apiEndpoints.js";

let currentTatvapadaData = [];




// --------------------- DOM Ready --------------------- //
document.addEventListener("DOMContentLoaded", () => {
    initializeFormSubmitHandler();
    setupNavigation();
    initializeDropdownHandlers();
    loadSamputas();


    document.addEventListener('hide.bs.modal', function (event) {
        if (document.activeElement) {
            document.activeElement.blur();
        }
    });

});

// --------------------- UI Navigation --------------------- //
function setupNavigation() {
    document.querySelectorAll('.top-navabar-bar .nav-btn').forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll('.top-navabar-bar .nav-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

// --------------------- Dropdown Setup --------------------- //
function initializeDropdownHandlers() {
    const samputaDropdown = document.getElementById("samputa");
    const authorDropdown = document.getElementById("tatvapadakarara_hesaru");
    const sankhyeDropdown = document.getElementById("tatvapada_sankhye");

    samputaDropdown.addEventListener("change", () => {
        const samputa = samputaDropdown.value;
        if (samputa) {
            fetchAuthorsAndSankhyas(samputa);
        } else {
            resetDropdown(authorDropdown, "ತತ್ವಪದಕಾರರ ಹೆಸರು", true);
            resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
        }
    });

    authorDropdown.addEventListener("change", () => {
        const authorId = authorDropdown.value;
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

        if (sankhye && samputa && authorId) {
            fetchSpecificTatvapada(samputa, authorId, sankhye);
        }
    });
}

// --------------------- Load Samputa --------------------- //
function loadSamputas() {
    apiClient.get(apiEndpoints.tatvapada.getSamputas)
        .then(samputas => {
            const dropdown = document.getElementById("samputa");
            resetDropdown(dropdown, "ಸಂಪುಟ ಆಯ್ಕೆಮಾಡಿ", false);

            samputas.forEach(sankhye => {
                const option = document.createElement("option");
                option.value = sankhye;
                option.textContent = `ಸಂಪುಟ ${sankhye}`;
                dropdown.appendChild(option);
            });

            dropdown.disabled = false;
        })
        .catch(error => {
            console.error("Error loading Samputas:", error);
        });
}

// --------------------- Fetch Author & Sankhya --------------------- //
function fetchAuthorsAndSankhyas(samputaSankhye) {
    const endpoint = apiEndpoints.tatvapada.getAuthorSankhyasBySamputa(samputaSankhye);

    apiClient.get(endpoint)
        .then(data => {
            currentTatvapadaData = data;

            const authorDropdown = document.getElementById("tatvapadakarara_hesaru");
            const sankhyeDropdown = document.getElementById("tatvapada_sankhye");

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
        .catch(error => {
            console.error("Error fetching authors for samputa:", error);
        });
}

// --------------------- Populate Sankhyes --------------------- //
function populateTatvapadaSankhyes(authorId) {
    const sankhyeDropdown = document.getElementById("tatvapada_sankhye");
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

// --------------------- Fetch & Populate Form --------------------- //
function fetchSpecificTatvapada(samputa, authorId, sankhye) {
    const endpoint = apiEndpoints.tatvapada.getSpecificTatvapada(samputa, authorId, sankhye);

    return apiClient.get(endpoint)
        .then(data => populateTatvapadaForm(data))
        .catch(error => {
            console.error("Error fetching specific Tatvapada:", error);
        });
}

function populateTatvapadaForm(data) {
    if (!data) return;
    document.getElementById("tatvapadakosha_sheershike").value = data.tatvapadakosha_sheershike || "";
    document.getElementById("tatvapada_sheershike").value = data.tatvapada_sheershike || "";
    document.getElementById("vibhag").value = data.vibhag || "";
    document.getElementById("tatvapadakarara_hesaru_update").value = data.tatvapadakarara_hesaru || "";
    document.getElementById("tatvapada_first_line").value = data.tatvapada_first_line || "";
    document.getElementById("tatvapada").value = data.tatvapada || "";
    document.getElementById("bhavanuvada").value = data.bhavanuvada || "";
    document.getElementById("klishta_padagalu_artha").value = data.klishta_padagalu_artha || "";
    document.getElementById("tippani").value = data.tippani || "";
}

// --------------------- Submit Handler --------------------- //


function initializeFormSubmitHandler() {
    const form = document.getElementById("tatvapada-update-form");

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const jsonData = Object.fromEntries(formData.entries());

        const samputa = document.getElementById("samputa").value;
        const sankhye = document.getElementById("tatvapada_sankhye").value;
        const authorId = document.getElementById("tatvapadakarara_hesaru").value;

        if (!samputa || !sankhye || !authorId) {
            alert("ಸಂಪುಟ, ತತ್ವಪದ ಸಂಖ್ಯೆ ಮತ್ತು ತತ್ವಪದಕಾರರ ಆಯ್ಕೆ ಅಗತ್ಯವಿದೆ");
            return;
        }

        jsonData.samputa_sankhye = samputa;
        jsonData.tatvapada_sankhye = sankhye;
        jsonData.tatvapada_author_id = authorId;

        apiClient.put(apiEndpoints.tatvapada.updateTatvapada, jsonData)
            .then((response) => {

                populateTatvapadaForm(response.updated_entry); // update immediately

                // show modal with optional callback
                showSuccessModal(null, response?.message || "ಅಪ್ಡೇಟ್ ಯಶಸ್ವಿಯಾಗಿದೆ.");
            })
            .catch(error => {
                handleErrorModal(error);
            });
    });
}



// --------------------- Modal Helpers --------------------- //



function showSuccessModal(callback, message = "ತತ್ತ್ವಪದ ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ.") {
    const modalElement = document.getElementById("successModal");

    if (!modalElement) return;

    const serverMessageElement = modalElement.querySelector("#successMessage");
    if (serverMessageElement) {
        serverMessageElement.textContent = message;
    }

    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    modalElement.addEventListener("hidden.bs.modal", () => {
        callback?.();
    }, { once: true });
}


function handleErrorModal(error) {

    const messageEl = document.getElementById("errorMessage");
    const defaultText = "ತತ್ತ್ವಪದವನ್ನು ಉಳಿಸಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ.";
    if (messageEl) {
        messageEl.textContent = error?.message || defaultText;
    }
    const modal = new bootstrap.Modal(document.getElementById("errorModal"));
    modal.show();
}



function resetDropdown(dropdown, placeholder, disable = false) {
    dropdown.innerHTML = `<option value="">${placeholder}</option>`;
    dropdown.disabled = disable;
}
