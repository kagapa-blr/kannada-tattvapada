// static/js/common.js

export function setFormFieldValue(fieldId, value) {
    const element = document.getElementById(fieldId);
    if (element) {
        element.value = value ?? "";
    } else {
        console.warn(`Element with ID "${fieldId}" not found.`);
    }
}
