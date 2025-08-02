import apiClient from "./apiClient.js";
import apiEndpoints from "./apiEndpoints.js";

let currentTatvapadaData = [];
let tatvapadakarara_hesaru_id = new Set()
// --------------------- DOM Ready --------------------- //
document.addEventListener("DOMContentLoaded", () => {
  initializeModeSwitching();
  initializeDropdownHandlers();
  loadSamputas();
  initializeFormSubmitHandler();
  setupNavigation();

  document.addEventListener("hide.bs.modal", function () {
    if (document.activeElement) {
      document.activeElement.blur();
    }
  });
});

// --------------------- UI Navigation --------------------- //
function setupNavigation() {
  document.querySelectorAll(".top-navabar-bar .nav-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document
        .querySelectorAll(".top-navabar-bar .nav-btn")
        .forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });
}

// --------------------- Mode Switching --------------------- //
function initializeModeSwitching() {
  const modeNew = document.getElementById("modeNew");
  const modeExisting = document.getElementById("modeExisting");
  const inputsContainer = document.getElementById("inputs-container");
  const cascadingSection = document.getElementById("cascading-section");

  function updateModeUI() {
    if (modeNew.checked) {
      inputsContainer.style.display = "";
      cascadingSection.style.display = "none";
      resetDropdown(document.getElementById("samputa"), "ತತ್ವಪದಕೋಶ ಸಂಪುಟ ಆಯ್ಕೆಮಾಡಿ", true);
      resetDropdown(document.getElementById("tatvapadakarara_hesaru"), "ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು", true);
      resetDropdown(document.getElementById("tatvapada_sankhye"), "ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ", true);
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
  const samputaDropdown = document.getElementById("samputa");
  const authorDropdown = document.getElementById("tatvapadakarara_hesaru");
  const sankhyeDropdown = document.getElementById("tatvapada_sankhye");

  samputaDropdown.addEventListener("change", () => {
    const samputa = samputaDropdown.value;
    if (samputa) {
      fetchAuthorsAndSankhyas(samputa);
    } else {
      resetDropdown(authorDropdown, "ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು", true);
      resetDropdown(sankhyeDropdown, "ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ", true);
      removeInlineNewAuthorInput();
      removeInlineNewSankhyeInput();
    }
  });

  authorDropdown.addEventListener("change", () => {
    const authorId = authorDropdown.value;
    const sankhyeDropdown = document.getElementById("tatvapada_sankhye");

    if (authorId === "__add_new__") {
      showInlineNewAuthorInput();
      // allow choosing or adding sankhye even if none selected
      sankhyeDropdown.disabled = false;
      resetDropdown(sankhyeDropdown, "ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ", false);
      appendAddNewSankhyeOption();
    } else {
      removeInlineNewAuthorInput();
      if (authorId) {
        populateTatvapadaSankhyes(authorId);
        sankhyeDropdown.disabled = false;
      } else {
        resetDropdown(sankhyeDropdown, "ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ", true);
        removeInlineNewSankhyeInput();
      }
    }
  });

  sankhyeDropdown.addEventListener("change", () => {
    const sankhye = sankhyeDropdown.value;
    const samputa = document.getElementById("samputa").value;
    const authorId = document.getElementById("tatvapadakarara_hesaru").value;

    if (sankhye === "__add_new_sankhye__") {
      showInlineNewSankhyeInput();
      return;
    } else {
      removeInlineNewSankhyeInput();
    }

    if (sankhye && samputa && authorId && authorId !== "__add_new__") {
      fetchSpecificTatvapada(samputa, authorId, sankhye).then((data) => {
        if (data) {
          populateTatvapadaForm(data);
        }
      });
    }
  });
}

// --------------------- Load Samputas --------------------- //
function loadSamputas() {
  apiClient
    .get(apiEndpoints.tatvapada.getSamputas)
    .then((samputas) => {
      const list = Array.isArray(samputas)
        ? samputas
        : samputas && typeof samputas === "object"
          ? Object.keys(samputas)
          : [];
      document.getElementById("samputa_suggestion_value").textContent = `[${list.join(", ")}]`;

      const dropdown = document.getElementById("samputa");
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
      console.error("Error loading Samputas:", error);
    });
}

// --------------------- Fetch Authors & Sankhyas --------------------- //
function fetchAuthorsAndSankhyas(samputaSankhye) {
  const endpoint = apiEndpoints.tatvapada.getAuthorSankhyasBySamputa(samputaSankhye);

  apiClient.get(endpoint).then((data) => {
    currentTatvapadaData = data || [];

    const authorDropdown = document.getElementById("tatvapadakarara_hesaru");
    const sankhyeDropdown = document.getElementById("tatvapada_sankhye");

    resetDropdown(authorDropdown, "ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು", false);
    resetDropdown(sankhyeDropdown, "ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ", true);
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

    // append "add new" sentinel for author
    const addNew = document.createElement("option");
    addNew.value = "__add_new__";
    addNew.textContent = "Add new ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು";
    authorDropdown.appendChild(addNew);
  })
    .catch((error) => {
      console.error("Error fetching authors for samputa:", error);
    });
}

// --------------------- Populate Sankhyes --------------------- //
function populateTatvapadaSankhyes(authorId) {
  const sankhyeDropdown = document.getElementById("tatvapada_sankhye");
  resetDropdown(sankhyeDropdown, "ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ", false);
  removeInlineNewSankhyeInput();

  const filtered = currentTatvapadaData.filter(
    (item) => item.tatvapadakarara_id.toString() === authorId.toString()
  );

  filtered.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.tatvapada_sankhye;
    option.textContent = `ತತ್ತ್ವಪದ ${item.tatvapada_sankhye}`;
    sankhyeDropdown.appendChild(option);
  });

  appendAddNewSankhyeOption();
}

// --------------------- Fetch & Populate Form --------------------- //
function fetchSpecificTatvapada(samputa, authorId, sankhye) {
  const endpoint = apiEndpoints.tatvapada.getSpecificTatvapada(
    samputa,
    authorId,
    sankhye
  );

  return apiClient
    .get(endpoint)
    .then((data) => data)
    .catch((error) => {
      console.error("Error fetching specific Tatvapada:", error);
    });
}

function populateTatvapadaForm(data) {
  if (!data) return;

  document.getElementById("tatvapadakosha_sheershike").value = data.tatvapadakosha_sheershike || "";
  document.getElementById("tatvapada_sheershike").value = data.tatvapada_sheershike || "";
  document.getElementById("tatvapada_first_line").value = data.tatvapada_first_line || "";
  document.getElementById("tatvapada").value = data.tatvapada || "";
  document.getElementById("klishta_padagalu_artha").value = data.klishta_padagalu_artha || "";
  document.getElementById("tippani").value = data.tippani || "";
  document.getElementById("samputa_input").value = data.samputa_sankhye || "";
  document.getElementById("bhavanuvada").value = data.bhavanuvada || "";
  document.getElementById("vibhag").value = data.vibhag || "";
}

// --------------------- Inline Add-New Helpers --------------------- //
function showInlineNewAuthorInput() {
  const container = document.getElementById("inline-author-container");
  if (document.getElementById("inline_new_author")) return;

  container.innerHTML = "";
  const input = document.createElement("input");
  input.type = "text";
  input.id = "inline_new_author";
  input.placeholder = "ಹೊಸ ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು";
  input.className = "form-control";
  input.setAttribute("aria-label", "ಹೊಸ ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು");

  const hint = document.createElement("div");
  hint.className = "form-text small text-muted";
  hint.textContent = "ನೀವು ಹೊಸ ತತ್ತ್ವಪದಕಾರರ ಹೆಸರನ್ನು ಇಲ್ಲಿ ಹಾಕಿ.";

  container.appendChild(input);
  container.appendChild(hint);
}

function removeInlineNewAuthorInput() {
  const container = document.getElementById("inline-author-container");
  container.innerHTML = "";
}

function appendAddNewSankhyeOption() {
  const sankhyeDropdown = document.getElementById("tatvapada_sankhye");
  // avoid duplicate sentinel
  if ([...sankhyeDropdown.options].some(o => o.value === "__add_new_sankhye__")) return;
  const addNew = document.createElement("option");
  addNew.value = "__add_new_sankhye__";
  addNew.textContent = "Add new ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ";
  sankhyeDropdown.appendChild(addNew);
}

function showInlineNewSankhyeInput() {
  const container = document.getElementById("inline-sankhye-container");
  if (document.getElementById("inline_new_sankhye")) return;

  container.innerHTML = "";
  const input = document.createElement("input");
  input.type = "number";
  input.id = "inline_new_sankhye";
  input.placeholder = "ಹೊಸ ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ";
  input.className = "form-control";
  input.setAttribute("aria-label", "ಹೊಸ ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ");

  const hint = document.createElement("div");
  hint.className = "form-text small text-muted";
  hint.textContent = "ನೀವು ಹೊಸ ತತ್ತ್ವಪದ ಸಂಖ್ಯೆಯನ್ನು ಇಲ್ಲಿ ಹಾಕಿ.";

  container.appendChild(input);
  container.appendChild(hint);
}

function removeInlineNewSankhyeInput() {
  const container = document.getElementById("inline-sankhye-container");
  container.innerHTML = "";
}

// --------------------- Submit Handler --------------------- //
function initializeFormSubmitHandler() {
  const form = document.getElementById("tatvapada-add-form");

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const isNewMode = document.getElementById("modeNew").checked;
    const formData = new FormData(form);
    const jsonData = Object.fromEntries(formData.entries());

    if (isNewMode) {
      const samputa = document.getElementById("samputa_input").value.trim();
      const authorName = document.getElementById("tatvapadakarara_hesaru_input_modeNew").value.trim();
      const sankhye = document.getElementById("tatvapada_sankhye_input")?.value.trim();

      if (!authorName) {
        alert("ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು ಅಗತ್ಯವಿದೆ");
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
          handleErrorModal(error);
        });
    }

    else {
      const samputa = document.getElementById("samputa").value;
      const sankhyeSelect = document.getElementById("tatvapada_sankhye");
      const authorDropdown = document.getElementById("tatvapadakarara_hesaru");
      const authorId = authorDropdown.value;
      const sankhyeValue = sankhyeSelect.value;

      if (!samputa) {
        alert("ಸಂಪುಟ ಆಯ್ಕೆ ಮಾಡಬೇಕು");
        return;
      }

      jsonData.samputa_sankhye = samputa;

      // author logic
      if (authorId === "__add_new__") {
        const inlineAuthorInput = document.getElementById("inline_new_author");
        if (!inlineAuthorInput || !inlineAuthorInput.value.trim()) {
          alert("ಹೊಸ ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು ನೀಡಿರಿ");
          return;
        }
        jsonData.tatvapadakarara_hesaru = inlineAuthorInput.value.trim();
      } else if (authorId) {
        jsonData.tatvapada_author_id = authorId;
      } else {
        alert("ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು ಆಯ್ಕೆ ಅಗತ್ಯವಿದೆ");
        return;
      }

      // sankhye logic
      if (sankhyeValue === "__add_new_sankhye__") {
        const inlineSankhyeInput = document.getElementById("inline_new_sankhye");
        if (!inlineSankhyeInput || !inlineSankhyeInput.value.trim()) {
          alert("ಹೊಸ ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ ನೀಡಿ");
          return;
        }
        jsonData.tatvapada_sankhye = inlineSankhyeInput.value.trim();
      } else if (sankhyeValue) {
        jsonData.tatvapada_sankhye = sankhyeValue;
      } else {
        alert("ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ ಆಯ್ಕೆ ಮಾಡಬೇಕು");
        return;
      }

      //console.log("json payload : ", jsonData)
      apiClient.post(apiEndpoints.tatvapada.addTatvapada, jsonData).then((response) => {
        showSuccessModal(null, response?.message || "ಅಪ್ಡೇಟ್ ಯಶಸ್ವಿಯಾಗಿದೆ.");
        if (response?.created_entry) {
          populateTatvapadaForm(response.created_entry);
        }
      })
        .catch((error) => {
          handleErrorModal(error);
        });
    }





  });
}

// --------------------- Modal Helpers --------------------- //
function showSuccessModal(callback, message = "ಯಶಸ್ವಿಯಾಗಿದೆ.") {
  const modalElement = document.getElementById("successModal");
  if (!modalElement) return;

  const serverMessageElement = modalElement.querySelector("#successMessage");
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
  const messageEl = document.getElementById("errorMessage");
  const defaultText = "ತತ್ತ್ವಪದವನ್ನು ಸೇರಿಸಲು ಸಾಧ್ಯವಾದಿಲ್ಲ.";
  if (messageEl) {
    messageEl.textContent = error?.message || defaultText;
  }
  const modal = new bootstrap.Modal(
    document.getElementById("errorModal")
  );
  modal.show();
}

// --------------------- Utility --------------------- //
function resetDropdown(dropdown, placeholder, disable = false) {
  dropdown.innerHTML = `<option value="">${placeholder}</option>`;
  dropdown.disabled = disable;
}
