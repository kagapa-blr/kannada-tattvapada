// static/js/login.js

console.log("login.js loaded");

document.addEventListener("DOMContentLoaded", () => {
    const signupForm = document.getElementById("signupForm");
    const loginForm = document.getElementById("loginForm");

    if (signupForm) {
        signupForm.addEventListener("submit", (e) => {
            e.preventDefault();

            const name = document.getElementById("name").value.trim();
            const phone = document.getElementById("phone").value.trim();
            const email = document.getElementById("email").value.trim();

            if (!name || !phone || !email) {
                alert("ದಯವಿಟ್ಟು ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ತುಂಬಿ.");
                return;
            }

            // Optionally: send signup data to server via fetch (TODO: server endpoint)
            console.log("Signed up with:", { name, phone, email });

            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById("signupModal"));
            modal.hide();

            // Show a message
            setTimeout(() => {
                alert("ಸೈನ್ ಅಪ್ ಯಶಸ್ವಿಯಾಗಿ ಆಗಿದೆ. ಈಗ ಲಾಗಿನ್ ಮಾಡಿ.");
            }, 300);
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();

            if (!username || !password) {
                e.preventDefault();
                alert("ಬಳಕೆದಾರಹೆಸರು ಮತ್ತು ಗುಪ್ತಪದ ನೀಡಬೇಕು.");
            }
        });
    }
});
