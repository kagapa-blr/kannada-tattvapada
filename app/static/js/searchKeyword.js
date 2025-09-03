import apiClient from "./apiClient.js";
import apiEndpoints from "./apiEndpoints.js";
import { showLoader, hideLoader } from "./loader.js";

// Escape HTML safely
function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/[&<>"'`=\/]/g, s => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;',
    "'": '&#39;', '/': '&#x2F;', '`': '&#x60;', '=': '&#x3D;'
  })[s]);
}

// Highlight search keyword
function highlightKeyword(text, keyword) {
  if (!keyword) return escapeHtml(text);

  const escapedKeyword = keyword.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
  const trailingCombining = '(?:[\u0CCD\\p{M}])*';
  const regex = new RegExp(`(${escapedKeyword}${trailingCombining})`, 'giu');

  return escapeHtml(text).replace(
    regex,
    '<span style="background-color: yellow;color: black; font-weight: bold">$1</span>'
  );
}

// Render search results
function renderResults(data, keyword) {
  const resultsDiv = document.getElementById('searchResults');
  const template = document.getElementById('searchResultTemplate');

  resultsDiv.innerHTML = '';

  const safeValue = (value) => (!value || value === "-") ? "" : escapeHtml(value.toString());

  data.forEach((item, idx) => {
    const clone = template.content.cloneNode(true);

    // Fill text fields
    clone.querySelector('[data-field="samputa_sankhye"]').innerHTML = safeValue(item.samputa_sankhye);
    clone.querySelector('[data-field="tatvapadakarara_hesaru"]').innerHTML = safeValue(item.tatvapadakarara_hesaru);
    clone.querySelector('[data-field="tatvapada_sankhye"]').innerHTML = safeValue(item.tatvapada_sankhye);
    clone.querySelector('[data-field="tatvapadakosha_sheershike"]').innerHTML = safeValue(item.tatvapadakosha_sheershike);
    clone.querySelector('[data-field="tatvapada_sheershike"]').innerHTML = safeValue(item.tatvapada_sheershike);
    clone.querySelector('[data-field="tatvapada_first_line"]').innerHTML = safeValue(item.tatvapada_first_line);

    // Vibhag
    if (item.vibhag && item.vibhag !== "-") {
      const vibhagEl = clone.querySelector('[data-section="vibhag"]');
      vibhagEl.classList.remove('d-none');
      vibhagEl.querySelector('[data-field="vibhag"]').innerHTML = safeValue(item.vibhag);
    }

    // Tatvapada
    if (item.tatvapada && item.tatvapada.trim() !== "-") {
      const tatvapadaEl = clone.querySelector('[data-section="tatvapada"]');
      tatvapadaEl.classList.remove('d-none');
      tatvapadaEl.querySelector('[data-field="tatvapada"]').innerHTML =
        highlightKeyword(item.tatvapada.trimStart(), keyword);
    }

    resultsDiv.appendChild(clone);

    // Add divider between results
    if (idx < data.length - 1) {
      resultsDiv.appendChild(document.createElement("hr"));
    }
  });
}

// Handle search
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
  showLoader();

  try {
    const data = await apiClient.post(apiEndpoints.tatvapada.searchByWord, { keyword });

    if (!data.length) {
      countDiv.innerHTML = '';
      resultsDiv.innerHTML = '<p>ಯಾವುದೇ ಫಲಿತಾಂಶಗಳು ಸಿಕ್ಕಿಲ್ಲ.</p>';
      return;
    }

    countDiv.innerHTML = `ಒಟ್ಟು ತತ್ವಪದ ಸಂಕೇತಗಳು ಸಿಕ್ಕಿವೆ: ${data.length}`;
    renderResults(data, keyword);

  } catch (error) {
    countDiv.innerHTML = '';
    resultsDiv.innerHTML = `<p class="text-danger">ಶೋಧನೆಯಲ್ಲಿ ದೋಷ: ${escapeHtml(error.message)}</p>`;
  } finally {
    hideLoader();
  }
}

// Open modal
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
  btnSearch.onclick = handleSearchClick;
}

// Attach trigger
document.addEventListener('DOMContentLoaded', () => {
  const openSearchBtn = document.getElementById('searchBtn');
  if (openSearchBtn) {
    openSearchBtn.addEventListener('click', searchContent);
  }
});
