// Parent class for communicator (user, channel) item on a page
class CommunicatorItem {
    constructor(template_item, itemsElemSelector) {
        // Attributes
        this.template_item = template_item;
        this.itemsElemSelector = itemsElemSelector;


        // Methods
        this.show = showCommunicator;
    }
}


function showCommunicator(context) {
    const content = this.template_item(context);
    document.querySelector(this.itemsElemSelector).innerHTML = content;
}



let template_message_file;
let template_message_none;


function setTemplatesMessages() {
    template_message_file = Handlebars.compile(document.querySelector('#message-file').innerHTML);
    template_message_none = Handlebars.compile(document.querySelector('#message-none').innerHTML);
}


function showMessages(messages) {
    items_count = 0;
    document.querySelector('#messages').innerHTML = '';

    const item_show_hide = 'item-hide';
    if (messages.length > 0) {
        messages.reverse().forEach(message => {
            addMessage(message, item_show_hide);
        });
    }
    else {
        const context = {
            item_show_hide: item_show_hide
        }
        const content = template_message_none(context);
        document.querySelector('#messages').innerHTML = content;
    }
}


function addMessage(message, item_show_hide) {
    let user_is_sender = false;
    if (message.sender.id === session_user_id) {
        user_is_sender = true;
    }

    let receiver_is_channel = false;
    let receiver_is_user = false;
    if (message.receiver.type === 'channel') {
        receiver_is_channel = true;
    }
    else if (message.receiver.type === 'user') {
        receiver_is_user = true;
    }

    const rows_number = calculateRowsNumber(message.text);

    message.timestamp = convertToLocaleString(message.timestamp);

    const context = {
        message: message,
        user_is_sender: user_is_sender,
        receiver_is_channel: receiver_is_channel,
        receiver_is_user: receiver_is_user,
        rows_number: rows_number,
        item_show_hide: item_show_hide
    }

    const content = template_item(context);
    const old_content = document.querySelector('#messages').innerHTML
    document.querySelector('#messages').innerHTML = content + old_content;

    showMessageFiles(message);

    items_count++;
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


// When a message is sent to a channel, add message
socket.on('send message', message => {
    const item_show_hide = 'item-show';
    addMessage(message, item_show_hide);

    const id_elem_add = `#message${message.id}`;
    const elem_add = document.querySelector(id_elem_add);

    elem_add.addEventListener('animationend', () =>  {
        elem_add.style.animationPlayState = 'paused';
        let class_old = elem_add.getAttribute("class");
        let class_new = class_old.replace("item-show", "item-hide");
        elem_add.setAttribute("class", class_new);

        const id_elem_remove = `#message-null`;
        const elem_remove = document.querySelector(id_elem_remove);

        if (elem_remove) {
            elem_remove.addEventListener('animationend', () =>  {
                elem_remove.remove();
            });
            elem_remove.style.animationPlayState = 'running';
        }
    });
    elem_add.style.animationPlayState = 'running';
});


// When a channel is removed, remove channel
socket.on('remove message', message => {
    const id_elem_remove = `#message${message.id}`;
    const elem_remove = document.querySelector(id_elem_remove);

    if (elem_remove) {
        elem_remove.addEventListener('animationend', () =>  {
            elem_remove.remove();

            items_count--;
            if ((items_count < 1) &&
                (document.querySelector(`#message-null`) == null)) {
                const context = {
                    item_show_hide: 'item-show'
                }
                const content = template_message_none(context);
                const old_content = document.querySelector('#messages').innerHTML;
                document.querySelector('#messages').innerHTML = content + old_content;
        
                const id_elem_add = '#message-null';
                const elem_add = document.querySelector(id_elem_add);
        
                elem_add.addEventListener('animationend', () =>  {
                    elem_add.style.animationPlayState = 'paused';
                    let class_old = elem_add.getAttribute("class");
                    let class_new = class_old.replace("item-show", "item-hide");
                    elem_add.setAttribute("class", class_new);
                });
                elem_add.style.animationPlayState = 'running';
            }
        });
        elem_remove.style.animationPlayState = 'running';
    }
});
