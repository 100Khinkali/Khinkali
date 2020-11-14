import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user = session['user_id']
    saxel = db.execute(f"SELECT username FROM users WHERE id = {user}")
    saxeli = saxel[0]["username"]

    cas = db.execute(f"SELECT cash FROM users WHERE id = {user}")
    cash = cas[0]["cash"]

    rows = db.execute(f"SELECT * FROM {saxeli} GROUP BY Name")
    saxelebi = len(db.execute(f"SELECT Name FROM {saxeli} GROUP BY Name"))
    cifri = len(db.execute(f"SELECT Name FROM {saxeli}"))



    quote = {}
    mayutiL = []
    for i in range(saxelebi):
        quote[i] = lookup((db.execute(f"SELECT Name FROM {saxeli} GROUP BY Name"))[i]["Name"])
    for j in range(cifri):
        mayutiL.append(db.execute(f"SELECT Amount FROM {saxeli}")[j]["Amount"])
    fulebi = usd(cash + sum(mayutiL))
    mayuti = db.execute(f"SELECT Name, SUM (Amount), SUM (Shares) FROM {saxeli} GROUP BY Name HAVING Name = Name")

    return render_template("index.html", rows=rows, cash=usd(cash), quote=quote, saxelebi=saxelebi, mayuti=mayuti, fulebi=fulebi)




@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        quote = {}
        quote = lookup(request.form.get("symbol"))
        znaki = request.form.get('symbol')
        wilebi = int(request.form.get('shares'))
        user = session['user_id']
        saxel = db.execute(f"SELECT username FROM users WHERE id = {user}")
        saxeli = saxel[0]["username"]

        db.execute(f"CREATE TABLE IF NOT EXISTS {saxeli}(Name varchar(255) NOT NULL,Shares int NOT NULL, Amount int NOT NULL, dro datetime NOT NULL)")

        if znaki not in quote["symbol"] or wilebi < 0:
            return render_template("apology.html", bottom = "Invalid Symbol or A Negative Number", top=403)
        else:
            dolla = int(wilebi) * float(quote["price"])
            db.execute(f"UPDATE users SET cash = cash - {dolla} WHERE id = {user}")
            db.execute(f"INSERT INTO {saxeli}(Name, Shares, Amount, dro) Values (:znaki, {wilebi}, {dolla}, datetime('now'))", znaki=znaki)



    return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user = session['user_id']
    saxel = db.execute(f"SELECT username FROM users WHERE id = {user}")
    saxeli = saxel[0]["username"]
    saxelebi = len(db.execute(f"SELECT Name FROM {saxeli}"))
    rows = db.execute(f"SELECT * FROM {saxeli}")
    quote = {}
    for i in range(saxelebi):
        quote[i] = lookup((db.execute(f"SELECT Name FROM {saxeli}"))[i]["Name"])

    return render_template("history.html", saxelebi=saxelebi, rows=rows, quote=quote)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

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

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    if request.method == "POST":
        quote = {}
        quote = lookup(request.form.get("symbol"))
        if request.form.get("symbol") in quote["symbol"]:
            return render_template("quoted.html", quote=quote)
        else:
            return render_template("apology.html", bottom = "That stonk doesnt exist", top = 403)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""


    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        usr = len(db.execute("SELECT username FROM users"))
        usernames = []
        for i in range(usr):
            usernames.append(db.execute("SELECT username FROM users")[i]["username"])

        if not username:
            return render_template("apology.html", bottom ="You must provide a Name", top = 403)
        password = request.form.get("password")
        if not password:
            return render_template("apology.html", bottom ="You Must provide a Password", top = 403)
        confirmation = request.form.get("confirm")
        if not confirmation:
            return render_template("apology.html", bottom ="You Must confirm your Password", top = 403)
        if password != confirmation:
            return render_template("apology.html", bottom ="Your passwords must match", top = 403)
        if username in usernames:
            return render_template("apology.html", bottom ="That username is taken", top = 403)
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)", username=username, password=generate_password_hash(password))
            db.execute(f"CREATE TABLE IF NOT EXISTS {request.form.get('username')}(Name varchar(255) NOT NULL,Shares int NOT NULL, Amount int NOT NULL, dro datetime NOT NULL)")




    return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        user = session['user_id']
        saxel = db.execute(f"SELECT username FROM users WHERE id = {user}")
        saxeli = saxel[0]["username"]
        saxeli = db.execute(f"SELECT Name FROM {saxeli} GROUP BY Name")
        imia = len(saxeli)
        return render_template("sell.html", saxeli=saxeli, imia=imia)
    else:
        symbol = request.form.get("symbol")
        wilebi = int(request.form.get("shares"))
        user = session['user_id']
        saxel = db.execute(f"SELECT username FROM users WHERE id = {user}")
        saxeli = saxel[0]["username"]
        quote = {}
        quote = lookup(symbol)
        # Im deliberetely leaving 0 values for display, because i think it would be user experience
        if wilebi > int((db.execute(f"SELECT Shares, SUM (Shares) FROM {saxeli} GROUP BY Name HAVING Name = '{symbol}'"))[0]["SUM (Shares)"]):
            return render_template("apology.html", bottom="You dont own that many shares", top=403)
        else:
            dolla = int(wilebi) * float(quote["price"])
            db.execute(f"INSERT INTO {saxeli}(Name, Shares, Amount, dro) Values ('{symbol}', {-wilebi}, {-dolla}, datetime('now'))")
            db.execute(f"UPDATE users SET cash = cash + {dolla} WHERE id = {user}")
        return redirect("/")

@app.route("/addfunds", methods=["GET", "POST"])
@login_required
def addfunds():
    if request.method == "GET":
        return render_template("funds.html")
    else:
        user = session['user_id']
        fuli = int(request.form.get("amount"))
        saxel = request.form.get("saxel")
        if saxel != ((db.execute(f"SELECT username FROM users WHERE id = {user}"))[0]["username"]):
            return render_template("apology.html", bottom="No such Username", top=403)
        else:
            db.execute(f"UPDATE users SET cash = cash + {fuli} WHERE id = {user}")
    return redirect("/")

@app.route("/donate", methods=["GET","POST"])
@login_required
def donate():
    if request.method == "GET":
        return render_template("donate.html")
    else:
        fuli = int(request.form.get("amount"))
        user = session['user_id']
        mayuti = (db.execute(f"SELECT cash FROM users WHERE id = {user}"))[0]["cash"]
        if mayuti < fuli:
            return render_template("apology.html", bottom="You dont own that much", top=403)
        else:
            db.execute(f"UPDATE users SET cash = cash - {fuli} WHERE id = {user}")
    return render_template("chairicxa.html", bottom="Youre the best", top=42069)

@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    if request.method == "GET":
        return render_template("pass.html")
    else:
        user = session['user_id']
        paroli = request.form.get("pass")
        paroli1 = request.form.get("pass1")
        paroli2 = request.form.get("pass2")
        fash = db.execute(f"SELECT hash FROM users WHERE id = {user}")
        if check_password_hash(fash, paroli) == 1:
            return render_template("apology.html", bottom="Incorect password", top=403)
        else:
            if paroli1 != paroli2:
                return render_template("apology.html", bottom="New passwords should match", top=403)
            else:
                db.execute(f"UPDATE users SET hash = (:password) WHERE id = {user}", password=generate_password_hash(paroli1))
                return render_template("gamovida.html", bottom="Your password has been changed", top=200)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
