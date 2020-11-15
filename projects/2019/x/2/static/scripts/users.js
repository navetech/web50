let items_count = 0;

let template_user_loggedin;
let template_user_loggedout;
let template_user_content;
let template_user_none;


document.addEventListener('DOMContentLoaded', () => {
    items_count = document.querySelectorAll(".user-item").length;

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
        session_user_id = data.session_user_id;
        showUsers(data.users);

        // Join room for real-time communication with server
        page = 'users';
        idCommunicator = null;
        joinRoom(page, idCommunicator);
    }
    // Send request
    request.send();


    // When a user is registered, add user
    socket.on('register', user => {
        const item_show_hide = 'item-show';
        addUserLoggedIn(user, item_show_hide);

        const id_elem_add = `#user-loggedin${user.current_logins[0].id}`
        const elem_add = document.querySelector(id_elem_add);

        elem_add.addEventListener('animationend', () =>  {
            elem_add.style.animationPlayState = 'paused';
            let class_old = elem_add.getAttribute("class");
            let class_new = class_old.replace("item-show", "item-hide");
            elem_add.setAttribute("class", class_new);

            const id_elem_remove = `#user-null`;
            const elem_remove = document.querySelector(id_elem_remove);
    
            if (elem_remove) {
                elem_remove.addEventListener('animationend', () =>  {
                    elem_remove.remove();
                });
                elem_remove.style.animationPlayState = 'running';
            }
        });
        elem_add.style.animationPlayState = 'running';
    });


    // When a user is unregistered, remove user
    socket.on('unregister', user => {
        const id_elem_remove = `#user-loggedin${user.current_logins[0].id}`
        const elem_remove = document.querySelector(id_elem_remove);

        if (elem_remove) {
            elem_remove.addEventListener('animationend', () =>  {
                elem_remove.remove();

                items_count--;
                if ((items_count < 1) &&
                    (document.querySelector(`#user-null`) == null)) {
                        const context = {
                            item_show_hide: 'item-show'
                        }
                        const content = template_user_none(context);
                        document.querySelector('#no-users').innerHTML = content;
                
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


    // When a user login, update user
    socket.on('login', user => {
        let id_elem_remove;
        if (user.current_logins.length > 1) {
            id_elem_remove = `#user-loggedin${user.current_logins[1].id}`
        }
        else {
            id_elem_remove = `#user-loggedout${user.current_logout.id}`
        }
        const elem_remove = document.querySelector(id_elem_remove);

        if (elem_remove) {
            elem_remove.addEventListener('animationend', () =>  {
                elem_remove.remove();
                items_count--;

                const item_show_hide = 'item-show';
                addUserLoggedIn(user, item_show_hide);
        
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


    // When a user logout, update user
    socket.on('logout', user => {
        setUserContent(user);
    });
});


function showUsers(users) {
    items_count = 0;

    if ((users.loggedin.length <= 0) && (users.loggedout.length <= 0)) {
        const item_show_hide = 'item-hide';
        const context = {
            item_show_hide: item_show_hide
        }
        const content = template_user_none(context);
        document.querySelector('#no-users').innerHTML = content;
    }
    else {
        document.querySelector('#no-users').innerHTML = '';
        showUsersLoggedIn(users.loggedin)
        showUsersLoggedOut(users.loggedout)
    }
}


function showUsersLoggedIn(users) {
    document.querySelector('#users-loggedin').innerHTML = '';

    const item_show_hide = 'item-hide';
    users.reverse().forEach(user => {
        addUserLoggedIn(user, item_show_hide);
    });
}


function showUsersLoggedOut(users) {
    document.querySelector('#users-loggedout').innerHTML = '';

    const item_show_hide = 'item-hide';
    users.reverse().forEach(user => {
        addUserLoggedOut(user, item_show_hide);
    });
}


function addUserLoggedIn(user, item_show_hide) {
    const context = {
        user: user,
        item_show_hide: item_show_hide
    };
    const content = template_user_loggedin(context);
    const old_content = document.querySelector('#users-loggedin').innerHTML;
    document.querySelector('#users-loggedin').innerHTML = content + old_content;
    setUserLoggedInContent(user);
    items_count++;
}


function addUserLoggedOut(user, item_show_hide) {
    const context = {
        user: user,
        item_show_hide: item_show_hide
    };
    const content = template_user_loggedout(context);
    const old_content = document.querySelector('#users-loggedout').innerHTML;
    document.querySelector('#users-loggedout').innerHTML = content + old_content;
    setUserLoggedOutContent(user);
    items_count++;
}


function setUserLoggedInContent(user) {
    user.timestamp = convertToLocaleString(user.timestamp);
    
    user.current_logins.forEach(login => {
        login.timestamp = convertToLocaleString(login.timestamp);
    });

    const context = {
        user: user
    }
    const content = template_user_content(context);
    const id = `#user-loggedin${user.current_logins[0].id}`
    const element = document.querySelector(id)
    element.innerHTML = content
}

function setUserLoggedOutContent(user) {
    user.timestamp = convertToLocaleString(user.timestamp);
    
    user.current_logout.timestamp = convertToLocaleString(user.current_logout.timestamp);

    const context = {
        user: user
    }
    const content = template_user_content(context);
    const id = `#user-loggedout${user.current_logout.id}`
    const element = document.querySelector(id)
    element.innerHTML = content
}
