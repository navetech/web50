document.addEventListener('DOMContentLoaded', () => {

    const template_create = Handlebars.compile(document.querySelector('#channel').innerHTML);

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When a user is registered, add user
    socket.on('announce create channel', channel => {

        let same_user = false;
        if (channel.creator.id === session_user_id) {
            same_user = true;
        }

        const context = {
            channel: channel,
            same_user: same_user
        }

        const content = template_create(context);
        const old_content = document.querySelector('#channels').innerHTML
        document.querySelector('#channels').innerHTML = content + old_content;

        const id = `#channel${channel.id}`
        const element = document.querySelector(id)

        element.addEventListener('animationend', () =>  {
            element.style.animationPlayState = 'paused';
            let clo = element.getAttribute("class");
            let cln = clo.replace("item-show", "item-hide");
            element.setAttribute("class", cln);
        });

        element.style.animationPlayState = 'running';
    });

/*
    // When a user is unregistered, remove user
    socket.on('announce unregister', user => {

        const id = `#user${user.id}`;
        const element = document.querySelector(id);

        element.addEventListener('animationend', () =>  {
            element.remove();
        });

        element.style.animationPlayState = 'running';
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

        const content = template_log(context);
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

        const content = template_log(context);
        const id = `#user${user.id}`
        const element = document.querySelector(id)
        element.innerHTML = content
    });
*/
});