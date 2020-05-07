import os

from flask import Flask, session, render_template, request, flash, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from helpers import login_required


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

"""
with engine.connect() as connection:
    result = connection.execute("select username from users")
    for row in result:
        print("username:", row['username'])
"""
con = engine.connect()

@app.route("/")
@login_required
def index():
#    return "Project 1: TODO"

    """ Home page """

    # Redirect user to search page
    return redirect("/search")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """ Search for a book"""

    # Empty books list
    books = []

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("search.html", books=books)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Ensure search key was submitted
        search_key = request.form.get("search-key")
        if not search_key:
            # Redirect user to search page
            return redirect("/search")

        # Query database for books
        search_key = "%" + search_key + "%"
        books = db.execute("SELECT * FROM books where \
                            isbn ILIKE :search_key OR title ILIKE :search_key OR \
                            author ILIKE :search_key",
                           {"search_key":search_key})

        return render_template("search.html", books=books)

    else:
        return apology("invalid method", 403)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("login.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            session.clear()
            return "must provide username", 403
#            return apology("must provide username", 403)

        """
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["username"]

        # Report message
        flash('You were successfully logged in')
        flash(request.form.get("username"))
        """
        session["user_id"] = 1
        session["user_name"] = username

        flash('You were successfully logged in')
        flash(username)

        # Redirect user to home page
        return redirect("/")

    else:
        return apology("invalid method", 403)



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/books/<string:book_isbn>")
@login_required
def book(book_isbn):
    """Show book info"""

    # Query database for book
    # Nao pode usar con.execute pois ocorre erro no placeholder :isbn
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()

    user_id = 999

    reviews = []
    reviews.append({"reviewer": "Ladislau", "date":"07/05/2020 11:45", "rating": 4, "comment": "review 1"})
    reviews.append({"reviewer": "Lygia", "date":"07/05/2020 11:45", "rating": 5})
    reviews.append({"reviewer": "Filipe", "date":"07/05/2020 11:45", "comment": "review 3"})
    reviews.append({"reviewer": "Maira", "date":"07/05/2020 11:45", "rating": None, "comment": None})
    reviews.append({"reviewer": "Julia", "date":"07/05/2020 11:45", "rating": 4, "comment": ""})
    reviews.append({"reviewer": "Jose", "date":"07/05/2020 11:45", "rating": 4, "comment": "Review 6"})
    
    reviews_count = len(reviews)
    
    s = 0
    ratings_count = 0
    comments_count = 0
    for review in reviews:
        if "rating" in review and review["rating"]:
            ratings_count += 1
            s += review["rating"]

        if "comment" in review and review["comment"]:
            comments_count += 1

    average_rating = s / ratings_count

    return render_template("book.html", user_id=user_id, book=book, average_rating=average_rating,
        ratings_count=ratings_count, comments_count=comments_count, reviews_count=reviews_count,
        reviews=reviews)


@app.route("/review/<string:book_isbn>/<int:user_id>", methods=["GET", "POST"])
@login_required
def review(book_isbn, user_id):
    """ Do a review """ 

    # Query database for book
    # Nao pode usar con.execute pois ocorre erro no placeholder :isbn
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()

    # Query database for user
#    user = db.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": user_id}).fetchone()
    reviewer = str(user_id)

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("review.html", book=book, reviewer=reviewer)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        return "Review Done"
