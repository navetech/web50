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


users_gl=[]
channels_gl = []


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

        # Get users
        users = users_gl

        # Ensure user does not exists
        for user in users:
            if user["name"] == name:
                return apology("name already exists", 403)

        # Register user
        user = {}
        user["name"] = name
        users_gl.append(user)

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

        # Get users
        users = users_gl

        # Ensure user exists
        found = False
        for user in users:
            if user["name"] == name:
                found = True
                break
        
        if not found:
            return apology("user does not exist", 403)

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

    users_gl = []
    channels_gl = []
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
            for channel in channels_gl:
                for message in channel["messages"]:
                    if message["sender"] == user:
                        channel["messages"].remove(message)

            # Unregister user
            try:
                users_gl.remove(user)
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

    # Get channels
    channels = channels_gl

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
        channel["messages"] = []
        channels_gl.append(channel)

        channels = channels_gl
        return render_template("channels.html", channels=channels)

    else:
        return apology("invalid method", 403)


@app.route("/channel/<string:name>")
@login_required
def channel(name):
    """Show channel's messages """

    # Get channels
    channels = channels_gl

    # Ensure channel exists
    for channel in channels:
        if channel["name"] == name:
            return render_template("channel.html", channel=channel,
                                   messages_config=messages_config)
    return apology("channel does not exists", 403)


@app.route("/message/<string:channel_name>", methods=["GET", "POST"])
@login_required
def message(channel_name):
    """ Send a message """

    # Get channels
    channels = channels_gl

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
        return render_template("message.html", channel=channel,
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
            dt = datetime.now(timezone.utc)
            message["timestamp"] = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
            channel_index = channels.index(channel)
            channels_gl[channel_index]["messages"].append(message)
            
        # Redirect user to channel page
        return redirect(url_for('channel', name=channel['name']))

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)
