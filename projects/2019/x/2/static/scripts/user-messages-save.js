let template_user;


function setTemplatesMessagesUsers() {
    template_user = Handlebars.compile(document.querySelector('#user').innerHTML);
    setTemplatesMessages();
}

function showUser(user) {
    document.querySelector('#user-id').innerHTML = '';

    if (user) {
        user.timestamp = convertToLocaleString(user.timestamp);
    
        user.current_logins.forEach(login => {
            login.timestamp = convertToLocaleString(login.timestamp);
        });

        const context = {
            user: user
        }

        const content = template_user(context);
        document.querySelector('#user-id').innerHTML = content;
    }
}

