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
        super(itemsElemSelector, template_item, noItemsElemSelector, template_item_none);

        // Attributes

        // Methods
        this.show = showChannels;
    }
}


function showChannels(channels) {
    // Zero number of channels on page
    items_count = 0;

    // If there are no channels
    if (channels.length <= 0) {
        // Put no channels info on page
        const item_show_hide = 'item-hide';
        this.putNoItems(item_show_hide);
    }
    // If there are channels
    else {
        // Show channels items
        super.show(channels);
    }
}


function addChannel(channel, item_show_hide) {
    // Convert time info to local time
    channel.timestamp = convertToLocaleString(channel.timestamp);

    // Generate HTML from template
    const context = {
        channel: channel,
        item_show_hide: item_show_hide
    }
    const content = template_channel(context);

    // Add HTML to page section
    const old_content = document.querySelector('#channels').innerHTML
    document.querySelector('#channels').innerHTML = content + old_content;

    // Increment number of channels on page
    channels_count++;
}


// On event: create channel
socket.on('create channel', channel => {
    // Add channel to page
    const item_show_hide = 'item-show';
    addChannel(channel, item_show_hide);

    // Show animation for creating the channel
    const id_elem_add = `#channel${channel.id}`;
    const id_elem_remove = `#channel-null`;
    showAnimationCreateItem(id_elem_add, id_elem_remove);
});

function showAnimationCreateItem(id_elem_add, id_elem_remove) {
    // Show animation for adding the item
    const elem_add = document.querySelector(id_elem_add);
    elem_add.addEventListener('animationend', () =>  {
        elem_add.style.animationPlayState = 'paused';
        let class_old = elem_add.getAttribute("class");
        let class_new = class_old.replace("item-show", "item-hide");
        elem_add.setAttribute("class", class_new);

        // Show animation for removing the no items info, if it exists
        const elem_remove = document.querySelector(id_elem_remove);
        if (elem_remove) {
            elem_remove.addEventListener('animationend', () =>  {
                elem_remove.remove();
            });
            elem_remove.style.animationPlayState = 'running';
        }
    });
    elem_add.style.animationPlayState = 'running';
}


// On event: remove channel
socket.on('remove channel', channel => {
    // Remove channel from page
    const id_elem_remove = `#channel${channel.id}`;
    const items_count = channels_count;
    const id_elem_item_null = '#channel-null';
    const addNoItemsInfo = addNoChannelsInfo;
    channels_count =  removeItem(id_elem_remove, items_count, id_elem_item_null, addNoItemsInfo);
});


function removeItem(id_elem_remove, items_count, id_elem_item_null, addNoItemsInfo) {
    // Remove item from page
    const elem_remove = document.querySelector(id_elem_remove);

    // Show animation for removing the item
    if (elem_remove) {
        elem_remove.addEventListener('animationend', () =>  {
            elem_remove.remove();
            items_count--;

            // If no more items on page
            if ((items_count < 1) &&
                (document.querySelector(id_elem_item_null) == null)) {
                
                // Add no items info on page
                const item_show_hide = 'item-show';
                addNoItemsInfo(item_show_hide);

                // Show animation for adding the no items info
                const id_elem_add = id_elem_item_null;
                const elem_add = document.querySelector(id_elem_add);
                elem_add.addEventListener('animationend', () =>  {
                    elem_add.style.animationPlayState = 'paused';
                    let class_old = elem_add.getAttribute("class");
                    let class_new = class_old.replace("item-show", "item-hide");
                    elem_add.setAttribute("class", class_new);
                });
                elem_add.style.animationPlayState = 'running';
            }
        });
        elem_remove.style.animationPlayState = 'running';
    }
    return items_count;
}
