// manageTippani.js
import apiClient from "../apiClient.js";
import apiEndpoints from "../apiEndpoints.js";
import { showLoader, hideLoader } from "../loader.js";

export async function initTippaniManageTab() {
    // ---------------- DOM Elements ----------------
    const samputaSelect = document.getElementById('tippani_manage_samputaSelect');
    const authorSelect = document.getElementById('tippani_manage_authorSelect');
    const tippaniForm = document.getElementById('tippani_manage_form');
    const tippaniIdInput = document.getElementById('tippani_manage_id');
    const tippaniContent = document.getElementById('tippani_manage_content');
    const saveBtn = document.getElementById('tippani_manage_saveBtn');
    const deleteBtn = document.getElementById('tippani_manage_deleteBtn');
    const confirmDeleteBtn = document.getElementById('tippani_manage_confirmDeleteBtn');

    const deleteModalEl = document.getElementById('tippani_manage_deleteModal');
    const deleteModal = new bootstrap.Modal(deleteModalEl);

    const infoModalEl = document.getElementById('tippani_manage_infoModal');
    const infoModal = new bootstrap.Modal(infoModalEl);
    const infoModalBody = document.getElementById('tippani_manage_infoModalBody');

    let samputaAuthorsData = [];

    // ---------------- Helper Functions ----------------
    function showInfo(msg) {
        infoModalBody.textContent = msg;
        infoModal.show();
    }

    async function loadSamputaAuthors() {
        try {
            showLoader();
            const resp = await apiClient.get(apiEndpoints.admin.samputaAuthor);
            if (resp.success) {
                samputaAuthorsData = resp.data;
                samputaAuthorsData.forEach(item => {
                    const opt = document.createElement('option');
                    opt.value = item.samputa;
                    opt.textContent = item.samputa;
                    samputaSelect.appendChild(opt);
                });
            }
        } catch (err) {
            console.error("loadSamputaAuthors:", err);
            showInfo("Failed to load Samputa data.");
        } finally {
            hideLoader();
        }
    }

    async function fetchTippani(samputa, authorId) {
        if (!samputa || !authorId) return;
        try {
            showLoader();
            const query = new URLSearchParams({ samputa, author_id: authorId }).toString();
            const resp = await apiClient.get(`${apiEndpoints.admin.manageTippani}?${query}`);
            tippaniForm.style.display = 'block';
            if (resp.success && resp.data) {
                tippaniIdInput.value = resp.data.id;
                tippaniContent.value = resp.data.content;
            } else {
                tippaniIdInput.value = '';
                tippaniContent.value = '';
            }
        } catch (err) {
            console.error("fetchTippani:", err);
            showInfo("Failed to fetch Tippani.");
        } finally {
            hideLoader();
        }
    }

    async function saveTippani() {
        const id = tippaniIdInput.value;
        const content = tippaniContent.value.trim();
        const samputa = samputaSelect.value;
        const authorId = authorSelect.value;

        if (!content || !samputa || !authorId) return showInfo('Samputa, Author, and content required.');

        try {
            showLoader();
            let resp;
            if (id) {
                resp = await apiClient.put(`${apiEndpoints.admin.manageTippani}/${id}`, { content });
            } else {
                resp = await apiClient.post(apiEndpoints.admin.manageTippani, { samputa, author_id: authorId, content });
                if (resp.success) tippaniIdInput.value = resp.data.id;
            }

            if (resp.success) showInfo(`Tippani ${id ? 'updated' : 'created'} successfully!`);
            else showInfo('Failed to save Tippani: ' + (resp.message || 'Unknown error'));
        } catch (err) {
            console.error("saveTippani:", err);
            showInfo('Failed to save Tippani.');
        } finally {
            hideLoader();
        }
    }

    async function deleteTippani() {
        const samputa = samputaSelect.value;
        const authorId = authorSelect.value;

        if (!samputa || !authorId) return showInfo('Please select Samputa and Author to delete.');

        try {
            showLoader();
            const resp = await apiClient.delete(apiEndpoints.admin.manageTippani, {
                samputa,
                author_id: authorId
            });

            deleteModal.hide();

            if (resp.success) {
                tippaniIdInput.value = '';
                tippaniContent.value = '';
                showInfo('Tippani deleted successfully!');
            } else {
                showInfo('Failed to delete Tippani: ' + (resp.message || 'Unknown error'));
            }
        } catch (err) {
            console.error("deleteTippani:", err);
            showInfo('Failed to delete Tippani.');
        } finally {
            hideLoader();
        }
    }

    // ---------------- Event Listeners ----------------
    samputaSelect.addEventListener('change', () => {
        const samputa = samputaSelect.value;
        authorSelect.innerHTML = '<option value="" selected>-- Select Author --</option>';
        tippaniForm.style.display = 'none';
        tippaniIdInput.value = '';
        tippaniContent.value = '';

        if (!samputa) {
            authorSelect.disabled = true;
            return;
        }

        const samputaObj = samputaAuthorsData.find(s => s.samputa === samputa);
        if (samputaObj && samputaObj.authors.length) {
            samputaObj.authors.forEach(author => {
                const opt = document.createElement('option');
                opt.value = author.id;
                opt.textContent = author.name;
                authorSelect.appendChild(opt);
            });
            authorSelect.disabled = false;
        } else {
            authorSelect.disabled = true;
        }
    });

    authorSelect.addEventListener('change', () => {
        fetchTippani(samputaSelect.value, authorSelect.value);
    });

    saveBtn.addEventListener('click', saveTippani);
    deleteBtn.addEventListener('click', () => deleteModal.show());
    confirmDeleteBtn.addEventListener('click', deleteTippani);

    // ---------------- Initialize ----------------
    await loadSamputaAuthors();
}
