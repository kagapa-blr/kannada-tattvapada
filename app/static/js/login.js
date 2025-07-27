document.addEventListener("DOMContentLoaded", () => {
    const signupForm = document.getElementById("signupForm");
    const loginForm = document.getElementById("loginForm");

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

            try {
                const response = await fetch("/signup", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    body: new URLSearchParams({
                        name,
                        phone,
                        email,
                        username,
                        password,
                    }),
                });

                if (response.ok) {
                    bootstrap.Modal.getInstance(document.getElementById("signupModal")).hide();
                    setTimeout(() => {
                        alert("ಸೈನ್ ಅಪ್ ಯಶಸ್ವಿಯಾಗಿ ಆಗಿದೆ. ಈಗ ಲಾಗಿನ್ ಮಾಡಿ.");
                        location.reload();
                    }, 500);
                } else {
                    const errorText = await response.text();
                    alert("ದೋಷ: " + errorText);
                }
            } catch (err) {
                console.error("Signup Error:", err);
                alert("ಸೈನ್ ಅಪ್ ವಿಫಲವಾಗಿದೆ.");
            }
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
