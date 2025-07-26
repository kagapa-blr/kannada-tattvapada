import apiClient from "./apiClient.js";

let currentTatvapadaData = [];

document.addEventListener("DOMContentLoaded", () => {
    initializeDropdownHandlers();
    loadSamputas();
});

// ---------- Setup Event Listeners ----------
function initializeDropdownHandlers() {
    const samputaDropdown = document.getElementById("samputa");
    const authorDropdown = document.getElementById("tatvapadakarara_hesaru");
    const sankhyeDropdown = document.getElementById("tatvapada_sankhye");

    // On selecting Samputa
    samputaDropdown.addEventListener("change", () => {
        const samputa = samputaDropdown.value;
        if (samputa) {
            console.log("Selected Samputa:", samputa);
            fetchAuthorsAndSankhyas(samputa);
        } else {
            resetDropdown(authorDropdown, "ತತ್ವಪದಕಾರರ ಹೆಸರು", true);
            resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
        }
    });

    // On selecting Tatvapadakarara
    authorDropdown.addEventListener("change", () => {
        const authorId = authorDropdown.value;
        if (authorId) {
            populateTatvapadaSankhyes(authorId);
            sankhyeDropdown.disabled = false;
        } else {
            resetDropdown(sankhyeDropdown, "ತತ್ವಪದ ಸಂಖ್ಯೆ", true);
        }
    });

    // On selecting Tatvapada Sankhye
    sankhyeDropdown.addEventListener("change", () => {
        const sankhye = sankhyeDropdown.value;
        const samputa = samputaDropdown.value;
        const authorId = authorDropdown.value;

        if (sankhye && samputa && authorId) {
            console.log("Final Selection:");
            console.log("Samputa:", samputa);
            console.log("Tatvapadakarara ID:", authorId);
            console.log("Tatvapada Sankhye:", sankhye);

            fetchSpecificTatvapada(samputa, authorId, sankhye);
        }
    });
}

// ---------- Load Samputas from API ----------
function loadSamputas() {
    apiClient.get("/tatvapada/samputas")
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

// ---------- Fetch Authors + Sankhyes by Selected Samputa ----------
function fetchAuthorsAndSankhyas(samputaSankhye) {
    const endpoint = `/tatvapada/author-sankhyes-by-samputa?samputa_sankhye=${samputaSankhye}`;

    apiClient.get(endpoint)
        .then(data => {
            currentTatvapadaData = data;

            const authorDropdown = document.getElementById("tatvapadakarara_hesaru");
            const sankhyeDropdown = document.getElementById("tatvapada_sankhye");

            // Reset and enable author dropdown; disable sankhye for now
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

// ---------- Populate Tatvapada Sankhyes for Given Author ----------
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
    const endpoint = `/tatvapada/${samputa}/${authorId}/${sankhye}`;

    apiClient.get(endpoint)
        .then(data => {
            console.log("Tatvapada Details:", data);
            // Optionally display this in the page
             renderTatvapada(data);
        })
        .catch(error => {
            console.error("Error fetching specific Tatvapada:", error);
        });
}





// ---------- Utility: Reset Any Dropdown ----------
function resetDropdown(dropdown, placeholderText, disable = false) {
    dropdown.innerHTML = `<option value="">${placeholderText}</option>`;
    dropdown.disabled = disable;
}



function renderTatvapada(data) {
    displayPoem({
        text: data.tatvapada_hesaru,
        poem: data.tatvapada,
        author: data.tatvapadakarara_hesaru
    });
}

function displayPoem(poemData) {
    const poemDisplayArea = document.getElementById('poem-display-area');
    poemDisplayArea.innerHTML = `
        <div class="poem-display">
            <div class="poem-title">${poemData.text}</div>
            <div class="poem-content">${poemData.poem}</div>
            <div class="poem-author">- ${poemData.author}</div>
        </div>
    `;
}
