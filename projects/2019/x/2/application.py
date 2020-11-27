import os
import sys

from datetime import datetime, timezone

from flask import Flask, redirect, request, render_template, session, flash, jsonify, url_for
from flask import send_from_directory
#from flask_session import Session
from flask_socketio import SocketIO, join_room, leave_room
from werkzeug.utils import secure_filename

import my_application
from helpers import login_check, apology, append_id_to_filename



app = Flask(__name__)
#app.config.from_object('my_application.default_settings')
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

        
    def remove(self):
        Message.remove_by_sender(self)



class Receiver(Communicator):
    def __init__(self, name):
        super().__init__(name)


    def remove(self):
        Message.remove_by_receiver(self)



class Channel(Receiver):
    channels = []


    @staticmethod
    def remove_by_list(to_remove):
        for channel in to_remove:
            channel.remove()


    @staticmethod
    def remove_by_creator(creator):
        to_remove = []
        for channel in Channel.channels:
            if channel.creator == creator:
                to_remove.append(channel)

        Channel.remove_by_list(to_remove)


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


    def remove(self):
        # Emit event
        data = self.to_dict()
        room = 'channels'
        socketio.emit('remove channel', data, room)

        # Remove channel
        try:
            Channel.channels.remove(self)
        except:
            raise RuntimeError("remove(): Channel does not exist")

        Receiver.remove(self)


    def to_dict(self):
        r = super().to_dict()
        r['creator'] = self.creator.to_dict()
        return r



class User(Sender, Receiver):
    users = []
    users_loggedin = []
    users_loggedout = []


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


    @staticmethod
    def insert_user_loggedin(user, to):
        to_timestamp = to.timestamp
        insertion_at = None

        to_index = len(User.users_loggedin)
        for u in User.users_loggedin:
            t = u.current_logins[0].timestamp

            if to_timestamp > t:
                to_index = User.users_loggedin.index(u)
                break

        User.users_loggedin.insert(to_index, user)

        if to_index > 0:
            insertion_at = User.users_loggedin[to_index - 1]
        else:
            insertion_at = None

        return insertion_at


    def __init__(self, name):
        super().__init__(name)

        self.current_logins = []
        self.current_logout = None

        User.users.insert(0, self)



    def login(self):
        if len(self.current_logins) > 0:
            # Remove user from loggedins
            try:
                User.users_loggedin.remove(self)
            except:
                raise RuntimeError("login(): Loggedin user does not exist")

        elif self.current_logout is not None:
            # Remove user from loggedouts
            try:
                User.users_loggedout.remove(self)
            except:
                raise RuntimeError("login(): Loggedout user does not exist")

        login = Login(self)

        self.current_logins.insert(0, login)

        for i in range(0, len(self.current_logins)):
            l = self.current_logins[i]
            l.index_in_current_logins = i

        User.users_loggedin.insert(0, self)
        
        return login


    def logout(self, from_login_id):
        from_login = Log.get_by_id(from_login_id)
        insertion_at = None

        if (from_login is not None) and (len(self.current_logins) > 0):
            if from_login.index_in_current_logins == 0:
                # Remove user from loggedins
                try:
                    User.users_loggedin.remove(self)
                except:
                    raise RuntimeError("login(): Loggedin user does not exist")

                if len(self.current_logins) > 1:
                    to = self.current_logins[1]
                    insertion_at = User.insert_user_loggedin(self, to)

            try:
                self.current_logins.remove(from_login)
            except:
                raise RuntimeError("logout(): User's current login does not exist")

            for i in range(0, len(self.current_logins)):
                l = self.current_logins[i]
                l.index_in_current_logins = i

        elif self.current_logout is not None :
            # Remove user from loggedouts
            try:
                User.users_loggedout.remove(self)
            except:
                raise RuntimeError("logout(): Loggedout user does not exist")

        logout = Logout(self, from_login)
        self.current_logout = logout

        if len(self.current_logins) < 1:
            User.users_loggedout.insert(0, self)

        return {"logout": logout, "insertion_at" : insertion_at} 

    
    def remove(self):
        # Remove created channels
        Channel.remove_by_creator(self)

        # Remove logs
        Log.remove_by_user(self)

        # Remove user
        try:
            User.users.remove(self)

            if self in User.users_loggedin:
                User.users_loggedin.remove(self)

            if self in User.users_loggedout:
                User.users_loggedout.remove(self)
                
        except:
            raise RuntimeError("remove(): User does not exist")

        Sender.remove(self)
        Receiver.remove(self)


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
            "timestamp": self.timestamp
        }



class Login(Log):

    def __init__(self, user):
        super().__init__(user)

        self.index_in_current_logins = -1


    def to_dict(self):
        r = super().to_dict()

        r['index_in_current_logins'] = self.index_in_current_logins

        return r



class Logout(Log):

    def __init__(self, user, from_login):
        super().__init__(user)

        self.from_login = from_login


    def to_dict(self):
        from_login = self.from_login

        r = super().to_dict()

        if from_login is not None:
            r['from_login'] = from_login.to_dict()
        else:
            r['from_login'] = None

        return r




class Message:
    messages = []
    max_seq_number = sys.maxsize - 1
    seq_number = 0


    @staticmethod
    def remove_by_list(to_remove):
        for message in to_remove:
            message.remove()


    @staticmethod
    def remove_by_sender(sender):
        to_remove = []
        for message in Message.messages:
            if message.sender == sender:
                to_remove.append(message)

        Message.remove_by_list(to_remove)


    @staticmethod
    def remove_by_receiver(receiver):
        to_remove = []
        for message in Message.messages:
            if message.receiver == receiver:
                to_remove.append(message)

        Message.remove_by_list(to_remove)
        
        
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

        self.files = []
        for file in files:
            file.message = self
            self.files.append(file)

        if Message.seq_number > Message.max_seq_number:
            raise RuntimeError("Max number of messages exceeded")
        self.id = Message.seq_number
        Message.seq_number += 1

        dt = datetime.now(timezone.utc)
        self.timestamp = dt.isoformat()

        Message.messages.insert(0, self)


    def remove(self):

        # Emit events
        data = self.to_dict()

        room = f'messages sent by user {self.sender.id}'
        socketio.emit('remove message', data, room)

        if is_channel(self.receiver):
            room = f'messages received by channel {self.receiver.id}'
            socketio.emit('remove message', data, room)
            
        elif is_user(self.receiver):
            room = f'messages received by user {self.receiver.id}'
            socketio.emit('remove message', data, room)

        # Remove files
        for file in self.files:
            file.remove()
        self.files = []

        # Remove message
        try:
            Message.messages.remove(self)
        except:
            raise RuntimeError("remove(): Message does not exist")


    def to_dict(self):
        r = {}
        r["id"] = self.id
        r["timestamp"] = self.timestamp
        r["sender"] = self.sender.to_dict()
        r["receiver"] = self.receiver.to_dict()

        if is_channel(self.receiver):
            r["receiver"]["type"] = "channel"
        elif is_user(self.receiver):
            r["receiver"]["type"] = "user"
        else:
            r["receiver"]["type"] = ""

        r["text"] = self.text;

        r["files"] = []
        for file in self.files:
            r["files"].append(file.to_dict())

        return r



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
    def remove_by_list(to_remove):
        for file in to_remove:
            file.remove()


    @staticmethod
    def remove_by_message(message):
        to_remove = []
        for file in File.files:
            if file.message == message:
                to_remove.append(message)

        File.remove_by_list(to_remove)


    @staticmethod
    def get_by_id(id):
        for file in File.files:
            if file.id == id:
                return file
        return None


    def remove(self):
        # Remove file from storage device
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], self.name_unique))

        # Remove file
        try:
            File.files.remove(self)
        except:
            raise RuntimeError("remove(): File does not exist")


    def __init__(self, name):
        self.name = name

        if File.seq_number > File.max_seq_number:
            raise RuntimeError("Max number of files exceeded")
        self.id = File.seq_number
        File.seq_number += 1

        dt = datetime.now(timezone.utc)
        self.timestamp = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")

        # Make the filename safe, remove unsupported chars
        filename_secure = secure_filename(name)

        self.name_unique = append_id_to_filename(self.id, filename_secure, File.max_seq_number)

        File.files.insert(0, self)


    def to_dict(self):
        r = {}
        r["id"] = self.id
        r["timestamp"] = self.timestamp
        r["name"] = self.name
        r["name_unique"] = self.name_unique

        return r



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



@app.route("/home", methods=["GET"])
@login_check(User.users)
def home():
    """ Home page """
    return redirect("/users")


#@app.route("/", methods=["GET"])
@app.route("/", methods=["GET", "POST"])
def index():
    """ Initial page (blank page, with only a script to get locale and timezone from client """

    # If logged in, redirect to home page
    user_id = session.get("user_id")
    if user_id is not None:
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("index.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Set session locale and timezone
        session.clear()

        loc = request.form.get("locale")
        if loc is not None:
            session["locale"] = loc
        else:
            session["locale"] = "en-US"

        dt = datetime.now(timezone.utc)

        tz = request.form.get("timezone")
        if tz is not None:
            session["timezone"] = tz
        else:
            session["timezone"] = timezone.utc.tzname(dt)

        timezone_offset = request.form.get("timezone-offset")
        if timezone_offset is not None:
            try:
                session["timezone_offset"] = int(timezone_offset)
            except ValueError:
                session["timezone_offset"] = timezone.utc.utcoffset(dt).seconds
        else:
            session["timezone_offset"] = timezone.utc.utcoffset(dt).seconds

        session["params_set"] = True

        # Redirect to login page
        return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""

    # If not logged in, redirect to logout
    user_id = session.get("user_id")
    if user_id is not None:
        return redirect("/logout")

    # If not yet accessed intitial page, redirect to initial page 
    params_set = session.get("params_set")
    if not params_set:
        return redirect ("/")

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
        room = 'users'
        socketio.emit('register', data, room)

        # Redirect to home page
        return redirect("/users")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # If not logged in, redirect to logout
    user_id = session.get("user_id")
    if user_id is not None:
        return redirect("/logout")

    # If not yet accessed intitial page, redirect to initial page 
    params_set = session.get("params_set")
    if not params_set:
        return redirect ("/")

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
        room = 'users'
        socketio.emit('login', data, room)

        # Redirect to home page
        return redirect("/home")


@app.route("/logout")
#@login_required
@login_check(User.users)
def logout():
    """ Log user out"""

    # Log out
    user = User.get_by_id(session.get("user_id"))
    ret = None
    if user is not None:
        ret = user.logout(session.get("login_id"))
        session.clear()

        u = user.to_dict()

        # Emit event
        if ret is not None:
            insertion_at = ret['insertion_at']

            a = None
            if insertion_at is not None:
                a = insertion_at.to_dict()

            data = {'user': u,
                    'insertion_at': a
                   }   
            room = 'users'
            socketio.emit('logout', data, room)

    # Redirect to initial page
    return redirect("/")


@app.route("/unregister", methods=["GET", "POST"])
#@login_required
@login_check(User.users)
def unregister():
    """Unregister the user"""

    # If not logged, redirect to initial page
    user = User.get_by_id(session.get("user_id"))
    if user is None:
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("unregister.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # If confirmed:
        if request.form.get("confirm"):

            # Remove user
            user = User.get_by_id(session.get("user_id"))
            if user is not None:
                data = user.to_dict()
                room = 'users'
                socketio.emit('unregister', data, room)
                user.remove()
                session.clear()

            # Redirect user to initial page
            return redirect("/")

        # If not confirmed
        else:
            # Redirect to home page
            return redirect("/home")


@app.route("/users", methods=["GET"])
#@login_required
@login_check(User.users)
def users_():
    """ Show users """
    return render_template("users.html")


@app.route("/api/users", methods=["GET"])
def api_users():
    """ Send users """

    # Get session user
    session_user_id = session.get("user_id")
    if session_user_id is None:
        return jsonify('')

    # Get users
    li = []
    for user in User.users_loggedin:
        li.append(user.to_dict())

    lo = []
    for user in User.users_loggedout:
        lo.append(user.to_dict())

    u = {'loggedin': li,
         'loggedout': lo
        }

    data = {'users': u, 'session_user_id': session_user_id}
    return jsonify(data)


@app.route("/channels", methods=["GET", "POST"])
#@login_required
@login_check(User.users)
def channels_():
    """ Show channels / Create a channel """

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("channels.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template("channels.html")

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

        # Emit event
        data = channel.to_dict()
        room = 'channels'
        socketio.emit('create channel', data, room)

        return render_template("channels.html")


@app.route("/api/channels", methods=["GET"])
def api_channels():
    """ Send channels """

    # Get user
    session_user_id = session.get("user_id")
    if session_user_id is None:
        return jsonify('')

    # Get channels
    c = []
    for channel in Channel.channels:
        c.append(channel.to_dict())

    data = {'channels': c, 'session_user_id': session_user_id}
    return jsonify(data)


@app.route("/message-to-channel/<int:id>", methods=["GET", "POST"])
@login_check(User.users)
def message_to_channel(id):
    """ Send a message to a channel"""

    # Ensure channel exists
    channel = Channel.get_by_id(id)
    if not channel:
        return apology("channel does not exist", 403)

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("message-to-any.html", channel=channel,
                               text_config=Text.config)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Get and send message to receiver
        receiver = channel
        message = message_to_any(receiver)

        # Emit event
        data = message.to_dict()
        room = f'messages received by channel {message.receiver.id}'
        socketio.emit('send message', data, room)

        # Redirect user to channel messages page
        return redirect(url_for('channel_messages', id=channel.id))

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


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
        message = message_to_any(receiver)

        # Emit event
        data = message.to_dict()
        room = f'messages received by user {message.receiver.id}'
        socketio.emit('send message', data, room)

        # Redirect to user messages page
        return redirect(url_for('user_messages_sent', id=session["user_id"]))

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


def message_to_any(receiver):

    # Get uploaded files
    uploaded_files = request.files.getlist("files[]")

    files_obj = []
    for file in uploaded_files:

        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):

            # Instatiate file
            file_obj = File(file.filename)
 
            # Move the file form the temporal folder to the upload
            # folder we setup
            filename_unique = file_obj.name_unique;
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_unique))

            files_obj.append(file_obj)

    # Get message text
    text = request.form.get("text")
    if text:
        text = text.strip()

    # Create message
    user_id = session.get("user_id")
    sender = User.get_by_id(user_id)
    message = Message(sender, receiver, text, files_obj)

    # Emit event
    data = message.to_dict()
    room = f'messages sent by user {message.sender.id}'
    socketio.emit('send message', data, room)

    return message


@app.route("/message-delete/<int:id>")
#@login_required
@login_check(User.users)
def message_delete(id):
    """ Delete a message """

    # Ensure message exists
    message = Message.get_by_id(id)
    if not message:
        return apology("message does not exist", 403)

    # Delete message
    message.remove()

    # Redirect user to previous page
    sender = message.sender
    receiver = message.receiver
    user_id = session.get("user_id")
    if isinstance(receiver, Channel):
        return redirect(url_for('channel_messages', id=receiver.id))
    elif receiver.id == user_id:
        return redirect(url_for('user_messages_received', id=user_id))
    elif sender.id == user_id:
        return redirect(url_for('user_messages_sent', id=user_id))
    else:
        return redirect("/")


@app.route("/channel-messages/<int:id>")
#@login_required
@login_check(User.users)
def channel_messages(id):
    """Show channel's messages """

    # Ensure channel exists
    channel = Channel.get_by_id(id)
    if not channel:
        return apology("channel does not exist", 403)

    return render_template("channel-messages.html", channel=channel)


@app.route("/api/channel-messages/<int:id>")
def api_channel_messages(id):
    """Send channel's messages """

    # Get user
    session_user_id = session.get("user_id")
    if session_user_id is None:
        return jsonify('')

    # Ensure channel exists
    channel = Channel.get_by_id(id)
    if not channel:
        return jsonify('')
    c = channel.to_dict()

    # Get channel's messages
    m = []
    for message in Message.messages:
        if message.receiver == channel:
            m.append(message.to_dict())

    data = {'channel': c, 'messages': m, 'session_user_id': session_user_id}
    return jsonify(data)


@app.route("/user-messages-received/<int:id>")
#@login_required
@login_check(User.users)
def user_messages_received(id):
    """Show user's received messages """

    # Ensure user exists
    user = User.get_by_id(id)
    if not user:
        return apology("user does not exist", 403)

    return render_template("user-messages-received.html", user=user)


@app.route("/api/user-messages-received/<int:id>")
def api_user_messages_received(id):
    """Send user's messages received"""

    # Get session user
    session_user_id = session.get("user_id")
    if session_user_id is None:
        return jsonify('')

    # Ensure user exists
    user = User.get_by_id(id)
    if not user:
        return jsonify('')
    u = user.to_dict()

    # Get user's messages received
    m = []
    for message in Message.messages:
        if message.receiver == user:
            m.append(message.to_dict())

    data = {'user': u, 'messages': m, 'session_user_id': session_user_id}
    return jsonify(data)


@app.route("/user-messages-sent/<int:id>")
#@login_required
@login_check(User.users)
def user_messages_sent(id):
    """Show user's sent messages """

    # Ensure user exists
    user = User.get_by_id(id)
    if not user:
        return apology("user does not exist", 403)

    return render_template("user-messages-sent.html", user=user)

                
@app.route("/api/user-messages-sent/<int:id>")
def api_user_messages_sent(id):
    """Send user's messages sent"""

    # Get session user
    session_user_id = session.get("user_id")
    if session_user_id is None:
        return jsonify('')

    # Ensure user exists
    user = User.get_by_id(id)
    if not user:
        return jsonify('')
    u = user.to_dict()

    # Get user's messages sent
    m = []
    for message in Message.messages:
        if message.sender == user:
            m.append(message.to_dict())

    data = {'user': u, 'messages': m, 'session_user_id': session_user_id}
    return jsonify(data)
    

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<int:file_id>/<filename>')
def uploaded_file(file_id, filename):

    # Ensure file exists
    file = File.get_by_id(file_id)
    if not file:
        return apology("file does not exist", 403)

    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               file.name_unique)


@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    socketio.emit('joined', data, request.sid)


@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    socketio.emit('left', data, request.sid)
