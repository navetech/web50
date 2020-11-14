let items_count = 0;

let template_channel;
let template_item;


document.addEventListener('DOMContentLoaded', () => {
    items_count = document.querySelectorAll(".message-item").length;

    template_channel = Handlebars.compile(document.querySelector('#channel').innerHTML);
    template_item = Handlebars.compile(document.querySelector('#channel-message').innerHTML);
    setTemplatesMessages();

    // Initialize new request
    const elem = document.querySelector('#channel-id');
    idCommunicator = elem.dataset.id;
    const request = new XMLHttpRequest();
    request.open('GET', `/api/channel-messages/${idCommunicator}`);

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);
        session_user_id = data.session_user_id;
        showChannel(data.channel);
        showChannelMessages(data.messages);

        // Join room for real-time communication with server
        page = 'messages channel';
        joinRoom(page, idCommunicator);
    }
    // Send request
    request.send();
});


// When a message is sent to a channel, add message
socket.on('send message to channel', message => {
    const item_show_hide = 'item-show';
    addChannelMessage(message, item_show_hide);

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
                        const content = template_item_none(context);
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
});


function showChannel(channel) {
    document.querySelector('#channel-id').innerHTML = '';

    if (channel) {
        channel.timestamp = convertToLocaleString(channel.timestamp);
    
        const context = {
            channel: channel
        }
    
        const content = template_channel(context);
        document.querySelector('#channel-id').innerHTML = content;
    }
}

function showChannelMessages(messages) {
    items_count = 0;
    document.querySelector('#messages').innerHTML = '';

    const item_show_hide = 'item-hide';
    if (messages.length > 0) {
        messages.reverse().forEach(message => {
            addChannelMessage(message, item_show_hide);
        });
    }
    else {
        const context = {
            item_show_hide: item_show_hide
        }
        const content = template_item_none(context);
        document.querySelector('#messages').innerHTML = content;
    }
}


function addChannelMessage(message, item_show_hide) {
    let user_is_sender = false;
    if (message.sender.id === session_user_id) {
        user_is_sender = true;
    }

    const rows_number = calculateRowsNumber(message.text);

    message.timestamp = convertToLocaleString(message.timestamp);

    const context = {
        message: message,
        user_is_sender: user_is_sender,
        rows_number: rows_number,
        item_show_hide: item_show_hide
    }

    const content = template_item(context);
    const old_content = document.querySelector('#messages').innerHTML
    document.querySelector('#messages').innerHTML = content + old_content;

    showMessageFiles(message);

    items_count++;
}

