// Escape HTML characters to avoid XSS
function escapeHtml(text) {
  if (!text) return '';
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

// Highlight keyword occurrences (inline styled span with yellow background)
function highlightKeyword(text, keyword) {
  if (!keyword) return escapeHtml(text);
  const escapedKeyword = keyword.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
  const regex = new RegExp(`(${escapedKeyword})`, 'gi');
  return escapeHtml(text).replace(
    regex,
    '<span style="background-color: yellow; color: black; font-weight: bold; padding: 0 2px; border-radius: 2px;">$1</span>'
  );
}

function searchContent() {
  // Show modal
  var searchModal = new bootstrap.Modal(document.getElementById('searchModal'));
  searchModal.show();

  // Clear previous state
  const keywordInput = document.getElementById('searchKeyword');
  keywordInput.value = '';
  const resultsDiv = document.getElementById('searchResults');
  const countDiv = document.getElementById('resultCount');
  resultsDiv.innerHTML = '<p class="text-muted">ಪದವನ್ನು ನಮೂದಿಸಿ ಮತ್ತು ಶೋಧಿಸಿ ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ.</p>';
  countDiv.innerHTML = '<p class="mb-0 text-primary">ಪದವನ್ನು ನಮೂದಿಸಿ ಮತ್ತು ಶೋಧಿಸಿ ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ.</p>';

  const btnSearch = document.getElementById('btnSearch');
  btnSearch.onclick = null;

  btnSearch.onclick = async function () {
    const keyword = keywordInput.value.trim();
    if (!keyword) {
      alert('ಶೋಧನೆಗಾಗಿ ಪದವನ್ನು ನಮೂದಿಸಿ.');
      keywordInput.focus();
      return;
    }

    countDiv.innerHTML = '';
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
        countDiv.innerHTML = '';
        resultsDiv.innerHTML = '<p>ಯಾವುದೇ ಫಲಿತಾಂಶಗಳು ಸಿಕ್ಕಿಲ್ಲ.</p>';
        return;
      }

      // Show total count
      countDiv.innerHTML = `ಒಟ್ಟು ತತ್ತ್ವಪದ ಸಂಕೇತಗಳು ಸಿಕ್ಕಿವೆ: ${data.length}`;

      // Render results using Bootstrap grid for alignment
      resultsDiv.innerHTML = data.map(item => `
        <div class="card mb-3 shadow-sm border-0 rounded">
          <div class="card-body">
            <div class="row g-2">
              <div class="col-md-4"><span class="fw-bold">ತತ್ತ್ವಪದ ಶೀರ್ಷಿಕೆ :</span><br>${escapeHtml(item.tatvapada_sheershike || '')}</div>
              <div class="col-md-4"><span class="fw-bold">ತತ್ತ್ವಪದಕೋಶ ಶೀರ್ಷಿಕೆ :</span><br>${escapeHtml(item.tatvapadakosha_sheershike || '')}</div>
              <div class="col-md-4"><span class="fw-bold">ತತ್ತ್ವಪದಕಾರರ ಹೆಸರು :</span><br>${escapeHtml(item.tatvapadakarara_hesaru || '')}</div>
            </div>
            <div class="row g-2 mt-2">
              <div class="col-md-4"><span class="fw-bold">ಸಂಪುಟ ಸಂಖ್ಯೆ :</span><br>${escapeHtml(item.samputa_sankhye?.toString() || '')}</div>
              <div class="col-md-4"><span class="fw-bold">ತತ್ವಪದ ಸಂಖ್ಯೆ :</span><br>${escapeHtml(item.tatvapada_sankhye || '')}</div>
              <div class="col-md-4"><span class="fw-bold">ಮೊದಲ ಸಾಲು :</span><br>${escapeHtml(item.tatvapada_first_line || '')}</div>
            </div>
            <hr>
            <div>
              <span class="fw-bold">ತತ್ತ್ವಪದ :</span>
              <div style="white-space: pre-wrap; margin-top: 4px;">

                 ${highlightKeyword((item.tatvapada || '').trimStart(), keyword)}
              </div>
            </div>
            <hr>
            <div class="mb-2">
              <span class="fw-bold">ಕ್ಲಿಷ್ಟ ಪದಗಳ ಅರ್ಥ :</span>
              <div style="white-space: pre-wrap; margin-top: 4px;">${escapeHtml(item.klishta_padagalu_artha || '')}</div>
            </div>
            <div class="mb-2">
              <span class="fw-bold">ಭಾವಾನುವಾದ :</span>
              <div style="white-space: pre-wrap; margin-top: 4px;">${escapeHtml(item.bhavanuvada || '')}</div>
            </div>
            <div class="mb-2">
              <span class="fw-bold">ಟಿಪ್ಪಣಿ :</span>
              <div style="white-space: pre-wrap; margin-top: 4px;">${escapeHtml(item.tippani || '')}</div>
            </div>
            <div class="mb-2"><span class="fw-bold">ವಿಭಾಗ :</span> ${escapeHtml(item.vibhag || '')}</div>
          </div>
        </div>`).join('');

    } catch (error) {
      countDiv.innerHTML = '';
      resultsDiv.innerHTML = `<p class="text-danger">ಶೋಧನೆಯಲ್ಲಿ ದೋಷ: ${escapeHtml(error.message)}</p>`;
    }
  };
}
