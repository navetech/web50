import os
import sys

from datetime import datetime, timezone

from flask import Flask, redirect, request, render_template, session, flash
#from flask_session import Session
from flask_socketio import SocketIO, emit

import my_application
from helpers import login_check, apology, append_id_to_filename, get_timestamp



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


import time
import locale


class Communicator:
    max_seq_number = sys.maxsize - 1
    seq_number = 0

    def __init__(self, name):
        self.name = name
        
        if Communicator.seq_number > Communicator.max_seq_number:
            raise RuntimeError("Max number of communicators exceeded")
        self.id = Communicator.seq_number
        Communicator.seq_number += 1

        self.timestamp = get_timestamp()


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


    def remove_messages(self):

        # Remove sent messages
        for message in self.messages_sent:
            if message.sender == self:
                message.remove()
        self.messages_sent = []

        
    def remove(self):
        self.remove_messages()


    def send_message(self, receiver, text, files_names):
        Message(self, receiver, text, files_names)


class Receiver(Communicator):
    def __init__(self, name):
        super().__init__(name)
        self.messages_received = []


    def remove_messages(self):

        # Remove received messages
        for message in self.messages_received:
            if message.receiver == self:
                message.remove()
        self.messages_received = []


    def remove(self):
        self.remove_messages()


class Channel(Receiver):
    channels = []

    @staticmethod
    def remove_by_creator(creator):
        to_remove = []
        for channel in Channel.channels:
            if channel.creator == creator:
                to_remove.append(channel)

        for channel in to_remove:
            Channel.channels.remove(channel)
            channel.remove()


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

        self.current_logins = []
        self.current_logout = None

        User.users.insert(0, self)


    def login(self):
        if self.current_logout is not None :
            self.current_logout.remove_from_currents()
        self.current_logout = None

        login = Login(self)
        self.current_logins.insert(0, login)

        return login


    def logout(self, login_id):
        login = Log.get_by_id(login_id)
        if login is not None:
            login.remove_from_currents()
            try:
                self.current_logins.remove(login)
            except:
                raise RuntimeError("remove(): User's current login does not exist")

        if self.current_logout is not None :
            self.current_logout.remove_from_currents()
        logout = Logout(self)
        self.current_log = logout

        return logout

    
    def remove(self):

        # Remove created channels
        Channel.remove_by_creator(self)

        # Remove logs
        Login.remove_by_user(self)
        self.current_logins = []

        Logout.remove_by_user(self)
        self.current_logout = None

        Log.remove_by_user(self)

        # Remove user
        try:
            User.users.remove(self)
        except:
            raise RuntimeError("remove(): User does not exist")
        super().remove()


    def create_channel(self, name):
        Channel(name, self)



    def to_dict(self):
        logins = []
        for login in self.current_logins:
            logins.append(login.to_dict())

        logout = self.current_logout

        r = super().to_dict()
        r['current_logins'] = logins

        if logout is not None:
            r['current_logout'] = logout.to_dict()
        else:
            r['current_logout'] = None

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


    def remove_from_currents(self):

        # Remove login
        try:
            Login.currents.remove(self)
        except:
            raise RuntimeError("remove(): Login from currents does not exist")


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


    def remove_from_currents(self):

        # Remove login
        try:
            Logout.currents.remove(self)
        except:
            raise RuntimeError("remove(): Logout from currents does not exist")


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


    def __init__(self, sender, receiver, text, files_names):
        self.sender = sender
        self.receiver = receiver
        self.text = text

        self.files = []
        for name in files_names:
            self.files.append(File( name, self))

        if Message.seq_number > Message.max_seq_number:
            raise RuntimeError("Max number of messages exceeded")
        self.id = Message.seq_number
        Message.seq_number += 1

        dt = datetime.now(timezone.utc)
        self.timestamp = dt.isoformat()

        Message.messages.insert(0, self)


    def remove(self):

        # Remove files
        File.remove_by_message(self)
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


class File:
    files = []
    max_seq_number = sys.maxsize - 1
    seq_number = 0


    @staticmethod
    def remove_by_message(message):
        to_remove = []
        for file in File.files:
            if file.message == message:
                to_remove.append(message)
        for file in to_remove:
            File.files.remove(file)


    def __init__(self, name, message):
        self.name = name
        self.message = message

        if File.seq_number > File.max_seq_number:
            raise RuntimeError("Max number of files exceeded")
        self.id = File.seq_number
        File.seq_number += 1

        dt = datetime.now(timezone.utc)
        self.timestamp = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")

        self.name_unique = append_id_to_filename(self.id, name, File.max_seq_number)

        File.files.insert(0, self)


@app.template_test('channel')
def is_channel(receiver):
    return isinstance(receiver, Channel)

@app.template_test('user')
def is_user(receiver):
    return isinstance(receiver, User)


UPLOAD_FOLDER = 'uploads'

# Create upload directory
try:
    files = os.listdir(UPLOAD_FOLDER)
except FileNotFoundError:
    os.mkdir(UPLOAD_FOLDER)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']



from flask import jsonify

@app.route("/session", methods=["GET"])
def session_():
    """ Session data """
    user_id = session.get("user_id")
    return jsonify(user_id)


@app.route("/", methods=["GET"])
#@app.route("/", methods=["GET", "POST"])
#@login_required
#@login_check(User.users)
def index():
    """ Home page """

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":

        # Set session locale and timezone
        print("GET index")
        session.clear()

        params = request.args.get("params")
        if not params:
            return render_template("index.html")

        loc = request.args.get("locale")
        if loc is not None:
            session["locale"] = loc
        else:
            session["locale"] = "en-US"
        print(session["locale"])

        dt = datetime.now(timezone.utc)

        tz = request.args.get("timezone")
        if tz is not None:
            session["timezone"] = tz
        else:
            session["timezone"] = timezone.utc.tzname(dt)
        print(session["timezone"])

        timezone_offset = request.args.get("timezone-offset")
        if timezone_offset is not None:
            try:
                session["timezone_offset"] = int(timezone_offset)
            except ValueError:
                session["timezone_offset"] = timezone.utc.utcoffset(dt).seconds
        else:
            session["timezone_offset"] = timezone.utc.utcoffset(dt).seconds
        print(session["timezone_offset"])

        return redirect("/login")

#        if loc is None and tz is None and timezone_offset is None:
 #           return render_template("index.html")
  #      else:
   #         return redirect("/login")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Set session locale and timezone
        print("index")
        session.clear()

        loc = request.form.get("locale")
        if loc is not None:
            session["locale"] = loc
        else:
            session["locale"] = "en-US"
        print(session["locale"])

        dt = datetime.now(timezone.utc)

        tz = request.form.get("timezone")
        if tz is not None:
            session["timezone"] = tz
        else:
            session["timezone"] = timezone.utc.tzname(dt)
        print(session["timezone"])

        timezone_offset = request.form.get("timezone-offset")
        if timezone_offset is not None:
            try:
                session["timezone_offset"] = int(timezone_offset)
            except ValueError:
                session["timezone_offset"] = timezone.utc.utcoffset(dt).seconds
        else:
            session["timezone_offset"] = timezone.utc.utcoffset(dt).seconds
        print(session["timezone_offset"])

        # Redirect page
        return redirect("/login")

    # Redirect page
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""

    user_id = session.get("user_id")
    if user_id is not None:
        return redirect("/")


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

        # Set session locale and timezone
        print("request")
        session.clear()

        loc = request.form.get("locale")
        if loc is not None:
            session["locale"] = loc
        else:
            session["locale"] = "en-US"
        print(session["locale"])

        dt = datetime.now(timezone.utc)

        tz = request.form.get("timezone")
        if tz is not None:
            session["timezone"] = tz
        else:
            session["timezone"] = timezone.utc.tzname(dt)
        print(session["timezone"])

        timezone_offset = request.form.get("timezone-offset")
        if timezone_offset is not None:
            try:
                session["timezone_offset"] = int(timezone_offset)
            except ValueError:
                session["timezone_offset"] = timezone.utc.utcoffset(dt).seconds
        else:
            session["timezone_offset"] = timezone.utc.utcoffset(dt).seconds
        print(session["timezone_offset"])

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
        return redirect("/users")

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
