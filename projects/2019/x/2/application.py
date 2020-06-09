#import os
import sys

from datetime import datetime, timezone

from flask import Flask, redirect, request, render_template, session, flash
#from flask_session import Session
from flask_socketio import SocketIO, emit

import my_application
from helpers import login_required, apology



app = Flask(__name__)
app.config.from_object('my_application.default_settings')
print(app.config["SECRET_KEY"])
app.config.from_envvar('APPLICATION_SETTINGS')
print(app.config["SECRET_KEY"])

# Configure session to use filesystem
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

#app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
# Configure socket
socketio = SocketIO(app)


class Communicator:
    max_seq_number = sys.maxsize - 1
    seq_number = 0

    def __init__(self, name):
        self.name = name
        
        if Communicator.seq_number > Communicator.max_seq_number:
            raise RuntimeError("Max number of communicators exceeded")
        self.id = Communicator.seq_number
        Communicator.seq_number += 1

        dt = datetime.now(timezone.utc)
        self.timestamp = dt.isoformat()


class Sender(Communicator):
    def __init__(self, name):
        super().__init__(name)
        self.messages_sent = []


class Receiver(Communicator):
    def __init__(self, name):
        super().__init__(name)
        self.messages_received = []


class Channel(Receiver):
    channels = []

    @staticmethod
    def get_by_id(id):
        for channel in Channel.channels:
            if channel.id == id:
                return channel
        return None


    @staticmethod
    def get_by_name(name):
        for channel in Channel.channels:
            if channel.name == name:
                return channel
        return None


    def __init__(self, name):
        super().__init__(name)
        Channel.channels.insert(0, self)


class User(Sender, Receiver):
    users = []

    @staticmethod
    def get_by_id(id):
        for user in User.users:
            if user.id == id:
                return user
        return None


    @staticmethod
    def get_by_name(name):
        for user in User.users:
            if user.name == name:
                return user
        return None


    def __init__(self, name):
        super().__init__(name)
        self.logs_history = []
        self.current_logins = []
        User.users.insert(0, self)


    def login(self):
        login = Login()
        self.logs_history.insert(0, login)
        self.current_logins.insert(0, login)


    def logout(self, login_id):
        logout = Logout()
        self.logs_history.insert(0, logout)

        to_remove = None
        for login in self.current_logins:
            if login.id == login_id:
                to_remove = login
                break

        if to_remove:
            self.current_logins.remove(to_remove)

    
    def remove(self):

        # Remove all user's messages
        self.messages_sent = []
        self.messages_received = []

        to_remove = []
        for message in Message.messages:
            if message.sender == self or message.receiver == self:
                to_remove.append(message)
        for message in to_remove:
            message.remove()

        # Remove logins
        self.logs_history = []
        self.current_logins = []

        # Remove user
        try:
            User.users.remove(self)
        except:
            raise RuntimeError("remove(): User does not exist")


class Log:
    max_seq_number = sys.maxsize - 1
    seq_number = 0

    def __init__(self):
        if Log.seq_number > Log.max_seq_number:
            raise RuntimeError("Max number of logins/logouts exceeded")
        self.id = Log.seq_number
        Log.seq_number += 1

        dt = datetime.now(timezone.utc)
        self.timestamp = dt.isoformat()


class Login(Log):
    pass


class Logout(Log):
    pass


class Message:
    messages = []
    max_seq_number = sys.maxsize - 1
    seq_number = 0

    @staticmethod
    def get_by_id(id):
        for message in Message.messages:
            if message.id == id:
                return message
        return None


    def __init__(self, sender, receiver, text, files):
        self.sender = sender
        self.receiver = receiver
        self.text = text
        self.files = files

        if Message.seq_number > Message.max_seq_number:
            raise RuntimeError("Max number of messages exceeded")
        self.id = Message.seq_number
        Message.seq_number += 1

        dt = datetime.now(timezone.utc)
        self.timestamp = dt.isoformat()

        Message.messages.insert(0, self)


    def remove(self):

        # Remove files
        self.files = []

        # Remove message
        try:
            Message.messages.remove(self)
        except:
            raise RuntimeError("remove(): Message does not exist")


class Text:
    config = {}
    config["columns_max"] = 80
    config["rows_number"] = 5
    config["max_length"] = config["columns_max"] * config["rows_number"]


@app.route("/")
@login_required
def index():
    """ Home page """

    # Redirect user to channels page
    return redirect("/users")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("register.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Ensure name was submitted
        name = request.form.get("name")
        if not name:
            return apology("must provide name", 403)

        # Ensure user does not exist
        user = User.get_by_name(name)
        if user:
            return apology("user already exists", 403)

        # Register user
        user = User(name)

        # Log out previous user
        if session.get("user_id"):
            previous_user = User.get_by_id(session["user_id"])
            previous_user.logout(session["login_id"])

        # Login user
        user.login()

        # Remember which user has logged in
        session.clear()
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["login_id"] = user.current_logins[0].id

        # Report message
        flash('You were successfully logged in')
        flash(user.name)
        
        # Redirect user to home page
        return redirect("/")

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("login.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Ensure name was submitted
        name = request.form.get("name")
        if not name:
            return apology("must provide name", 403)

        # Ensure user exists
        user = User.get_by_name(name)
        if not user:
            return apology("user does not exist", 403)

        # Log out previous user
        if session.get("user_id"):
            previous_user = User.get_by_id(session["user_id"])
            previous_user.logout(session["login_id"])

        # Login user
        user.login()

        # Remember which user has logged in
        session.clear()
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["login_id"] = user.current_logins[0].id

        # Report message
        flash('You were successfully logged in')
        flash(user.name)
        
        # Redirect user to home page
        return redirect("/")

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Get user
    user = User.get_by_id(session["user_id"])

    #Log out user
    user.logout(session["login_id"])

    session.clear()

    # Redirect user to home page
    return redirect("/")


@app.route("/unregister", methods=["GET", "POST"])
@login_required
def unregister():
    """Unregister the user"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("unregister.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        if request.form.get("confirm"):

            # Get user
            user = User.get_by_id(session["user_id"])

            # Remove user
            user.remove()

            session.clear()

        # Redirect user to home page
        return redirect("/")

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/channels", methods=["GET", "POST"])
@login_required
def channels_():
    """ Show channels / Create a channel """

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("channels.html", channels=Channel.channels)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template("channels.html", channels=Channel.channels)

        # Ensure channel does not exist
        channel = Channel.get_by_name(name)
        if channel:
            return apology("channel already exists", 403)

        # Create channel
        channel = Channel(name)

        return render_template("channels.html", channels=Channel.channels)

    else:
        return apology("invalid method", 403)


@app.route("/channel-messages/<int:id>")
@login_required
def channel_messages(id):
    """Show channel's messages """

    # Ensure channel exists
    channel = Channel.get_by_id(id)
    if not channel:
        return apology("channel does not exist", 403)

    # Get channel's messages
    m = []
    for message in Message.messages:
        if message.receiver == channel:
            m.append(message)

    return render_template("channel-messages.html", channel=channel,
                           messages=m, text_config=Text.config)



@app.route("/users", methods=["GET"])
@login_required
def users_():
    """ Show users """

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("users.html", users=User.users)
    else:
        return apology("invalid method", 403)


@app.route("/user-messages-received/<int:id>")
@login_required
def user_messages_received(id):
    """Show user's received messages """

    # Ensure user exists
    user = User.get_by_id(id)
    if not user:
        return apology("user does not exist", 403)

    # Get messages received by user
    m = []
    for message in Message.messages:
        if message.receiver == user:
            m.append(message)

    return render_template("user-messages-received.html", user=user, messages=m,
                           text_config=Text.config)


@app.route("/user-messages-sent/<int:id>")
@login_required
def user_messages_sent(id):
    """Show user's sent messages """

    # Ensure user exists
    user = User.get_by_id(id)
    if not user:
        return apology("user does not exist", 403)

    # Get messages sent by user
    m = []
    for message in Message.messages:
        if message.sender == user:
            m.append(message)

    return render_template("user-messages-sent.html", user=user, messages=m,
                           text_config=Text.config)


@app.route("/message-to-user/<int:id>", methods=["GET", "POST"])
@login_required
def message_to_user(id):
    """ Send a message to a user"""

    # Ensure user exists
    user = User.get_by_id(id)
    if not user:
        return apology("user does not exist", 403)

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("message-to-any.html", user=user,
                               text_config=Text.config)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Get and send message to receiver
        receiver = user
        message_to_any(receiver)

        # Redirect to user messages page
        return redirect(url_for('user_messages_sent', id=session["user_id"]))

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)
