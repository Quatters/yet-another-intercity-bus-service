function selectRowAsCheckbox(row) {
    const checkbox = row.querySelector('input[type="checkbox"]')
    checkbox.checked = !checkbox.checked;
}
