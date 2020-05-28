import os

from flask import Flask, session, redirect, request, render_template, flash
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

users=[]
channels = []


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
        users.append(user)

        # Remember which user has logged in
        session["user"] = user

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

        # Remember which user has logged in
        session["user"] = user

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

    # Forget which user had logged in
    session["user"] = None

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

            # Unregister user
            user = session["user"]
            try:
                users.remove(user)
            except:
                return apology("user does not exist", 403)

            # Forget which user had logged in
            session["user"] = None

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

        # Create channel
        channel = {}
        channel["name"] = name
        channel["owner"] = session["user"]
        channel["timestamp"] = "28/05/2020 13:00"
        channel["messages"] = []
        channels.append(channel)

        return render_template("channels.html", channels=channels)

    else:
        return apology("invalid method", 403)


@app.route("/channel/<string:name>")
@login_required
def channel(name):
    """Show channel's messages """

    # Ensure channel exists
    for channel in channels:
        if channel["name"] == name:
            return render_template("channel.html", channel=channel)

    return apology("channel does not exists", 403)

    """
    # Query database for book
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    # Set database timezone
    gmt_offset = session["gmt_offset"]
    minutes_offset = (int(abs(gmt_offset) / 60)) % 60
    h = gmt_offset // 3600
    hours_offset = ((h > 0) - (h < 0)) * (abs(h) % 24)
    db.execute(f"SET LOCAL TIME ZONE INTERVAL \'{hours_offset:+03}:{minutes_offset:02}\' \
                HOUR TO MINUTE")
    
    # Query database for book reviews
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id ORDER BY timestamp DESC",
                         {"book_id": book.id}).fetchall()

    reviews_count = len(reviews)

    # Build reviews data
    reviews_data = []
    s = 0
    ratings_count = 0
    comments_count = 0
    for review in reviews:
        rating = review["rating"]
        if rating:
            if rating >= rating_min and rating <= rating_max:
                ratings_count += 1
                s += rating
            else:
                rating = None

        comment = review.comment
        if comment:
            if comment.strip():
                comments_count += 1
            else:
                comment = None

        # Query database for book reviewer
        reviewer = db.execute("SELECT * FROM users WHERE id = :reviewer_id",
                              {"reviewer_id": review.reviewer_id}).fetchone()

        review_data = {}
        review_data["reviewer"] = reviewer.name
        review_data["rating"] = rating
        review_data["comment"] = comment

        dt = datetime.fromisoformat(str(review.timestamp))

        # Set locale for formatting datetime according local language
        language_code = session["language_code"]
        locale.setlocale(locale.LC_TIME, language_code)

        review_data["datetime"] = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")

        reviews_data.append(review_data)

    if ratings_count != 0:
        average_rating = f"{s / ratings_count:.2f}"
    else:
        average_rating = None
 
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": f"{apikey}", "isbns": f"{isbn}"})

    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
      
    review_adds = res.json()["books"][0]

    return render_template("book.html", book=book, average_rating=average_rating,
                           ratings_count=ratings_count, comments_count=comments_count,
                           reviews_count=reviews_count, reviews=reviews_data,
                           review_adds=review_adds, reviews_cfg=reviews_cfg)
    """
