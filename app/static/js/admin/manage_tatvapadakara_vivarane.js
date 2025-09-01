// app/static/js/admin/manage_tatvapadakara_vivarane.js

import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

let authorModal = null;
let deleteModal = null;
let editingId = null;
let deletingId = null;
let quill = null;

export function initAuthorsTab() {
    authorModal = new bootstrap.Modal(document.getElementById("authorModal"));
    deleteModal = new bootstrap.Modal(document.getElementById("deleteAuthorModal"));

    // Initialize Quill editor
    quill = new Quill("#authorContentEditor", {
        theme: "snow",
        modules: {
            toolbar: {
                container: "#authorContentToolbar"
            }
        },
        bounds: "#authorModal .modal-content"
    });

    // Keep hidden textarea synced
    quill.on("text-change", () => {
        document.getElementById("authorContent").value = quill.root.innerHTML;
    });

    // Add Author button
    document.getElementById("openAddAuthorModal").addEventListener("click", openAddAuthorModal);

    // Save Author
    document.getElementById("authorForm").addEventListener("submit", async e => {
        e.preventDefault();
        await saveAuthor();
    });

    // Confirm Delete
    document.getElementById("confirmDeleteAuthorBtn").addEventListener("click", async () => {
        if (deletingId) await deleteAuthor(deletingId);
    });

    // Reset on close
    document.getElementById("authorModal").addEventListener("hidden.bs.modal", () => {
        editingId = null;
        quill.setContents([{ insert: "\n" }]);
        document.getElementById("authorForm").reset();
    });

    document.getElementById("deleteAuthorModal").addEventListener("hidden.bs.modal", () => {
        deletingId = null;
    });

    loadAuthors();
}

// Load Authors
async function loadAuthors() {
    showLoader();
    try {
        const authors = await apiClient.get(apiEndpoints.authors.list);
        renderAuthorsTable(authors);
    } catch (err) {
        console.error("Failed to load authors", err);
        alert("Failed to load authors.");
    } finally {
        hideLoader();
    }
}

function renderAuthorsTable(authors) {
    const tbody = document.querySelector("#authorsTable tbody");
    tbody.innerHTML = "";

    if (!authors || authors.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center">No authors found</td></tr>`;
        return;
    }

    authors.forEach((a, idx) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="text-center">${idx + 1}</td>
            <td>${escapeHtml(a.author_name)}</td>
            <td class="text-center">${formatDate(a.created_at)}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-primary me-1" title="Edit">✏️</button>
                <button class="btn btn-sm btn-outline-danger" title="Delete">🗑</button>
            </td>
        `;
        tr.querySelector("button[title='Edit']").addEventListener("click", () => openEditAuthorModal(a.id));
        tr.querySelector("button[title='Delete']").addEventListener("click", () => openDeleteAuthorModal(a));
        tbody.appendChild(tr);
    });
}

// Add Modal
function openAddAuthorModal() {
    editingId = null;
    document.getElementById("authorModalTitle").textContent = "Add Author";
    document.getElementById("authorForm").reset();
    quill.setContents([{ insert: "\n" }]);
    authorModal.show();
}

// Edit Modal
async function openEditAuthorModal(authorId) {
    editingId = authorId;
    document.getElementById("authorModalTitle").textContent = "Edit Author";

    showLoader();
    try {
        // Fetch full author details
        const author = await apiClient.get(apiEndpoints.authors.getById(authorId));

        document.getElementById("authorId").value = author.id;
        document.getElementById("authorName").value = author.author_name;

        // Load content into Quill
        quill.root.innerHTML = sanitizeHtmlContent(author.content || "");
        document.getElementById("authorContent").value = quill.root.innerHTML;

        authorModal.show();
    } catch (err) {
        console.error("Failed to fetch author details", err);
        alert("Failed to fetch author details.");
    } finally {
        hideLoader();
    }
}

// Save Author
async function saveAuthor() {
    const name = document.getElementById("authorName").value.trim();
    let contentHtml = sanitizeHtmlContent(quill.root.innerHTML);

    if (!name) {
        alert("Author name is required.");
        return;
    }

    if (!contentHtml || contentHtml.replace(/<[^>]+>/g, "").trim() === "") {
        alert("Content is required.");
        return;
    }

    const payload = { author_name: name, content: contentHtml };

    const saveBtn = document.querySelector("#authorForm button[type='submit']");
    saveBtn.disabled = true;
    saveBtn.textContent = "Saving...";
    showLoader();

    try {
        if (editingId) {
            await apiClient.put(apiEndpoints.authors.update(editingId), payload);
        } else {
            await apiClient.post(apiEndpoints.authors.create, payload);
        }
        authorModal.hide();
        loadAuthors();
    } catch (err) {
        console.error("Save failed", err);
        alert(
            err?.response?.data?.message ||
            (err?.message ? "Save failed: " + err.message : "Unknown error on save.")
        );
    } finally {
        hideLoader();
        saveBtn.disabled = false;
        saveBtn.textContent = "💾 Save";
    }
}

// Delete Modal
function openDeleteAuthorModal(author) {
    deletingId = author.id;
    document.getElementById("deleteAuthorName").textContent = author.author_name;
    deleteModal.show();
}

async function deleteAuthor(id) {
    showLoader();
    try {
        await apiClient.delete(apiEndpoints.authors.delete(id));
        deleteModal.hide();
        loadAuthors();
    } catch (err) {
        console.error("Delete failed", err);
        alert(
            err?.response?.data?.message ||
            (err?.message ? "Delete failed: " + err.message : "Unknown error on delete.")
        );
    } finally {
        hideLoader();
    }
}

// Helpers
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatDate(dt) {
    if (!dt) return "";
    return new Date(dt).toLocaleString();
}

function sanitizeHtmlContent(html) {
    if (!html) return "";
    html = html.replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, "");
    html = html.replace(/\s(on\w+)=["'][^"']*["']/gi, "");
    html = html.replace(/\s(href|src)=["']javascript:[^"']*["']/gi, "");
    return html;
}
