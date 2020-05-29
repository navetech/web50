import os

from datetime import datetime, timezone
import time
import locale

from flask import Flask, session, redirect, request, render_template, flash, url_for
from flask_session import Session
from flask_socketio import SocketIO, emit

from helpers import login_required, apology


app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure socket
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

text_columns_max = 80
text_rows_number = 10
text_max_length = text_columns_max * text_rows_number
texts_config = {}
texts_config["columns_max"] = text_columns_max
texts_config["rows_number"] = text_rows_number
texts_config["max_length"] = text_max_length

messages_config = {}
messages_config["texts"] = texts_config


users=[]
channels = []
messages = []


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

        # Ensure user does not exists
        for user in users:
            if user["name"] == name:
                return apology("name already exists", 403)

        # Register user
        user = {}
        user["name"] = name
        dt = datetime.now(timezone.utc)
        user["timestamp"] = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
        users.append(user)

        # Login user
        login = {}
        dt = datetime.now(timezone.utc)
        login["timestamp"] = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
        user_index = users.index(user)
        users[user_index]["login"] = login
        user = users[user_index]

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
        flash(user["name"])

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
        found = False
        for user in users:
            if user["name"] == name:
                found = True
                break
        
        if not found:
            return apology("user does not exist", 403)

        # Login user
        login = {}
        dt = datetime.now(timezone.utc)
        login["timestamp"] = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
        user_index = users.index(user)
        users[user_index]["login"] = login
        user = users[user_index]

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
        flash(user["name"])

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


@app.route("/clear-all")
@login_required
def clear_all():
    """Clear all """

    users = []
    channels = []
    messages = []
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
            
            # For each channel, delete all messages from user
            user = session["user"]
            name = user["name"]
            for message in messages:
                sender = message["sender"]["name"]
                receiver = message["receiver"]["user"]["name"]
                if sender == name or receiver == name:
                        messages.remove(message)

            # Unregister user
            try:
                users.remove(user)
            except:
                return apology("user does not exist", 403)
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
        return render_template("channels.html", channels=channels)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template("channels.html", channels=channels)

        # Ensure channel does not exists
        for channel in channels:
            if channel["name"] == name:
                return apology("channel already exists", 403)

        # Set locale for formatting datetime according local language
        language_code = session["language_code"]
        locale.setlocale(locale.LC_TIME, language_code)

        # Create channel
        channel = {}
        channel["name"] = name
        dt = datetime.now(timezone.utc)
        channel["timestamp"] = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
        channels.append(channel)

        return render_template("channels.html", channels=channels)

    else:
        return apology("invalid method", 403)


@app.route("/channel-messages/<string:channel_name>")
@login_required
def channel_messages(channel_name):
    """Show channel's messages """

    # Ensure channel exists
    found = False
    for channel in channels:
        if channel["name"] == channel_name:
            found = True
            break

    if not found:
        return apology("channel does not exists", 403)

    ms = []
    for message in messages:
        if message["receiver"]["channel"]["name"] == channel["name"]:
            ms.append(message)

    return render_template("channel-messages.html", channel=channel,
                           messages=ms, messages_config=messages_config)


@app.route("/message-to-channel/<string:channel_name>", methods=["GET", "POST"])
@login_required
def message_to_channel(channel_name):
    """ Send a message to a channel"""

    # Get channel
    found = False
    for channel in channels:
        if channel["name"] == channel_name:
            found = True
            break
    if not found:
        return apology("channel does not exists", 403)

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("message-to-channel.html", channel=channel,
                               messages_config=messages_config)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Get message
        text = request.form.get("text")
        if text:
            text_stripped = text.strip()
        else:
            text_stripped = None

        # Set locale for formatting datetime according local language
        language_code = session["language_code"]
        locale.setlocale(locale.LC_TIME, language_code)

        # Send message
        if text_stripped:
            message = {}
            message["text"] = text_stripped
            message["sender"] = session["user"]
            message["receiver"] = {}
            message["receiver"]["channel"] = channel
            message["receiver"]["user"] = {}
            dt = datetime.now(timezone.utc)
            message["timestamp"] = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
            messages.append(message)
            
        # Redirect user to channel messages page
        return redirect(url_for('channel_messages', channel_name=channel['name']))

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/users", methods=["GET"])
@login_required
def users_():
    """ Show users """

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("users.html", users=users)

    else:
        return apology("invalid method", 403)


@app.route("/user-messages-received/<string:user_name>")
@login_required
def user_messages_received(user_name):
    """Show user's received messages """

    # Ensure user exists
    found = False
    for user in users:
        if user["name"] == user_name:
            found = True
            break
    if not found:
        return apology("user does not exists", 403)

    # Get messages received by user
    ms = []
    for message in messages:
        if message["receiver"]["user"]["name"] == user["name"]:
            ms.append(message)

    return render_template("user-messages.html", user=user, messages=ms,
                           messages_config=messages_config)


@app.route("/user-messages-sent/<string:user_name>")
@login_required
def user_messages_sent(user_name):
    """Show user's sent messages """

    # Ensure user exists
    found = False
    for user in users:
        if user["name"] == user_name:
            found = True
            break
    if not found:
        return apology("user does not exists", 403)

    # Get messages sent by user
    ms = []
    for message in messages:
        if message["sender"]["name"] == user["name"]:
            ms.append(message)

    return render_template("user-messages.html", user=user, messages=ms,
                           messages_config=messages_config)


@app.route("/message-to-user/<string:user_name>", methods=["GET", "POST"])
@login_required
def message_to_user(user_name):
    """ Send a message to a user"""

    # Get user
    found = False
    for user in users:
        if user["name"] == user_name:
            found = True
            break
    if not found:
        return apology("user does not exists", 403)

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("message-to-user.html", user=user,
                               messages_config=messages_config)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Get message
        text = request.form.get("text")
        if text:
            text_stripped = text.strip()
        else:
            text_stripped = None

        # Set locale for formatting datetime according local language
        language_code = session["language_code"]
        locale.setlocale(locale.LC_TIME, language_code)

        # Send message
        if text_stripped:
            message = {}
            message["text"] = text_stripped
            message["sender"] = session["user"]
            message["receiver"] = {}
            message["receiver"]["user"] = user
            message["receiver"]["channel"] = {}
            dt = datetime.now(timezone.utc)
            message["timestamp"] = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
            messages.append(message)
            
        # Redirect user to channel page
        return redirect(url_for('user_messages_sent', user_name=session["user"]['name']))

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)
