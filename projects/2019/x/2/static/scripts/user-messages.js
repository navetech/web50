// Class for user item on a page
class UserItem extends CommunicatorItem {
    constructor() {
        const template_user = Handlebars.compile(document.querySelector('#user').innerHTML);
        const userElemSelector = '#user-id';
        
        super(template_user, userElemSelector);

        // Attributes


        // Methods
        this.show = showUser;
    }
}

function showUser(user) {
    // Clear page section
    document.querySelector(this.itemsElemSelector).innerHTML = '';

    if (user) {
        // Convert time info to local time
        user.timestamp = convertToLocaleString(user.timestamp);
    
        user.current_logins.forEach(login => {
            login.timestamp = convertToLocaleString(login.timestamp);
        });

        // Generate HTML from template
        const context = {
            user: user
        }

        // show user item
        super.show(context);
    }
}

