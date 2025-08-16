import apiEndpoints from "../apiEndpoints.js";
import apiClient from "../apiClient.js";
import { showLoader, hideLoader } from "../loader.js";

let pendingDeleteAction = null;

export async function initDeleteTab() {
    await loadDeleteKeys();
}

async function loadDeleteKeys() {
    try {
        showLoader();
        const data = await apiClient.get(apiEndpoints.tatvapada.deleteKeys);

        const tbody = document.querySelector("#deleteTatvapadaTable tbody");
        if (!tbody) return;

        tbody.innerHTML = "";
        const deleteKeys = Array.isArray(data.delete_keys) ? data.delete_keys : (data.delete_keys?.delete_keys || []);

        deleteKeys.forEach(entry => {
            const row = document.createElement("tr");

            const sankhyaCheckboxes = entry.tatvapada_sankhyes.map(s => `
                <div class="form-check form-check-inline">
                  <input class="form-check-input row-select" type="checkbox"
                    data-samputa="${entry.samputa_sankhye}"
                    data-author="${entry.tatvapada_author_id}"
                    data-author-name="${entry.tatvapadakarara_hesaru}"
                    data-sankhya="${s}">
                  <label class="form-check-label">${s}</label>
                </div>
            `).join(" ");

            row.innerHTML = `
                <td>
                  <input type="checkbox" class="row-author-select"
                    data-samputa="${entry.samputa_sankhye}"
                    data-author="${entry.tatvapada_author_id}">
                </td>
                <td>${entry.samputa_sankhye}</td>
                <td>${entry.tatvapada_author_id}</td>
                <td>${entry.tatvapadakarara_hesaru}</td>
                <td>${sankhyaCheckboxes}</td>
                <td>
                  <button class="btn btn-danger btn-sm delete-btn"
                    data-samputa="${entry.samputa_sankhye}"
                    data-author="${entry.tatvapada_author_id}"
                    data-author-name="${entry.tatvapadakarara_hesaru}">
                    Delete All
                  </button>
                </td>
            `;

            tbody.appendChild(row);
        });

        attachEventHandlers();
    } catch (err) {
        showFailure("Failed to load Tatvapadas");
        console.error(err);
    } finally {
        hideLoader();
    }
}

function attachEventHandlers() {
    const modal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"));
    const confirmBtn = document.getElementById("confirmDeleteBtn");
    const confirmMessage = document.getElementById("deleteConfirmMessage");
    const bulkDeleteBtn = document.getElementById("bulkDeleteBtn");
    const selectAll = document.getElementById("selectAll");

    // Confirm delete
    confirmBtn.onclick = async () => {
        if (pendingDeleteAction) {
            await pendingDeleteAction();
            pendingDeleteAction = null;
        }
        modal.hide();
    };

    // Single Delete All
    document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const samputa = btn.dataset.samputa;
            const authorId = btn.dataset.author;
            const authorName = btn.dataset.authorName;

            confirmMessage.innerHTML = `
                <strong>Samputa:</strong> ${samputa} <br>
                <strong>Author ID:</strong> ${authorId} <br>
                <strong>Author Name:</strong> ${authorName} <br>
                <span class="text-danger">This will delete <strong>ALL</strong> Tatvapada(s) for this author.</span>
            `;

            pendingDeleteAction = async () => {
                try {
                    showLoader();
                    const result = await apiClient.delete(apiEndpoints.tatvapada.deleteBySamputaAuthor(samputa, authorName));
                    showSuccess(result.message || "Deleted successfully");
                    await loadDeleteKeys();
                } catch (err) {
                    showFailure(err.message || "Delete failed");
                } finally {
                    hideLoader();
                }
            };

            modal.show();
        });
    });

    // Select All checkbox
    if (selectAll) {
        selectAll.addEventListener("change", () => {
            const checkboxes = document.querySelectorAll(".row-select");
            checkboxes.forEach(cb => (cb.checked = selectAll.checked));
            bulkDeleteBtn.disabled = !selectAll.checked;
        });
    }

    // Enable/disable bulk delete
    document.querySelectorAll(".row-select").forEach(cb => {
        cb.addEventListener("change", () => {
            bulkDeleteBtn.disabled = document.querySelectorAll(".row-select:checked").length === 0;
        });
    });

    // Bulk delete selected
    if (bulkDeleteBtn) {
        bulkDeleteBtn.addEventListener("click", () => {
            const selected = Array.from(document.querySelectorAll(".row-select:checked")).map(cb => ({
                samputa: cb.dataset.samputa,
                authorId: cb.dataset.author,
                authorName: cb.dataset.authorName,
                sankhya: cb.dataset.sankhya
            }));

            if (selected.length === 0) return;

            const { samputa, authorId, authorName } = selected[0];
            const tatvapadaNumbers = selected.map(s => s.sankhya).join(", ");

            confirmMessage.innerHTML = `
                <strong>Samputa:</strong> ${samputa} <br>
                <strong>Author ID:</strong> ${authorId} <br>
                <strong>Author Name:</strong> ${authorName} <br>
                <strong>Selected Tatvapada(s):</strong> ${tatvapadaNumbers}
            `;

            pendingDeleteAction = async () => {
                try {
                    showLoader();
                    const result = await apiClient.delete(apiEndpoints.tatvapada.bulkDelete, { items: selected });
                    showSuccess(result.message || "Selected Tatvapada(s) deleted");
                    await loadDeleteKeys();
                } catch (err) {
                    showFailure(err.message || "Delete failed");
                } finally {
                    hideLoader();
                }
            };

            modal.show();
        });
    }
}

// Utility: show success/failure modals
function showSuccess(msg) {
    document.getElementById("deleteSuccessMessage").textContent = msg;
    new bootstrap.Modal(document.getElementById("deleteSuccessModal")).show();
}

function showFailure(msg) {
    document.getElementById("deleteFailureMessage").textContent = msg;
    new bootstrap.Modal(document.getElementById("deleteFailureModal")).show();
}
