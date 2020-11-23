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
        session_user_id = data.session_user_id;

        // Set elements selectors
        const itemsElemSelector = null;
        const noItemsElemSelector = '#no-users';

        // Set templates
        const template_user = null;
        const template_user_content = Handlebars.compile(document.querySelector('#user-content').innerHTML);
        const template_user_none = Handlebars.compile(document.querySelector('#user-none').innerHTML);

        // Instatiate page items object
        const pageItems = new UsersPageItems(itemsElemSelector, template_user, template_user_content, noItemsElemSelector, template_user_none);

        // Show channels on page
        pageItems.show(data.users);
        
        // Join room for real-time communication with server
        page = 'users';
        idCommunicator = null;
        joinRoom(page, idCommunicator);
    }
    // Send request
    request.send();
});


// Class for user items on a page
class UsersPageItems extends PageItems {
    constructor(itemsElemSelector, template_item, template_item_content, noItemsElemSelector, template_item_none) {
        super(itemsElemSelector, template_item, template_item_content, noItemsElemSelector, template_item_none);

        // Set elements selectors and templates for users logged in/out
        const noItemsElemSelector = null;
        const template_item_none = null;

        // Set elements selectors and templates for users logged in
        const loggedInElemSelector = '#users-loggedin';
        const template_loggedin = Handlebars.compile(document.querySelector('#user-loggedin').innerHTML);

        // Set elements selectors and templates for users logged out
        const loggedOutElemSelector = '#users-loggedout';
        const template_loggedout = Handlebars.compile(document.querySelector('#user-loggedout').innerHTML);

        // Attributes
        this.loggedIn = new LoggedInsPageItems(this, loggedInElemSelector, template_loggedin, template_item_content, noItemsElemSelector, template_item_none)
        this.loggedOut = new LoggedOutsPageItems(this, loggedOutElemSelector, template_loggedout, template_item_content, noItemsElemSelector, template_item_none)

        // Methods
        this.show = showUsers;
    }
}


// Parent class for logged in/out user items on a page
class LoggedsPageItems extends PageItems {
    constructor(user, itemsElemSelector, template_item,  template_item_content, noItemsElemSelector, template_item_none) {
        super(itemsElemSelector, template_item, template_item_content, noItemsElemSelector, template_item_none);

        // Attributes
        this.user = user;

        // Methods
        this.append = appendLogged;
    }
}


// Class for logged in user items on a page
class LoggedInsPageItems extends LoggedsPageItems {
    constructor(user, itemsElemSelector, template_item,  template_item_content, noItemsElemSelector, template_item_none) {
        super(user, itemsElemSelector, template_item, template_item_content, noItemsElemSelector, template_item_none);

        // Attributes

        // Methods
        this.putContent = putLoggedInContent;
        this.insert = insertLoggedIn;
    }
}


// Class for logged out user items on a page
class LoggedOutsPageItems extends LoggedsPageItems {
    constructor(user, itemsElemSelector, template_item,  template_item_content, noItemsElemSelector, template_item_none) {
        super(user, itemsElemSelector, template_item, template_item_content, noItemsElemSelector, template_item_none);

        // Attributes

        // Methods
        this.putContent = putLoggedOutContent;
    }
}


function showUsers(users) {
    // If there are no users (no logged in and no logged out)
    if ((users.loggedin.length <= 0) && (users.loggedout.length <= 0)) {
        // Put no users info on page
        const item_show_hide = 'item-hide';
        this.putNo(item_show_hide);
    }
    // If there are users
    else {
        // Clear no users section on page 
        document.querySelector(this.noItemsElemSelector).innerHTML = '';

        // Show logged in and logged out users items
        this.loggedIn.show(users.loggedin)
        this.loggedOut.show(users.loggedout)
        this.items_count = this.loggedIn.items_count + this.loggedOut.items_count;
    }
}


function appendLogged(user, item_show_hide) {
    // Generate HTML from template
    const context = {
        user: user,
        item_show_hide: item_show_hide
    };

    // Append logged in item
    super.append(context);

    // Put user data contents
    this.putContent(user);
}


function insertLoggedIn(insertionAt, user, item_show_hide) {
    // Generate HTML from template
    const context = {
        user: user,
        item_show_hide: item_show_hide
    };
    const content = template_item(context);

    // Insert HTML at the insertion point of the page section
    const id_elem = `#user-loggedin${insertionAt.current_logins[0].id}`
    const elem = document.querySelector(id_elem);
    elem.insertAdjacentHTML("afterend", content);

    // Put user data contents
    this.putContent(user);

    // Increment number of logged in users on page
    this.items_count++;
}


function putLoggedInContent(user) {
    // Convert time info to local time
    user.timestamp = convertToLocaleString(user.timestamp);
    user.current_logins.forEach(login => {
        login.timestamp = convertToLocaleString(login.timestamp);
    });

    // Generate HTML from template
    const context = {
        user: user
    }
    const content = template_item_content(context);

    // Add HTML to page section
    const id = `#user-loggedin${user.current_logins[0].id}`
    const element = document.querySelector(id)
    element.innerHTML = content
}

function putLoggedOutContent(user) {
    // Convert time info to local time
    user.timestamp = convertToLocaleString(user.timestamp);
    user.current_logout.timestamp = convertToLocaleString(user.current_logout.timestamp);

    // Generate HTML from template
    const context = {
        user: user
    }
    const content = template_item_content(context);

    // Add HTML to page section
    const id = `#user-loggedout${user.current_logout.id}`
    const element = document.querySelector(id)
    element.innerHTML = content
}


// On event: register
socket.on('register', user => {
    // Add logged in user to page
    const item_show_hide = 'item-show';
    pageItems.loggedIn.append(user, item_show_hide);
    pageItems.items_count++;

    // Show animation for creating the user
    const id_elem_add = `#user-loggedin${user.current_logins[0].id}`
    const id_elem_remove = `#user-null`;
    showAnimationCreateItem(id_elem_add, id_elem_remove);
});


// On event: unregister
socket.on('unregister', user => {
    // Remove logged in user from page
    const id_elem_remove = `#user-loggedin${user.current_logins[0].id}`
    const id_elem_item_null = '#user-null';
    pageItems.loggedIn.remove(id_elem_remove, id_elem_item_null);
    pageItems.items_count--;
});


// On event login
socket.on('login', user => {
    // Remove user from page section corresponding to if it was logged in or logged out
    let id_elem_remove;
    let loggedItems;
    if (user.current_logins.length > 1) {
        id_elem_remove = `#user-loggedin${user.current_logins[1].id}`
        loggedItems = pageItems.loggedIn;
    }
    else if (user.current_logins.length === 1) {
        id_elem_remove = `#user-loggedout${user.current_logout.id}`
        loggedItems = pageItems.loggedOut;
    }
    else {
        id_elem_remove = null;
        loggedItems = null;
    }
    const elem_remove = document.querySelector(id_elem_remove);

    // Show animation for removing the user
    if (elem_remove) {
        elem_remove.addEventListener('animationend', () =>  {
            elem_remove.remove();
            loggedItems.items_count--;

            // Add logged in user to page
            const item_show_hide = 'item-show';
            pageItems.loggedIn.append(user, item_show_hide);
    
            // Show animation for adding the user
            const id_elem_add = `#user-loggedin${user.current_logins[0].id}`
            const elem_add = document.querySelector(id_elem_add);
            elem_add.addEventListener('animationend', () =>  {
                elem_add.style.animationPlayState = 'paused';
                let class_old = elem_add.getAttribute("class");
                let class_new = class_old.replace("item-show", "item-hide");
                elem_add.setAttribute("class", class_new);
            });
            elem_add.style.animationPlayState = 'running';
        });
        elem_remove.style.animationPlayState = 'running';
    }
});


// On event logot
socket.on('logout', data => {
    user = data.user;
    insertionAt = data.insertion_at;
    fromLogin = user.current_logout.fromLogin;

    // Check if logout was from the most recent login previously done
    if (fromLogin.indexInCurrentLogins != 0 ) {
        return;
    }

    // Remove user from page section corresponding to the most recent login previously done
    const id_elem_remove = `#user-loggedin${fromLogin.id}`
    const elem_remove = document.querySelector(id_elem_remove);

    // Show animation for removing the user
    if (elem_remove) {
        elem_remove.addEventListener('animationend', () =>  {
            elem_remove.remove();
            pageItems.loggedIn.items_count--;

            // If user still logged in
            const item_show_hide = 'item-show';
            let id_elem_add;
            if (user.current_logins.length > 0) {
                // If users is the most recently logged in
                if (!insertionAt) {
                    // Append user to the page
                    pageItems.loggedIn.append(user, item_show_hide);
                }
                // If user is NOT the most recently logged in
                else {
                    // Insert user in the middle of the page
                    pageItems.loggedIn.insert(insertionAt, user, item_show_hide);
                }
                id_elem_add = `#user-loggedin${user.current_logins[0].id}`
            }
            // If user is now logged out
            else {
                    // Add user at the logged out section of the page
                    pageItems.loggedOut.append(user, item_show_hide);

                    id_elem_add = `#user-loggedout${user.current_logout.id}`
            }
            // Show animation for adding the user
            const elem_add = document.querySelector(id_elem_add);
            elem_add.addEventListener('animationend', () =>  {
                elem_add.style.animationPlayState = 'paused';
                let class_old = elem_add.getAttribute("class");
                let class_new = class_old.replace("item-show", "item-hide");
                elem_add.setAttribute("class", class_new);
            });
            elem_add.style.animationPlayState = 'running';
        });
        elem_remove.style.animationPlayState = 'running';
    }
});
