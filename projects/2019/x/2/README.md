# [CS50's Web Programming with Python and JavaScript](https://cs50.harvard.edu/web/2018/)<br><br>


## [Project 2: Flack](https://docs.cs50.net/ocw/web/projects/2/project2.html)<br><br>


### **Overview**<br>

This is a project for an *online messaging service*.

Users are able to register for the website and then log in using their username (display name). Once they log in, they are able to create channels (i.e. chatrooms) to communicate in, as well as see and join existing channels. Once a channel is selected, users are able to send and receive messages with one another in real time.

Users can also see the others users signed into the service, knowing whom of them are online or offline; as well as send and receive private messages with one another individual user in real time.

The messages can have attachments (file uploads) to them, and also can be deleted by their owners (senders or receivers).

Service's events (such as: users registrations/unregistrations/logins/logouts; channels creations; messages sendings and deletions) are sent in real time to the logged in users.

<br>

### **Features**<br>

This project has the following main features:

- **Registration:** Users are able to register for the website, providing a username (display name). The display name will eventually be associated with every channel the user creates, and every message the user sends.

- **Login:** Users, once registered, are able to log in the website with their username. An user can be logged in on several devices at the same time.

- **Logout**: Logged in users are able to log out of the site. The user is logged out of the corresponding device's login, remaining logged in on the others devices.

- **Unregistration:** Users can unregister from the website. Once unregistered, all the user's logins are canceled; all the channels created by them are deleted; as well as all the messages sent or received by them are also deleted.

- **Users List:** Users are able to see a list of all registered users, ordered by logins times at the top, followed by the logged out users at the bottom of the list. Selecting one user from the list allows the selector user to send a private message to the selected user.

- **Channel Creation:** Any user can create a new channel, so long as its name doesn’t conflict with the name of an existing channel. The display name of the creator is associated with the channel.

- **Channels List:** Users are able to see a list of all current channels, and selecting one allows the user to view the channel's messages and send a message to it.

- **Messages View:** Once a channel is selected, the user can see any messages that have already been sent in that channel. Is provided a page with the messages sent by the user, and also another page with their received messages.

- **Sending Messages:** Once in a channel, users are able to send messages to others through the channel. All users in the channel can then see the new message appear on their channel page.
By the other hand, once a user is selected, the selector user can send a private message to the selected user.
All the messages can have attachments (file uploads) to them, and are sent in real time.
When a user sends a message, their display name is associated with the message.

- **Deleting messages:** Messages owners (senders or receivers) can delete any message (private or to channels).

- **Real-time events:** Service's events (such as: users registrations/unregistrations/logins/logouts; channels creations; messages sendings and deletions) are sent in real time to the logged in users.
These events change the views of the website's pages in real time, showing animations when creating or deleting items (such as users, channels and messages) on the page. When deleting, the item fades out until disappear, then the remaining items are moved to the freed location. When creating, the opposite occurs, the items are moved away to release space to the new item, which then gradually comes out in the place. 

<br>

### **Tools**<br>

Mainly, this project makes use of the following tools:

- **[Python](https://www.python.org/downloads/):** (*version 3.6 or higher*). The list of the *Python packages* that need to be installed in order to run the web application, is added to the *requirements.txt* file.

- **[Flask](https://palletsprojects.com/p/flask/):** A lightweight WSGI web application framework.

- **Flask-SocketIO:** Flask-SocketIO gives Flask applications access to bi-directional communications between the clients and the server.

- **HTML5**

- **CSS3**

- **[Bootstrap 4](https://getbootstrap.com/docs/4.0/getting-started/introduction/):** Bootstrap is a popular front-end open source toolkit for building responsive sites.

- **[Sass](https://sass-lang.com/):** Sass is a stylesheet language that is compiled to CSS.

- **JavaScript**

- **[JavaScript Socket.IO](https://socket.io/docs/v3/client-api/):** A Javascript client library for the browser that enables real-time, bidirectional and event-based communication between the browser and the server.

- **[Handlebars](https://handlebarsjs.com/):** A templating language

- **CSS3 Animation**

- **Object-oriented Programming (OOP)** 