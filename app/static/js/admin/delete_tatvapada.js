import apiEndpoints from "../apiEndpoints.js";
import apiClient from "../apiClient.js";
import { showLoader, hideLoader } from "../loader.js";

// Track action awaiting user confirmation
let pendingDeleteAction = null;

// Initialization: Load the delete keys and render UI table
export async function initDeleteTab() {
    await loadDeleteKeys();
}

// Load all delete keys and build delete table
async function loadDeleteKeys() {
    try {
        showLoader();
        const data = await apiClient.get(apiEndpoints.tatvapada.deleteKeys);

        const tbody = document.querySelector("#deleteTatvapadaTable tbody");
        if (!tbody) return;

        tbody.innerHTML = "";

        // Flatten delete keys array depending on backend shape
        const deleteKeys = Array.isArray(data.delete_keys)
            ? data.delete_keys
            : (data.delete_keys?.delete_keys || []);

        deleteKeys.forEach(entry => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>
                    <input type="checkbox" class="row-author-select" data-samputa="${entry.samputa_sankhye}" data-author="${entry.tatvapada_author_id}">
                </td>
                <td>${entry.samputa_sankhye}</td>
                <td>${entry.tatvapadakarara_hesaru}</td>
                <td>${entry.tatvapada_sankhyes.length}</td>
                <td class="col-sankhya">
                    <button class="btn btn-sm btn-outline-primary toggle-sankhya-btn">Show</button>
                    <div class="sankhya-scrollable mt-1" style="display:none; max-height:150px; overflow-y:auto;"></div>
                </td>
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

            // Add sankhya checkboxes inside scrollable div
            const sankhyaContainer = row.querySelector(".sankhya-scrollable");
            entry.tatvapada_sankhyes
                .sort((a, b) => parseInt(a) - parseInt(b))
                .forEach(s => {
                    const div = document.createElement("div");
                    div.className = "form-check form-check-inline";
                    div.innerHTML = `
                        <input class="form-check-input row-select" type="checkbox"
                            data-samputa="${entry.samputa_sankhye}"
                            data-author="${entry.tatvapada_author_id}"
                            data-author-name="${entry.tatvapadakarara_hesaru}"
                            data-sankhya="${s}">
                        <label class="form-check-label">${s}</label>
                    `;
                    sankhyaContainer.appendChild(div);
                });

            // Toggle show/hide sankhya list
            row.querySelector(".toggle-sankhya-btn").addEventListener("click", function () {
                if (sankhyaContainer.style.display === "none") {
                    sankhyaContainer.style.display = "block";
                    this.textContent = "Hide";
                } else {
                    sankhyaContainer.style.display = "none";
                    this.textContent = "Show";
                }
            });
        });

        attachEventHandlers();
        attachDeleteTableSearch();

    } catch (err) {
        showFailure("Failed to load Tatvapadas");
        console.error(err);
    } finally {
        hideLoader();
    }
}

// Attach all event handlers for delete actions and UI controls
function attachEventHandlers() {
    // Bootstrap modal references
    const modal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"));
    const confirmBtn = document.getElementById("confirmDeleteBtn");
    const confirmMessage = document.getElementById("deleteConfirmMessage");
    const bulkDeleteBtn = document.getElementById("bulkDeleteBtn");
    const selectAll = document.getElementById("selectAll");

    // Perform the pending delete action on confirmation modal confirm button
    confirmBtn.onclick = async () => {
        if (pendingDeleteAction) {
            await pendingDeleteAction();
            pendingDeleteAction = null;
        }
        modal.hide();
    };

    // Delete all Tatvapadas for one author in a samputa ("Delete All" buttons)
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
                    const result = await apiClient.delete(
                        apiEndpoints.tatvapada.deleteBySamputaAuthor(samputa, authorId)
                    );
                    showSuccess(result.message || "Deleted successfully");
                    await loadDeleteKeys();
                } catch (err) {
                    showFailure((err && err.message) || "Delete failed");
                } finally {
                    hideLoader();
                }
            };

            modal.show();
        });
    });

    // Select/Deselect all sankhya checkboxes
    if (selectAll) {
        selectAll.addEventListener("change", () => {
            const checkboxes = document.querySelectorAll(".row-select");
            checkboxes.forEach(cb => cb.checked = selectAll.checked);
            bulkDeleteBtn.disabled = !selectAll.checked;
        });
    }

    // Enable/disable bulk delete button based on any sankhya checkbox checked
    document.querySelectorAll(".row-select").forEach(cb => {
        cb.addEventListener("change", () => {
            const anyChecked = document.querySelectorAll(".row-select:checked").length > 0;
            bulkDeleteBtn.disabled = !anyChecked;
            if (!cb.checked && selectAll.checked) selectAll.checked = false;
        });
    });

    // Bulk deletion of checked Tatvapadas
    if (bulkDeleteBtn) {
        bulkDeleteBtn.addEventListener("click", () => {
            const selected = Array.from(document.querySelectorAll(".row-select:checked")).map(cb => ({
                samputa: cb.dataset.samputa,
                authorId: cb.dataset.author,
                authorName: cb.dataset.authorName,
                sankhya: cb.dataset.sankhya
            }));
            if (!selected.length) return;

            // Group selected sankhyas by samputa and author for confirmation display
            const groups = {};
            selected.forEach(item => {
                const key = `${item.samputa}|${item.authorId}|${item.authorName}`;
                if (!groups[key]) {
                    groups[key] = {
                        samputa: item.samputa,
                        authorId: item.authorId,
                        authorName: item.authorName,
                        sankhyas: []
                    };
                }
                groups[key].sankhyas.push(item.sankhya);
            });

            let html = '';
            Object.values(groups).forEach(group => {
                html += `
                    <div class="mb-1">
                        <strong>Samputa:</strong> ${group.samputa} <br>
                        <strong>Author ID:</strong> ${group.authorId} <br>
                        <strong>Author Name:</strong> ${group.authorName} <br>
                        <strong>Selected Tatvapada(s):</strong> ${group.sankhyas.join(", ")}
                    </div>
                    <hr>
                `;
            });

            confirmMessage.innerHTML = html;

            pendingDeleteAction = async () => {
                try {
                    showLoader();
                    // Prepare keys for backend bulk deletion API call
                    const apiItems = selected.map(item => ({
                        samputa: item.samputa,
                        authorId: item.authorId,
                        sankhya: item.sankhya
                    }));
                    const result = await apiClient.delete(apiEndpoints.tatvapada.bulkDelete, { items: apiItems });
                    showSuccess(result.message || "Selected Tatvapada(s) deleted");
                    await loadDeleteKeys();
                } catch (err) {
                    showFailure((err && err.message) || "Bulk delete failed");
                } finally {
                    hideLoader();
                }
            };

            modal.show();
        });
    }

    // --- New: Delete entire samputa by input ---

    const deleteSamputaBtn = document.getElementById("deleteSamputaBtn");
    const deleteSamputaInput = document.getElementById("deleteSamputaInput");

    if (deleteSamputaBtn && deleteSamputaInput) {
        deleteSamputaBtn.addEventListener("click", () => {
            const samputaNumber = deleteSamputaInput.value.trim();
            if (!samputaNumber) {
                alert("Please enter a samputa number to delete.");
                return;
            }

            confirmMessage.innerHTML = `
                <strong>Samputa Number:</strong> ${samputaNumber} <br>
                <span class="text-danger">This will delete <strong>ALL</strong> Tatvapada entries under this samputa. This action is irreversible.</span>
            `;

            pendingDeleteAction = async () => {
                try {
                    showLoader();
                    const result = await apiClient.delete(apiEndpoints.tatvapada.deleteBySamputa(samputaNumber));
                    showSuccess(result.message || "Samputa deleted successfully");
                    await loadDeleteKeys();
                } catch (err) {
                    showFailure((err && err.message) || "Delete failed");
                } finally {
                    hideLoader();
                }
            };

            modal.show();
        });
    }
}

// Show success notification modal
function showSuccess(msg) {
    const modal = new bootstrap.Modal(document.getElementById("deleteSuccessModal"));
    document.getElementById("deleteSuccessMessage").textContent = msg;
    modal.show();
}

// Show failure notification modal
function showFailure(msg) {
    const modal = new bootstrap.Modal(document.getElementById("deleteFailureModal"));
    document.getElementById("deleteFailureMessage").textContent = msg;
    modal.show();
}

// Attach live search filter to delete table
function attachDeleteTableSearch() {
    const searchInput = document.getElementById("deleteTatvapadaSearch");
    if (!searchInput) return;
    searchInput.addEventListener("input", function () {
        const filter = this.value.trim().toLowerCase();
        const tbody = document.querySelector("#deleteTatvapadaTable tbody");
        if (!tbody) return;
        Array.from(tbody.rows).forEach(row => {
            const text = Array.from(row.cells).map(td =>
                td.innerText || td.textContent || ""
            ).join(" ").toLowerCase();
            row.style.display = (!filter || text.includes(filter)) ? "" : "none";
        });
    });
}
