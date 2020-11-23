// On page loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize new request
    const elem = document.querySelector('#channel-id');
    idCommunicator = elem.dataset.id;
    const request = new XMLHttpRequest();
    request.open('GET', `/api/channel-messages/${idCommunicator}`);

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);

        // Get session user
        session_user_id = data.session_user_id;

        // Set elements selectors

        // Set templates
        const template_channel_message = Handlebars.compile(document.querySelector('#channel-message').innerHTML);

        // Instatiate page items objects
        const channelItem = new ChannelItem();
        const messagesItems = new MessagesPageItems(template_channel_message);

        // Show items on page
        channelItem.show(data.channel);
        messagesItems.show(data.messages);

        // Join room for real-time communication with server
        page = 'messages received by channel';
        joinRoom(page, idCommunicator);
    }
    // Send request
    request.send();
});


// Class for channel item on a page
class ChannelItem extends CommunicatorItem {
    constructor() {
        const template_channel = Handlebars.compile(document.querySelector('#channel').innerHTML);
        const channelElemSelector = '#channel-id';
        
        super(template_channel, channelElemSelector);

        // Attributes


        // Methods
        this.show = showChannel;
    }
}


function showChannel(channel) {
    // Clear page section
    document.querySelector(this.itemsElemSelector).innerHTML = '';

    if (channel) {
        // Convert time info to local time
        channel.timestamp = convertToLocaleString(channel.timestamp);
    
        // Generate HTML from template
        const context = {
            channel: channel
        }

        // show channel item
        super.show(context);
    }
}

