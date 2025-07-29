//static/js/login.js


import apiEndpoints from "./apiEndpoints.js";
import apiClient, { BASE_URL } from "./apiClient.js";
document.addEventListener("DOMContentLoaded", () => {
    const signupForm = document.getElementById("signupForm");
    const loginForm = document.getElementById("loginForm");

    // Handle Signup
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const name = document.getElementById("name").value.trim();
            const phone = document.getElementById("phone").value.trim();
            const email = document.getElementById("email").value.trim();
            const username = document.getElementById("signup-username").value.trim();
            const password = document.getElementById("signup-password").value.trim();

            if (!name || !phone || !email || !username || !password) {
                alert("ದಯವಿಟ್ಟು ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ತುಂಬಿ.");
                return;
            }

            const payload = { name, phone, email, username, password };

            try {
                const response = await apiClient.post(apiEndpoints.auth.signup, payload, {
                    headers: {
                        "Content-Type": "application/json"
                    }
                });

                // Close the signup modal
                const modalElement = document.getElementById("signupModal");
                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                if (modalInstance) modalInstance.hide();

                setTimeout(() => {
                    alert("ಸೈನ್ ಅಪ್ ಯಶಸ್ವಿಯಾಗಿ ಆಗಿದೆ. ಈಗ ಲಾಗಿನ್ ಮಾಡಿ.");
                    location.reload();
                }, 500);
            } catch (err) {
                console.error("Signup Error:", err);
                alert("ಸೈನ್ ಅಪ್ ವಿಫಲವಾಯಿತು: " + (err.response?.data?.error || err.message));
            }
        });
    }

    // Handle Login
// Handle Login
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();  // ✅ Prevent form from submitting normally

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        if (!username || !password) {
            alert("ಬಳಕೆದಾರಹೆಸರು ಮತ್ತು ಗುಪ್ತಪದ ನೀಡಬೇಕು.");
            return;
        }

        try {
            const response = await apiClient.post(apiEndpoints.auth.login, {
                username,
                password
            }, {
                headers: {
                    "Content-Type": "application/json"
                }
            });

            // On success, redirect
            window.location.href = "/";
        } catch (err) {
            console.error("Login Error:", err);
            alert("ಲಾಗಿನ್ ವಿಫಲವಾಯಿತು: " + (err.response?.data?.error || err.message));
        }
    });
}



});
