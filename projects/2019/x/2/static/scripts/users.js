// Number of users on page
let users_count = 0;

// Templates
let template_user_loggedin;
let template_user_loggedout;
let template_user_content;
let template_user_none;


// On page loaded
document.addEventListener('DOMContentLoaded', () => {
    // Set templates
    template_user_loggedin = Handlebars.compile(document.querySelector('#user-loggedin').innerHTML);
    template_user_loggedout = Handlebars.compile(document.querySelector('#user-loggedout').innerHTML);
    template_user_content = Handlebars.compile(document.querySelector('#user-content').innerHTML);
    template_user_none = Handlebars.compile(document.querySelector('#user-none').innerHTML);

    // Initialize new request
    const request = new XMLHttpRequest();
    request.open('GET', '/api/users');

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);

        // Get session user
        session_user_id = data.session_user_id;

        // Show users on page
        showUsers(data.users);

        // Join room for real-time communication with server
        page = 'users';
        idCommunicator = null;
        joinRoom(page, idCommunicator);
    }
    // Send request
    request.send();
});


function showUsers(users) {
    // Zero number of users on page
    users_count = 0;

    // If there are no users (no logged in and no logged out)
    if ((users.loggedin.length <= 0) && (users.loggedout.length <= 0)) {
        // Add no users info on page
        const item_show_hide = 'item-hide';
        addNoUsersInfo(item_show_hide);
    }
    // If there are users
    else {
        // Clear no users section on page 
        document.querySelector('#no-users').innerHTML = '';

        // Show logged in and logged out users
        showUsersLoggedIn(users.loggedin)
        showUsersLoggedOut(users.loggedout)
    }
}


function addNoUsersInfo(item_show_hide) {
    // Generate HTML from template
    const context = {
        item_show_hide: item_show_hide
    }
    const content = template_user_none(context);

    // Add HTML to page
    document.querySelector('#no-users').innerHTML = content;
}


function showUsersLoggedIn(users) {
    // Clear page section
    document.querySelector('#users-loggedin').innerHTML = '';

    // Add each user to page
    const item_show_hide = 'item-hide';
    users.reverse().forEach(user => {
        addUserLoggedIn(user, item_show_hide);
    });
}


function showUsersLoggedOut(users) {
    // Clear page section
    document.querySelector('#users-loggedout').innerHTML = '';

    // Add each user to page
    const item_show_hide = 'item-hide';
    users.reverse().forEach(user => {
        addUserLoggedOut(user, item_show_hide);
    });
}


function addUserLoggedIn(user, item_show_hide) {
    // Generate HTML from template
    const context = {
        user: user,
        item_show_hide: item_show_hide
    };
    const content = template_user_loggedin(context);

    // Add HTML to page section
    const old_content = document.querySelector('#users-loggedin').innerHTML;
    document.querySelector('#users-loggedin').innerHTML = content + old_content;

    // Set user data contents
    setUserLoggedInContent(user);

    // Increment number of users on page
    users_count++;
}


function insertUserLoggedIn(insertionAt, user, item_show_hide) {
    // Generate HTML from template
    const context = {
        user: user,
        item_show_hide: item_show_hide
    };
    const content = template_user_loggedin(context);

    // Insert HTML at the insertion point of the page section
    const id_elem = `#user-loggedin${insertionAt.current_logins[0].id}`
    const elem = document.querySelector(id_elem);
    elem.insertAdjacentHTML("afterend", content);

    // Set user data contents
    setUserLoggedInContent(user);

    // Increment number of users on page
    users_count++;
}


function addUserLoggedOut(user, item_show_hide) {
    // Generate HTML from template
    const context = {
        user: user,
        item_show_hide: item_show_hide
    };
    const content = template_user_loggedout(context);

    // Add HTML to page section
    const old_content = document.querySelector('#users-loggedout').innerHTML;
    document.querySelector('#users-loggedout').innerHTML = content + old_content;

    // Set user data contents
    setUserLoggedOutContent(user);

    // Increment number of users on page
    users_count++;
}


function setUserLoggedInContent(user) {
    // Convert time info to local time
    user.timestamp = convertToLocaleString(user.timestamp);
    user.current_logins.forEach(login => {
        login.timestamp = convertToLocaleString(login.timestamp);
    });

    // Generate HTML from template
    const context = {
        user: user
    }
    const content = template_user_content(context);

    // Add HTML to page section
    const id = `#user-loggedin${user.current_logins[0].id}`
    const element = document.querySelector(id)
    element.innerHTML = content
}

function setUserLoggedOutContent(user) {
    // Convert time info to local time
    user.timestamp = convertToLocaleString(user.timestamp);
    user.current_logout.timestamp = convertToLocaleString(user.current_logout.timestamp);

    // Generate HTML from template
    const context = {
        user: user
    }
    const content = template_user_content(context);

    // Add HTML to page section
    const id = `#user-loggedout${user.current_logout.id}`
    const element = document.querySelector(id)
    element.innerHTML = content
}


// On event: register
socket.on('register', user => {
    // Add user to page
    const item_show_hide = 'item-show';
    addUserLoggedIn(user, item_show_hide);

    // Show animation for creating the user
    const id_elem_add = `#user-loggedin${user.current_logins[0].id}`
    const id_elem_remove = `#user-null`;
    showAnimationCreateItem(id_elem_add, id_elem_remove);
});


// On event: unregister
socket.on('unregister', user => {
    // Remove user from page
    const id_elem_remove = `#user-loggedin${user.current_logins[0].id}`
    const id_elem_item_null = '#user-null';
    removeItem(id_elem_remove, users_count, id_elem_item_null);
});

    const elem_remove = document.querySelector(id_elem_remove);

    // Show animation for removing the user
    if (elem_remove) {
        elem_remove.addEventListener('animationend', () =>  {
            elem_remove.remove();
            users_count--;

            // If no more users
            if ((users_count < 1) &&
                (document.querySelector(`#user-null`) == null)) {
                // Add no users info on page section
                const item_show_hide = 'item-show';
                addNoUsersInfo(item_show_hide);
        
                // Show animation for adding the no users info
                const id_elem_add = '#user-null';
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
});


// On event login
socket.on('login', user => {
    // Remove user from page section corresponding to if it was logged in or logged out
    let id_elem_remove;
    if (user.current_logins.length > 1) {
        id_elem_remove = `#user-loggedin${user.current_logins[1].id}`
    }
    else {
        id_elem_remove = `#user-loggedout${user.current_logout.id}`
    }
    const elem_remove = document.querySelector(id_elem_remove);

    // Show animation for removing the user
    if (elem_remove) {
        elem_remove.addEventListener('animationend', () =>  {
            elem_remove.remove();
            users_count--;

            // Add user to page
            const item_show_hide = 'item-show';
            addUserLoggedIn(user, item_show_hide);
    
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
            users_count--;

            // If user still logged in
            const item_show_hide = 'item-show';
            let id_elem_add;
            if (user.current_logins.length > 0) {
                // If users is the most recently logged in
                if (!insertionAt) {
                    // Add user at the top of the page
                    addUserLoggedIn(user, item_show_hide);
                }
                // If user is NOT the most recently logged in
                else {
                    // Insert user in the middle of the page
                    insertUserLoggedIn(insertionAt, user, item_show_hide);
                }
                id_elem_add = `#user-loggedin${user.current_logins[0].id}`
            }
            // If user is now logged out
            else {
                    // Add user at the logged out section of the page
                    addUserLoggedOut(user, item_show_hide);
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
