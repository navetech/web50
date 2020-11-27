// Items (messages) on page
let pageItems;



// Parent class for communicator (user, channel) item on a page
class CommunicatorItem {
    constructor(itemSelector, templateItem) {
        // Attributes
        this.itemSelector = itemSelector;
        this.templateItem = templateItem;


        // Methods
    }


    putItem(context) {
        const content = this.templateItem(context);
        document.querySelector(this.itemSelector).innerHTML = content;
    }
}


// Class for messages items on a page
class MessagesItems extends PageSectionItems {
    constructor(templateMessage) {
        // Set elements selectors
        const messagesSelector = '#messages';
        const noMessagesSelector = '#messages';

        // Set templates
        const templateMessageNone = Handlebars.compile(document.querySelector('#message-none').innerHTML);

        // Clear template for item contents
        //   because, for messages, it is included in template for item
        const templateMessageContent = null;
        
        super(messagesSelector, templateMessage, templateMessageContent, noMessagesSelector, templateMessageNone);

        // Attributes

        // Methods
    }


    putItems(messages) {
        // If there are no messages
        if (messages.length <= 0) {
            // Put no messages info on page
            const itemShowHide = 'item-hide';
            this.putNoItems(itemShowHide);
        }
        // If there are messages
        else {
            // Show messages items
            super.putItems(messages);
        }
    }


    appendItem(message, itemShowHide) {
        // Generate HTML from template
        let userIsSender = false;
        if (message.sender.id === sessionUserId) {
            userIsSender = true;
        }
    
        let receiverIsChannel = false;
        let receiverIsUser = false;
        if (message.receiver.type === 'channel') {
            receiverIsChannel = true;
        }
        else if (message.receiver.type === 'user') {
            receiverIsUser = true;
        }
    
        const rows_number = calculateRowsNumber(message.text);
    
        message.timestamp = convertToLocaleString(message.timestamp);
    
        const context = {
            message: message,
            user_is_sender: userIsSender,
            receiver_is_channel: receiverIsChannel,
            receiver_is_user: receiverIsUser,
            rows_number: rows_number,
            item_show_hide: itemShowHide
        }
    
        // Append logged in item
        super.putContext(context);
    
        // Put message files
        const filesSelector = `#message${message.id}-files`;
        const templateFile = Handlebars.compile(document.querySelector('#message-file').innerHTML);
        this.files = new FilesItems(filesSelector, templateFile);
        this.files.putItems(message.files);
    }
    }


function calculateRowsNumber(text) {
    const rn1 = Math.floor((text.length - 1) / 80) + 1;
    const rn2 = (text.match(/\n/g) || []).length + 1;
    const rn = Math.max(rn1, rn2);
    const rows_number = Math.min(rn, 5);
    return rows_number;
}


// Class for files items on a page section
class FilesItems extends PageSectionItems {
    constructor(filesSelector, templateFile) {
        // Set elements selectors
        const noFilesSelector = null;

        // Set templates
        const templateFileNone = null;

        // Clear template for item contents
        //   because, for files, it is included in template for item
        const templateFileContent = null;
        
        super(filesSelector, templateFile, templateFileContent, noFilesSelector, templateFileNone);

        // Attributes

        // Methods
    }


    appendItem(file, itemShowHide) {
        // Convert time info to local time
        file.timestamp = convertToLocaleString(file.timestamp);
    
        // Generate HTML from template
        const context = {
            file: file
        }
    
        // Append file item
        super.putContext(context);
    }
    }


// On event: send message
socket.on('send message', message => {
    // Add message to page
    const itemShowHide = 'item-show';
    pageItems.appendItem(message, itemShowHide);

    // Show animation for creating the message
    const itemAddSelector = `#message${message.id}`;
    const itemRemoveSelector = `#message-null`;
    createItemElement(itemAddSelector, itemRemoveSelector);
});


// On event: remove message
socket.on('remove message', message => {
    // Remove message from page
    const itemRemoveSelector = `#message${message.id}`;
    const itemNullSelector = '#message-null';
    pageItems.removeItem(itemRemoveSelector, itemNullSelector);
});
