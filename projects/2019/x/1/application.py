import os

from datetime import datetime
import time
import locale

from flask import Flask, session, render_template, request, flash, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

import requests

from helpers import login_required, apology, query_books


app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Check for environment variables
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

apikey = os.getenv("API_KEY")
if not apikey:
    raise RuntimeError("API_KEY is not set")


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Set reviews configuration
rating_min = 1
rating_max = 5
ratings_cfg = {}
ratings_cfg["min"] = rating_min
ratings_cfg["max"] = rating_max

comment_columns_max = 80
comment_rows_number = 10
comment_max_length = comment_columns_max * comment_rows_number
comments_cfg = {}
comments_cfg["columns_max"] = comment_columns_max
comments_cfg["rows_number"] = comment_rows_number
comments_cfg["max_length"] = comment_max_length

reviews_cfg = {}
reviews_cfg["ratings"] = ratings_cfg
reviews_cfg["comments"] = comments_cfg


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

        # Ensure name was submitted
        name = request.form.get("name")
        if not name:
            return apology("must provide name", 403)

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
        db.execute("INSERT INTO users (username, password, name) VALUES \
                    (:username, :password, :name)",
                   {"username": username, "password": generate_password_hash(password),
                    "name": name})
        db.commit()

        # Query database for user
        user = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username}).fetchone()

        # Ensure user was inserted
        if not user:
            return apology("internal server error", 500)

        # Remember which user has logged in
        session["user_id"] = user.id
        session["user_name"] = user.name

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
        flash(' / ')
        flash(user.username)

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
        session["user_name"] = user.name

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
        flash(' / ')
        flash(user.username)

        # Redirect user to home page
        return redirect("/")

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to home page
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Show/Change user profile"""

    # Query database for user
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      {"user_id": user_id}).fetchone()

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("profile.html", user=user)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        # Ensure data submitted are proper
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not name:
            name = user.name

        if not username:
            username = user.username

        if not password:
            if confirmation:
                return apology("must provide password", 403)
        else:
            if not confirmation:
                return apology("must provide password confirmation", 403)
            else:
                if not password == confirmation:
                    return apology("password confirmation does not match", 403)

        # Ensure username does not exists
        if username != user.username:
            other_user = db.execute("SELECT * FROM users WHERE username = :username",
                                    {"username": username}).fetchall()
            if other_user:
                return apology("username already exists", 403)

        # Update profile into database
        if name != user.name or username != user.username or password:
            db.execute("UPDATE users SET username = :username, password = :password, \
                        name = :name WHERE id = :user_id",
                       {"user_id": user_id, "username": username,
                        "password": generate_password_hash(password), "name": name})
            db.commit()

            # Ensure profile was changed
            user = db.execute("SELECT * FROM users WHERE id = :user_id",
                              {"user_id": user_id}).fetchone()

            if not user:
                return apology("internal server error", 500)

            # Remember name of user that is logged in
            session["user_name"] = user.name

            # Report message
            flash('You successfully changed profile')
            flash(user.name)
            flash(' / ')
            flash(user.username)

        # Redirect user to home page
        return redirect("/")

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/book/<string:isbn>")
@login_required
def book(isbn):
    """Show book's data """

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


@app.route("/review/<string:book_isbn>/<int:user_id>", methods=["GET", "POST"])
@login_required
def review(book_isbn, user_id):
    """ Do a review """

    # Query database for book
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()

    # Query database for review
    review = db.execute("SELECT * FROM reviews WHERE reviewer_id = :reviewer_id AND \
                         book_id = :book_id",
                        {"reviewer_id": user_id, "book_id": book.id}).fetchone()

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("review.html", book=book, review=review,
                               reviews_cfg=reviews_cfg)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        rating = request.form.get("rating")
        comment = request.form.get("comment")
        if comment:
            comment_stripped = comment.strip()
        else:
            comment_stripped = None

        if review:
            # Delete review from database
            db.execute("DELETE FROM reviews WHERE reviewer_id = :reviewer_id AND \
                        book_id = :book_id",
                       {"reviewer_id": user_id, "book_id": book.id})
            db.commit()

        if rating and comment_stripped:

            # Insert review into database with rating and comment
            db.execute("INSERT INTO reviews (reviewer_id, book_id, rating, comment, timestamp) \
                        VALUES (:reviewer_id, :book_id, :rating, :comment, 'now')",
                       {"reviewer_id": user_id, "book_id": book.id,
                        "rating": rating, "comment": comment})
            db.commit()

        elif rating:
            
            # Insert review into database with rating and without comment
            db.execute("INSERT INTO reviews (reviewer_id, book_id, rating, timestamp) \
                        VALUES (:reviewer_id, :book_id, :rating, 'now')",
                       {"reviewer_id": user_id, "book_id": book.id, "rating": rating})
            db.commit()

        elif comment_stripped:

            # Insert review into database with comment and without rating
            db.execute("INSERT INTO reviews (reviewer_id, book_id, comment, timestamp) \
                        VALUES (:reviewer_id, :book_id, :comment, 'now')",
                       {"reviewer_id": user_id, "book_id": book.id, "comment": comment})
            db.commit()

        # Redirect user to book page
        return redirect(url_for('book', isbn=book['isbn']))

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)


@app.route("/api/books/<string:isbn>")
def book_api(isbn):
    """ Return details about a single book """

    # Query database for book
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

    # Make sure book exists
    if not book:
        return jsonify({"error": "book not found"}), 404

    # Query database for book reviews
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id ORDER BY timestamp DESC",
                         {"book_id": book.id}).fetchall()

    reviews_count = len(reviews)

    # Build reviews data
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

    if ratings_count != 0:
        average_rating = f"{s / ratings_count:.2f}"
    else:
        average_rating = None

    return jsonify(
        {
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "reviews_count": reviews_count,
            "average_rating": average_rating,
            "ratings_count": ratings_count,
            "comments_count": comments_count
        })


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

            # Delete user reviews from database
            user_id = session["user_id"]

            db.execute("DELETE FROM reviews WHERE reviewer_id = :reviewer_id",
                       {"reviewer_id": user_id})
            db.commit()

            # Delete user from database
            db.execute("DELETE FROM users WHERE id = :user_id", {"user_id": user_id})
            db.commit()

            # Forget any user_id
            session.clear()

        # Redirect user to home page
        return redirect("/")

    # User reached route not via GET neither via POST
    else:
        return apology("invalid method", 403)
