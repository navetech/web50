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
        showMessages(data.messages);

        // Join room for real-time communication with server
        page = 'messages received by channel';
        joinRoom(page, idCommunicator);
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

