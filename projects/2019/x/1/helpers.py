from flask import redirect, session, render_template
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def query_books(db, query_key):
    """ Query books from data base """

    books = []

    if not db or not query_key:
        return books

    if query_key["all"]:
        search_key = query_key["all"]["search_key"]

        if query_key["all"]["year"]:
            year = query_key["all"]["year"]

            # Query database for books by isbn, or title, or author, or year
            books = db.execute("SELECT * FROM books WHERE \
                                isbn ILIKE :search_key OR title ILIKE :search_key OR \
                                author ILIKE :search_key OR year = :year \
                                ORDER BY author, year DESC, title",
                               {"search_key": search_key, "year": year}).fetchall()

        else:
            # Query database for books by isbn, or title, or author
            books = db.execute("SELECT * FROM books WHERE \
                                isbn ILIKE :search_key OR title ILIKE :search_key OR \
                                author ILIKE :search_key \
                                ORDER BY author, year DESC, title",
                               {"search_key": search_key}).fetchall()

    elif query_key["author"]:
        author = query_key["author"]

        # Query database for books by author
        books = db.execute("SELECT * FROM books WHERE author = :author \
                            ORDER BY year DESC, title",
                           {"author": author}).fetchall()

    elif query_key["year"]:
        year = query_key["year"]

        # Query database for books by year
        books = db.execute("SELECT * FROM books WHERE year = :year \
                            ORDER BY author, title",
                           {"year": year}).fetchall()

    return books
