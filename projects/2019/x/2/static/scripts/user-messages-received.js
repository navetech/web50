let template_item;


document.addEventListener('DOMContentLoaded', () => {
    template_item = Handlebars.compile(document.querySelector('#user-message-received').innerHTML);
    setTemplatesMessagesUsers();

    // Initialize new request
    const elem = document.querySelector('#user-id');
    const id = elem.dataset.id;
    const request = new XMLHttpRequest();
    request.open('GET', `/api/user-messages-received/${id}`);

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);
        session_user_id = data.session_user_id;
        showUser(data.user);
        showUserMessagesReceived(data.messages);
    }
    // Send request
    request.send();
});


function showUserMessagesReceived(messages) {
    document.querySelector('#messages').innerHTML = '';

    if (messages.length > 0) {
        messages.reverse().forEach(message => {
            addUserMessageReceived(message);
        });
    }
    else {
        const content = template_item_none();
        document.querySelector('#messages').innerHTML = content;
    }
}


function addUserMessageReceived(message) {
    const rows_number = calculateRowsNumber(message.text);

    message.timestamp = convertToLocaleString(message.timestamp);

    const context = {
        message: message,
        rows_number: rows_number
    }

    const content = template_item(context);
    const old_content = document.querySelector('#messages').innerHTML
    document.querySelector('#messages').innerHTML = content + old_content;

    showMessageFiles(message);
}


