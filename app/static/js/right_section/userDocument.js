import apiClient from '../apiClient.js';
import apiEndpoints from '../apiEndpoints.js';

const container = document.getElementById('user-document-container');
const pagination = document.getElementById('user-document-pagination');

// Fullscreen overlay elements (hidden initially)
const overlay = document.getElementById('doc-viewer-overlay');
const viewerTitle = document.getElementById('doc-viewer-title');
const viewerCategory = document.getElementById('doc-viewer-category');
const viewerDescription = document.getElementById('doc-viewer-description');
const viewerContent = document.getElementById('doc-viewer-content');
const viewerPageIndicator = document.getElementById('doc-page-indicator');

const nextBtn = document.getElementById('doc-next');
const prevBtn = document.getElementById('doc-prev');
const printBtn = document.getElementById('print-doc');

let documents = [];
let currentPage = 1;
const pageSize = 6; // documents per page in grid
let currentDocIndex = 0;

// Load all documents metadata (no content)
async function loadDocuments() {
    try {
        documents = await apiClient.get(apiEndpoints.documents.list);
        renderPage(1);
        overlay.style.display = 'none'; // hide viewer initially
    } catch (err) {
        console.error('Failed to load documents:', err);
        container.innerHTML = '<p class="text-danger">Failed to load documents.</p>';
    }
}

// Render document cards for a page
function renderPage(page) {
    currentPage = page;
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const pageDocs = documents.slice(start, end);

    container.innerHTML = '';
    pageDocs.forEach((doc, idx) => {
        const card = createDocumentCard(doc, start + idx);
        container.appendChild(card);
    });

    renderPagination();
}

// Create single document card element
function createDocumentCard(doc, index) {
    const cardCol = document.createElement('div');
    cardCol.className = 'col-md-4';

    const card = document.createElement('div');
    card.className = 'card user-document-card h-100';

    card.innerHTML = `
    <div class="card-body d-flex flex-column">
      <h5 class="card-title">${doc.title}</h5>
      <p class="card-text text-truncate">${doc.description || ''}</p>
      <button class="btn btn-primary mt-auto user-document-view-btn">View</button>
    </div>`;

    card.querySelector('.user-document-view-btn')
        .addEventListener('click', () => openDocViewer(index));

    cardCol.appendChild(card);
    return cardCol;
}

// Render pagination control for grid
function renderPagination() {
    const totalPages = Math.ceil(documents.length / pageSize);
    pagination.innerHTML = '';

    if (totalPages <= 1) return;

    for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === currentPage ? 'active' : ''}`;
        const a = document.createElement('a');
        a.className = 'page-link';
        a.href = '#';
        a.textContent = i;
        a.addEventListener('click', e => {
            e.preventDefault();
            renderPage(i);
        });

        li.appendChild(a);
        pagination.appendChild(li);
    }
}

// Open fullscreen document viewer and fetch full content by ID
async function openDocViewer(index) {
    currentDocIndex = index;
    const doc = documents[index];

    try {
        const fullDoc = await apiClient.get(apiEndpoints.documents.getById(doc.id));

        viewerTitle.textContent = fullDoc.title;
        viewerCategory.textContent = fullDoc.category || 'N/A';
        viewerDescription.textContent = fullDoc.description || '';
        viewerContent.innerHTML = fullDoc.content || '';

        viewerPageIndicator.textContent = `Document ${index + 1} of ${documents.length}`;
        prevBtn.disabled = (index === 0);
        nextBtn.disabled = (index === documents.length - 1);

        overlay.style.display = 'flex';
    } catch (err) {
        console.error('Failed to load document content:', err);
        alert('Failed to load document content.');
    }
}

// Close the fullscreen viewer
function closeDocViewer() {
    overlay.style.display = 'none';
}

// Print the current document content
function printDocument() {
    const printContainer = document.getElementById('print-container');
    printContainer.innerHTML = ''; // clear previous content

    const category = viewerCategory.textContent;
    const description = viewerDescription.textContent;
    const contentHTML = viewerContent.innerHTML;

    const page = document.createElement('div');
    page.className = 'print-page';
    page.innerHTML = `
        <p><strong>Category:</strong> ${category}</p>
        <p><strong>Description:</strong></p>
        <p>${description}</p>
        <hr/>
        <div>${contentHTML}</div>
    `;

    printContainer.appendChild(page);

    setTimeout(() => {
        window.print();
        printContainer.innerHTML = '';
    }, 50);
}

// Event listeners for navigation buttons
nextBtn.addEventListener('click', () => {
    if (currentDocIndex < documents.length - 1) {
        openDocViewer(currentDocIndex + 1);
    }
});
prevBtn.addEventListener('click', () => {
    if (currentDocIndex > 0) {
        openDocViewer(currentDocIndex - 1);
    }
});

// Event listener for print button
if (printBtn) {
    printBtn.addEventListener('click', printDocument);
}

// Keyboard event handlers to navigate and close overlay
document.addEventListener('keydown', (e) => {
    if (overlay.style.display !== 'flex') return;

    if (e.key === 'Escape') closeDocViewer();
    if (e.key === 'ArrowRight' && currentDocIndex < documents.length - 1) {
        openDocViewer(currentDocIndex + 1);
    }
    if (e.key === 'ArrowLeft' && currentDocIndex > 0) {
        openDocViewer(currentDocIndex - 1);
    }
});

// Make close function globally accessible for inline onclick attribute
window.closeDocViewer = closeDocViewer;

// Initial load
loadDocuments();

export {
    loadDocuments,
    renderPage,
    openDocViewer,
    closeDocViewer
};
