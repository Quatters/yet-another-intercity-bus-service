function selectTicket(ticket) {
    ticket.selected = !ticket.selected;
    if (ticket.selected) {
        ticket.classList.remove('btn-primary');
        ticket.classList.add('btn-success');
    } else {
        ticket.classList.add('btn-primary');
        ticket.classList.remove('btn-success');
    }
    for (const input of Array.from(document.querySelector('#id_ticket').querySelectorAll('option'))) {
        if (input.innerText === ticket.innerText) {
            input.selected = !input.selected;
        }
    }
}
