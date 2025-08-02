import apiClient from "./apiClient.js";
import apiEndpoints from "./apiEndpoints.js";

let currentTatvapadaData = [];

document.addEventListener("DOMContentLoaded", () => {
    function selectTab(element) {
        document.querySelectorAll('.top-navabar-bar .nav-btn').forEach(btn => btn.classList.remove('active'));
        element.classList.add('active');
    }

    initializeDropdownHandlers();
    loadSamputas();
});

// ---------- Setup Event Listeners ----------
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

// ---------- Load Samputas from API ----------
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

// ---------- Fetch Authors + Sankhyes ----------
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

// ---------- Populate Sankhyes ----------
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

// ---------- Fetch Specific Tatvapada ----------
function fetchSpecificTatvapada(samputa, authorId, sankhye) {
    const endpoint = apiEndpoints.tatvapada.getSpecificTatvapada(samputa, authorId, sankhye);

    apiClient.get(endpoint)
        .then(data => {
            renderTatvapada(data);
            //populateTatvapadaForm(data);
        })
        .catch(error => {
            console.error("Error fetching specific Tatvapada:", error);
        });
}

// ---------- Reset Any Dropdown ----------
function resetDropdown(dropdown, placeholderText, disable = false) {
    dropdown.innerHTML = `<option value="">${placeholderText}</option>`;
    dropdown.disabled = disable;
}

// ---------- Render Tatvapada ----------
function renderTatvapada(data) {
    displayPoem({
        text: data.tatvapada_sheershike,
        poem: data.tatvapada,
        author: data.tatvapadakarara_hesaru
    });

    displayOtherFields(data);
}

function displayOtherFields(data) {

    document.getElementById('tatvapadakosha_sheershike_value').textContent = data.tatvapadakosha_sheershike || "";
    document.getElementById('tatvapadakarara_hesaru_value').textContent = data.tatvapadakarara_hesaru || "";
    document.getElementById('tatvapada_sheershike_value').textContent = data.tatvapada_sheershike || "";
    document.getElementById('klishta_padagalu_artha_value').textContent = data.klishta_padagalu_artha || "";
    document.getElementById('tippani_value').textContent = data.tippani || "";
    document.getElementById('tatvapada_first_line_value').textContent = data.tatvapada_first_line || "";
    document.getElementById('bhavanuvada_value').textContent = data.bhavanuvada || "";
}

function displayPoem(poemData) {
    const poemDisplayArea = document.getElementById('poem-display-area');
    if (!poemDisplayArea) {
        console.error("Poem display area not found");
        return;
    }

    const cleanedPoem = poemData.poem
        .trim()
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => `<p>${line}</p>`)
        .join("");

    poemDisplayArea.innerHTML = `
        <div class="poem-display enhanced">
            <h3 class="poem-title">${poemData.text}</h3>
            <div class="poem-content">${cleanedPoem}</div>
            <div class="poem-author">- ${poemData.author}</div>
        </div>
    `;
}

// ---------- Populate Form ----------
function populateTatvapadaForm(data) {
    if (!data) return;

    document.getElementById('tatvapadakosha').value = data.tatvapadakosha || "";
    document.getElementById('tatvapadakosha_sheershike').value = data.tatvapadakosha_sheershike || "";
    document.getElementById('mukhya_sheershike').value = data.mukhya_sheershike || "";

    document.getElementById('tatvapadakarara_hesaru-edit').value = data.tatvapadakarara_hesaru || "";
    document.getElementById('tatvapada_hesaru').value = data.tatvapada_hesaru || "";
    document.getElementById('tatvapada_first_line').value = data.tatvapada_first_line || "";

    document.getElementById('tatvapada').value = data.tatvapada || "";
    document.getElementById('klishta_padagalu_artha').value = data.klishta_padagalu_artha || "";
    document.getElementById('tippani').value = data.tippani || "";
}
