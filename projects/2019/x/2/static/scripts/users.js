// Items (users) on page
let pageItems;



// On page loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize new request
    const request = new XMLHttpRequest();
    request.open('GET', '/api/users');

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);

        // Get session user
        sessionUserId = data.session_user_id;

        // Instatiate page items object
        pageItems = new UsersItems();

        // Show channels on page
        pageItems.putItems(data.users);
        
        // Join room for real-time communication with server
        const page = 'users';
        const idCommunicator = null;
        joinRoom(page, idCommunicator);
    }
    // Send request
    request.send();
});


// Class for user items on a page
class UsersItems extends PageSectionItems {
    constructor() {
        // Set elements selectors
        const usersSelector = null;
        const noUsersSelector = '#no-users';

        // Set templates
        const templateUser = null;
        const templateUserContent = Handlebars.compile(document.querySelector('#user-content').innerHTML);
        const templateUserNone = Handlebars.compile(document.querySelector('#user-none').innerHTML);

        super(usersSelector, templateUser, templateUserContent, noUsersSelector, templateUserNone);

        // Set elements selectors and templates for users logged in/out
        const noLogsSelector = null;
        const templateLogNone = null;

        // Set elements selectors and templates for users logged in
        const logInsSelector = '#users-loggedin';
        const templateLogIn = Handlebars.compile(document.querySelector('#user-loggedin').innerHTML);

        // Set elements selectors and templates for users logged out
        const logOutsSelector = '#users-loggedout';
        const templateLogOut = Handlebars.compile(document.querySelector('#user-loggedout').innerHTML);

        // Attributes
        this.logIns = new LogInsItems(logInsSelector, templateLogIn, templateUserContent, noLogsSelector, templateLogNone);
        this.logOuts = new LogOutsItems(logOutsSelector, templateLogOut, templateUserContent, noLogsSelector, templateLogNone);

        // Methods
        this.putItems = putUsers;
        this.removeItem = removeUser;
        this.appendItem = appendUser;
    }
}


// Parent class for logged in/out user items on a page
class LogsItems extends PageSectionItems {
    constructor(logsSelector, templateLog,  templateLogContent, noLogsSelector, templateLogNone) {
        super(logsSelector, templateLog,  templateLogContent, noLogsSelector, templateLogNone);

        // Attributes

        // Methods
    }


    appendItem(user, itemShowHide) {
        // Generate HTML from template
        const context = {
            user: user,
            item_show_hide: itemShowHide
        };

        // Append logged in/out item
        super.putContext(context);

        // Put user data contents
        this.putItemContent(user);
    }
}


// Class for logged in user items on a page
class LogInsItems extends LogsItems {
    constructor(logInsSelector, templateLogIn, templateLogInContent, noLogInsSelector, templateLogInNone) {
        super(logInsSelector, templateLogIn, templateLogInContent, noLogInsSelector, templateLogInNone);

        // Attributes

        // Methods
        this.putItemContent = putLogInContent;
        this.insertItem = insertLogIn;
    }
}


// Class for logged out user items on a page
class LogOutsItems extends LogsItems {
    constructor(logOutsSelector, templateLogOut, templateLogOutContent, noLogOutsSelector, templateLogOutNone) {
        super(logOutsSelector, templateLogOut, templateLogOutContent, noLogOutsSelector, templateLogOutNone);

        // Attributes

        // Methods
        this.putItemContent = putLogOutContent;
    }
}


function putUsers(users) {
    // If there are no users (no logged in and no logged out)
    if ((users.loggedin.length <= 0) && (users.loggedout.length <= 0)) {
        // Put no users info on page
        const itemShowHide = 'item-hide';
        this.putNoItems(itemShowHide);
    }
    // If there are users
    else {
        // Clear no users section on page 
        document.querySelector(this.noItemsSelector).innerHTML = '';

        // Show logged in and logged out users items
        this.logIns.putItems(users.loggedin)
        this.logOuts.putItems(users.loggedout)
        this.itemsCount = this.logIns.itemsCount + this.logOuts.itemsCount;
    }
}


function appendUser(user) {
    // Add logged in user to page
    const itemShowHide = 'item-show';
    this.logIns.appendItem(user, itemShowHide);

    this.itemsCount++;

    // Show animation for creating the user
    const itemAddSelector = `#user-loggedin${user.current_logins[0].id}`
    const itemRemoveSelector = `#user-null`;
    createItemElement(itemAddSelector, itemRemoveSelector);
}


function removeUser(user) {
    // Remove logged in user from page
    const itemRemoveSelector = `#user-loggedin${user.current_logins[0].id}`;
    let itemNullSelector;

    this.itemsCount--;
    if (this.itemsCount > 0) {
        itemNullSelector = null;
        this.logIns.noItemsSelector = null;
        this.logIns.templateItemNone = null;
    }
    else {
        itemNullSelector = '#user-null';
        this.logIns.noItemsSelector = '#no-users';
        this.logIns.templateItemNone = Handlebars.compile(document.querySelector('#user-none').innerHTML);
    }
    this.logIns.removeItem(itemRemoveSelector, itemNullSelector);
}


function insertLogIn(insertionAt, user, itemShowHide) {
    // Generate HTML from template
    const context = {
        user: user,
        item_show_hide: itemShowHide
    };
    const content = templateItem(context);

    // Insert HTML at the insertion point of the page section
    const itemSelector = `#user-loggedin${insertionAt.current_login[0].id}`
    const elem = document.querySelector(itemSelector);
    elem.insertAdjacentHTML("afterend", content);

    // Put user data contents
    this.putItemContent(user);

    // Increment number of logged in users on page
    this.itemsCount++;
}


function putLogInContent(user) {
    // Convert time info to local time
    user.timestamp = convertToLocaleString(user.timestamp);
    user.current_logins.forEach(login => {
        login.timestamp = convertToLocaleString(login.timestamp);
    });

    // Generate HTML from template
    const context = {
        user: user
    }
    const content = this.templateItemContent(context);

    // Add HTML to page section
    const itemSelector = `#user-loggedin${user.current_logins[0].id}`
    const elem = document.querySelector(itemSelector)
    elem.innerHTML = content
}


function putLogOutContent(user) {
    // Convert time info to local time
    user.timestamp = convertToLocaleString(user.timestamp);
    user.current_logout.timestamp = convertToLocaleString(user.current_logout.timestamp);

    // Generate HTML from template
    const context = {
        user: user
    }
    const content = this.templateItemContent(context);

    // Add HTML to page section
    const itemSelector = `#user-loggedout${user.current_logout.id}`
    const elem = document.querySelector(itemSelector)
    elem.innerHTML = content
}


// On event: register
socket.on('register', user => {
    // Add user to page
    pageItems.appendItem(user);
});


// On event: unregister
socket.on('unregister', user => {
    // Remove user from page
    pageItems.removeItem(user);
});


// On event login
socket.on('login', user => {
    // Remove user from page section corresponding to if it was logged in or logged out
    let itemRemoveSelector;
    let logItems;
    if (user.current_logins.length > 1) {
        itemRemoveSelector = `#user-loggedin${user.current_logins[1].id}`
        logItems = pageItems.logIns;
    }
    else if (user.current_logins.length === 1) {
        itemRemoveSelector = `#user-loggedout${user.current_logout.id}`
        logItems = pageItems.logOuts;
    }
    else {
        itemRemoveSelector = null;
        logItems = null;
    }
    const elemRemove = document.querySelector(itemRemoveSelector);

    // Show animation for removing the user
    if (elemRemove) {
        elemRemove.addEventListener('animationend', () =>  {
            elemRemove.remove();
            logItems.itemsCount--;

            // Add logged in user to page
            const itemShowHide = 'item-show';
            pageItems.logIns.appendItem(user, itemShowHide);
    
            // Show animation for adding the user
            const itemAddSelector = `#user-loggedin${user.current_logins[0].id}`
            addItemElement(itemAddSelector);
        });
        elemRemove.style.animationPlayState = 'running';
    }
});


// On event logot
socket.on('logout', data => {
    const user = data.user;
    const fromLogin = user.current_logout.from_login;
    const insertionAt = data.insertion_at;

    // Check if logout was from the most recent login previously done
    if (fromLogin.index_in_current_logins != 0 ) {
        return;
    }

    // Remove user from page section corresponding to the most recent login previously done
    const itemRemoveSelector = `#user-loggedin${fromLogin.id}`
    const elemRemove = document.querySelector(itemRemoveSelector);

    // Show animation for removing the user
    if (elemRemove) {
        elemRemove.addEventListener('animationend', () =>  {
            elemRemove.remove();
            pageItems.logIns.itemsCount--;

            // If user still logged in
            const itemShowHide = 'item-show';
            let itemAddSelector;
            if (user.current_logins.length > 0) {
                // If users is the most recently logged in
                if (!insertionAt) {
                    // Append user to the page
                    pageItems.logIns.appendItem(user, itemShowHide);
                }
                // If user is NOT the most recently logged in
                else {
                    // Insert user in the middle of the page
                    pageItems.logIns.insert(insertionAt, user, itemShowHide);
                }
                itemAddSelector = `#user-loggedin${user.current_logins[0].id}`
            }
            // If user is now logged out
            else {
                    // Add user at the logged out section of the page
                    pageItems.logOuts.appendItem(user, itemShowHide);

                    itemAddSelector = `#user-loggedout${user.current_logout.id}`
            }
            // Show animation for adding the user
            addItemElement(itemAddSelector);
        });
        elemRemove.style.animationPlayState = 'running';
    }
});
