let template_message_file;
let template_item_none;

function setTemplatesMessages() {
    template_message_file = Handlebars.compile(document.querySelector('#message-file').innerHTML);
    template_item_none = Handlebars.compile(document.querySelector('#message-none').innerHTML);
}

function calculateRowsNumber(text) {
    const rn1 = Math.floor((text.length - 1) / 80) + 1;
    const rn2 = (text.match(/\n/g) || []).length + 1;
    const rn = Math.max(rn1, rn2);
    const rows_number = Math.min(rn, 5);
    return rows_number;
}

function showMessageFiles(message) {
    const id_elem = `#message${message.id}-files`;
    document.querySelector(id_elem).innerHTML = '';

    message.files.reverse().forEach(file => {
        addMessageFile(message, file);
    });
}

function addMessageFile(message, file) {
    file.timestamp = convertToLocaleString(file.timestamp);

    const context = {
        file: file
    }

    const content = template_message_file(context);
    const id_elem = `#message${message.id}-files`;
    const old_content = document.querySelector(id_elem).innerHTML
    document.querySelector(id_elem).innerHTML = content + old_content;
}



