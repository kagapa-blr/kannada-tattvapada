import apiEndpoints from "./apiEndpoints.js";
import apiClient, { BASE_URL } from "./apiClient.js";
import { showLoader, hideLoader } from "./loader.js";

// Show modal message
function showMessage(message, title = "ದೋಷ", type = "danger") {
    const modal = document.getElementById("messageModal");
    const modalTitle = document.getElementById("messageModalLabel");
    const modalBody = document.getElementById("messageModalBody");
    const modalHeader = document.getElementById("messageModalHeader");

    modalTitle.innerText = title;
    modalBody.innerHTML = message.replace(/\n/g, "<br>");
    modalHeader.className = "modal-header text-white";

    if (type === "danger") modalHeader.classList.add("bg-danger");
    else if (type === "success") modalHeader.classList.add("bg-success");
    else modalHeader.classList.add("bg-primary");

    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");

    // Login
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();
            if (!username || !password) {
                showMessage("ಬಳಕೆದಾರಹೆಸರು ಮತ್ತು ಗುಪ್ತಪದ ಅಗತ್ಯವಿದೆ.", "ಗಮನಿಸಿ");
                return;
            }
            showLoader();
            try {
                const res = await apiClient.post(apiEndpoints.auth.login, { username, password });
                hideLoader();
                // Successful login, redirect directly
                window.location.href = BASE_URL + "/";
            } catch (err) {
                hideLoader();
                // Show user-friendly message
                const msg = err.response?.data?.error || "ಲಾಗಿನ್ ವಿಫಲವಾಗಿದೆ";
                showMessage(msg, "ಲಾಗಿನ್ ವಿಫಲವಾಗಿದೆ", "danger");
            }
        });
    }

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
                showMessage("ದಯವಿಟ್ಟು ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ.", "ಗಮನಿಸಿ");
                return;
            }
            if (!/^\d{10}$/.test(phone)) {
                showMessage("ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ 10 ಅಂಕಿಗಳ ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ.", "ಗಮನಿಸಿ");
                return;
            }

            showLoader();
            try {
                await apiClient.post(apiEndpoints.auth.signup, { name, phone, email, username, password });
                hideLoader();
                bootstrap.Modal.getInstance(document.getElementById("signupModal")).hide();
                showMessage("ಸೈನ್ ಅಪ್ ಯಶಸ್ವಿಯಾಗಿದೆ. ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಮಾಡಿ.", "ಯಶಸ್ಸು", "success");
            } catch (err) {
                hideLoader();
                const msg = err.response?.data?.error || "ಸೈನ್ ಅಪ್ ವಿಫಲವಾಗಿದೆ";
                showMessage(msg, "ಸೈನ್ ಅಪ್ ವಿಫಲವಾಗಿದೆ", "danger");
            }
        });
    }

    // Switch to login from signup modal
    const switchToLoginBtn = document.getElementById("switchToLogin");
    if (switchToLoginBtn) {
        switchToLoginBtn.addEventListener("click", () => {
            bootstrap.Modal.getInstance(document.getElementById("signupModal")).hide();
        });
    }
});
