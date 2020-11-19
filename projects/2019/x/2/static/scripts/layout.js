let session_user_id;

const socket = connectToServer();

let room = null;
let page = null;
let idCommunicator = null;



function convertToLocaleString(timestamp) {
    const locales = window.navigator.language;
    const options = {dateStyle: 'full', timeStyle: 'full'};

    const d = new Date(timestamp);
    return d.toLocaleString(locales, options);
}


function connectToServer() {
    // Connect to websocket
    const url = location.protocol + '//' + document.domain + ':' + location.port;
    const url2 = window.location;
    s = io.connect(url);
    return s;
}


function joinRoom(page_, idCommunicator_) {
    if (!page_) {
        return;
    }

    let room_;
    if ((idCommunicator_ != null) && (idCommunicator_ != undefined) && (idCommunicator_ >= 0)) {
        room_ = `${page_} ${idCommunicator_}`;
    }
    else {
        room_ = `${page_}`;
    }
    const data = {'room': room_};
    socket.emit('join', data);
}


socket.on('connect', () => {
    room = null;
});


socket.on('joined', data => {
    room = data['room'];
});



// Parent class for items (users, channels, messages) on a page
class PageItems {
    constructor(itemsElemSelector, template_item, noItemsElemSelector, template_item_none) {
        // Attributes
        this.itemsElemSelector = itemsElemSelector;
        this.template_item = template_item;
        this.noItemsElemSelector = noItemsElemSelector;
        this.template_item_none = template_item_none;

        this.items_count = 0;

        // Methods
        this.show = showItems;
    }
}


function showItems(items) {
    // Clear page section
    document.querySelector(this.itemsElemSelector).innerHTML = '';

    // Add each user to page
    const item_show_hide = 'item-hide';
    items.reverse().forEach(item => {
        this.appendItem(item, item_show_hide);
    });
}

function putNoItems(item_show_hide) {
    // Generate HTML from template
    const context = {
        item_show_hide: item_show_hide
    }
    const content = this.template_item_none(context);
 
    // Add HTML to page section
    document.querySelector(this.noItemsElemSelector).innerHTML = content;
}


