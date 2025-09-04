import apiClient from '../apiClient.js';
import apiEndpoints from '../apiEndpoints.js';
import { showLoader, hideLoader } from "../loader.js";

const container = document.getElementById('user-document-container');
const pagination = document.getElementById('user-document-pagination');
const searchBar = document.getElementById('search-bar'); // search input

// Fullscreen overlay elements
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
let filteredDocuments = [];
let currentPage = 1;
const pageSize = 6;
let currentDocIndex = 0;

// ----------------- Load all documents metadata -----------------
async function loadDocuments() {
    try {
        showLoader(); // show loader while fetching
        documents = await apiClient.get(apiEndpoints.documents.list);
        filteredDocuments = documents.slice();
        renderPage(1);
        overlay.style.display = 'none';
    } catch (err) {
        console.error('Failed to load documents:', err);
        container.innerHTML = '<p class="text-danger">Failed to load documents.</p>';
    } finally {
        hideLoader(); // hide loader after fetching
    }
}

// ----------------- Render page -----------------
function renderPage(page) {
    currentPage = page;
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const pageDocs = filteredDocuments.slice(start, end);

    container.innerHTML = '';
    pageDocs.forEach((doc, idx) => {
        const card = createDocumentCard(doc, start + idx);
        container.appendChild(card);
    });

    renderPagination();
}

// ----------------- Create single document card -----------------
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

// ----------------- Pagination -----------------
function renderPagination() {
    const totalPages = Math.ceil(filteredDocuments.length / pageSize);
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

// ----------------- Open document viewer -----------------
async function openDocViewer(index) {
    currentDocIndex = index;
    const doc = filteredDocuments[index];

    try {
        showLoader(); // show loader while fetching document content
        const fullDoc = await apiClient.get(apiEndpoints.documents.getById(doc.id));

        viewerTitle.textContent = fullDoc.title;
        viewerCategory.textContent = fullDoc.category || 'N/A';
        viewerDescription.textContent = fullDoc.description || '';
        viewerContent.innerHTML = fullDoc.content || '';

        viewerPageIndicator.textContent = `ದಸ್ತಾವೇಜು ${index + 1} / ${filteredDocuments.length}`;
        prevBtn.disabled = (index === 0);
        nextBtn.disabled = (index === filteredDocuments.length - 1);

        overlay.style.display = 'flex';
    } catch (err) {
        console.error('Failed to load document content:', err);
        alert('Failed to load document content.');
    } finally {
        hideLoader(); // hide loader after fetching
    }
}

// ----------------- Close viewer -----------------
function closeDocViewer() {
    overlay.style.display = 'none';
}

// ----------------- Print document -----------------
function printDocument() {
    const printContainer = document.getElementById('print-container');
    printContainer.innerHTML = '';

    const category = viewerCategory.textContent;
    const description = viewerDescription.textContent;
    const contentHTML = viewerContent.innerHTML;

    const page = document.createElement('div');
    page.className = 'print-page';
    page.innerHTML = `
        <p><strong>ವರ್ಗ:</strong> ${category}</p>
        <p><strong>ವಿವರಣೆ:</strong></p>
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

// ----------------- Navigation buttons -----------------
nextBtn.addEventListener('click', () => {
    if (currentDocIndex < filteredDocuments.length - 1) {
        openDocViewer(currentDocIndex + 1);
    }
});
prevBtn.addEventListener('click', () => {
    if (currentDocIndex > 0) {
        openDocViewer(currentDocIndex - 1);
    }
});

if (printBtn) {
    printBtn.addEventListener('click', printDocument);
}

// ----------------- Keyboard navigation -----------------
document.addEventListener('keydown', (e) => {
    if (overlay.style.display !== 'flex') return;

    if (e.key === 'Escape') closeDocViewer();
    if (e.key === 'ArrowRight' && currentDocIndex < filteredDocuments.length - 1) {
        openDocViewer(currentDocIndex + 1);
    }
    if (e.key === 'ArrowLeft' && currentDocIndex > 0) {
        openDocViewer(currentDocIndex - 1);
    }
});

window.closeDocViewer = closeDocViewer;





// Helper: convert English digits to Kannada digits
function engToKannadaDigits(str) {
    return str.replace(/\d/g, d => String.fromCharCode(0x0CE6 + Number(d)));
}

// Normalize string for search: lower case + convert digits
function normalizeForSearch(str) {
    if (!str) return '';
    return engToKannadaDigits(str.toLowerCase());
}

// ----------------- Search functionality -----------------
if (searchBar) {
    searchBar.addEventListener('input', () => {
        const query = normalizeForSearch(searchBar.value);

        filteredDocuments = documents.filter(doc => {
            const title = normalizeForSearch(doc.title);
            const description = normalizeForSearch(doc.description);
            return title.includes(query) || description.includes(query);
        });

        renderPage(1);
    });
}




// ----------------- Initial load -----------------
loadDocuments();

export {
    loadDocuments,
    renderPage,
    openDocViewer,
    closeDocViewer
};
