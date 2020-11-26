// On page loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize new request
    const elem = document.querySelector('#channel-id');
    const idCommunicator = elem.dataset.id;
    const request = new XMLHttpRequest();
    request.open('GET', `/api/channel-messages/${idCommunicator}`);

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);

        // Get session user
        sessionUserId = data.session_user_id;

        // Set elements selectors

        // Set templates
        const templateChannelMessage = Handlebars.compile(document.querySelector('#channel-message').innerHTML);

        // Instatiate page items objects
        const channelItem = new ChannelItem();
        pageItems = new MessagesItems(templateChannelMessage);

        // Show items on page
        channelItem.putItem(data.channel);
        pageItems.putItems(data.messages);

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
        const channelSelector = '#channel-id';
        const templateChannel = Handlebars.compile(document.querySelector('#channel').innerHTML);
        
        super(channelSelector, templateChannel);

        // Attributes


        // Methods
    }


    putItem(channel) {
        // Clear page section
        document.querySelector(this.itemSelector).innerHTML = '';
    
        if (channel) {
            // Convert time info to local time
            channel.timestamp = convertToLocaleString(channel.timestamp);
        
            // Generate HTML from template
            const context = {
                channel: channel
            }
    
            // show channel item
            super.putItem(context);
        }
    }
}

