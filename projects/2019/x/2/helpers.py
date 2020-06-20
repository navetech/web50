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


def not_login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is not None:
            return redirect("/home")
        return f(*args, **kwargs)
    return decorated_function


def login_check(users):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            user_id = session.get("user_id")
            if user_id is None:
                session.clear()
                return redirect("/login")

            for user in users:
                if user.id == user_id:
                    return func(*args, **kwargs)
            session.clear()
            return redirect("/login")
        return decorated_function
    return decorator


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


def append_id_to_filename(file_id, filename, max_seq_number):

    # Append file id precededed by zeros to the beginning of filename
    d = 0
    n = max_seq_number
    while n > 0:
        d += 1
        n //= 10
    f = "0" + str(d)
    p = "{:" + f + "}"
    x = f"{p}".format(file_id)
    appended_name = x + "-" + filename

    return appended_name


from datetime import tzinfo, timedelta, datetime

class ClientTimezone(tzinfo):

    def utcoffset(self, dt):
        offset = session.get("timezone_offset")
        return timedelta(seconds=offset)

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return session.get("timezone")


import locale

def get_timestamp():
    tz = ClientTimezone()
    dt = datetime.now(tz)

    loc_save = locale.getlocale(locale.LC_CTYPE)
    loc = session.get("locale")
    locale.setlocale(locale.LC_TIME, loc)

#   timestamp = dt.isoformat()
    timestamp = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")

    (language_code, encoding) = loc_save
    # language_code format returned by getlocale is like 'pt_BR' but 
    # language_code format required by setlocale is like 'pt-BR' 
    language_code = language_code.replace("_", "-", 1)
    locale.setlocale(locale.LC_TIME, language_code)

    return timestamp
