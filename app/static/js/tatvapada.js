document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("tatvapadaForm");
    const statusBox = document.getElementById("statusBox");

    if (!form) return;

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            data[key] = value.trim();
        });

        if (!data.tatvapadakosha || !data.tatvapada_hesaru || !data.tatvapada) {
            showStatus("ತತ್ತ್ವಪದಕೋಶ, ಹೆಸರು ಮತ್ತು ತತ್ತ್ವಪದ ಅಗತ್ಯವಿದೆ.", "error");
            return;
        }

        fetch("/tatvapada/add", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(response => {
            if (response.message) {
                showStatus("ತತ್ತ್ವಪದ ಯಶಸ್ವಿಯಾಗಿ ಸೇರಿಸಲಾಗಿದೆ.", "success");
                form.reset();
            } else {
                showStatus(response.error || "ಸೇರಿಸಲು ವಿಫಲವಾಗಿದೆ.", "error");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            showStatus("ಸಿಬ್ಬಂದಿಗೆ ಸಂಪರ್ಕ ವಿಫಲವಾಗಿದೆ.", "error");
        });
    });

    function showStatus(message, type) {
        if (!statusBox) return;
        statusBox.textContent = message;
        statusBox.className = "status " + type;
    }
});
