import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helper import apology, login_required

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///project.db")
db.execute("CREATE TABLE IF NOT EXISTS users(ID INTEGER PRIMARY KEY, username varchar(255) NOT NULL, pass varchar(255) NOT NULL)")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    val = '+'

    user = session['user_id']
    saxel = db.execute(f"SELECT username FROM users WHERE ID = {user}")
    saxeli = saxel[0]["username"]

    traki = db.execute(f"SELECT complete FROM {saxeli}pt")

    dat = db.execute(f"SELECT * FROM {saxeli} GROUP BY time")
    data = len(db.execute(f"SELECT time FROM {saxeli}"))

    med = len(db.execute(f"SELECT meds FROM {saxeli}meds"))

    rows = db.execute(f"SELECT * FROM {saxeli}meds GROUP BY meds")

    ssp = db.execute(f"SELECT blood, sugar, pulse FROM {saxeli} GROUP BY time HAVING time = time")

    racxa = []
    mtliani = []

    if request.method == "GET":
        return render_template("index.html", dat=dat, data=data, med=med, rows=rows, ssp=ssp, traki=traki, val=val)
    else:
        for i in range(data):
            for l in range(med):
                racxa.append(request.form.get(f"symbol{i}{l}"))
        for x in range(data):
            mtliani.append(racxa[0:med])
            del racxa[0:med]

        for k in range(data):
            if all(x == '\u2714' for x in mtliani[k]) == True:
                db.execute(f"UPDATE {saxeli}pt SET complete = '\u2714' WHERE rowid={k+1}")
                traki = db.execute(f"SELECT complete FROM {saxeli}pt")


        return render_template("index.html", dat=dat, data=data, med=med, rows=rows, ssp=ssp, traki=traki, val=val)


@app.route("/mtavari", methods=["GET"])
def mtavari():
    session.clear()
    if request.method == "GET":
        return render_template("entry.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("apology.html", bottom="Must provide Username and Password", top=403)

        xazebi = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))

        if len(xazebi) != 1 or not check_password_hash(xazebi[0]["pass"], request.form.get("password")):
            return render_template("apology.html", bottom="Invalid Username or Password", top= 403)

        session["user_id"] = xazebi[0]["ID"]

        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        usr = len(db.execute("SELECT username FROM users"))
        usernames = []
        for i in range(usr):
            usernames.append(db.execute("SELECT username FROM users")[i]["username"])

        if not username or not password or not confirm:
            return render_template("apology.html", bottom="Please Input All Of The Fields", top=403)
        if password != confirm:
            return render_template("apology.html", bottom="Passwords Must Match", top=403)
        if username in usernames:
            return render_template("apology.html", bottom ="That username is taken", top = 403)
        else:
            db.execute("INSERT INTO users (username, pass) VALUES (:username, :password)", username=username, password=generate_password_hash(password))
            db.execute(f"CREATE TABLE IF NOT EXISTS {username}(time datetime NOT NULL, blood int NOT NULL, pulse int NOT NULL,sugar int NOT NULL, bool BOOLEAN)")
            db.execute(f"CREATE TABLE IF NOT EXISTS {username}meds(meds varchar(255) NOT NULL, bool BOOLEAN)")
            db.execute(f"CREATE TABLE IF NOT EXISTS {username}pt(time datetime NOT NULL,complete varchar(255) NOT NULL DEFAULT '\u2718')")
        return redirect("/mtavari")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/mtavari")


@app.route("/BPS", methods=["GET", "POST"])
@login_required
def BPS():
    if request.method == ("GET"):
        return render_template("bps.html")
    else:
        user = session['user_id']
        saxel = db.execute(f"SELECT username FROM users WHERE ID = {user}")
        saxeli = saxel[0]["username"]
        sisxli = request.form.get("blood")
        pulsi = request.form.get("pulse")
        shaqari = request.form.get("sugar")
        if not sisxli or not pulsi or not shaqari:
            return render_template("apology.html", bottom="Fields Must Not Be Empty", top=403)
        db.execute(f"INSERT INTO {saxeli}(time,blood,pulse,sugar,bool) VALUES ( datetime('now'),{sisxli},{pulsi},{shaqari},1)")
        db.execute(f"INSERT INTO {saxeli}pt(time) VALUES (datetime('now'))")
        return redirect("/")


@app.route("/meds", methods=["GET"])
@login_required
def meds():
    if request.method == "GET":
        user = session['user_id']
        saxel = db.execute(f"SELECT username FROM users WHERE ID = {user}")
        saxeli = saxel[0]["username"]
        lis = db.execute(f"SELECT meds FROM {saxeli}meds")
        lislen = len(lis)
        return render_template("medikamentebi.html", lis=lis, lislen=lislen)

@app.route("/AddMeds", methods=["GET", "POST"])
@login_required
def addmeds():
    if request.method == "GET":
        return render_template("meds.html")
    else:
        user = session['user_id']
        saxel = db.execute(f"SELECT username FROM users WHERE ID = {user}")
        saxeli = saxel[0]["username"]
        wamlebi = request.form.get("meds")
        if not wamlebi:
            return render_template("apology.html", bottom="Field Must Not Be Empty", top=403)
        db.execute(f"INSERT INTO {saxeli}meds(meds) VALUES ('{wamlebi}')")
        db.execute(f"ALTER TABLE {saxeli}pt ADD {wamlebi} varchar(255)")
    return redirect("/")

@app.route("/ClearMeds", methods=["GET", "POST"])
@login_required
def clear():
    if request.method == "GET":
        user = session['user_id']
        saxel = db.execute(f"SELECT username FROM users WHERE ID = {user}")
        saxeli = saxel[0]["username"]
        lis = db.execute(f"SELECT meds FROM {saxeli}meds")
        lislen = len(lis)
        return render_template("amoshla.html",lis=lis, lislen=lislen)
    else:
        user = session['user_id']
        saxel = db.execute(f"SELECT username FROM users WHERE ID = {user}")
        saxeli = saxel[0]["username"]
        raqvia = request.form.get("saxl")
        db.execute(f"DELETE FROM {saxeli}meds WHERE meds = '{raqvia}'")
        return redirect("/meds")


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    if request.method == "GET":
        return render_template("change.html")
    else:
        user = session['user_id']
        paroli = request.form.get("pass")
        paroli2 = request.form.get("pass1")
        paroli3 = request.form.get("pass2")
        parol = db.execute(f"SELECT pass FROM users WHERE id = {user}")
        if check_password_hash(parol, paroli) == 1:
            return render_template("apology.html", bottom="Incorect password", top=403)
        else:
            if paroli2 != paroli3:
                return render_template("apology.html", bottom="New passwords should match", top=403)
            else:
                db.execute(f"UPDATE users SET pass = (:password) WHERE id = {user}", password=generate_password_hash(paroli2))
                return render_template("gamovida.html")

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "GET":
        return render_template("washla.html")
    else:
        yes = request.form.get("yes")
        if yes is not None:
            user = session['user_id']
            saxel = db.execute(f"SELECT username FROM users WHERE ID = {user}")
            saxeli = saxel[0]["username"]
            db.execute(f"DELETE FROM {saxeli}")
            db.execute(f"DELETE FROM {saxeli}pt")
        else:
            return redirect("/")

    return redirect("/")
