#import os
import sys

from datetime import datetime, timezone

from flask import Flask, redirect, request, render_template, session, flash
#from flask_session import Session
from flask_socketio import SocketIO, emit

import my_application
from helpers import login_check, apology



app = Flask(__name__)
app.config.from_object('my_application.default_settings')
app.config.from_envvar('APPLICATION_SETTINGS')

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


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "timestamp" : self.timestamp
        }


class Sender(Communicator):
    def __init__(self, name):
        super().__init__(name)
        self.messages_sent = []

        
    def remove(self):

        # Remove sent messages
        for message in self.messages_sent:
            if message.sender == self:
                message.remove()
        self.messages_sent = []


class Receiver(Communicator):
    def __init__(self, name):
        super().__init__(name)
        self.messages_received = []


    def remove(self):

        # Remove receive messages
        for message in self.messages_received:
            if message.receiver == self:
                message.remove()
        self.messages_received = []


class Channel(Receiver):
    channels = []

    @staticmethod
    def remove_by_user(user):
        to_remove = []
        for channel in Channel.channels:
            if channel.creator == user:
                to_remove.append(channel)
        for channel in to_remove:
            Channel.channels.remove(channel)


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


    def __init__(self, name, creator):
        super().__init__(name)
        self.creator = creator
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

        self.current_log = None
        self.last_login = None
        self.last_logout = None

        User.users.insert(0, self)


    def login(self):
        if self.last_logout is not None :
            self.last_logout.remove_from_currents()

        login = Login(self)
        self.last_login = login
        self.current_log = login

        return login


    def logout(self, login_id):
        login = Log.get_by_id(login_id)
        if login is not None:
            login.remove_from_currents()

        logout = Logout(self)
        self.last_logout = logout
        self.current_log = logout

        return logout

    
    def remove(self):

        # Remove created channels
        Channel.remove_by_user(self)

        # Remove logs
        Login.remove_by_user(self)
        Logout.remove_by_user(self)
        Log.remove_by_user(self)

        # Remove user
        try:
            User.users.remove(self)
        except:
            raise RuntimeError("remove(): User does not exist")
        super().remove()


    def to_dict(self):
        c_logins = []
        for login in self.current_logins:
            c_logins.append(login.to_dict())
        r = super().to_dict()
        r['current_logins'] = c_logins
        return r


class Log:
    logs = []
    max_seq_number = sys.maxsize - 1
    seq_number = 0

    @staticmethod
    def remove_by_user(user):
        to_remove = []
        for log in Log.logs:
            if log.user == user:
                to_remove.append(log)
        for log in to_remove:
            Log.logs.remove(log)


    @staticmethod
    def get_by_id(id):
        for log in Log.logs:
            if log.id == id:
                return log
        return None


    def __init__(self, user):
        self.user = user

        if Log.seq_number > Log.max_seq_number:
            raise RuntimeError("Max number of logins/logouts exceeded")
        self.id = Log.seq_number
        Log.seq_number += 1

        dt = datetime.now(timezone.utc)
        self.timestamp = dt.isoformat()

        Log.logs.insert(0, self)


    def remove(self):

        # Remove log
        try:
            Log.logs.remove(self)
        except:
            raise RuntimeError("remove(): Logins/logouts does not exist")


    def to_dict(self):
        return {
            "id": self.id,
            "timestamp" : self.timestamp
        }


class Login(Log):
    currents = []

    @staticmethod
    def remove_by_user(user):
        to_remove = []
        for log in Login.currents:
            if log.user == user:
                to_remove.append(log)
        for log in to_remove:
            Login.currents.remove(log)


    def __init__(self, user):
        super().__init__(user)
        Login.currents.insert(0, self)


    def remove(self):

        # Remove login
        try:
            Login.currents.remove(self)
        except:
            pass

        super().remove()


    def remove_from_currents(self):

        # Remove login
        try:
            Login.currents.remove(self)
        except:
            pass


class Logout(Log):
    currents = []

    @staticmethod
    def remove_by_user(user):
        to_remove = []
        for log in Logout.currents:
            if log.user == user:
                to_remove.append(log)
        for log in to_remove:
            Logout.currents.remove(log)


    def __init__(self, user):
        super().__init__(user)
        Logout.currents.insert(0, self)


    def remove(self):

        # Remove logout
        try:
            Logout.currents.remove(self)
        except:
            pass

        super().remove()


    def remove_from_currents(self):

        # Remove login
        try:
            Logout.currents.remove(self)
        except:
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


from flask import jsonify

@app.route("/session", methods=["GET"])
def session_():
    """ Session data """
    user_id = session.get("user_id")
    return jsonify(user_id)


@app.route("/")
#@login_required
@login_check(User.users)
def index():
    """ Home page """

    # Redirect page
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
        if user is not None:
            return apology("user already exists", 403)

        # Register user
        user = User(name)

        # Log out previous user
        previous_user = User.get_by_id(session.get("user_id"))
        if previous_user is not None:
            previous_user.logout(session.get("login_id"))
        session.clear()

        # Login user
        login = user.login()

        # Remember which user has logged in
        session.clear()
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["login_id"] = login.id

        # Report message
        flash('You were successfully logged in')
        flash(user.name)

        # Emit event
        data = user.to_dict()
        socketio.emit('announce register', data)

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
        if user is None:
            return apology("user does not exist", 403)

        # Log out previous user
        previous_user = User.get_by_id(session.get("user_id"))
        if previous_user is not None:
            previous_user.logout(session.get("login_id"))
        session.clear()

        # Login user
        login = user.login()

        # Remember which user has logged in
        session.clear()
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["login_id"] = login.id

        # Report message
        flash('You were successfully logged in')
        flash(user.name)
        
        # Redirect user to home page
        return redirect("/")

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/logout")
#@login_required
@login_check(User.users)
def logout():
    """ Log user out"""

    # Log out user
    user = User.get_by_id(session.get("user_id"))
    if user is not None:
        user.logout(session.get("login_id"))
    session.clear()

    # Redirect user to home page
    return redirect("/")


@app.route("/unregister", methods=["GET", "POST"])
#@login_required
@login_check(User.users)
def unregister():
    """Unregister the user"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("unregister.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        if request.form.get("confirm"):

            # Remove user
            user = User.get_by_id(session.get("user_id"))
            if user is not None:
                data = user.to_dict()
                socketio.emit('announce unregister', data)
                user.remove()
            session.clear()

        # Redirect user to home page
        return redirect("/")

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/channels", methods=["GET", "POST"])
#@login_required
@login_check(User.users)
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
        if channel is not None:
            return apology("channel already exists", 403)

        # Ensure user exists
        user = User.get_by_id(session.get("user_id"))
        if user is None:
            return apology("user does not exist", 403)

        # Create channel
        channel = Channel(name, creator=user)

        return render_template("channels.html", channels=Channel.channels)

    else:
        return apology("invalid method", 403)


@app.route("/channel-messages/<int:id>")
#@login_required
@login_check(User.users)
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
#@login_required
@login_check(User.users)
def users_():
    """ Show users """

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("users.html", users=User.users)
    else:
        return apology("invalid method", 403)


@app.route("/user-messages-received/<int:id>")
#@login_required
@login_check(User.users)
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
#@login_required
@login_check(User.users)
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
#@login_required
@login_check(User.users)
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
