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


// Class for messages items on a page
class MessagesPageItems extends PageItems {
    constructor(itemsElemSelector, template_message, noItemsElemSelector, template_item_none) {
        const itemsElemSelector = '#messages';
        const noItemsElemSelector = '#messages';
        const template_message_file = Handlebars.compile(document.querySelector('#message-file').innerHTML);
        const template_message_none = Handlebars.compile(document.querySelector('#message-none').innerHTML);
        
        // Clear template for items contents
        //   because, for messages, it is included in template for items
        const template_item_content = null;
        
        super(itemsElemSelector, template_message, template_item_content, noItemsElemSelector, template_message_none);

        // Attributes
        this.files = new FilesPageItems(template_message_file);

        // Methods
        this.show = showMessages;
        this.append = appendMessage;
    }
}


// Class for files items on a page
class FilesPageItems extends PageItems {
    constructor(itemsElemSelector, template_message, noItemsElemSelector, template_item_none) {
        const itemsElemSelector = '#messages';
        const noItemsElemSelector = '#messages';
        const template_message_file = Handlebars.compile(document.querySelector('#message-file').innerHTML);
        const template_message_none = Handlebars.compile(document.querySelector('#message-none').innerHTML);
        
        // Clear template for items contents
        //   because, for messages, it is included in template for items
        const template_item_content = null;
        
        super(itemsElemSelector, template_message, template_item_content, noItemsElemSelector, template_message_none);

        // Attributes

        // Methods
        this.append = appendFile;
    }
}


function showMessages(messages) {
    // If there are no messages
    if (messages.length <= 0) {
        // Put no messages info on page
        const item_show_hide = 'item-hide';
        this.putNo(item_show_hide);
    }
    // If there are messages
    else {
        // Show messages items
        super.show(messages);
    }
}


function appendMessage(message, item_show_hide) {
    // Generate HTML from template
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

    // Append logged in item
    super.append(context);

    // Put message files
    this.files.itemsElemSelector = `#message${message.id}-files`;
    this.files.show(message.files);
}


function calculateRowsNumber(text) {
    const rn1 = Math.floor((text.length - 1) / 80) + 1;
    const rn2 = (text.match(/\n/g) || []).length + 1;
    const rn = Math.max(rn1, rn2);
    const rows_number = Math.min(rn, 5);
    return rows_number;
}


function appendFile(file, item_show_hide) {
    // Convert time info to local time
    file.timestamp = convertToLocaleString(file.timestamp);

    // Generate HTML from template
    const context = {
        file: file
    }

    // Append file item
    super.append(context);
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
