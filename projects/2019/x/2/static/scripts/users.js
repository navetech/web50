const template = Handlebars.compile(document.querySelector('#user').innerHTML);

document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When a user is registered, add user
    socket.on('announce register', user => {

        let same_user = false;
        if (user.id === session_user_id) {
            same_user = true;
        }

        const d = new Date(user.timestamp);
        console.log(d)
        user.timestamp = d.toString();

        const context = {
            user: user,
            same_user: same_user
        }

        const content = template(context);
        const old_content = document.querySelector('#users').innerHTML
        document.querySelector('#users').innerHTML = content + old_content;

        const id = `#user${user.id}`
        const element = document.querySelector(id)

        element.addEventListener('animationend', () =>  {
            element.style.animationPlayState = 'paused';
            let clo = element.getAttribute("class");
            let cln = clo.replace("item-show", "item-hide");
            element.setAttribute("class", cln);
        });

        element.style.animationPlayState = 'running';
    });


    // When a user is unregistered, remove user
    socket.on('announce unregister', user => {

        const id = `#user${user.id}`;
        const element = document.querySelector(id);

        element.addEventListener('animationend', () =>  {
            element.remove();
        });

        element.style.animationPlayState = 'running';
    }); 
});