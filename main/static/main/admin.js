const createFromExistingButton = document.querySelector('#create-from-existing-button');
const disabled = !Array.from(document.querySelectorAll('input[type=radio]')).some(input => input.checked);

if (disabled) {
    createFromExistingButton.classList.add('disabled');
} else {
    createFromExistingButton.classList.remove('disabled');
}

function selectRowAsCheckbox(row) {
    for (const input of document.querySelectorAll('input[type="radio"]')) {
        input.checked = false;
    }
    const radio = row.querySelector('input[type="radio"]')
    radio.checked = !radio.checked;
    createFromExistingButton.classList.remove('disabled');
}

function createFromExisting() {
    const id = document
        .querySelector('input[type=radio]:checked')
        .parentElement
        .parentElement
        .id;
    window.location.href = `/admin/new-flight?from_existing=${id}`
}
