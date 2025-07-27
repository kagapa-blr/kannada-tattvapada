import apiClient from "./apiClient.js";
import apiEndpoints from "./apiEndpoints.js";

let currentTatvapadaData = [];

document.addEventListener("DOMContentLoaded", () => {
    setupNavigation();
    initializeDropdownHandlers();
    loadSamputas();
    initializeFormSubmitHandler();
});

// ---------- UI Tab Highlighting ----------
function setupNavigation() {
    document.querySelectorAll('.top-navabar-bar .nav-btn').forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll('.top-navabar-bar .nav-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

// ---------- Initialize Dropdown Logic ----------
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

// ---------- Load Samputa Dropdown ----------
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

// ---------- Fetch Authors & Sankhyas for Samputa ----------
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

// ---------- Populate Sankhyes for Selected Author ----------
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

// ---------- Fetch a Specific Tatvapada Entry ----------
function fetchSpecificTatvapada(samputa, authorId, sankhye) {
    const endpoint = apiEndpoints.tatvapada.getSpecificTatvapada(samputa, authorId, sankhye);

    apiClient.get(endpoint)
        .then(data => populateTatvapadaForm(data))
        .catch(error => {
            console.error("Error fetching specific Tatvapada:", error);
        });
}

// ---------- Populate Form Fields ----------
function populateTatvapadaForm(data) {
    if (!data) return;

    document.getElementById("tatvapadakosha").value = data.tatvapadakosha || "";
    document.getElementById("tatvapadakosha_sheershike").value = data.tatvapadakosha_sheershike || "";
    document.getElementById("mukhya_sheershike").value = data.mukhya_sheershike || "";

    document.getElementById("tatvapadakarara_hesaru-edit").value = data.tatvapadakarara_hesaru || "";
    document.getElementById("tatvapada_hesaru").value = data.tatvapada_hesaru || "";
    document.getElementById("tatvapada_first_line").value = data.tatvapada_first_line || "";

    document.getElementById("tatvapada").value = data.tatvapada || "";
    document.getElementById("klishta_padagalu_artha").value = data.klishta_padagalu_artha || "";
    document.getElementById("tippani").value = data.tippani || "";
}

// ---------- Submit Updated Tatvapada ----------
function initializeFormSubmitHandler() {
    const form = document.getElementById("tatvapada-update-form");

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const jsonData = Object.fromEntries(formData.entries());

        const samputa_sankhye = document.getElementById("samputa").value;
        const tatvapada_sankhye = document.getElementById("tatvapada_sankhye").value;
        const tatvapada_author_id = document.getElementById("tatvapadakarara_hesaru").value;

        if (!samputa_sankhye || !tatvapada_sankhye || !tatvapada_author_id) {
            alert("ಸಂಪುಟ, ತತ್ವಪದ ಸಂಖ್ಯೆ ಮತ್ತು ತತ್ವಪದಕಾರರ ಆಯ್ಕೆ ಅಗತ್ಯವಿದೆ");
            return;
        }

        jsonData.samputa_sankhye = samputa_sankhye;
        jsonData.tatvapada_sankhye = tatvapada_sankhye;
        jsonData.tatvapada_author_id = tatvapada_author_id;

        apiClient.put(apiEndpoints.tatvapada.updateTatvapada, jsonData)
            .then(response => {
                console.log("Update response:", response);
                alert("ತತ್ತ್ವಪದ ಯಶಸ್ವಿಯಾಗಿ ಅಪ್‌ಡೇಟ್ ಮಾಡಲಾಗಿದೆ!");
            })
            .catch(error => {
                console.error("PUT error:", error);
                alert("ಅಪ್‌ಡೇಟ್ ವಿಫಲವಾಯಿತು. ದಯವಿಟ್ಟು ನಂತರ ಪ್ರಯತ್ನಿಸಿ.");
            });
    });
}

// ---------- Reset a Dropdown ----------
function resetDropdown(dropdown, placeholderText, disable = false) {
    dropdown.innerHTML = `<option value="">${placeholderText}</option>`;
    dropdown.disabled = disable;
}
