import os

from datetime import datetime
from datetime import date

from flask import Flask, session, render_template, request, flash, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology, query_books


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

# Set rating limits
rating_min = 1
rating_max = 5


@app.route("/")
@login_required
def index():
    """ Home page """

    # Redirect user to search page
    return redirect("/search")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """ Search for a book """

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":

        # Query books with last query key
        books_query_key = session.get("books_query_key")
        books = query_books(db, books_query_key)

        return render_template("search.html", books=books, searched=False)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        search_key = request.form.get("search-key").strip()
        if not search_key:

            # Query books with last query key
            books_query_key = session.get("books_query_key")
            books = query_books(db, books_query_key)

            return render_template("search.html", books=books, searched=False)

        # Query books with all query key
        try:
            year = int(search_key)
        except ValueError:
            year = None

        search_key = "%" + search_key + "%"

        books_query_key = {}
        books_query_key["all"] = {}
        books_query_key["all"]["search_key"] = search_key
        books_query_key["all"]["year"] = year
        books_query_key["author"] = None
        books_query_key["year"] = None
        session["books_query_key"] = books_query_key

        books = query_books(db, books_query_key)

        return render_template("search.html", books=books, searched=True)

    else:
        return apology("invalid method", 403)


@app.route("/books/<string:author>/", methods=["GET"])
@login_required
def books_by_author(author):
    """ Show books by author """

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":

        # Query books with author query key
        books_query_key = {}
        books_query_key["all"] = None
        books_query_key["author"] = author
        books_query_key["year"] = None
        session["books_query_key"] = books_query_key

        books = query_books(db, books_query_key)

        return render_template("search.html", books=books, searched=True)

    else:
        return apology("invalid method", 403)


@app.route("/books/<int:year>/", methods=["GET"])
@login_required
def books_in_year(year):
    """ Show books in year """

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":

        # Query books with year query key
        books_query_key = {}
        books_query_key["all"] = None
        books_query_key["author"] = None
        books_query_key["year"] = year
        session["books_query_key"] = books_query_key

        books = query_books(db, books_query_key)

        return render_template("search.html", books=books, searched=True)

    else:
        return apology("invalid method", 403)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""

    # Forget any user_id
    session.clear()

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("register.html")

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Ensure fullname was submitted
        fullname = request.form.get("fullname")
        if not fullname:
            return apology("must provide full name", 403)

        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            return apology("must provide password", 403)

        # Ensure password confirmation was submitted
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("must provide password confirmation", 403)

        if not password == confirmation:
            return apology("password confirmation does not match", 403)

        # Query database for username
        user = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username}).fetchall()

        # Ensure username does not exists
        if user:
            return apology("username already exists", 403)

        # Insert user into database
        db.execute("INSERT INTO users (username, password, fullname) VALUES \
                    (:username, :password, :fullname)",
                   {"username": username, "password": generate_password_hash(password),
                    "fullname": fullname})
        db.commit()

        # Query database for username
        user = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username}).fetchone()

        # Ensure user was inserted
        if not user:
            return apology("internal server error", 500)

        # Remember which user has logged in
        session["user_id"] = user.id
        session["user_fullname"] = user.fullname

        # Report message
        flash('You were successfully logged in')
        flash(user.fullname)

        # Redirect user to home page
        return redirect("/")

    # User reached route not via GET neither via POST
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
            return apology("must provide username", 403)

        # Ensure password was submitted
        password = request.form.get("password")
        if not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        user = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username}).fetchone()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.password, password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user.id
        session["user_fullname"] = user.fullname

        # Report message
        flash('You were successfully logged in')
        flash(user.fullname)

        # Redirect user to home page
        return redirect("/")

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to home page
    return redirect("/")


@app.route("/book/<string:isbn>")
@login_required
def book(isbn):
    """Show book's data """

    # Query database for book
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    # Query database for book reviews
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id",
                         {"book_id": book.id}).fetchall()

    reviews_count = len(reviews)

    # Build reviews data
    reviews_data = []
    s = 0
    ratings_count = 0
    comments_count = 0
    for review in reviews:
        rating = review["rating"]
        if rating and rating >= rating_min and rating <= rating_max:
            ratings_count += 1
            s += rating
        else:
            rating = None

        comment = review.comment.strip()
        if comment:
            comments_count += 1

        # Query database for book reviews
        reviewer = db.execute("SELECT * FROM users WHERE id = :reviewer_id",
                              {"reviewer_id": review.reviewer_id}).fetchone()

        review_data = {}
        review_data["reviewer"] = reviewer.fullname
        review_data["rating"] = review.rating
        review_data["comment"] = comment

        dt = datetime.fromisoformat(str(review.timestamp))
        cdt = dt.ctime()
        tzn = dt.tzname()
        review_data["datetime"] = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")

        reviews_data.append(review_data)

    if ratings_count != 0:
        average_rating = s / ratings_count
    else:
        average_rating = None

    return render_template("book.html", book=book, average_rating=average_rating,
                           ratings_count=ratings_count, comments_count=comments_count,
                           reviews_count=reviews_count, reviews=reviews_data)


@app.route("/review/<string:book_isbn>/<int:user_id>", methods=["GET", "POST"])
@login_required
def review(book_isbn, user_id):
    """ Do a review """

    # Query database for book
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()

    # Query database for user
    reviewer = db.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": user_id}).fetchone()

    # Query database for review
    review = db.execute("SELECT * FROM reviews WHERE reviewer_id = :reviewer_id AND \
                         book_id = :book_id",
                        {"reviewer_id": reviewer.id, "book_id": book.id}).fetchone()

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("review.html", book=book, reviewer=reviewer.fullname,
                               review=review)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        rating = request.form.get("rating")
        if not rating:
            rating = 0

        if review:
            # Update review into database
            db.execute("UPDATE reviews SET date = 'now', time = 'now', rating = :rating, \
                        comment = :comment, timestamp = 'now' \
                        WHERE reviewer_id = :reviewer_id AND book_id = :book_id",
                       {"reviewer_id": reviewer.id, "book_id": book.id,
                        "rating": rating, "comment": request.form.get("comment")})
            db.commit()

        else:
            # Insert review into database
            db.execute("INSERT INTO reviews (reviewer_id, book_id, date, time, rating, comment, timestamp) \
                        VALUES (:reviewer_id, :book_id, 'now', 'now', :rating, :comment, 'now')",
                       {"reviewer_id": reviewer.id, "book_id": book.id,
                        "rating": rating, "comment": request.form.get("comment")})
            db.commit()

        # Redirect user to book page
        return redirect("/books/" + book['isbn'])

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/unregister")
@login_required
def unregister():
    """Unregister the user"""

    user_id = session["user_id"]

    # Delete user reviews from database
    db.execute("DELETE FROM reviews WHERE reviewer_id = :reviewer_id", {"reviewer_id": user_id})
    db.commit()

    # Delete user from database
    db.execute("DELETE FROM users WHERE id = :user_id", {"user_id": user_id})
    db.commit()

    # Forget any user_id
    session.clear()

    # Redirect user to home page
    return redirect("/")


@app.route("/unregisterall")
@login_required
def unregister_all():
    """Unregister all users"""

    # Query database for all users
    users = db.execute("SELECT * FROM users").fetchall()

    # Repeat for each user
    for user in users:

        # Delete user reviews from database
        db.execute("DELETE FROM reviews WHERE reviewer_id = :reviewer_id", {"reviewer_id": user.id})
        db.commit()

        # Delete user from database
        db.execute("DELETE FROM users WHERE id = :user_id", {"user_id": user.id})
        db.commit()

    # Forget any user_id
    session.clear()

    # Redirect user to home page
    return redirect("/")


@app.route("/allusers")
def all_users():
    """ Show all users"""

    # Query database for all users
    users = db.execute("SELECT * FROM users").fetchall()

    return render_template("allusers.html", users=users)


@app.route("/allreviews")
def all_reviews():
    """ Show all reviews"""

    # Query database for all reviews
    reviews = db.execute("SELECT * FROM reviews").fetchall()

    return render_template("allreviews.html", reviews=reviews)
