import os
import requests
import json

from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from statistics import mean
from helper import login_required

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
db.execute("CREATE TABLE IF NOT EXISTS users(id int PRIMARY KEY, username varchar(255) NOT NULL, pass varchar(255) NOT NULL)")
db.commit()

res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "4bCn32jGbsLwL9xJ6Pfvtg", "isbns": "148234873X"})

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method=="GET":
		return render_template("register.html")
	else:
		username = request.form.get("login")
		password = request.form.get("pass")
		password1 = request.form.get("pass1")

		checkuser = db.execute("SELECT * FROM users WHERE username = :username",
                        	{"username":request.form.get("username")}).fetchone()

		if checkuser:
			return render_template("apology.html", text="Username Already Exists")

		if not username or not password or not password1:
			return render_template("apology.html", text="Must Provide All Details")
		elif password != password1:
			return render_template("apology.html", text="Passwords Must Match")
		else:
			db.execute("INSERT INTO users(username,pass) VALUES(:username,:password)", 
							{"username":username, "password":generate_password_hash(password)})
			db.commit()
		return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
	session.clear()
	if request.method == "GET":
		return render_template("login.html")
	else:
		username = request.form.get("username")
		password = request.form.get("pass")

	if not username or not password:
		return render_template("apology.html", text="Must Provide All Details")

	checkuser = db.execute("SELECT * FROM users WHERE username = :username", 
											{"username":username}).fetchone()

	if not checkuser or not check_password_hash(checkuser["pass"], password):
		return render_template("apology.html", text="Username or Password Invalid")

	session['user_id'] = checkuser["id"]

	return redirect("/main")

@app.route("/logout")
@login_required
def logout():
	session.clear()
	return redirect("/	")

@app.route("/main", methods=["GET"])
@login_required
def main():
	return render_template("main.html")

@app.route("/books", methods=["GET", "POST"])
@login_required
def books():
	if not request.form.get("search"):
		return render_template("apology.html", text="Must Provide Book Title, Author or ISBN Number")

	if request.method == "POST": 
		Q = request.form.get("search").title()

		books = db.execute(f"SELECT title, author, year, isbn FROM books WHERE title LIKE '%{Q}%' OR author LIKE '%{Q}%' OR isbn LIKE '%{Q}%'").fetchall()
		if not books:
			return render_template("apology.html", text="No Such Book")

		leng = len(books)
		return render_template("books.html", books=books, leng=leng)

@app.route("/books/<isbn>", methods=["GET", "POST"])
@login_required
def info(isbn):
	db.execute("CREATE TABLE IF NOT EXISTS reviews(username varchar(255) NOT NULL, review varchar(255) NOT NULL, rating real NOT NULL, isbn varchar(20) NOT NULL)")
	db.commit()

	user = session['user_id']
	saxel = db.execute(f"SELECT username FROM users WHERE ID = {user}").fetchone()
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "4bCn32jGbsLwL9xJ6Pfvtg", "isbns": isbn})
	jeisona = res.json()['books'][0]
	book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
	review = db.execute("SELECT review, rating, username FROM reviews WHERE isbn=:isbn", {"isbn":isbn}).fetchall()
	lenview = len(review)
	usr = db.execute("SELECT username FROM reviews WHERE username=:saxel AND isbn=:isbn", {'saxel':saxel[0], "isbn":isbn}).fetchone()

	if saxel != usr:
		test=2
	elif saxel == usr:
		test=1

	if request.method == "GET":		
		return render_template("info.html", j=jeisona, book=book, review=review, lenview=lenview, test=test)
	else:
		reviewRate = request.form.get("rate")	
		reviewForm = request.form.get("review")

		if test == 2:
			db.execute("INSERT INTO reviews(username, review, rating, isbn) VALUES(:user, :review, :rating, :isbn)",
									{"user":saxel[0], "review":reviewForm, "rating":reviewRate, "isbn":isbn})
			db.commit()

		return redirect("/books/" + isbn)

@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):
	number = db.execute("SELECT isbn FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()

	if isbn is None:
		return jsonify({"error": "You must enter an isbn Number"}), 422
	elif isbn != number[0]:
		return jsonify({"error": "No Such Book"}), 404

	books = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
	rev = db.execute("SELECT review FROM reviews WHERE isbn=:isbn", {"isbn":isbn}).fetchall()

	rate = db.execute("SELECT rating FROM reviews WHERE isbn=:isbn", {"isbn":isbn}).fetchall()

	listi = []

	for i in range(len(rate)):
		listi.append(rate[i][0])

	return jsonify({
		"title": books['title'],
		"author": books['author'],
		"year": books['year'],
		"isbn": books['isbn'],
		"review_count": len(rev),
		"average_score": mean(listi)
		})