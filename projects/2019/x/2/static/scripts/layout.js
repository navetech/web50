// Session user
let sessionUserId;

// Variables for real-time communication with server
const socket = connectToServer();
let room = null;



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



// Parent class for items (users, channels, messages, files) on a page section
class PageSectionItems {
    constructor(itemsSelector, templateItem, templateItemContent, noItemsSelector, templateItemNone) {
        // Attributes
        this.itemsSelector = itemsSelector;
        this.templateItem = templateItem;
        this.templateItemContent = templateItemContent;
        this.noItemsSelector = noItemsSelector;
        this.templateItemNone = templateItemNone;

        this.itemsCount = 0;

        // Methods
        this.putNoItems = putNoItems;
        this.removeItem = removeItem;
    }


    putItems(items) {
        // Zero number of items on page
        this.itemsCount = 0;
    
        // Clear page section
        document.querySelector(this.itemsSelector).innerHTML = '';
    
        // Add each item to page
        const itemShowHide = 'item-hide';
        items.reverse().forEach(item => {
            this.appendItem(item, itemShowHide);
        });
    }
    

    putContext(context) {
        // Generate HTML from template
        const content = this.templateItem(context);
    
        // Add HTML to page section
        const oldContent = document.querySelector(this.itemsSelector).innerHTML
        document.querySelector(this.itemsSelector).innerHTML = content + oldContent;
    
        // Increment number of items on page
        this.itemsCount++;
    }
   
}


function putNoItems(itemShowHide) {
    // Generate HTML from template
    const context = {
        item_show_hide: itemShowHide
    }
    const content = this.templateItemNone(context);
 
    // Add HTML to page section
    document.querySelector(this.noItemsSelector).innerHTML = content;

    // Zero number of items on page
    this.itemsCount = 0;
}


function removeItem(itemRemoveSelector, itemNullSelector) {
    // Remove item from page
    const elemRemove = document.querySelector(itemRemoveSelector);

    // Show animation for removing the item
    if (elemRemove) {
        elemRemove.addEventListener('animationend', () =>  {
            elemRemove.remove();
            this.itemsCount--;

            // If no more items on page
            if ((this.itemsCount < 1) &&
                itemNullSelector && (document.querySelector(itemNullSelector) == null)) {
                // Add no items info on page
                const itemShowHide = 'item-show';
                this.putNoItems(itemShowHide);

                // Show animation for adding the no items info
                const itemAddSelector = itemNullSelector;
                addItemElement(itemAddSelector);
            }
        });
        elemRemove.style.animationPlayState = 'running';
    }
}


function createItemElement(itemAddSelector, itemRemoveSelector) {
    // Show animation for adding the item
    const elemAdd = document.querySelector(itemAddSelector);
    if (elemAdd) {
        elemAdd.addEventListener('animationend', () =>  {
            elemAdd.style.animationPlayState = 'paused';
            const classOld = elemAdd.getAttribute("class");
            const classNew = classOld.replace("item-show", "item-hide");
            elemAdd.setAttribute("class", classNew);

            // Show animation for removing the no items info, if it exists
            const elemRemove = document.querySelector(itemRemoveSelector);
            if (elemRemove) {
                elemRemove.addEventListener('animationend', () =>  {
                    elemRemove.remove();
                });
                elemRemove.style.animationPlayState = 'running';
            }
        });
        elemAdd.style.animationPlayState = 'running';
    }
}


function addItemElement(itemAddSelector) {
    const elemAdd = document.querySelector(itemAddSelector);
    if (elemAdd) {
        elemAdd.addEventListener('animationend', () =>  {
            elemAdd.style.animationPlayState = 'paused';
            const classOld = elemAdd.getAttribute("class");
            const classNew = classOld.replace("item-show", "item-hide");
            elemAdd.setAttribute("class", classNew);
        });
        elemAdd.style.animationPlayState = 'running';
    }
}




