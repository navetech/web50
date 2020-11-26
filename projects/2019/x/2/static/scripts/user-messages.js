// Class for user item on a page
class UserItem extends CommunicatorItem {
    constructor() {
        const userSelector = '#user-id';
        const templateUser = Handlebars.compile(document.querySelector('#user').innerHTML);
        
        super(userSelector, templateUser);

        // Attributes


        // Methods
    }

    
    putItem(user) {
        // Clear page section
        document.querySelector(this.itemSelector).innerHTML = '';
    
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
            super.putItem(context);
        }
    }
}

