// Items (channels) on page
let pageItems;



// On page loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize new request
    const request = new XMLHttpRequest();
    request.open('GET', '/api/channels');

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);

        // Get session user
        sessionUserId = data.session_user_id;

        // Instatiate page items object
        pageItems = new ChannelsItems();

        // Put channels on page
        pageItems.putItems(data.channels);

        // Join room for real-time communication with server
        const page = 'channels';
        const idCommunicator = null;
        joinRoom(page, idCommunicator);
    }
    // Send request
    request.send();
});


// Class for channel items on a page
class ChannelsItems extends PageSectionItems {
    constructor() {
        // Set elements selectors
        const channelsSelector = '#channels';
        const noChannelsSelector = '#channels';

        // Set templates
        const templateChannel = Handlebars.compile(document.querySelector('#channel').innerHTML);
        const templateChannelNone = Handlebars.compile(document.querySelector('#channel-none').innerHTML);

        // Clear template for item contents
        //   because, for channels, it is included in template for item
        const templateChannelContent = null;
        
        super(channelsSelector, templateChannel, templateChannelContent, noChannelsSelector, templateChannelNone);

        // Attributes

        // Methods
    }


    appendItem(channel, itemShowHide) {
        // Convert time info to local time
        channel.timestamp = convertToLocaleString(channel.timestamp);
    
        // Generate HTML from template
        const context = {
            channel: channel,
            item_show_hide: itemShowHide
        }
    
        // Append channel item
        super.putContext(context);
    }


    putItems(channels) {
        // If there are no channels
        if (channels.length <= 0) {
            // Put no channels info on page
            const itemShowHide = 'item-hide';
            this.putNoItems(itemShowHide);
        }
        // If there are channels
        else {
            // Show channels items
            super.putItems(channels);
        }
    }
}


// On event: create channel
socket.on('create channel', channel => {
    // Add channel to page
    const itemShowHide = 'item-show';
    pageItems.appendItem(channel, itemShowHide);

    // Show animation for creating the channel
    const itemAddSelector = `#channel${channel.id}`;
    const itemRemoveSelector = `#channel-null`;
    createItemElement(itemAddSelector, itemRemoveSelector);
});


// On event: remove channel
socket.on('remove channel', channel => {
    // Remove channel from page
    const itemRemoveSelector = `#channel${channel.id}`;
    const itemNullSelector = '#channel-null';
    pageItems.removeItem(itemRemoveSelector, itemNullSelector);
});
