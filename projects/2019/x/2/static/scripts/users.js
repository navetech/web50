document.addEventListener('DOMContentLoaded', () => {

    let items_count = document.querySelectorAll(".user-item").length;

    const template_item = Handlebars.compile(document.querySelector('#user').innerHTML);
    const template_item_content = Handlebars.compile(document.querySelector('#user-content').innerHTML);
    const template_item_none = Handlebars.compile(document.querySelector('#user-none').innerHTML);

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When a user is registered, add user
    socket.on('announce register', user => {
        let same_user = false;
        if (user.id === session_user_id) {
            same_user = true;
        }

        const context = {
            user: user,
            same_user: same_user
        };

        const content = template_item(context);
        const old_content = document.querySelector('#users').innerHTML;
        document.querySelector('#users').innerHTML = content + old_content;
        items_count++;

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

                    const content = template_item_none();
                    const old_content = document.querySelector('#users').innerHTML;
                    document.querySelector('#users').innerHTML = content + old_content;
            
                    const id_elem_add = `#user-null`;
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
        let same_user = false;
        if (user.id === session_user_id) {
            same_user = true;
        }

        const context = {
            user: user,
            same_user: same_user
        }

        const content = template_item_content(context);
        const id = `#user${user.id}`
        const element = document.querySelector(id)
        element.innerHTML = content
    });


    // When a user logout, update user
    socket.on('announce logout', user => {
        let same_user = false;
        if (user.id === session_user_id) {
            same_user = true;
        }

        const context = {
            user: user,
            same_user: same_user
        }

        const content = template_item_content(context);
        const id = `#user${user.id}`
        const element = document.querySelector(id)
        element.innerHTML = content
    });
});