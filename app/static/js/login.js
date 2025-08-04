// static/js/login.js

import apiEndpoints from "./apiEndpoints.js";
import apiClient, { BASE_URL } from "./apiClient.js";

// Helper to Show Bootstrap Modal as Message
function showMessage(message, title = "ದೋಷ", type = "danger", callback = null) {
    const modalElement = document.getElementById("messageModal");
    const modalTitle = document.getElementById("messageModalLabel");
    const modalBody = document.getElementById("messageModalBody");
    const modalHeader = document.getElementById("messageModalHeader");

    modalTitle.innerText = title;

    // Replace newlines with <br> for line breaks in HTML
    modalBody.innerHTML = message.replace(/\n/g, "<br>");

    modalHeader.className = "modal-header text-white";
    if (type === "danger") modalHeader.classList.add("bg-danger");
    else if (type === "success") modalHeader.classList.add("bg-success");
    else if (type === "info") modalHeader.classList.add("bg-primary");
    else modalHeader.classList.add("bg-secondary");

    const bsModal = new bootstrap.Modal(modalElement);

    if (callback) {
        modalElement.addEventListener("hidden.bs.modal", function onClose() {
            callback();
            modalElement.removeEventListener("hidden.bs.modal", onClose);
        });
    }
    bsModal.show();
}

document.addEventListener("DOMContentLoaded", () => {
    const signupForm = document.getElementById("signupForm");
    const loginForm = document.getElementById("loginForm");

    // Signup
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const name = document.getElementById("name").value.trim();
            const phone = document.getElementById("phone").value.trim();
            const email = document.getElementById("email").value.trim();
            const username = document.getElementById("signup-username").value.trim();
            const password = document.getElementById("signup-password").value.trim();

            if (!name || !phone || !email || !username || !password) {
                showMessage("ದಯವಿಟ್ಟು ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ತುಂಬಿ.", "ಗಮನಿಸಿ", "danger");
                return;
            }
            if (!/^\d{10}$/.test(phone)) {
                showMessage("ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ 10 ಅಂಕಿಗಳ ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ.", "ಗಮನಿಸಿ", "danger");
                return;
            }

            const payload = { name, phone, email, username, password };

            try {
                await apiClient.post(apiEndpoints.auth.signup, payload, {
                    headers: { "Content-Type": "application/json" }
                });

                // Close the signup modal
                bootstrap.Modal.getInstance(document.getElementById("signupModal")).hide();

                // Show message → reload when closed
                showMessage("ಸೈನ್ ಅಪ್ ಯಶಸ್ವಿಯಾಗಿ ಪೂರೈಸಲಾಗಿದೆ. ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಮಾಡಿ.", "ಯಶಸ್ಸು", "success", () => location.reload());
            } catch (err) {
                let errorMsg = err.response?.data?.error || err.message || "ಅಪರಿಚಿತ ದೋಷ";
                const cleanedMsg = getCleanErrorMessage(errorMsg)
                showMessage("ಸೈನ್ ಅಪ್ ವಿಫಲವಾಗಿದೆ: \n" + cleanedMsg, "ದೋಷ", "danger");
            }
        });
    }
    function getCleanErrorMessage(errorMsg) {
        return errorMsg.split(':').pop().replace(/[^a-zA-Z0-9\s]/g, '').trim();
    }

    // Login
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();

            if (!username || !password) {
                showMessage("ಬಳಕೆದಾರಹೆಸರು ಮತ್ತು ಗುಪ್ತಪದ ನೀಡಬೇಕು.", "ಗಮನಿಸಿ", "danger");
                return;
            }

            try {
                await apiClient.post(apiEndpoints.auth.login, { username, password }, {
                    headers: { "Content-Type": "application/json" }
                });

                // Redirect on success
                window.location.href = BASE_URL + "/";
            } catch (err) {

                let errorMsg = err.response?.data?.error || err.message || "ಲಾಗಿನ್ ಅಪರಿಚಿತ ದೋಷ";
                const cleanedMsg = getCleanErrorMessage(errorMsg);

                showMessage("ಲಾಗಿನ್ ವಿಫಲವಾಯಿತು: \n" + cleanedMsg, "ದೋಷ", "danger");

                console.log("Cleaned message:", cleanedMsg);


            }
        });
    }
});
