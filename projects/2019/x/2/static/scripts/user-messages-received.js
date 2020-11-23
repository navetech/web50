// On page loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize new request
    const elem = document.querySelector('#user-id');
    const idCommunicator = elem.dataset.id;
    const request = new XMLHttpRequest();
    request.open('GET', `/api/user-messages-received/${idCommunicator}`);

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);

        // Get session user
        session_user_id = data.session_user_id;

        // Set elements selectors

        // Set templates
        const template_user_message_received = Handlebars.compile(document.querySelector('#user-message-received').innerHTML);

        // Instatiate page items objects
        const userItem = new UserItem();
        const messagesItems = new MessagesPageItems(template_user_message_received);

        // Show items on page
        userItem.show(data.user);
        messagesItems.show(data.messages);

        // Join room for real-time communication with server
        page = 'messages received by user';
        joinRoom(page, idCommunicator);
    }
    // Send request
    request.send();
});
