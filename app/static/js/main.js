import apiClient from "./apiClient.js";
import apiEndpoints from "./apiEndpoints.js";

let currentTatvapadaData = [];
let choicesInstances = {};

document.addEventListener("DOMContentLoaded", () => {
    initializeDropdownsWithChoices();
    initializeDropdownHandlers();
    loadSamputas();
});

// ---------- Initialize Dropdowns with Choices ----------
function initializeDropdownsWithChoices() {
    const samputa = document.getElementById("samputa");
    const author = document.getElementById("tatvapadakarara_hesaru");
    const sankhye = document.getElementById("tatvapada_sankhye");

    choicesInstances.samputa = new Choices(samputa, {
        searchEnabled: true,
        itemSelectText: '',
        shouldSort: false,
        placeholderValue: 'ಸಂಪುಟ ಆಯ್ಕೆಮಾಡಿ'
    });

    choicesInstances.author = new Choices(author, {
        searchEnabled: true,
        itemSelectText: '',
        shouldSort: false,
        placeholderValue: 'ತತ್ವಪದಕಾರರ ಹೆಸರು'
    });

    choicesInstances.sankhye = new Choices(sankhye, {
        searchEnabled: true,
        itemSelectText: '',
        shouldSort: false,
        placeholderValue: 'ತತ್ವಪದ ಸಂಖ್ಯೆ'
    });

    // Disable initially
    choicesInstances.author.disable();
    choicesInstances.sankhye.disable();
}

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

// ---------- Load Samputas ----------
function loadSamputas() {
    apiClient.get(apiEndpoints.tatvapada.getSamputas)
        .then(samputas => {
            const dropdown = document.getElementById("samputa");
            resetDropdown(dropdown, "ಸಂಪುಟ ಆಯ್ಕೆಮಾಡಿ", false);

            const choices = samputas.map(sankhye => ({
                value: sankhye,
                label: `ಸಂಪುಟ ${sankhye}`
            }));

            choicesInstances.samputa.setChoices(choices, 'value', 'label', true);
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
            const authorChoices = [];

            data.forEach(item => {
                if (!seen.has(item.tatvapadakarara_id)) {
                    authorChoices.push({
                        value: item.tatvapadakarara_id,
                        label: item.tatvapadakarara_hesaru
                    });
                    seen.add(item.tatvapadakarara_id);
                }
            });

            choicesInstances.author.setChoices(authorChoices, 'value', 'label', true);
            choicesInstances.author.enable();
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

    const sankhyeChoices = filtered.map(item => ({
        value: item.tatvapada_sankhye,
        label: `ತತ್ವಪದ ${item.tatvapada_sankhye}`
    }));

    choicesInstances.sankhye.setChoices(sankhyeChoices, 'value', 'label', true);
    choicesInstances.sankhye.enable();
}

// ---------- Fetch Specific Tatvapada ----------
function fetchSpecificTatvapada(samputa, authorId, sankhye) {
    const endpoint = apiEndpoints.tatvapada.getSpecificTatvapada(samputa, authorId, sankhye);

    apiClient.get(endpoint)
        .then(data => {
            renderTatvapada(data);
        })
        .catch(error => {
            console.error("Error fetching specific Tatvapada:", error);
        });
}

// ---------- Reset Any Dropdown ----------
function resetDropdown(dropdown, placeholderText, disable = false) {
    const id = dropdown.id;

    if (choicesInstances[id]) {
        choicesInstances[id].clearChoices();
        choicesInstances[id].setChoices(
            [{ value: '', label: placeholderText, disabled: true, selected: true }],
            'value',
            'label',
            true
        );

        if (disable) {
            choicesInstances[id].disable();
        } else {
            choicesInstances[id].enable();
        }
    }
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

// ---------- Display Additional Tatvapada Info ----------
function displayOtherFields(data) {
    document.getElementById('tatvapadakosha_sheershike_value').textContent = data.tatvapadakosha_sheershike || "";
    document.getElementById('tatvapadakarara_hesaru_value').textContent = data.tatvapadakarara_hesaru || "";
    document.getElementById('tatvapada_sheershike_value').textContent = data.tatvapada_sheershike || "";
    document.getElementById('klishta_padagalu_artha_value').textContent = data.klishta_padagalu_artha || "";
    document.getElementById('tippani_value').textContent = data.tippani || "";
    document.getElementById('tatvapada_first_line_value').textContent = data.tatvapada_first_line || "";
    document.getElementById('bhavanuvada_value').textContent = data.bhavanuvada || "";
}

// ---------- Display Poem Nicely ----------
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
