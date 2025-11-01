import apiClient, { BASE_URL } from "../apiClient.js";
import { showLoader, hideLoader } from "../loader.js";

document.addEventListener('DOMContentLoaded', () => {
    let bookToDeleteId = null;

    // Initialize DataTable (still needs jQuery)
    const table = $('#booksTable').DataTable({
        serverSide: true,
        processing: true,
        searching: false,
        ordering: false,
        ajax: {
            url: `${BASE_URL}/books/api/`,
            type: 'GET',
            data: d => ({
                draw: d.draw,
                start: d.start,
                length: d.length,
                search_word: document.getElementById('manualSearchInput').value.trim() || ''
            }),
            dataSrc: json => {
                hideLoader();
                return json.data || [];
            },
            beforeSend: () => showLoader(),
            error: () => {
                hideLoader();
                showErrorModal('Failed to load books.');
            }
        },
        columns: [
            { data: null, render: (data, type, row, meta) => meta.row + meta.settings._iDisplayStart + 1 },
            {
                data: 'cover_image_url',
                render: data => data ? `<img src="${data}" width="50" class="rounded">` : '<span class="text-muted">No image</span>',
                orderable: false
            },
            { data: 'title', defaultContent: '-' },
            { data: 'author_name', defaultContent: '-' },
            { data: 'price', render: d => d ? `₹${parseFloat(d).toFixed(2)}` : '-' },
            { data: 'stock_quantity', defaultContent: '0' },
            { data: 'rating', render: d => d ? parseFloat(d).toFixed(1) : '-', defaultContent: '-' },
            {
                data: null,
                render: d => `
          <button class="btn btn-info btn-sm edit" data-id="${d.id}">Edit</button>
          <button class="btn btn-danger btn-sm delete" data-id="${d.id}">Delete</button>
        `,
                orderable: false
            }
        ],
        lengthMenu: [10, 25, 50, 100],
        pageLength: 10,
        language: { emptyTable: "No books available." }
    });

    // Utility: Show error modal
    function showErrorModal(message) {
        const errorBody = document.getElementById('errorModalBody');
        if (errorBody) errorBody.textContent = message;
        const errorModalElement = document.getElementById('errorModal');
        if (errorModalElement) {
            const modal = new bootstrap.Modal(errorModalElement);
            modal.show();
        }
    }

    // Reset form helper
    function resetForm(form) {
        form.reset();
        form.classList.remove('was-validated');
    }

    // Fill form with book data
    function fillBookForm(book) {
        const form = document.getElementById('bookForm');
        if (!form) return;
        form.elements['id'].value = book.id || '';
        form.elements['title'].value = book.title || '';
        form.elements['subtitle'].value = book.subtitle || '';
        form.elements['author_name'].value = book.author_name || '';
        form.elements['language'].value = book.language || '';
        form.elements['price'].value = book.price || '';
        form.elements['discount_price'].value = book.discount_price || '';
        form.elements['stock_quantity'].value = book.stock_quantity || '';
        form.elements['number_of_pages'].value = book.number_of_pages || '';
        form.elements['description'].value = book.description || '';
        form.elements['book_code'].value = book.book_code || '';
        form.elements['catalog_number'].value = book.catalog_number || '';
        form.elements['publisher_name'].value = book.publisher_name || '';
        form.elements['publication_date'].value = book.publication_date ? book.publication_date.split('T')[0] : '';
        form.elements['rating'].value = book.rating || '';

        const coverPreview = document.getElementById('coverPreview');
        if (coverPreview) {
            if (book.cover_image_url) {
                coverPreview.src = book.cover_image_url;
                coverPreview.classList.remove('d-none');
            } else {
                coverPreview.src = '';
                coverPreview.classList.add('d-none');
            }
        }
    }

    // Show modal helper
    function showModalById(id) {
        const modalElement = document.getElementById(id);
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            return modal;
        }
    }

    // Attach event listeners

    // Refresh & Search buttons
    document.getElementById('refreshBtn').addEventListener('click', () => table.ajax.reload());
    document.getElementById('searchBtn').addEventListener('click', () => table.ajax.reload());

    // Add Book button
    document.getElementById('addBookBtn').addEventListener('click', () => {
        const form = document.getElementById('bookForm');
        resetForm(form);
        form.elements['id'].value = '';
        const coverPreview = document.getElementById('coverPreview');
        if (coverPreview) {
            coverPreview.src = '';
            coverPreview.classList.add('d-none');
        }
        const formError = document.getElementById('formError');
        if (formError) {
            formError.classList.add('d-none');
            formError.textContent = '';
        }
        showModalById('bookModal');
    });

    // Auto Fill button
    document.getElementById('autoFillBtn').addEventListener('click', () => {
        const form = document.getElementById('autoFillForm');
        resetForm(form);
        const autoFillError = document.getElementById('autoFillError');
        if (autoFillError) {
            autoFillError.classList.add('d-none');
            autoFillError.textContent = '';
        }
        showModalById('autoFillModal');
    });

    // Delegate Edit and Delete buttons in the table
    document.getElementById('booksTable').addEventListener('click', async (event) => {
        const editBtn = event.target.closest('.edit');
        const deleteBtn = event.target.closest('.delete');

        if (editBtn) {
            event.preventDefault();
            const id = editBtn.dataset.id;
            const formError = document.getElementById('formError');
            if (formError) {
                formError.classList.add('d-none');
                formError.textContent = '';
            }
            try {
                showLoader();
                const book = await apiClient.get(`/books/api/${id}`);
                fillBookForm(book);
                showModalById('bookModal');
            } catch {
                showErrorModal('Failed to fetch book details.');
            } finally {
                hideLoader();
            }
        }

        if (deleteBtn) {
            event.preventDefault();
            bookToDeleteId = deleteBtn.dataset.id;
            showModalById('confirmationModal');
        }
    });

    // Confirm delete button
    document.getElementById('confirmDeleteBtn').addEventListener('click', async () => {
        if (!bookToDeleteId) return;
        const confirmationModalEl = document.getElementById('confirmationModal');
        const confirmationModal = bootstrap.Modal.getInstance(confirmationModalEl);
        confirmationModal.hide();
        try {
            showLoader();
            await apiClient.delete(`/books/api/${bookToDeleteId}`);
            table.ajax.reload();
            bookToDeleteId = null;
        } catch (err) {
            showErrorModal('Failed to delete book. ' + (err?.data?.error || ''));
        } finally {
            hideLoader();
        }
    });

    // Cover preview on file select
    document.getElementById('coverFileInput').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
            const preview = document.getElementById('coverPreview');
            preview.src = ev.target.result;
            preview.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
    });

    // Save Book form submit
    document.getElementById('bookForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }
        const formError = document.getElementById('formError');
        formError.classList.add('d-none');
        formError.textContent = '';

        const formData = new FormData(form);
        const id = form.elements['id'].value;
        const endpoint = id ? `/books/api/${id}` : '/books/api/';
        const method = id ? 'put' : 'post';

        try {
            showLoader();
            document.getElementById('saveBtn').disabled = true;
            await apiClient.request({ method, endpoint, body: formData, headers: {} });
            bootstrap.Modal.getInstance(document.getElementById('bookModal')).hide();
            resetForm(form);
            table.ajax.reload();
        } catch (err) {
            formError.textContent = err?.data?.error || 'Failed to save book.';
            formError.classList.remove('d-none');
        } finally {
            document.getElementById('saveBtn').disabled = false;
            hideLoader();
        }
    });

    // Auto Fill form submit
    document.getElementById('autoFillForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }
        const autoFillError = document.getElementById('autoFillError');
        autoFillError.classList.add('d-none');
        autoFillError.textContent = '';

        try {
            showLoader();
            const formData = new FormData(form);
            const res = await apiClient.post('/books/api/autofill', formData, {});
            alert(`Created ${res.created} books.\nSkipped: ${res.skipped}`);
            bootstrap.Modal.getInstance(document.getElementById('autoFillModal')).hide();
            resetForm(form);
            table.ajax.reload();
        } catch (err) {
            autoFillError.textContent = err?.data?.error || 'Auto-fill failed.';
            autoFillError.classList.remove('d-none');
        } finally {
            hideLoader();
        }
    });

    // Initially hide loader and load table
    hideLoader();
    table.ajax.reload();
});
