//static/js/searchKeyword.js

  // Function to escape special HTML characters to avoid XSS & markup issues
function escapeHtml(text) {
  return text.replace(/[&<>"'`=\/]/g, function (s) {
    return ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
      '/': '&#x2F;',
      '`': '&#x60;',
      '=': '&#x3D;'
    })[s];
  });
}

// Highlight keyword occurrences (case-insensitive) inside a text with <mark>
function highlightKeyword(text, keyword) {
  if (!keyword) return escapeHtml(text);
  // Escape keyword for RegExp
  const escapedKeyword = keyword.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
  const regex = new RegExp(`(${escapedKeyword})`, 'gi');
  // Replace matches with a span having inline styles for yellow background
  return escapeHtml(text).replace(
    regex,
    '<span style="background-color: yellow; color: black; font-weight: bold; padding: 0 2px; border-radius: 2px;">$1</span>'
  );
}

function searchContent() {
  // Show the modal
  var searchModal = new bootstrap.Modal(document.getElementById('searchModal'));
  searchModal.show();

  // Clear previous input and results
  const keywordInput = document.getElementById('searchKeyword');
  keywordInput.value = '';
  const resultsDiv = document.getElementById('searchResults');
  resultsDiv.innerHTML = '<p class="text-muted">ಪದವನ್ನು eing ಮಾಡಿ ಮತ್ತು ಶೋಧಿಸಿ ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ.</p>';

  // Add event listener for search button inside modal
  const btnSearch = document.getElementById('btnSearch');



btnSearch.onclick = async function () {
  const keyword = keywordInput.value.trim();
  if (!keyword) {
    alert('ಶೋಧನೆಗಾಗಿ ಪದವನ್ನು ನಮೂದಿಸಿ.');
    keywordInput.focus();
    return;
  }

  resultsDiv.innerHTML = '<p>ಶೋಧನೆ ನಡೆಯುತ್ತಿದೆ...</p>';

  try {
    const response = await fetch('/api/tatvapada/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keyword })
    });
    if (!response.ok) {
      throw new Error('ಸರ್ವರ್‌ನಲ್ಲಿ ದೋಷವಾಗಿದೆ');
    }
    const data = await response.json();

    if (!data.length) {
      resultsDiv.innerHTML = '<p>ಯಾವುದೇ ಫಲಿತಾಂಶಗಳು ಸಿಕ್ಕಿಲ್ಲ.</p>';
      return;
    }

    // Add total count display above results
    const countHtml = `<p class="fw-bold mb-3">ಒಟ್ಟು ತತ್ತ್ವಪದ ಸಂಕೇತಗಳು ಸಿಕ್ಕಿವೆ: ${data.length}</p>`;

    // Render results with highlighted keyword
    const resultsHtml = data.map(item => `
      <div class="card mb-3">
        <div class="card-body">
          <h5 class="card-title">${escapeHtml(item.tatvapada_sheershike || '')}</h5>
          <h6 class="card-subtitle mb-2 text-muted">${escapeHtml(item.tatvapadakosha_sheershike || '')} - ${escapeHtml(item.tatvapadakarara_hesaru?.hesaru || '')}</h6>
          <p class="card-text" style="white-space: pre-wrap;">${highlightKeyword(item.tatvapada || '', keyword)}</p>
          <small class="text-muted">ಸಂಪುಟ ಸಂಖ್ಯೆ: ${escapeHtml(item.samputa_sankhye?.toString() || '')}, ತತ್ವಪದ ಸಂಖ್ಯೆ: ${escapeHtml(item.tatvapada_sankhye || '')}</small>
        </div>
      </div>`).join('');

    resultsDiv.innerHTML = countHtml + resultsHtml;

  } catch (error) {
    resultsDiv.innerHTML = `<p class="text-danger">ಶೋಧನೆಯಲ್ಲಿ ದೋಷ: ${escapeHtml(error.message)}</p>`;
  }
};




}


