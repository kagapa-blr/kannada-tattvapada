// Sample data with Kannada poems
const appData = {
  samputa1: {
    kosha: [
      { value: "kosha1", text: "ಹರಿದಾಸ ಸಾಹಿತ್ಯ ಕೋಶ" },
      { value: "kosha2", text: "ವಚನ ಸಾಹಿತ್ಯ ಕೋಶ" },
      { value: "kosha3", text: "ಚಾಮರಾಜ ಸಾಹಿತ್ಯ ಕೋಶ" },
    ],
    authors: [
      { value: "author1", text: "ಕನಕದಾಸ" },
      { value: "author2", text: "ಪುರಂದರದಾಸ" },
      { value: "author3", text: "ವಿಜಯದಾಸ" },
    ],
    numbers: [
      { value: "num1", text: "೧ - ಭಕ್ತಿ ತತ್ವ" },
      { value: "num2", text: "೨ - ಜ್ಞಾನ ತತ್ವ" },
      { value: "num3", text: "೩ - ಕರ್ಮ ತತ್ವ" },
    ],
    tatvapadas: [
      {
        value: "pada1",
        text: "ಹರಿ ಭಜನೆ ಮಾಡು",
        poem: `ಹರಿ ಭಜನೆ ಮಾಡು ಮನವೇ
ಹರಿ ಭಜನೆ ಮಾಡು
ಕರಿ ಕಾಲದಲ್ಲಿ ಕೇಶವನ ಸ್ಮರಣೆ
ಮರೆಯದಿರು ಮನವೇ

ಸುಖ ದುಃಖಗಳಲ್ಲಿ ಸಮ ಬುದ್ಧಿಯಿಂದ
ಮುಖ್ಯ ಪ್ರಾಣನ ಧ್ಯಾನ ಮಾಡು
ಅಖಿಲಾಂಡ ಕೋಟಿ ಬ್ರಹ್ಮಾಂಡ ನಾಯಕ
ಮಹಿಮೆ ಅಪಾರ ಅನಂತ

ಜನ್ಮ ಮರಣ ಚಕ್ರದಿಂದ ಮುಕ್ತಿ
ಪಡೆಯಲು ಹರಿ ನಾಮ ಸ್ಮರಣೆ
ಕನಕದಾಸನ ಪ್ರಭುವೇ ಕೇಶವ
ಕೃಪೆ ಮಾಡು ಸದಾ ಕಾಲ`,
        author: "ಕನಕದಾಸ",
        category: "ಭಕ್ತಿ ತತ್ವ",
      },
      {
        value: "pada2",
        text: "ಸತ್ಯ ಮಾರ್ಗ ಹಿಡಿ",
        poem: `ಸತ್ಯ ಮಾರ್ಗ ಹಿಡಿದು ನಡೆ
ಸತ್ಯವೇ ಪರಮಾತ್ಮ
ಮಿಥ್ಯೆ ಬಿಟ್ಟು ಸತ್ಯ ಹಿಡಿ
ಮೋಕ್ಷ ಸಿಗುವುದು ನಿಶ್ಚಯ

ಅಸತ್ಯದ ಮಾರ್ಗ ಬಿಟ್ಟು
ಸತ್ಯದ ಮಾರ್ಗ ಹಿಡಿದವರು
ಪರಮಾತ್ಮನ ಕೃಪೆಯಿಂದ
ಮುಕ್ತಿ ಪಡೆಯುವರು ಖಂಡಿತ

ಸತ್ಯ ಧರ್ಮ ಅಹಿಂಸೆ ದಯೆ
ಇವೇ ಮೋಕ್ಷದ ಮಾರ್ಗ
ಕನಕದಾಸನ ಪ್ರಭುವೇ ಕೇಶವ
ಸತ್ಯ ಮಾರ್ಗ ತೋರು ಸದಾ`,
        author: "ಕನಕದಾಸ",
        category: "ಜ್ಞಾನ ತತ್ವ",
      },
      {
        value: "pada3",
        text: "ದಯೆ ತೋರು",
        poem: `ದಯೆ ತೋರು ಜೀವರ ಮೇಲೆ
ದಯೆಯೇ ಧರ್ಮದ ಮೂಲ
ಪಯ್ಯ ಪಶುಗಳ ಮೇಲೆ ದಯೆ
ಪಾಪ ಪರಿಹಾರವಾಗುವುದು

ಅಹಿಂಸೆಯೇ ಪರಮ ಧರ್ಮ
ಹಿಂಸೆ ಮಾಡದಿರು ಯಾರಿಗೂ
ಸರ್ವ ಜೀವರಲ್ಲಿ ಪರಮಾತ್ಮ
ಸನ್ನಿಧಿ ಇರುವುದು ನಿತ್ಯ

ದಯೆ ಕರುಣೆ ಪ್ರೀತಿ ಸೇವೆ
ಇವೇ ಭಗವಂತನ ಗುಣಗಳು
ಪುರಂದರ ವಿಠಲನ ಭಕ್ತರೇ
ದಯೆ ತೋರಿ ಜೀವಿಸಿರಿ`,
        author: "ಪುರಂದರದಾಸ",
        category: "ಕರ್ಮ ತತ್ವ",
      },
      {
        value: "pada4",
        text: "ಭಕ್ತಿ ಮಾರ್ಗ",
        poem: `ಭಕ್ತಿ ಮಾರ್ಗದಲ್ಲಿ ನಡೆದವರು
ಭವ ಸಾಗರ ದಾಟುವರು
ಪ್ರೀತಿಯಿಂದ ಪ್ರಭುವನ್ನು ಸೇವಿಸಿ
ಪರಮ ಪದ ಪಡೆಯುವರು

ಮನಸ್ಸು ವಾಕ್ಕು ಕಾಯದಿಂದ
ಮಾಧವನನ್ನು ಭಜಿಸಿದವರು
ಜನ್ಮ ಜನ್ಮಾಂತರದ ಪಾಪ
ಪರಿಹಾರವಾಗುವುದು ನಿಶ್ಚಯ

ಭಕ್ತಿ ಯೋಗ ಜ್ಞಾನ ಮಾರ್ಗ
ಮೂರೂ ಒಂದೇ ಗುರಿಗೆ ಸೇರುವುದು
ವಿಜಯದಾಸನ ವಿಠಲ ಪ್ರಭುವೇ
ಭಕ್ತಿ ಮಾರ್ಗ ತೋರು ಸದಾ`,
        author: "ವಿಜಯದಾಸ",
        category: "ಭಕ್ತಿ ತತ್ವ",
      },
    ],
  },
  samputa2: {
    kosha: [
      { value: "kosha4", text: "ಶರಣ ಸಾಹಿತ್ಯ ಕೋಶ" },
      { value: "kosha5", text: "ಸೂಫಿ ಸಾಹಿತ್ಯ ಕೋಶ" },
    ],
    authors: [
      { value: "author4", text: "ಬಸವಣ್ಣ" },
      { value: "author5", text: "ಅಕ್ಕ ಮಹಾದೇವಿ" },
    ],
    numbers: [
      { value: "num4", text: "೪ - ಶರಣ ತತ್ವ" },
      { value: "num5", text: "೫ - ಲಿಂಗ ತತ್ವ" },
    ],
    tatvapadas: [
      {
        value: "pada5",
        text: "ಕಾಯಕವೇ ಕೈಲಾಸ",
        poem: `ಕಾಯಕವೇ ಕೈಲಾಸ
ಕೈಲಾಸವೇ ಕಾಯಕ
ಕೆಲಸವೇ ಪೂಜೆ
ಪೂಜೆಯೇ ಕೆಲಸ

ಕೈಯಿಂದ ಮಾಡುವ ಕೆಲಸವೇ
ಕೈಲಾಸದ ಪೂಜೆ
ಮನಸ್ಸಿನಿಂದ ಮಾಡುವ ಧ್ಯಾನವೇ
ಮಹೇಶ್ವರನ ಸೇವೆ

ಕಾಯಕ ಮಾಡದವನಿಗೆ
ಕೈಲಾಸ ಎಲ್ಲಿ ಸಿಗುವುದು
ಬಸವಣ್ಣನ ಕೂಡಲಸಂಗಮದೇವ
ಕಾಯಕವೇ ಪರಮ ಧರ್ಮ`,
        author: "ಬಸವಣ್ಣ",
        category: "ಶರಣ ತತ್ವ",
      },
      {
        value: "pada6",
        text: "ಇಷ್ಟಲಿಂಗ ಪೂಜೆ",
        poem: `ಇಷ್ಟಲಿಂಗವನ್ನು ಪೂಜಿಸು
ಇದೇ ಪರಮ ಧರ್ಮ
ಲಿಂಗವೇ ಪರಬ್ರಹ್ಮ
ಲಿಂಗವೇ ಪರಮಾತ್ಮ

ಹೃದಯದಲ್ಲಿ ಇಷ್ಟಲಿಂಗ
ಹಸ್ತದಲ್ಲಿ ಪ್ರಾಣಲಿಂಗ
ಶಿರಸ್ಸಿನಲ್ಲಿ ಭಾವಲಿಂಗ
ಶಿವನೇ ಸರ್ವಸ್ವ

ಚೆನ್ನಮಲ್ಲಿಕಾರ್ಜುನನ
ಮಲ್ಲಿಕಾರ್ಜುನ ಪ್ರಭುವೇ
ಇಷ್ಟಲಿಂಗ ಪೂಜೆಯಿಂದ
ಮುಕ್ತಿ ಸಿಗುವುದು ನಿಶ್ಚಯ`,
        author: "ಅಕ್ಕ ಮಹಾದೇವಿ",
        category: "ಲಿಂಗ ತತ್ವ",
      },
    ],
  },
  samputa3: {
    kosha: [{ value: "kosha6", text: "ಆಧುನಿಕ ಸಾಹಿತ್ಯ ಕೋಶ" }],
    authors: [{ value: "author6", text: "ಕುವೆಂಪು" }],
    numbers: [{ value: "num6", text: "೬ - ಮಾನವೀಯ ತತ್ವ" }],
    tatvapadas: [
      {
        value: "pada7",
        text: "ಮಾನವೀಯತೆ ಬೆಳೆಸು",
        poem: `ಮಾನವೀಯತೆ ಬೆಳೆಸು ಮನದಲ್ಲಿ
ಮಾನವತೆಯೇ ದೇವತೆ
ಜಾತಿ ಧರ್ಮ ಮರೆತು
ಮಾನವನಾಗಿ ಬಾಳು

ಸರ್ವ ಮಾನವರೂ ಸಮಾನರು
ಸಮಾನತೆಯೇ ಸತ್ಯ
ಪ್ರೀತಿಯಿಂದ ಸೇವೆ ಮಾಡು
ಪರಮಾರ್ಥವೇ ಜೀವನ

ಜಗದ್ಗುರು ಶ್ರೀ ಶಿವರಾತ್ರೀಶ್ವರ
ಮಹಾಸ್ವಾಮಿಗಳ ಆಶೀರ್ವಾದದಿಂದ
ಮಾನವೀಯತೆಯ ಮಾರ್ಗದಲ್ಲಿ
ಮುನ್ನಡೆಯಲಿ ಮಾನವ ಸಮಾಜ`,
        author: "ಕುವೆಂಪು",
        category: "ಮಾನವೀಯ ತತ್ವ",
      },
    ],
  },
}

// Initialize app when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  setupDropdownHandlers()
  console.log("🎉 ಕನ್ನಡ ತತ್ವಪದ ಕೋಶ ಆಪ್ ಸಿದ್ಧವಾಗಿದೆ!")
})

// Setup dropdown event handlers
function setupDropdownHandlers() {
  const samputa = document.getElementById("samputa")
  const kosha = document.getElementById("kosha")
  const author = document.getElementById("author")
  const number = document.getElementById("number")
  const tatvapada = document.getElementById("tatvapada")

  // Samputa change handler
  samputa.addEventListener("change", function () {
    const selectedSamputa = this.value

    if (selectedSamputa && appData[selectedSamputa]) {
      populateDropdown(kosha, appData[selectedSamputa].kosha, "ತತ್ವಪದಕೋಶದ ಹೆಸರು")
      enableDropdown(kosha)

      resetDropdown(author, "ತತ್ವಪದಕಾರರ ಹೆಸರು")
      resetDropdown(number, "ತತ್ವಪದ ಸಂಖ್ಯೆ ಮತ್ತು ಶೀರ್ಷಿಕೆ")
      resetDropdown(tatvapada, "ತತ್ವಪದ ಆಯ್ಕೆಮಾಡಿ")
      resetPoemDisplay()
    } else {
      resetAllDropdowns()
    }
  })

  // Kosha change handler
  kosha.addEventListener("change", () => {
    const selectedSamputa = samputa.value

    if (selectedSamputa && appData[selectedSamputa]) {
      populateDropdown(author, appData[selectedSamputa].authors, "ತತ್ವಪದಕಾರರ ಹೆಸರು")
      enableDropdown(author)

      resetDropdown(number, "ತತ್ವಪದ ಸಂಖ್ಯೆ ಮತ್ತು ಶೀರ್ಷಿಕೆ")
      resetDropdown(tatvapada, "ತತ್ವಪದ ಆಯ್ಕೆಮಾಡಿ")
      resetPoemDisplay()
    }
  })

  // Author change handler
  author.addEventListener("change", () => {
    const selectedSamputa = samputa.value

    if (selectedSamputa && appData[selectedSamputa]) {
      populateDropdown(number, appData[selectedSamputa].numbers, "ತತ್ವಪದ ಸಂಖ್ಯೆ ಮತ್ತು ಶೀರ್ಷಿಕೆ")
      enableDropdown(number)

      resetDropdown(tatvapada, "ತತ್ವಪದ ಆಯ್ಕೆಮಾಡಿ")
      resetPoemDisplay()
    }
  })

  // Number change handler
  number.addEventListener("change", () => {
    const selectedSamputa = samputa.value

    if (selectedSamputa && appData[selectedSamputa]) {
      populateDropdown(tatvapada, appData[selectedSamputa].tatvapadas, "ತತ್ವಪದ ಆಯ್ಕೆಮಾಡಿ")
      enableDropdown(tatvapada)
      resetPoemDisplay()
    }
  })

  // Tatvapada change handler
  tatvapada.addEventListener("change", function () {
    const selectedSamputa = samputa.value
    const selectedValue = this.value

    if (selectedSamputa && selectedValue && appData[selectedSamputa]) {
      const selectedPoem = appData[selectedSamputa].tatvapadas.find((poem) => poem.value === selectedValue)
      if (selectedPoem) {
        displayPoem(selectedPoem)
      }
    } else {
      resetPoemDisplay()
    }
  })
}

// Utility functions for dropdown management
function populateDropdown(selectElement, options, placeholder) {
  selectElement.innerHTML = `<option value="">${placeholder}</option>`

  options.forEach((option) => {
    const optionElement = document.createElement("option")
    optionElement.value = option.value
    optionElement.textContent = option.text
    selectElement.appendChild(optionElement)
  })
}

function resetDropdown(selectElement, placeholder) {
  selectElement.innerHTML = `<option value="">${placeholder}</option>`
  selectElement.disabled = true
}

function enableDropdown(selectElement) {
  selectElement.disabled = false
}

function resetAllDropdowns() {
  resetDropdown(document.getElementById("kosha"), "ತತ್ವಪದಕೋಶದ ಹೆಸರು")
  resetDropdown(document.getElementById("author"), "ತತ್ವಪದಕಾರರ ಹೆಸರು")
  resetDropdown(document.getElementById("number"), "ತತ್ವಪದ ಸಂಖ್ಯೆ ಮತ್ತು ಶೀರ್ಷಿಕೆ")
  resetDropdown(document.getElementById("tatvapada"), "ತತ್ವಪದ ಆಯ್ಕೆಮಾಡಿ")
  resetPoemDisplay()
}

// Poem display functions
function resetPoemDisplay() {
  const poemDisplayArea = document.getElementById("poem-display-area")
  poemDisplayArea.innerHTML = `
        <div class="poem-placeholder">
            <div class="placeholder-icon">📜</div>
            <h4>ತತ್ವಪದ ಪ್ರದರ್ಶನ ಪ್ರದೇಶ</h4>
            <p>ಮೇಲಿನ ಡ್ರಾಪ್‌ಡೌನ್‌ಗಳಿಂದ ತತ್ವಪದವನ್ನು ಆಯ್ಕೆಮಾಡಿ</p>
        </div>
    `
}

function displayPoem(poemData) {
  const poemDisplayArea = document.getElementById("poem-display-area")
  poemDisplayArea.innerHTML = `
        <div class="poem-display">
            <div class="poem-header">
                <div class="poem-title">${poemData.text}</div>
                <div class="poem-subtitle">${poemData.category || ""}</div>
            </div>
            <div class="poem-content">${poemData.poem}</div>
            <div class="poem-footer">
                <div class="poem-author">${poemData.author}</div>
            </div>
        </div>
    `
}

// Navigation functions
function searchContent() {
  showContent(`
        <h3>🔍 ಶೋಧನೆ ಫಲಿತಾಂಶಗಳು</h3>
        <div class="message success">ಶೋಧನೆ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ!</div>
        <p>ನಿಮ್ಮ ಆಯ್ಕೆಗಳ ಆಧಾರದ ಮೇಲೆ ಫಲಿತಾಂಶಗಳನ್ನು ತೋರಿಸಲಾಗುತ್ತಿದೆ...</p>
        <p><strong>ಒಟ್ಟು ಫಲಿತಾಂಶಗಳು:</strong> ೧೨೫ ತತ್ವಪದಗಳು</p>
        <hr style="margin: 20px 0; border: none; height: 1px; background: #e9ecef;">
        <h4>ಇತ್ತೀಚಿನ ಶೋಧನೆಗಳು:</h4>
        <ul style="margin-top: 15px; padding-left: 20px;">
            <li>ಕನಕದಾಸರ ಭಕ್ತಿ ತತ್ವಪದಗಳು - ೨೩ ಫಲಿತಾಂಶಗಳು</li>
            <li>ಬಸವಣ್ಣನ ಶರಣ ವಚನಗಳು - ೧೮ ಫಲಿತಾಂಶಗಳು</li>
            <li>ಮಾನವೀಯತೆ ಸಂಬಂಧಿತ ತತ್ವಪದಗಳು - ೧೫ ಫಲಿತಾಂಶಗಳು</li>
        </ul>
    `)
}

function showIndex() {
  showContent(`
        <h3>📋 ತತ್ತ್ವಪದ ಅಕಾರಾದಿ ಸೂಚಿ</h3>
        <div class="message success">ವರ್ಣಮಾಲೆಯ ಕ್ರಮದಲ್ಲಿ ಪ್ರಮುಖ ವಿಷಯಗಳು</div>
        <div style="columns: 2; column-gap: 30px; line-height: 1.8;">
            <p><strong>ಅ:</strong> ಅಹಿಂಸೆ, ಆತ್ಮ, ಆನಂದ, ಅಭಯ, ಅಮೃತ</p>
            <p><strong>ಇ:</strong> ಇಷ್ಟಲಿಂಗ, ಈಶ್ವರ, ಇಂದ್ರಿಯ, ಇಚ್ಛೆ</p>
            <p><strong>ಕ:</strong> ಕರ್ಮ, ಕೃಪೆ, ಕಾಯಕ, ಕೈಲಾಸ, ಕೃಷ್ಣ</p>
            <p><strong>ಗ:</strong> ಗುರು, ಗೋವಿಂದ, ಗ್ಞಾನ, ಗುಣ</p>
            <p><strong>ಭ:</strong> ಭಕ್ತಿ, ಭಗವಂತ, ಭಾವ, ಭೂಮಿ</p>
            <p><strong>ಮ:</strong> ಮಾನವೀಯತೆ, ಮೋಕ್ಷ, ಮನಸ್ಸು, ಮಾಯೆ</p>
            <p><strong>ಸ:</strong> ಸತ್ಯ, ಸೇವೆ, ಸಮಾನತೆ, ಶಿವ, ಶರಣ</p>
            <p><strong>ಹ:</strong> ಹರಿ, ಹರಿದಾಸ, ಹೃದಯ, ಹಿಂಸೆ</p>
        </div>
    `)
}

function showDictionary() {
  showContent(`
        <h3>📖 ಅರ್ಥಕೋಶ</h3>
        <div class="message success">ಪ್ರಮುಖ ಪದಗಳ ವಿವರಣೆ</div>
        <div style="line-height: 1.8;">
            <p><strong>ತತ್ವಪದ:</strong> ತತ್ವವನ್ನು ಸೂಚಿಸುವ ಪದ ಅಥವಾ ವಾಕ್ಯ, ಆಧ್ಯಾತ್ಮಿಕ ಸತ್ಯವನ್ನು ವ್ಯಕ್ತಪಡಿಸುವ ಸಾಹಿತ್ಯ</p>
            <p><strong>ಸಂಪುಟ:</strong> ಗ್ರಂಥದ ಭಾಗ ಅಥವಾ ಸಂಪುಟ, ವಿಷಯಾಧಾರಿತ ವರ್ಗೀಕರಣ</p>
            <p><strong>ಕಾಯಕ:</strong> ಕೈಯಿಂದ ಮಾಡುವ ಕೆಲಸ, ಶ್ರಮ, ಶರಣ ಸಾಹಿತ್ಯದಲ್ಲಿ ಪೂಜೆಯ ಸ್ಥಾನ</p>
            <p><strong>ಇಷ್ಟಲಿಂಗ:</strong> ವೈಯಕ್ತಿಕ ಪೂಜೆಗಾಗಿ ಧರಿಸುವ ಲಿಂಗ, ವೀರಶೈವ ಸಂಪ್ರದಾಯದ ಪ್ರಮುಖ ಸಂಕೇತ</p>
            <p><strong>ವಚನ:</strong> ಶರಣರ ಗದ್ಯ ಕಾವ್ಯ, ಆಧ್ಯಾತ್ಮಿಕ ಮತ್ತು ಸಾಮಾಜಿಕ ಸಂದೇಶಗಳನ್ನು ಹೊಂದಿದ ಸಾಹಿತ್ಯ</p>
            <p><strong>ಹರಿದಾಸ:</strong> ವಿಷ್ಣು ಭಕ್ತ ಸಂತ ಕವಿ, ಭಕ್ತಿ ಸಾಹಿತ್ಯದ ಪ್ರವರ್ತಕ</p>
            <p><strong>ಶರಣ:</strong> ಶಿವನ ಆಶ್ರಯ ಪಡೆದವರು, ವೀರಶೈವ ಸಂಪ್ರದಾಯದ ಸಂತರು</p>
        </div>
    `)
}

function showNotes() {
  showContent(`
        <h3>📝 ಟಿಪ್ಪಣಿ ಮತ್ತು ಬಳಕೆಯ ಸೂಚನೆಗಳು</h3>
        <div class="message success">ಈ ಆಪ್ ಅನ್ನು ಪರಿಣಾಮಕಾರಿಯಾಗಿ ಬಳಸುವ ವಿಧಾನ</div>
        <div style="line-height: 1.8;">
            <h4 style="color: #667eea; margin: 20px 0 10px 0;">📌 ಮೂಲಭೂತ ಬಳಕೆ:</h4>
            <p><strong>೧.</strong> ಮೊದಲು <em>"ತತ್ವಪದಕೋಶ ಸಂಪುಟ"</em> ಆಯ್ಕೆಮಾಡಿ (ಸಂಪುಟ ೧, ೨ ಅಥವಾ ೩)</p>
            <p><strong>೨.</strong> ನಂತರ ಕ್ರಮವಾಗಿ <em>"ಕೋಶದ ಹೆಸರು"</em> ಆಯ್ಕೆಮಾಡಿ</p>
            <p><strong>೩.</strong> <em>"ತತ್ವಪದಕಾರರ ಹೆಸರು"</em> ಆಯ್ಕೆಮಾಡಿ</p>
            <p><strong>೪.</strong> <em>"ತತ್ವಪದ ಸಂಖ್ಯೆ ಮತ್ತು ಶೀರ್ಷಿಕೆ"</em> ಆಯ್ಕೆಮಾಡಿ</p>
            <p><strong>೫.</strong> ಅಂತಿಮವಾಗಿ <em>"ತತ್ವಪದ"</em> ಆಯ್ಕೆಮಾಡಿ</p>

            <h4 style="color: #667eea; margin: 20px 0 10px 0;">🎯 ವಿಶೇಷ ಗುಣಲಕ್ಷಣಗಳು:</h4>
            <p><strong>•</strong> ತತ್ವಪದ ಆಯ್ಕೆ ಮಾಡಿದಾಗ ಪೂರ್ಣ ಕವಿತೆ ಡ್ರಾಪ್‌ಡೌನ್‌ಗಳ ಕೆಳಗೆ ಸುಂದರವಾಗಿ ಪ್ರದರ್ಶಿಸಲಾಗುತ್ತದೆ</p>
            <p><strong>•</strong> ಕವಿತೆಯ ಪ್ರದೇಶವು ಸ್ಕ್ರೋಲ್ ಮಾಡಬಹುದಾಗಿದೆ</p>
            <p><strong>•</strong> ಮೇಲಿನ ನ್ಯಾವಿಗೇಶನ್ ಬಟನ್‌ಗಳು ಹೆಚ್ಚುವರಿ ಮಾಹಿತಿಗಾಗಿ</p>
            <p><strong>•</strong> ಮೊಬೈಲ್ ಮತ್ತು ಟ್ಯಾಬ್ಲೆಟ್‌ನಲ್ಲಿ ಸಹ ಚೆನ್ನಾಗಿ ಕೆಲಸ ಮಾಡುತ್ತದೆ</p>

            <h4 style="color: #667eea; margin: 20px 0 10px 0;">💡 ಸಲಹೆಗಳು:</h4>
            <p><strong>•</strong> ಪ್ರತಿ ಸಂಪುಟದಲ್ಲಿ ವಿಭಿನ್ನ ಕಾಲಘಟ್ಟದ ಸಾಹಿತ್ಯ ಇದೆ</p>
            <p><strong>•</strong> ಪ್ರತಿ ಕವಿಗೆ ವಿಶಿಷ್ಟ ಶೈಲಿ ಮತ್ತು ವಿಷಯ ಇದೆ</p>
            <p><strong>•</strong> ಸಂಪೂರ್ಣ ಅನುಭವಕ್ಕಾಗಿ ಎಲ್ಲಾ ನ್ಯಾವಿಗೇಶನ್ ಆಯ್ಕೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ</p>
        </div>
    `)
}

function showBiography() {
  showContent(`
        <h3>👤 ತತ್ವಪದಕಾರರ ಜೀವನ ವಿವರ</h3>
        <div class="message success">ಮಹಾನ್ ಸಂತ ಕವಿಗಳು ಮತ್ತು ಅವರ ಕಾಲ</div>
        <div style="line-height: 1.8;">
            <h4 style="color: #667eea; margin: 20px 0 10px 0;">🕉️ ಹರಿದಾಸ ಸಾಹಿತ್ಯದ ಮಹಾನ್ ವ್ಯಕ್ತಿಗಳು:</h4>
            <p><strong>ಕನಕದಾಸ (೧೫೦೯-೧೬೦೯):</strong> ಕರ್ನಾಟಕದ ಮಹಾನ್ ಸಂತ ಕವಿ, ಹರಿದಾಸ ಸಾಹಿತ್ಯದ ಪ್ರಮುಖ ಪ್ರತಿನಿಧ��. ಬಂಡವಾಳ ಜಾತಿಯಲ್ಲಿ ಜನಿಸಿ ಸಾಮಾಜಿಕ ಸಮಾನತೆಯ ಸಂದೇಶ ನೀಡಿದರು.</p>
            <p><strong>ಪುರಂದರದಾಸ (೧೪೮೪-೧೫೬೪):</strong> ಕರ್ನಾಟಕ ಸಂಗೀತದ ಪಿತಾಮಹ, ಅರ್ಥಪೂರ್ಣ ಭಕ್ತಿಗೀತೆಗಳ ರಚಯಿತ. ಮೂಲತಃ ವರ್ತಕ, ನಂತರ ಸಂತರಾದರು.</p>
            <p><strong>ವಿಜಯದಾಸ (೧೬೮೨-೧೭೫೫):</strong> ಹರಿದಾಸ ಸಂಪ್ರದಾಯದ ಕೊನೆಯ ಮಹಾನ್ ಕವಿ, ತತ್ವ ಪದಗಳ ಮೂಲಕ ಆಧ್ಯಾತ್ಮಿಕ ಸಂದೇಶ ನೀಡಿದರು.</p>

            <h4 style="color: #667eea; margin: 20px 0 10px 0;">🔱 ಶರಣ ಸಾಹಿತ್ಯದ ಮಹಾನ್ ವ್ಯಕ್ತಿಗಳು:</h4>
            <p><strong>ಬಸವಣ್ಣ (೧೧೩೪-೧೧೯೬):</strong> ಶರಣ ಸಾಹಿತ್ಯದ ಪ್ರವರ್ತಕ, ಸಮಾಜ ಸುಧಾರಕ. ಕಾಯಕ ಸಿದ್ಧಾಂತದ ಮೂಲಕ ಕೆಲಸವೇ ಪೂಜೆ ಎಂಬ ಸಂದೇಶ ನೀಡಿದರು.</p>
            <p><strong>ಅಕ್ಕ ಮಹಾದೇವಿ (೧೧೩೦-೧೧೬೦):</strong> ಶರಣ ಸಾಹಿತ್ಯದ ಮಹಾನ್ ಕವಯಿತ್ರಿ, ಚೆನ್ನಮಲ್ಲಿಕಾರ್ಜುನನ ಭಕ್ತೆ. ಸ್ತ್ರೀ ಸ್ವಾತಂತ್ರ್ಯದ ಪ್ರತೀಕ.</p>

            <h4 style="color: #667eea; margin: 20px 0 10px 0;">📚 ಆಧುನಿಕ ಕಾಲದ ಮಹಾಕವಿ:</h4>
            <p><strong>ಕುವೆಂಪು (೧೯೦೪-೧೯೯೪):</strong> ಆಧುನಿಕ ಕನ್ನಡ ಸಾಹಿತ್ಯದ ಮಹಾಕವಿ, ಮಾನವೀಯತೆಯ ಕವಿ. ಸಾರ್ವಭೌಮ, ಶ್ರೀ ರಾಮಾಯಣ ದರ್ಶನಂ ಇವರ ಪ್ರಮುಖ ಕೃತಿಗಳು.</p>
        </div>
    `)
}

function showEditorNote() {
  showContent(`
        <h3>✍️ ಪ್ರಧಾನ ಸಂಪಾದಕರ ನುಡಿ</h3>
        <div class="message success">ಸಂಪಾದಕೀಯ</div>
        <div style="line-height: 1.8;">
            <p><strong>ಪ್ರಿಯ ಓದುಗರೇ,</strong></p>
            <p>ಈ <em>ಸಮಗ್ರ ಕನ್ನಡ ತತ್ವಪದ ಕೋಶ</em> ವು ನಮ್ಮ ಸಂಸ್ಕೃತಿಯ ಅಮೂಲ್ಯ ಸಂಪತ್ತು. ಶತಮಾನಗಳ ಕಾಲ ನಮ್ಮ ಮಹಾನ್ ಸಂತರು ಮತ್ತು ಕವಿಗಳು ರಚಿಸಿದ ತತ್ವಪದಗಳನ್ನು ಒಂದೇ ಸ್ಥಳದಲ್ಲಿ ಸಂಗ್ರಹಿಸುವ ಪ್ರಯತ್ನ ಇದು.</p>

            <p>ಈ ಕೋಶದ ಮೂಲಕ ಹೊಸ ಪೀಳಿಗೆಯು ನಮ್ಮ ಸಂಸ್ಕೃತಿಯ ಮೌಲ್ಯಗಳನ್ನು ಅರಿತುಕೊಳ್ಳಲಿ ಎಂಬುದು ನಮ್ಮ ಆಶಯ. ಪ್ರತಿ ತತ್ವಪದವೂ ಒಂದು ಜೀವನ ಶೈಲಿಯ ಮಾರ್ಗದರ್ಶಿ.</p>

            <p>ಡಿಜಿಟಲ್ ಯುಗದಲ್ಲಿ ಈ ಪ್ರಾಚೀನ ಜ್ಞಾನವನ್ನು ಸುಲಭವಾಗಿ ಪ್ರವೇಶಿಸಬಹುದಾದಂತೆ ಮಾಡಿರುವುದು ನಮ್ಮ ಹೆಮ್ಮೆಯ ವಿಷಯ.</p>

            <p style="margin-top: 25px;"><em>ಧನ್ಯವಾದಗಳು,<br><strong>ಡಾ. ರಾಮಚಂದ್ರ ಶಾಸ್ತ್ರಿ</strong><br>ಪ್ರಧಾನ ಸಂಪಾದಕ<br>ಸಂತ ಮಹಾಕವಿ ಕನಕದಾಸ ಅಧ್ಯಯನ ಮತ್ತು ಸಂಶೋಧನಾ ಕೇಂದ್ರ</em></p>
        </div>
    `)
}

function showVolumeEditor() {
  showContent(`
        <h3>📚 ಸಂಪುಟ ಸಂಪಾದಕರ ನುಡಿ</h3>
        <div class="message success">ಪ್ರತಿ ಸಂಪುಟದ ವಿವರಣೆ</div>
        <div style="line-height: 1.8;">
            <h4 style="color: #667eea; margin: 20px 0 10px 0;">📖 ಮೊದಲ ಸಂಪುಟ - ಹರಿದಾಸ ಸಾಹಿತ್ಯ:</h4>
            <p>ಈ ಸಂಪುಟದಲ್ಲಿ ಕನಕದಾಸ, ಪುರಂದರದಾಸ, ವಿಜಯದಾಸರ ತತ್ವಪದಗಳನ್ನು ಸಂಗ್ರಹಿಸಲಾಗಿದೆ. <strong>ಒಟ್ಟು ೮೫ ತತ್ವಪದಗಳು</strong> ಭಕ್ತಿ, ಜ್ಞಾನ, ಕರ್ಮ ತತ್ವಗಳ ಮೇಲೆ ಕೇಂದ್ರೀಕೃತವಾಗಿವೆ.</p>
            <p><em>ಸಂಪಾದಕ: ಪ್ರೊ. ಸುಧಾ ರಾವ್</em></p>

            <h4 style="color: #667eea; margin: 20px 0 10px 0;">📜 ಎರಡನೇ ಸಂಪುಟ - ಶರಣ ಸಾಹಿತ್ಯ:</h4>
            <p>ಬಸವಣ್ಣ, ಅಕ್ಕ ಮಹಾದೇವಿ ಮತ್ತು ಇತರ ಶರಣರ ವಚನಗಳನ್ನು ಒಳಗೊಂಡಿದೆ. <strong>ಒಟ್ಟು ೬೭ ವಚನಗಳು</strong> ಶರಣ ಮತ್ತು ಲಿಂಗ ತತ್ವಗಳ ಮೇಲೆ ಆಧಾರಿತ.</p>
            <p><em>ಸಂಪಾದಕ: ಡಾ. ಮಲ್ಲಿಕಾರ್ಜುನ ಮಠಪತಿ</em></p>

            <h4 style="color: #667eea; margin: 20px 0 10px 0;">🌟 ಮೂರನೇ ಸಂಪುಟ - ಆಧುನಿಕ ಸಾಹಿತ್ಯ:</h4>
            <p>ಕುವೆಂಪು ಮತ್ತು ಇತರ ಆಧುನಿಕ ಕವಿಗಳ ತತ್ವಪ್ರಧಾನ ಕೃತಿಗಳು. <strong>ಒಟ್ಟು ೪೨ ಕೃತಿಗಳು</strong> ಮಾನವೀಯ ಮೌಲ್ಯಗಳ ಮೇಲೆ ಕೇಂದ್ರೀಕೃತ.</p>
            <p><em>ಸಂಪಾದಕ: ಪ್ರೊ. ಚಂದ್ರಶೇಖರ ಕಂಬಾರ</em></p>

            <hr style="margin: 25px 0; border: none; height: 1px; background: #e9ecef;">
            <p><strong>ಒಟ್ಟು ಸಂಗ್ರಹ:</strong> ೧೯೪ ತತ್ವಪದಗಳು ಮತ್ತು ವಚನಗಳು</p>
            <p><strong>ಭಾಷೆಗಳು:</strong> ಹಳೆಯ ಕನ್ನಡ ಮತ್ತು ನವ್ಯ ಕನ್ನಡ</p>
            <p><strong>ಕಾಲಾವಧಿ:</strong> ೧೧ನೇ ಶತಮಾನದಿಂದ ೨೦ನೇ ಶತಮಾನದವರೆಗೆ</p>
        </div>
    `)
}

function showReferences() {
  showContent(`
        <h3>📄 ಪರಾಮರ್ಶನ ಸಾಹಿತ್ಯ ಮತ್ತು ಗ್ರಂಥಸೂಚಿ</h3>
        <div class="message success">ಸಂಶೋಧನಾ ಆಧಾರಗಳು ಮತ್ತು ಮೂಲ ಗ್ರಂಥಗಳು</div>
        <div style="line-height: 1.8;">
            <h4 style="color: #667eea; margin: 20px 0 10px 0;">📚 ಮೂಲ ಗ್ರಂಥಗಳು:</h4>
            <p>೧. <strong>ಕನಕದಾಸ ಗ್ರಂಥಾವಳಿ</strong> - ಮೈಸೂರು ವಿಶ್ವವಿದ್ಯಾಲಯ, ೧೯೬೮</p>
            <p>೨. <strong>ವಚನ ಸಾಹಿತ್ಯ ಸಂಪುಟ</strong> - ಕರ್ನಾಟಕ ವಿಶ್ವವಿದ್ಯಾಲಯ, ೧೯೭೫</p>
            <p>೩. <strong>ಹರಿದಾಸ ಸಾಹಿತ್ಯ ಸಂಶೋಧನೆ</strong> - ಬೆಂಗಳೂರು ವಿಶ್ವವಿದ್ಯಾಲಯ, ೧೯೮೨</p>
            <p>೪. <strong>ಶರಣ ಸಾಹಿತ್ಯದ ಇತಿಹಾಸ</strong> - ಕುವೆಂಪು ವಿಶ್ವವಿದ್ಯಾಲಯ, ೧೯೯೦</p>
            <p>೫. <strong>ಕುವೆಂಪು ಗ್ರಂಥಾವಳಿ</strong> - ಕುವೆಂಪು ಪ್ರತಿಷ್ಠಾನ, ೨೦೦೪</p>

            <h4 style="color: #667eea; margin: 20px 0 10px 0;">📖 ಸಂಶೋಧನಾ ಪತ್ರಿಕೆಗಳು:</h4>
            <p>• <strong>ಕನ್ನಡ ಸಾಹಿತ್ಯ ಪತ್ರಿಕೆ</strong> - ಕರ್ನಾಟಕ ವಿಶ್ವವಿದ್ಯಾಲಯ</p>
            <p>• <strong>ವಚನ ಅಧ್ಯಯನ</strong> - ಜಗದ್ಗುರು ರೆಣುಕಾಚಾರ್ಯ ವಿಶ್ವವಿದ್ಯಾಲಯ</p>
            <p>• <strong>ಹರಿದಾಸ ಸಂಶೋಧನೆ</strong> - ಅಖಿಲ ಭಾರತೀಯ ಹರಿದಾಸ ಸಂಘ</p>
            <p>• <strong>ತತ್ವವಾದ</strong> - ದ್ವೈತ ವೇದಾಂತ ಸಂಶೋಧನಾ ಕೇಂದ್ರ</p>

            <h4 style="color: #667eea; margin: 20px 0 10px 0;">🏛️ ಸಹಕಾರಿ ಸಂಸ್ಥೆಗಳು:</h4>
            <p>• ಅಖಿಲ ಭಾರತೀಯ ವೀರಶೈವ ಮಹಾಸಭಾ</p>
            <p>• ಕನ್ನಡ ಸಾಹಿತ್ಯ ಪರಿಷತ್</p>
            <p>• ಕರ್ನಾಟಕ ಸಂಸ್ಕೃತಿ ಇಲಾಖೆ</p>
            <p>• ಕುವೆಂಪು ರಾಷ್ಟ್ರೀಯ ಸ್ಮಾರಕ ಟ್ರಸ್ಟ್</p>

            <h4 style="color: #667eea; margin: 20px 0 10px 0;">💻 ಡಿಜಿಟಲ್ ಸಂಪನ್ಮೂಲಗಳು:</h4>
            <p>• ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಇ-ಗ್ರಂಥಾಲಯ</p>
            <p>• ಭಾರತೀಯ ಭಾಷಾ ಸಾಹಿತ್ಯ ಸಂಗ್ರಹ</p>
            <p>• ಡಿಜಿಟಲ್ ಲೈಬ್ರರಿ ಆಫ್ ಇಂಡಿಯಾ</p>

            <hr style="margin: 25px 0; border: none; height: 1px; background: #e9ecef;">
            <p style="font-style: italic; color: #6c757d;">
                <strong>ಟಿಪ್ಪಣಿ:</strong> ಈ ಕೋಶದ ನಿರ್ಮಾಣದಲ್ಲಿ ೫೦+ ವಿದ್ವಾಂಸರು ಮತ್ತು ಸಂಶೋಧಕರ ಕೊಡುಗೆ ಇದೆ.
                ಎಲ್ಲಾ ಮೂಲ ಗ್ರಂಥಗಳನ್ನು ಪರಿಶೀಲಿಸಿ ಪ್ರಮಾಣಿಕ ಪಠ್ಯ ಸಿದ್ಧಪಡಿಸಲಾಗಿದೆ.
            </p>
        </div>
    `)
}

function showContent(content) {
  const contentArea = document.getElementById("content-area")
  contentArea.innerHTML = content
}

// Log initialization message
console.log("🎉 ಕನ್ನಡ ತತ್ವಪದ ಕೋಶ ಆಪ್ ಸಿದ್ಧವಾಗಿದೆ!")
console.log(
  "📚 Total Tatvapadas loaded:",
  Object.values(appData).reduce((total, samputa) => total + samputa.tatvapadas.length, 0),
)
