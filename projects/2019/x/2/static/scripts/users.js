const template = Handlebars.compile(document.querySelector('#user').innerHTML);

document.addEventListener('DOMContentLoaded', () => {

    console.log("users.js")

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When a user is registered, add user
    socket.on('announce register', user => {
        console.log("rec announce")
        console.log(user.name)
        console.log(user.timestamp)
        const content = template({'name': user.name, 'timestamp': user.timestamp});
        console.log(content)
        document.querySelector('#users').innerHTML += content;
    }); 
});