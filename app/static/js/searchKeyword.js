import apiClient from "./apiClient.js";
import apiEndpoints from "./apiEndpoints.js";

// Escape HTML characters to avoid XSS
function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/[&<>"'`=\/]/g, s => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
    '/': '&#x2F;',
    '`': '&#x60;',
    '=': '&#x3D;'
  })[s]);
}

// Highlight keyword in Tatvapada text
function highlightKeyword(text, keyword) {
  if (!keyword) return escapeHtml(text);

  const escapedKeyword = keyword.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
  const trailingCombining = '(?:[\u0CCD\\p{M}])*';
  const regex = new RegExp(`(${escapedKeyword}${trailingCombining})`, 'giu');

  return escapeHtml(text).replace(
    regex,
    '<span style="background-color: yellow; color: black; font-weight: bold; padding: 0 2px; border-radius: 2px;">$1</span>'
  );
}

// Main search function
async function handleSearchClick() {
  const keywordInput = document.getElementById('searchKeyword');
  const keyword = keywordInput.value.trim();

  const resultsDiv = document.getElementById('searchResults');
  const countDiv = document.getElementById('resultCount');

  if (!keyword) {
    alert('ಶೋಧನೆಗಾಗಿ ಪದವನ್ನು ನಮೂದಿಸಿ.');
    keywordInput.focus();
    return;
  }

  countDiv.innerHTML = '';
  resultsDiv.innerHTML = '<p>ಶೋಧನೆ ನಡೆಯುತ್ತಿದೆ...</p>';

  try {
    const data = await apiClient.post(apiEndpoints.tatvapada.searchByWord, { keyword });

    if (!data.length) {
      countDiv.innerHTML = '';
      resultsDiv.innerHTML = '<p>ಯಾವುದೇ ಫಲಿತಾಂಶಗಳು ಸಿಕ್ಕಿಲ್ಲ.</p>';
      return;
    }

    countDiv.innerHTML = `ಒಟ್ಟು ತತ್ತ್ವಪದ ಸಂಕೇತಗಳು ಸಿಕ್ಕಿವೆ: ${data.length}`;

    resultsDiv.innerHTML = data.map(item => `
      <div class="card mb-3 shadow-sm border-0 rounded">
        <div class="card-body">
          <div class="row g-2">
            <div class="col-md-4"><span class="fw-bold">ತತ್ತ್ವಪದ ಶೀರ್ಷಿಕೆ :</span><br>${escapeHtml(item.tatvapada_sheershike)}</div>
            <div class="col-md-4"><span class="fw-bold">ತತ್ತ್ವಪದಕೋಶ ಶೀರ್ಷಿಕೆ :</span><br>${escapeHtml(item.tatvapadakosha_sheershike)}</div>
            <div class="col-md-4"><span class="fw-bold">ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು :</span><br>${escapeHtml(item.tatvapadakarara_hesaru)}</div>
          </div>
          <div class="row g-2 mt-2">
            <div class="col-md-4"><span class="fw-bold">ಸಂಪುಟ ಸಂಖ್ಯೆ :</span><br>${escapeHtml(item.samputa_sankhye?.toString())}</div>
            <div class="col-md-4"><span class="fw-bold">ತತ್ವಪದ ಸಂಖ್ಯೆ :</span><br>${escapeHtml(item.tatvapada_sankhye)}</div>
            <div class="col-md-4"><span class="fw-bold">ಮೊದಲ ಸಾಲು :</span><br>${escapeHtml(item.tatvapada_first_line)}</div>
          </div>
          <hr>
          <div>
            <span class="fw-bold">ತತ್ತ್ವಪದ :</span>
            <div style="white-space: pre-wrap; margin-top: 4px;">
              ${highlightKeyword(item.tatvapada?.trimStart(), keyword)}
            </div>
          </div>
          <hr>
          <div class="mb-2">
            <span class="fw-bold">ಕ್ಲಿಷ್ಟ ಪದಗಳ ಅರ್ಥ :</span>
            <div style="white-space: pre-wrap; margin-top: 4px;">${escapeHtml(item.klishta_padagalu_artha)}</div>
          </div>
          <div class="mb-2">
            <span class="fw-bold">ಭಾವಾನುವಾದ :</span>
            <div style="white-space: pre-wrap; margin-top: 4px;">${escapeHtml(item.bhavanuvada)}</div>
          </div>
          <div class="mb-2">
            <span class="fw-bold">ಟಿಪ್ಪಣಿ :</span>
            <div style="white-space: pre-wrap; margin-top: 4px;">${escapeHtml(item.tippani)}</div>
          </div>
          <div class="mb-2"><span class="fw-bold">ವಿಭಾಗ :</span> ${escapeHtml(item.vibhag)}</div>
        </div>
      </div>
    `).join('');

  } catch (error) {
    countDiv.innerHTML = '';
    resultsDiv.innerHTML = `<p class="text-danger">ಶೋಧನೆಯಲ್ಲಿ ದೋಷ: ${escapeHtml(error.message)}</p>`;
  }
}

// Show modal and initialize inputs
function searchContent() {
  const searchModal = new bootstrap.Modal(document.getElementById('searchModal'));
  searchModal.show();

  const keywordInput = document.getElementById('searchKeyword');
  const resultsDiv = document.getElementById('searchResults');
  const countDiv = document.getElementById('resultCount');

  keywordInput.value = '';
  resultsDiv.innerHTML = '<p class="text-muted">ಪದವನ್ನು ನಮೂದಿಸಿ ಮತ್ತು ಶೋಧಿಸಿ ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ.</p>';
  countDiv.innerHTML = '<p class="mb-0 text-primary">ಪದವನ್ನು ನಮೂದಿಸಿ ಮತ್ತು ಶೋಧಿಸಿ ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ.</p>';

  const btnSearch = document.getElementById('btnSearch');
  btnSearch.onclick = null; // Remove any existing handler
  btnSearch.onclick = handleSearchClick;
}

// Attach search modal trigger on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const openSearchBtn = document.getElementById('searchBtn');
  if (openSearchBtn) {
    openSearchBtn.addEventListener('click', searchContent);
  }
});
