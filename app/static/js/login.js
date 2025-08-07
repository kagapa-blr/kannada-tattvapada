// static/js/login.js

import apiEndpoints from "./apiEndpoints.js";
import apiClient, { BASE_URL } from "./apiClient.js";
import { showLoader, hideLoader } from "./loader.js";

// Helper function to show modal with message
function showMessage(message, title = "ದೋಷ", type = "danger", callback = null) {
    const modalElement = document.getElementById("messageModal");
    const modalTitle = document.getElementById("messageModalLabel");
    const modalBody = document.getElementById("messageModalBody");
    const modalHeader = document.getElementById("messageModalHeader");

    // Set modal title and body
    modalTitle.innerText = title;
    modalBody.innerHTML = message.replace(/\n/g, "<br>");

    // Set appropriate background color based on message type
    modalHeader.className = "modal-header text-white";
    if (type === "danger") modalHeader.classList.add("bg-danger");
    else if (type === "success") modalHeader.classList.add("bg-success");
    else if (type === "info") modalHeader.classList.add("bg-primary");
    else modalHeader.classList.add("bg-secondary");

    const bsModal = new bootstrap.Modal(modalElement);

    // Attach callback after modal is hidden (if provided)
    if (callback) {
        modalElement.addEventListener("hidden.bs.modal", function onClose() {
            callback();
            modalElement.removeEventListener("hidden.bs.modal", onClose);
        });
    }

    bsModal.show();
}

// Run this when DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const signupForm = document.getElementById("signupForm");
    const loginForm = document.getElementById("loginForm");

    // Handle Signup Form Submission
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault(); // Prevent default form submission

            // Read form values
            const name = document.getElementById("name").value.trim();
            const phone = document.getElementById("phone").value.trim();
            const email = document.getElementById("email").value.trim();
            const username = document.getElementById("signup-username").value.trim();
            const password = document.getElementById("signup-password").value.trim();

            // Validate required fields
            if (!name || !phone || !email || !username || !password) {
                showMessage("ದಯವಿಟ್ಟು ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ.", "ಗಮನಿಸಿ", "danger");
                return;
            }

            // Validate phone number format
            if (!/^\d{10}$/.test(phone)) {
                showMessage("ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ೧೦ ಅಂಕಿಗಳ ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ.", "ಗಮನಿಸಿ", "danger");
                return;
            }

            const payload = { name, phone, email, username, password };

            showLoader(); // Show loading indicator
            try {
                // Send signup request
                await apiClient.post(apiEndpoints.auth.signup, payload, {
                    headers: { "Content-Type": "application/json" }
                });

                // Close signup modal on success
                bootstrap.Modal.getInstance(document.getElementById("signupModal")).hide();

                // Show success message and reload page
                showMessage("ಸೈನ್‌ಅಪ್ ಯಶಸ್ವಿಯಾಗಿದೆ. ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಮಾಡಿ.", "ಯಶಸ್ಸು", "success", () => location.reload());
            } catch (err) {
                // Extract and show error message
                let errorMsg = err.response?.data?.error || err.message || "ಅಪರಿಚಿತ ದೋಷ";
                const cleanedMsg = getCleanErrorMessage(errorMsg);
                showMessage("ಸೈನ್‌ಅಪ್ ವಿಫಲವಾಗಿದೆ:\n" + cleanedMsg, "ದೋಷ", "danger");
            } finally {
                hideLoader(); // Hide loading indicator
            }
        });
    }

    // Clean and simplify backend error message
    function getCleanErrorMessage(errorMsg) {
        return errorMsg.split(':').pop().replace(/[^a-zA-Z0-9\s]/g, '').trim();
    }

    // Handle Login Form Submission
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault(); // Prevent default form submission

            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();

            // Validate login fields
            if (!username || !password) {
                showMessage("ಬಳಕೆದಾರಹೆಸರು ಮತ್ತು ಗುಪ್ತಪದ ಅಗತ್ಯವಿದೆ.", "ಗಮನಿಸಿ", "danger");
                return;
            }

            showLoader(); // Show loading indicator
            try {
                // Send login request
                await apiClient.post(apiEndpoints.auth.login, { username, password }, {
                    headers: { "Content-Type": "application/json" }
                });

                // Redirect to home on success
                window.location.href = BASE_URL + "/";
            } catch (err) {
                // Show error message
                let errorMsg = err.response?.data?.error || err.message || "ಲಾಗಿನ್ ವಿಫಲವಾಗಿದೆ";
                const cleanedMsg = getCleanErrorMessage(errorMsg);
                showMessage("ಲಾಗಿನ್ ವಿಫಲವಾಯಿತು:\n" + cleanedMsg, "ದೋಷ", "danger");
            } finally {
                hideLoader(); // Hide loading indicator
            }
        });
    }
});
