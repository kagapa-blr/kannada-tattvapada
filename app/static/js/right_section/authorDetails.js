import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

const authorSelect = document.getElementById("authorSelect");
const viewBtn = document.getElementById("viewAuthorBtn");
const authorCard = document.getElementById("authorCard");
const authorContent = document.getElementById("authorContent");

// --- UI Animation Helpers ---
function fadeInCard() {
    authorCard.style.display = "block";
    setTimeout(() => {
        authorCard.style.opacity = "1";
        authorCard.style.transform = "translateY(0)";
    }, 50);
}

function resetCardAnimation() {
    authorCard.style.opacity = "0";
    authorCard.style.transform = "translateY(20px)";
}

function resetContentAnimation() {
    authorContent.style.opacity = "0";
}

function fadeInContent() {
    setTimeout(() => {
        authorContent.style.opacity = "1";
    }, 200);
}

// --- Utility: Normalize API responses ---
function unwrapResponse(response) {
    if (!response) return null;
    if (response.data !== undefined) return response.data; // handle { data: ... }
    return response; // handle plain object or array
}

// --- Fetch all authors and populate dropdown ---
async function loadAuthors() {
    showLoader();
    try {
        const response = await apiClient.get(apiEndpoints.authors.list);
        console.log("Full response:", response);

        const authors = unwrapResponse(response);

        if (!Array.isArray(authors)) {
            throw new Error("Invalid authors response");
        }

        // Reset dropdown
        authorSelect.innerHTML = `<option value="">-- ತತ್ವಪದಕಾರರನ್ನು ಆಯ್ಕೆಮಾಡಿ --</option>`;

        authors.forEach(a => {
            const option = document.createElement("option");
            option.value = a.id;
            option.textContent = a.author_name;
            authorSelect.appendChild(option);
        });

        if (authors.length > 0) {
            authorSelect.value = authors[0].id;
            await viewAuthor(); // auto-load first author
        } else {
            authorContent.innerHTML = "<em>ಯಾವುದೇ ತತ್ವಪದಕಾರರಿಲ್ಲ.</em>";
        }
    } catch (err) {
        console.error("Failed to load authors:", err);
        alert("ತತ್ವಪದಕಾರರನ್ನು ಲೋಡ್ ಮಾಡಲು ವಿಫಲವಾಗಿದೆ.");
    } finally {
        hideLoader();
    }
}

// --- Fetch single author by ID ---
async function viewAuthor() {
    const authorId = authorSelect.value;
    if (!authorId) return;

    showLoader();
    try {
        const response = await apiClient.get(apiEndpoints.authors.getById(authorId));
        console.log("Author detail response raw:", response);

        const author = unwrapResponse(response);

        if (!author || !author.id || !author.author_name) {
            throw new Error("Invalid author detail response");
        }

        // Render content
        resetContentAnimation();
        authorContent.innerHTML = `
            <h3>${author.author_name}</h3>
            <p class="text-sm text-gray-500">
                📅 ರಚನೆ: ${author.created_at} | 📝 ನವೀಕರಣ: ${author.updated_at}
            </p><br>
            <div>${author.content || "<em>ಯಾವುದೇ ವಿವರಗಳಿಲ್ಲ</em>"}</div>

        `;
        fadeInContent();
        fadeInCard();
    } catch (err) {
        console.error("Failed to load author details:", err);
        alert("ತತ್ವಪದಕಾರರ ವಿವರಗಳನ್ನು ಲೋಡ್ ಮಾಡಲು ವಿಫಲವಾಗಿದೆ.");
    } finally {
        hideLoader();
    }
}

// --- Event Listeners ---
viewBtn.addEventListener("click", viewAuthor);

// --- Init ---
loadAuthors();
