let template_item;


document.addEventListener('DOMContentLoaded', () => {
    template_item = Handlebars.compile(document.querySelector('#user-message-sent').innerHTML);
    setTemplatesMessagesUsers();

    // Initialize new request
    const elem = document.querySelector('#user-id');
    const idCommunicator = elem.dataset.id;
    const request = new XMLHttpRequest();
    request.open('GET', `/api/user-messages-sent/${idCommunicator}`);

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);
        session_user_id = data.session_user_id;
        showUser(data.user);
        showUserMessagesSent(data.messages);

        // Join room for real-time communication with server
        page = 'messages sent user';
        joinRoom(page, idCommunicator);
    }
    // Send request
    request.send();
});


function showUserMessagesSent(messages) {
    document.querySelector('#messages').innerHTML = '';

    if (messages.length > 0) {
        messages.reverse().forEach(message => {
            addUserMessageSent(message);
        });
    }
    else {
        const content = template_item_none();
        document.querySelector('#messages').innerHTML = content;
    }
}


function addUserMessageSent(message) {
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
        receiver_is_channel: receiver_is_channel,
        receiver_is_user: receiver_is_user,
        rows_number: rows_number
    }

    const content = template_item(context);
    const old_content = document.querySelector('#messages').innerHTML
    document.querySelector('#messages').innerHTML = content + old_content;

    showMessageFiles(message);
}


