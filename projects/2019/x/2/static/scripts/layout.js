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
    constructor(elemIdItems, template_item, template_item_none) {
        // Attributes
        this.template_item = template_item;
        this.template_item_none = template_item_none;

        this.items_count = 0;

        // Methods
        this.show = showItems;
    }
}


function showItems(items) {
    // Clear list of items on page
    document.querySelector(this.elemIdItems).innerHTML = '';

    // Zero number of items on page
    this.items_count = 0;

    // If there are no items
    if (items.length <= 0) {
        // Put no items info on page
        const item_show_hide = 'item-hide';
        this.putNoItemsInfo(item_show_hide);
    }
    // If there are items
    else {
        // Append each item to page
        const item_show_hide = 'item-hide';
        items.reverse().forEach(items => {
            appendItem(item, item_show_hide);
        });
    }
}


