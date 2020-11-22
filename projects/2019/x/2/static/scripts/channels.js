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
        session_user_id = data.session_user_id;

        // Set elements selectors
        const itemsElemSelector = '#channels';
        const noItemsElemSelector = '#channels';

        // Set templates
        const template_channel = Handlebars.compile(document.querySelector('#channel').innerHTML);
        const template_channel_none = Handlebars.compile(document.querySelector('#channel-none').innerHTML);

        // Instatiate page items object
        const pageItems = new ChannelPageItems(itemsElemSelector, template_channel, noItemsElemSelector, template_channel_none);

        // Show channels on page
        pageItems.show(data.channels);

        // Join room for real-time communication with server
        page = 'channels';
        idCommunicator = null;
        joinRoom(page, idCommunicator);
    }
    // Send request
    request.send();
});


// Class for channel items on a page
class ChannelPageItems extends PageItems {
    constructor(itemsElemSelector, template_item, noItemsElemSelector, template_item_none) {
        // Clear template for items contents
        //   because, for channels, it is included in template for items
        const template_item_content = null;
        
        super(itemsElemSelector, template_item, template_item_content, noItemsElemSelector, template_item_none);

        // Attributes

        // Methods
        this.show = showChannels;
        this.append = appendChannel;
    }
}


function showChannels(channels) {
    // If there are no channels
    if (channels.length <= 0) {
        // Put no channels info on page
        const item_show_hide = 'item-hide';
        this.putNo(item_show_hide);
    }
    // If there are channels
    else {
        // Show channels items
        super.show(channels);
    }
}


function appendChannel(channel, item_show_hide) {
    // Convert time info to local time
    channel.timestamp = convertToLocaleString(channel.timestamp);

    // Generate HTML from template
    const context = {
        channel: channel,
        item_show_hide: item_show_hide
    }

    // Append channel item
    super.append(context);
}


// On event: create channel
socket.on('create channel', channel => {
    // Add channel to page
    const item_show_hide = 'item-show';
    pageItems.append(channel, item_show_hide);

    // Show animation for creating the channel
    const id_elem_add = `#channel${channel.id}`;
    const id_elem_remove = `#channel-null`;
    showAnimationCreateItem(id_elem_add, id_elem_remove);
});


// On event: remove channel
socket.on('remove channel', channel => {
    // Remove channel from page
    const id_elem_remove = `#channel${channel.id}`;
    const id_elem_item_null = '#channel-null';
    pageItems.remove(id_elem_remove, id_elem_item_null);
});
