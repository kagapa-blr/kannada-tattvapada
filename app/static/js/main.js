import apiClient from "./apiClient.js";
import apiEndpoints from "./apiEndpoints.js";

let currentTatvapadaData = [];  // Stores author+sankhye list for selected samputa
let choicesInstances = {};      // Stores Choices.js instances for dropdowns

document.addEventListener("DOMContentLoaded", () => {
    initializeDropdowns();
    setupEventListeners();
    loadSamputaOptions();
});

// --------- Choices Initialization ---------
function initializeDropdowns() {
    initChoices("samputa", "ಸಂಪುಟ ಆಯ್ಕೆಮಾಡಿ");
    initChoices("tatvapadakarara_hesaru", "ತತ್ವಪದಕಾರರ ಹೆಸರು", true);
    initChoices("tatvapada_sankhye", "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
}

function initChoices(id, placeholder, disable = false) {
    const el = document.getElementById(id);
    if (choicesInstances[id]) {
        choicesInstances[id].destroy();
    }

    choicesInstances[id] = new Choices(el, {
        searchEnabled: true,
        itemSelectText: '',
        shouldSort: false,
        placeholderValue: placeholder
    });

    el.disabled = disable;
    el.innerHTML = ''; // Clear native options
}

// --------- Dropdown Events ---------
function setupEventListeners() {
    const samputa = document.getElementById("samputa");
    const author = document.getElementById("tatvapadakarara_hesaru");
    const sankhye = document.getElementById("tatvapada_sankhye");

    samputa.addEventListener("change", () => {
        const selected = samputa.value;
        if (selected) {
            fetchAuthorsAndSankhyas(selected);
        } else {
            resetDropdown("tatvapadakarara_hesaru", "ತತ್ವಪದಕಾರರ ಹೆಸರು", true);
            resetDropdown("tatvapada_sankhye", "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
        }
    });

    author.addEventListener("change", () => {
        const selected = author.value;
        if (selected) {
            populateSankhyesForAuthor(selected);
        } else {
            resetDropdown("tatvapada_sankhye", "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
        }
    });

    sankhye.addEventListener("change", () => {
        const samputa = document.getElementById("samputa").value;
        const authorId = author.value;
        const sankhyeVal = sankhye.value;

        if (samputa && authorId && sankhyeVal) {
            fetchSpecificTatvapada(samputa, authorId, sankhyeVal);
        }
    });
}

// --------- Load Samputa List ---------
function loadSamputaOptions() {
    apiClient.get(apiEndpoints.tatvapada.getSamputas)
        .then(samputas => {
            const options = samputas.map(s => ({ value: s, label: `ಸಂಪುಟ ${s}` }));
            updateChoices("samputa", options);
        })
        .catch(err => console.error("Samputa Load Error:", err));
}

// --------- Fetch Authors and Sankhyas ---------
function fetchAuthorsAndSankhyas(samputa) {
    const endpoint = apiEndpoints.tatvapada.getAuthorSankhyasBySamputa(samputa);

    apiClient.get(endpoint)
        .then(data => {
            currentTatvapadaData = data; // Reset fresh data for current samputa

            const authors = [...new Map(data.map(item => [
                item.tatvapadakarara_id,
                { value: item.tatvapadakarara_id, label: item.tatvapadakarara_hesaru }
            ])).values()];

            resetDropdown("tatvapadakarara_hesaru", "ತತ್ವಪದಕಾರರ ಹೆಸರು", false);
            resetDropdown("tatvapada_sankhye", "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);

            updateChoices("tatvapadakarara_hesaru", authors);
        })
        .catch(err => console.error("Author fetch error:", err));
}

// --------- Populate Sankhyes for Selected Author ---------
function populateSankhyesForAuthor(authorId) {
    const filtered = currentTatvapadaData.filter(
        item => item.tatvapadakarara_id.toString() === authorId
    );

    const sankhyes = filtered.map(item => ({
        value: item.tatvapada_sankhye,
        label: `ತತ್ವಪದ ${item.tatvapada_sankhye}`
    }));

    resetDropdown("tatvapada_sankhye", "ತತ್ವಪದ ಸಂಖ್ಯೆ", false);
    updateChoices("tatvapada_sankhye", sankhyes);
}

// --------- Fetch and Display Specific Tatvapada ---------
function fetchSpecificTatvapada(samputa, authorId, sankhye) {
    const endpoint = apiEndpoints.tatvapada.getSpecificTatvapada(samputa, authorId, sankhye);

    apiClient.get(endpoint)
        .then(renderTatvapada)
        .catch(err => console.error("Tatvapada fetch error:", err));
}

// --------- Choices Utilities ---------
function updateChoices(id, options) {
    const instance = choicesInstances[id];
    instance.clearChoices();
    instance.setChoices(options, 'value', 'label', true);
    instance.enable();
}

function resetDropdown(id, placeholder, disable = false) {
    const el = document.getElementById(id);
    el.innerHTML = ''; // Clear native HTML options
    initChoices(id, placeholder, disable);
}

// --------- Render Tatvapada ---------
function renderTatvapada(data) {
    const display = document.getElementById('poem-display-area');
    const formattedPoem = (data.tatvapada || "")
        .split('\n')
        .map(line => `<p>${line.trim()}</p>`)
        .join("");

    display.innerHTML = `
        <div class="poem-display enhanced">
            <h3 class="poem-title">${data.tatvapada_sheershike}</h3>
            <div class="poem-content">${formattedPoem}</div>
            <div class="poem-author">- ${data.tatvapadakarara_hesaru}</div>
        </div>
    `;

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
