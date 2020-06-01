import os
import sys

from datetime import datetime, timezone
import time
import locale

from flask import Flask, session, redirect, request, render_template, flash, url_for, send_from_directory
from flask_session import Session
from flask_socketio import SocketIO, emit
from werkzeug import secure_filename

from helpers import login_required, apology


app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure socket
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
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
        self.timestamp = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")


class Sender(Communicator):
    pass


class Receiver(Communicator):
    pass


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


class Login:
    max_seq_number = sys.maxsize - 1
    seq_number = 0

    def __init__(self):
        if Login.seq_number > Login.max_seq_number:
            raise RuntimeError("Max number of logins exceeded")
        self.id = Login.seq_number
        Login.seq_number += 1

        dt = datetime.now(timezone.utc)
        self.timestamp = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")


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
        self.logins = []
        User.users.insert(0, self)


    def login(self):
        self.logins.insert(0, Login())

    
    def remove(self):

        # Remove all user's messages
        to_remove = []
        for message in Message.messages:
            if message.sender == self or message.receiver == self:
                to_remove.append(message)
        for message in to_remove:
            message.remove()

        # Remove logins
        self.logins = []

        # Remove user
        try:
            User.users.remove(self)
        except:
            raise RuntimeError("remove(): User does not exist")


class Text:
    config = {}
    config["columns_max"] = 80
    config["rows_number"] = 5
    config["max_length"] = config["columns_max"] * config["rows_number"]


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
        self.timestamp = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")

        Message.messages.insert(0, self)


    def remove(self):

        # Remove files
        self.files = []

        # Remove message
        try:
            Message.messages.remove(self)
        except:
            raise RuntimeError("remove(): Message does not exist")


class File:
    files = []
    max_seq_number = sys.maxsize - 1
    seq_number = 0

    def __init__(self, name):
        self.name = name

        if File.seq_number > File.max_seq_number:
            raise RuntimeError("Max number of files exceeded")
        self.id = File.seq_number
        File.seq_number += 1

        dt = datetime.now(timezone.utc)
        self.timestamp = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")

        File.files.insert(0, self)


    def remove(self):

        # Remove file
        try:
            File.files.remove(self)
        except:
            raise RuntimeError("remove(): File does not exist")


@app.template_test('channel')
def is_channel(receiver):
    return isinstance(receiver, Channel)

@app.template_test('user')
def is_user(receiver):
    return isinstance(receiver, User)


UPLOAD_FOLDER = 'static/uploads'

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


@app.route("/")
@login_required
def index():
    """ Home page """

    # Redirect user to channels page
    return redirect("/channels")


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

        # Login user
        user.login()

        # Remember which user has logged in
        session.clear()
        session["user"] = user

        # Get locale
        loc = locale.getlocale(locale.LC_CTYPE)
        (language_code, encoding) = loc
        # language_code format returned by getlocale is like 'pt_BR' but 
        # language_code format required by setlocale is like 'pt-BR' 
        language_code = language_code.replace("_", "-", 1)
        session["language_code"] = language_code

        # Get local time zone
        lt = time.localtime()   # localtime returns tm_gmtoff in seconds
        gmt_offset = lt.tm_gmtoff
        session["gmt_offset"] = gmt_offset

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

        # Login user
        user.login()

        # Remember which user has logged in
        session.clear()
        session["user"] = user

        # Get locale
        loc = locale.getlocale(locale.LC_CTYPE)
        (language_code, encoding) = loc
        # language_code format returned by getlocale is like 'pt_BR' but 
        # language_code format required by setlocale is like 'pt-BR' 
        language_code = language_code.replace("_", "-", 1)
        session["language_code"] = language_code

        # Get local time zone
        lt = time.localtime()   # localtime returns tm_gmtoff in seconds
        gmt_offset = lt.tm_gmtoff
        session["gmt_offset"] = gmt_offset

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
            user = User.get_by_id(session["user"].id)

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



def append_id_to_filename(file_id, filename):

    # Append file id precededed by zeros to the beginning of filename
    d = 0
    n = File.max_seq_number
    while n > 0:
        d += 1
        n //= 10
    f = "0" + str(d)
    p = "{:" + f + "}"
    x = f"{p}".format(file_id)
    appended_name = x + "-" + filename

    return appended_name


def message_to_any(receiver):

    # Get the name of the uploaded files
    uploaded_files = request.files.getlist("file")
    files_obj = []
    for file in uploaded_files:
        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)

            # Instatiate file
            file_obj = File(filename)

            # Append file id precededed by zeros to the beginning of filename
            filename = append_id_to_filename(file_obj.id, filename)
 
            # Move the file form the temporal folder to the upload
            # folder we setup
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Save the filename into a list, we'll use it later
            files_obj.append(file_obj)

    # Get message text
    text = request.form.get("text")
    if text:
        text = text.strip()

    # Create message
    sender = User.get_by_id(session["user"].id)
    message = Message(sender, receiver, text, files_obj)

    return message


@app.route("/message-to-channel/<int:id>", methods=["GET", "POST"])
@login_required
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
        message_to_any(receiver)

        # Redirect user to channel messages page
        return redirect(url_for('channel_messages', id=channel.id))

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


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
        return redirect(url_for('user_messages_sent', id=session["user"].id))

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/message-delete/<int:id>")
@login_required
def message_delete(id):
    """ Delete a message """

    # Ensure message exists
    message = Message.get_by_id(id)
    if not message:
        return apology("message does not exist", 403)

    # Delete message
    message.remove()

    # Redirect user to previous page
    s = message.sender
    r = message.receiver
    if isinstance(r, Channel):
        return redirect(url_for('channel_messages', id=r.id))
    elif r.id == session['user'].id:
        return redirect(url_for('user_messages_received', id=session["user"].id))
    elif s.id == session['user'].id:
        return redirect(url_for('user_messages_sent', id=session["user"].id))
    else:
        return redirect("/")


# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<int:file_id>/<filename>')
def uploaded_file(file_id, filename):

    # Append file id precededed by zeros to the beginning of filename
    filename = append_id_to_filename(file_id, filename)

    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
