// app/static/js/admin/documents.js

import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

let documentModal = null;
let deleteModal = null;
let editingId = null;
let deletingId = null;
let quill = null;

export function initDocumentsTab() {
    documentModal = new bootstrap.Modal(document.getElementById("documentModal"));
    deleteModal = new bootstrap.Modal(document.getElementById("deleteDocumentModal"));

    // Initialize Quill editor
    quill = new Quill('#docContent', {
        theme: 'snow',
        modules: {
            toolbar: [
                [{ header: [1, 2, 3, 4, 5, 6, false] }],
                [{ font: [] }],                      // Font family dropdown
                [{ size: ['small', false, 'large', 'huge'] }], // Font size dropdown
                ['bold', 'italic', 'underline', 'strike', 'blockquote', 'code-block'],
                [{ color: [] }, { background: [] }], // Text color and background color
                [{ script: 'sub' }, { script: 'super' }],      // Subscript/superscript
                [{ list: 'ordered' }, { list: 'bullet' }],
                [{ indent: '-1' }, { indent: '+1' }],           // Indent
                [{ align: [] }],                      // Text alignments
                ['link', 'image', 'video'],
                ['clean']                             // Remove formatting button
            ]
        },
        bounds: '#documentModal .modal-content' // Confine dropdowns/popups within modal for better UX
    });


    document.getElementById("openAddDocumentModal").addEventListener("click", openAddDocumentModal);

    document.getElementById("documentForm").addEventListener("submit", async e => {
        e.preventDefault();
        await saveDocument();
    });

    document.getElementById("confirmDeleteDocBtn").addEventListener("click", async () => {
        if (deletingId) await deleteDocument(deletingId);
    });

    document.getElementById("documentModal").addEventListener("hidden.bs.modal", () => {
        editingId = null;
        quill.setContents([{ insert: '\n' }]);
    });
    document.getElementById("deleteDocumentModal").addEventListener("hidden.bs.modal", () => {
        deletingId = null;
    });

    loadDocuments();
}

async function loadDocuments() {
    showLoader();
    try {
        const docs = await apiClient.get(apiEndpoints.documents.list);
        renderDocumentsTable(docs);
    } catch (err) {
        console.error("Failed to load documents", err);
        alert("Failed to load documents.");
    } finally {
        hideLoader();
    }
}

function renderDocumentsTable(docs) {
    const tbody = document.querySelector("#documentTable tbody");
    tbody.innerHTML = "";

    docs.forEach((doc, idx) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="text-center">${idx + 1}</td>
            <td>${escapeHtml(doc.title)}</td>
            <td>${escapeHtml(doc.category || "")}</td>
            <td>${escapeHtml(doc.description || "")}</td>
            <td class="text-center">${formatDate(doc.created_at)}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-primary me-1" title="Edit">✏️</button>
                <button class="btn btn-sm btn-outline-danger" title="Delete">🗑</button>
            </td>
        `;
        tr.querySelector("button[title='Edit']").addEventListener("click", () => openEditDocumentModal(doc));
        tr.querySelector("button[title='Delete']").addEventListener("click", () => openDeleteDocumentModal(doc));

        tbody.appendChild(tr);
    });
}

function openAddDocumentModal() {
    editingId = null;
    document.getElementById("documentModalTitle").textContent = "Add Document";
    document.getElementById("documentForm").reset();
    quill.setContents([{ insert: '\n' }]);
    documentModal.show();
}

function openEditDocumentModal(doc) {
    editingId = doc.id;
    document.getElementById("documentModalTitle").textContent = "Edit Document";
    document.getElementById("documentId").value = doc.id;
    document.getElementById("docTitle").value = doc.title;
    document.getElementById("docCategory").value = doc.category || "";
    document.getElementById("docDescription").value = doc.description || "";
    // Manually sanitize minimal harmful tags and attributes
    quill.root.innerHTML = sanitizeHtmlContent(doc.content || "");
    documentModal.show();
}

async function saveDocument() {
    const title = document.getElementById("docTitle").value.trim();
    const category = document.getElementById("docCategory").value.trim();
    const description = document.getElementById("docDescription").value.trim();

    let contentHtml = quill.root.innerHTML;
    contentHtml = sanitizeHtmlContent(contentHtml);

    if (!title) {
        alert("Title is required.");
        return;
    }
    if (!contentHtml || contentHtml.replace(/<[^>]+>/g, '').trim() === "") {
        alert("Content is required.");
        return;
    }

    const payload = { title, category, description, content: contentHtml };

    const saveBtn = document.querySelector("#documentForm button[type='submit']");
    saveBtn.disabled = true;
    saveBtn.textContent = "Saving...";
    showLoader();

    try {
        if (editingId) {
            await apiClient.put(apiEndpoints.documents.update(editingId), payload);
        } else {
            await apiClient.post(apiEndpoints.documents.create, payload);
        }
        documentModal.hide();
        loadDocuments();
    } catch (err) {
        console.error("Save failed", err);
        alert(
            err?.response?.data?.message
            || (err?.message ? "Save failed: " + err.message : "Unknown error on save.")
        );
    } finally {
        hideLoader();
        saveBtn.disabled = false;
        saveBtn.textContent = "💾 Save";
    }
}

function openDeleteDocumentModal(doc) {
    deletingId = doc.id;
    document.getElementById("deleteDocTitle").textContent = doc.title;
    deleteModal.show();
}

async function deleteDocument(id) {
    showLoader();
    try {
        await apiClient.delete(apiEndpoints.documents.delete(id));
        deleteModal.hide();
        loadDocuments();
    } catch (err) {
        console.error("Delete failed", err);
        alert(
            err?.response?.data?.message
            || (err?.message ? "Delete failed: " + err.message : "Unknown error on delete.")
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

/**
 * Basic HTML sanitizer to remove <script> tags and on* event handlers.
 * Preserves allowed tags used by Quill like p, b, i, u, strike, ul, ol, li, a, img, code-block, etc.
 * Be cautious: this is NOT a complete sanitizer but protects against common XSS.
 */
function sanitizeHtmlContent(html) {
    if (!html) return "";

    // Remove script tags entirely (case insensitive)
    html = html.replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, "");

    // Remove event handler attributes like onclick, onerror, onload...
    html = html.replace(/\s(on\w+)=["'][^"']*["']/gi, "");

    // Remove javascript: scheme in href or src attributes
    html = html.replace(/\s(href|src)=["']javascript:[^"']*["']/gi, "");

    return html;
}
