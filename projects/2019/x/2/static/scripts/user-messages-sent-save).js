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
        showMessages(data.messages);

        // Join room for real-time communication with server
        page = 'messages sent by user';
        joinRoom(page, idCommunicator);
    }
    // Send request
    request.send();
});
