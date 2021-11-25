function addReview(name, id) {
    document.getElementById(`contactparent-${id}`).value = id;
    document.getElementById(`parenttext-${id}`).innerText = `${name}, `;
    const textarea = document.getElementById(`parenttext-${id}`)
    textarea.hidden = !textarea.hidden;
    const button = document.getElementById(`button-${id}`)
    button.hidden = !button.hidden;

}

function addAnotherReview(name, id, main_id) {
    document.getElementById(`another_contactparent-${id}`).value = id;
    document.getElementById(`contactparent-${id}`).value = main_id;
    document.getElementById(`parenttext-${id}`).innerText = `${name}, `;
    const textarea = document.getElementById(`parenttext-${id}`)
    textarea.hidden = !textarea.hidden;
    const button = document.getElementById(`button-${id}`)
    button.hidden = !button.hidden;

}