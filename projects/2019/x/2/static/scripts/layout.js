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
    constructor(itemsElemSelector, template_item, template_item_content, noItemsElemSelector, template_item_none) {
        // Attributes
        this.itemsElemSelector = itemsElemSelector;
        this.template_item = template_item;
        this.template_item_content = template_item_content;
        this.noItemsElemSelector = noItemsElemSelector;
        this.template_item_none = template_item_none;

        this.items_count = 0;

        // Methods
        this.show = showItems;
        this.putNo = putNoItems;
        this.append = appendItem;
        this.remove = removeItem;
    }
}


function showItems(items) {
    // Zero number of items on page
    this.items_count = 0;

    // Clear page section
    document.querySelector(this.itemsElemSelector).innerHTML = '';

    // Add each user to page
    const item_show_hide = 'item-hide';
    items.reverse().forEach(item => {
        this.append(item, item_show_hide);
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

    // Zero number of items on page
    this.items_count = 0;
}


function appendItem(context) {
    // Generate HTML from template
    const content = this.template_item(context);

    // Add HTML to page section
    const old_content = document.querySelector(this.itemsElemSelector).innerHTML
    document.querySelector(itemsElemSelector).innerHTML = content + old_content;

    // Increment number of items on page
    this.items_count++;
}


function removeItem(id_elem_remove, id_elem_item_null) {
    // Remove item from page
    const elem_remove = document.querySelector(id_elem_remove);

    // Show animation for removing the item
    if (elem_remove) {
        elem_remove.addEventListener('animationend', () =>  {
            elem_remove.remove();
            this.items_count--;

            // If no more items on page
            if ((this.items_count < 1) &&
                (document.querySelector(id_elem_item_null) == null)) {
                
                // Add no items info on page
                const item_show_hide = 'item-show';
                this.putNo(item_show_hide);

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
}


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


