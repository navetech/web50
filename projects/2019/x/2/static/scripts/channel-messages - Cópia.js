let template_channel;
let template_item;

document.addEventListener('DOMContentLoaded', () => {
    template_channel = Handlebars.compile(document.querySelector('#channel').innerHTML);
    template_item = Handlebars.compile(document.querySelector('#channel-message').innerHTML);
    setTemplatesMessages();

    // Initialize new request
    const elem = document.querySelector('#channel-id');
    const id = elem.dataset.id;
    const request = new XMLHttpRequest();
    request.open('GET', `/api/channel-messages/${id}`);

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);
        session_user_id = data.session_user_id;
        showChannel(data.channel);
        showChannelMessages(data.messages);
    }
    // Send request
    request.send();
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
    document.querySelector('#messages').innerHTML = '';

    if (messages.length > 0) {
        messages.reverse().forEach(message => {
            addChannelMessage(message);
        });
    }
    else {
        const content = template_item_none();
        document.querySelector('#messages').innerHTML = content;
    }
}


function addChannelMessage(message) {
    let user_is_sender = false;
    if (message.sender.id === session_user_id) {
        user_is_sender = true;
    }

    const rows_number = calculateRowsNumber(message.text);

    message.timestamp = convertToLocaleString(message.timestamp);

    const context = {
        message: message,
        user_is_sender: user_is_sender,
        rows_number: rows_number
    }

    const content = template_item(context);
    const old_content = document.querySelector('#messages').innerHTML
    document.querySelector('#messages').innerHTML = content + old_content;

    showMessageFiles(message);
}

