let items_count = 0;

let template_item;
let template_item_content;
let template_item_none;


document.addEventListener('DOMContentLoaded', () => {
    items_count = document.querySelectorAll(".user-item").length;

    template_item = Handlebars.compile(document.querySelector('#user').innerHTML);
    template_item_content = Handlebars.compile(document.querySelector('#user-content').innerHTML);
    template_item_none = Handlebars.compile(document.querySelector('#user-none').innerHTML);
    
    // Connect to websocket
    let socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Initialize new request
    const request = new XMLHttpRequest();
    request.open('GET', '/api/users');

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);
        session_user_id = data.session_user_id;
        showUsers(data.users);
    }
    // Send request
    request.send();


    // When a user is registered, add user
    socket.on('announce register', user => {
        const item_show_hide = 'item-show';
        addUser(user, item_show_hide);

        const id_elem_add = `#user${user.id}`;
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
    socket.on('announce unregister', user => {
        const id_elem_remove = `#user${user.id}`;
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
                        const content = template_item_none(context);
                        const old_content = document.querySelector('#users').innerHTML;
                        document.querySelector('#users').innerHTML = content + old_content;
                
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
    socket.on('announce login', user => {
        setUserContent(user);
    });


    // When a user logout, update user
    socket.on('announce logout', user => {
        setUserContent(user);
    });
});


function showUsers(users) {
    items_count = 0;
    document.querySelector('#users').innerHTML = '';

    const item_show_hide = 'item-hide';
    if (users.length > 0) {
        users.reverse().forEach(user => {
            addUser(user, item_show_hide);
        });
    }
    else {
        const context = {
            item_show_hide: item_show_hide
        }
        const content = template_item_none(context);
        document.querySelector('#users').innerHTML = content;
    }
}


function addUser(user, item_show_hide) {
    const context = {
        user: user,
        item_show_hide: item_show_hide
    };
    const content = template_item(context);
    const old_content = document.querySelector('#users').innerHTML;
    document.querySelector('#users').innerHTML = content + old_content;
    setUserContent(user);
    items_count++;
}


function setUserContent(user) {
    user.timestamp = convertToLocaleString(user.timestamp);
    
    user.current_logins.forEach(login => {
        login.timestamp = convertToLocaleString(login.timestamp);
    });

    const context = {
        user: user
    }
    const content = template_item_content(context);
    const id = `#user${user.id}`
    const element = document.querySelector(id)
    element.innerHTML = content
}

