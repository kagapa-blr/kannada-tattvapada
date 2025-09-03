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
                [{ font: [] }],
                [{ size: ['small', false, 'large', 'huge'] }],
                ['bold', 'italic', 'underline', 'strike', 'blockquote', 'code-block'],
                [{ color: [] }, { background: [] }],
                [{ script: 'sub' }, { script: 'super' }],
                [{ list: 'ordered' }, { list: 'bullet' }],
                [{ indent: '-1' }, { indent: '+1' }],
                [{ align: [] }],
                ['link', 'image', 'video'],
                ['clean']
            ]
        },
        bounds: '#documentModal .modal-content'
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
        tr.querySelector("button[title='Edit']").addEventListener("click", () => openEditDocumentModal(doc.id));
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

async function openEditDocumentModal(id) {
    showLoader();
    try {
        const doc = await apiClient.get(apiEndpoints.documents.getById(id)); // fetch full content

        editingId = doc.id;
        document.getElementById("documentModalTitle").textContent = "Edit Document";
        document.getElementById("documentId").value = doc.id;
        document.getElementById("docTitle").value = doc.title;
        document.getElementById("docCategory").value = doc.category || "";
        document.getElementById("docDescription").value = doc.description || "";
        quill.root.innerHTML = sanitizeHtmlContent(doc.content || "");

        documentModal.show();
    } catch (err) {
        console.error("Failed to load document for editing", err);
        alert("Could not load document content. Please try again.");
    } finally {
        hideLoader();
    }
}

async function saveDocument() {
    const title = document.getElementById("docTitle").value.trim();
    const category = document.getElementById("docCategory").value.trim();
    const description = document.getElementById("docDescription").value.trim();

    let contentHtml = sanitizeHtmlContent(quill.root.innerHTML);

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

function sanitizeHtmlContent(html) {
    if (!html) return "";

    html = html.replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, "");
    html = html.replace(/\s(on\w+)=["'][^"']*["']/gi, "");
    html = html.replace(/\s(href|src)=["']javascript:[^"']*["']/gi, "");

    return html;
}
