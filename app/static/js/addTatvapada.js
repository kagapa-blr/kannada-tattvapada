import apiClient from "./apiClient.js";
import apiEndpoints from "./apiEndpoints.js";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("tatvapada-add-form");
  const modeNew = document.getElementById("modeNew");
  const modeExisting = document.getElementById("modeExisting");
  const cascadingSection = document.getElementById("cascading-section");

  // Toggle visibility of cascading section
  function toggleCascadingVisibility() {
    if (modeExisting.checked) {
      cascadingSection.style.display = "block";
    } else {
      cascadingSection.style.display = "none";
    }
  }

  modeNew.addEventListener("change", toggleCascadingVisibility);
  modeExisting.addEventListener("change", toggleCascadingVisibility);
  toggleCascadingVisibility();

  // Form Submission
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const jsonData = Object.fromEntries(formData.entries());

    // Validate required fields
    if (!jsonData.samputa_sankhye || !jsonData.tatvapada_sankhye || !jsonData.tatvapadakarara_hesaru) {
      alert("ಸಂಪುಟ, ತತ್ತ್ವಪದ ಸಂಖ್ಯೆ ಮತ್ತು ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು ಅಗತ್ಯವಿದೆ.");
      return;
    }

    apiClient
      .post(apiEndpoints.tatvapada.addTatvapada, jsonData)
      .then((response) => {
        showSuccessModal(null, response?.message || "ತತ್ತ್ವಪದ ಯಶಸ್ವಿಯಾಗಿ ಸೇರಿಸಲಾಗಿದೆ.");
        form.reset();
      })
      .catch((error) => {
        handleErrorModal(error);
      });
  });
});

function showSuccessModal(callback, message) {
  const modalEl = document.getElementById("successModal");
  const msg = modalEl.querySelector("#successMessage");
  if (msg) msg.textContent = message;
  const modal = new bootstrap.Modal(modalEl);
  modal.show();

  modalEl.addEventListener("hidden.bs.modal", () => {
    callback?.();
  }, { once: true });
}

function handleErrorModal(error) {
  const msg = document.getElementById("errorMessage");
  msg.textContent = error?.message || "ತತ್ತ್ವಪದವನ್ನು ಸೇರಿಸಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ.";
  const modal = new bootstrap.Modal(document.getElementById("errorModal"));
  modal.show();
}
