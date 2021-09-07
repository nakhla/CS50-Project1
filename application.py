import os
from flask import Flask, session, render_template, request, url_for, flash, redirect, Markup, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import random
import requests
from passlib.hash import pbkdf2_sha256

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

@app.route("/")
@app.route("/home")
def home():
    books = db.execute("SELECT * FROM books").fetchall()
# shuffle books array and in jinja2 show 10 different results on each refresh for homepage as encouraging to signup
    random.shuffle(books)
    return render_template('home.html', books=books)

@app.route("/lastrated")
def lastrated():
# I used this query to fetch lastrated books with no dublicates
    books = db.execute("SELECT books.isbn, title, author, year FROM books JOIN reviews ON books.isbn = reviews.isbn GROUP BY books.isbn ORDER BY MAX(review_id) DESC LIMIT 10").fetchall()
#    books = db.execute("SELECT books.isbn, title, author, year FROM books JOIN reviews ON books.isbn = reviews.isbn ORDER BY review_id DESC LIMIT 10").fetchall()
    return render_template('lastrated.html', books=books)

@app.route("/book/<string:book_isbn>", methods=["GET", "POST"])
def book(book_isbn):

# check if user is logged in or not in order to view , search and rate books, I used Markup to write html tags in flash message
# if not logged in then show login page
    if not session.get("LoggedUserID"):
        flash(Markup('You have to login to view, search and rate books, Don\'t have an account? <a href="/register">Register</a> now it is FREE!'),"warning")
        return render_template('login.html')

# when submitting a review form by POST
    if request.method == "POST":
# fetch form fields
        rating = request.form.get("rating")
        details = request.form.get("details")
# store logged user info
        username = session["LoggedUserID"]
        LoggedUserID = db.execute("SELECT user_id FROM users WHERE username = :username",
                    {"username": username}).fetchone()
        userid = LoggedUserID["user_id"]
# search book by ISBN and userid in review table, no multiple user review for the same isbn
        row = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND isbn = :isbn",
                    {"user_id": userid , "isbn": book_isbn}).fetchall()

# check if user tries to submit another review for the same book if there is a row fetched flash you cannot submit another review
# if there is no reviews for that book by the same user then add that certian review to reviews table.
        if len(row) == 0:
            db.execute("INSERT INTO reviews (isbn, user_id, review_stars, review_details) VALUES (:isbn, :user_id, :review_stars, :review_details)",
                        {"isbn": book_isbn, "user_id": userid, "review_stars": rating, "review_details": details })
# commit
            db.commit()
            flash("your review has been submitted","success")
            return redirect(f"/book/{book_isbn}")

        else:
            flash(f"You can NOT submit another review for the same book","warning")
            return redirect(f"/book/{book_isbn}")

# when viewing a book by a simple GET
    b = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                {"isbn": book_isbn}).fetchone()
# if book is not existed and no book with such isbn
    if b is None:
        flash(f'No book with that ISBN {book_isbn}',"warning")
        books = db.execute("SELECT * FROM books").fetchall()
        random.shuffle(books)
        return render_template('home.html', books=books)

# get response from the goodreads api with key and isbn as parameters
#    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "td4eTrcOjBDtdEB1t5rF1Q", "isbns":book_isbn })
#    if res.status_code != 200:
#        raise Exception ("Error:goodreads API request unsuccessful.")
# convert goodread response to json
#    data = res.json()
# store goodread reviews average, reviews count, isbn13.
#    gd_ravg = data['books'][0]['average_rating']
#    gd_rcount = data['books'][0]['work_ratings_count']
#    gd_isbn= data['books'][0]['isbn13']
# get response from the Google Book api with isbn as parameter to get book cover image
    googleres= requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{book_isbn}")
    if googleres.status_code != 200:
        raise Exception ("Error: Google Book API request unsuccessful")
# convert googlebook response to json
    googledata = googleres.json()
# store google reviews average, reviews count, isbn13, previewlink used google books api instead of goodreads api as of December 8th 2020 goodreads dropped support pf api
    g_ravg = googledata['items'][0]['volumeInfo']['averageRating']
    g_rcount = googledata['items'][0]['volumeInfo']['ratingsCount']
    g_isbn= googledata['items'][0]['volumeInfo']['industryIdentifiers'][0]['identifier']
    g_previewlink = googledata['items'][0]['volumeInfo']['previewLink']
# check if book cover image exists in the response, if not pass a no_book_cover jpg instead
    if googledata['totalItems']!= 0 and 'imageLinks' in  googledata['items'][0]['volumeInfo']:
        googleimg = googledata['items'][0]['volumeInfo']['imageLinks']['thumbnail']
    else:
        googleimg = "/static/img/no_book_cover.jpg"
# fetch book reviews
    reviews = db.execute("SELECT review_stars, review_details, username FROM reviews JOIN users ON reviews.user_id = users.user_id WHERE isbn = :isbn",
            {"isbn": book_isbn}).fetchall()
# get count of reviews per book
    reviewscount = len(reviews)
    return render_template('book.html',b=b, g_ravg= g_ravg, g_rcount= g_rcount, g_isbn=g_isbn, g_previewlink=g_previewlink, googleimg=googleimg, reviews=reviews, reviewscount=reviewscount )

@app.route("/about")
def about():
    return render_template('about.html',title='about')

@app.route("/register",methods=["GET","POST"])
def register():
# if user reached register route by GET
    if request.method == "GET":
        if session.get("LoggedUserID"):
            flash("You are already logged in","primary")
            return redirect(url_for('home'))
        else:
            return render_template("register.html")
# if user reached register route by POST as in submitting the registration form
# fetch form fields
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
# check fields constraints
        if password != confirm or password == "" or confirm == "" or username == "":
            flash("Password don't match or empty fields","danger")
            return redirect(url_for('register'))
#check if chosen username already exists in database
        userexists= db.execute("SELECT * FROM users WHERE username = :username",
                    {"username": username}).fetchone()
        if userexists:
            flash("username already taken!, try another username","warning")
            return redirect(url_for('register'))
# create hash for user's password
        hash = pbkdf2_sha256.hash(password)
# insert the registered user into database and commit changes
        db.execute("INSERT INTO users (username, password) VALUES (:name, :hash)",
                   {"name": username, "hash": hash})
        db.commit()
        flash("Register successful","success")
# uncomment the next line for auto login after registration
#        session["LoggedUserID"] =  username
        return redirect(url_for('login'))

@app.route("/login",methods=["GET","POST"])
def login():
# if user reached login route by GET
    if request.method == "GET":
        if session.get("LoggedUserID"):
            flash("You are already logged in","primary")
            return redirect(url_for('home'))
        else:
            return render_template("login.html")
# if user reached login route by POST as in submitting the login form
# fetch form fields
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        exists = db.execute("SELECT * FROM users WHERE username = :username ",
                            {"username": username }).fetchone()
# check if username exists and the password is correct
# https://passlib.readthedocs.io/en/stable/narr/hash-tutorial.html
        if exists is not None:
            if pbkdf2_sha256.verify(password, exists.password):
                flash("Login successful","success")
                session["LoggedUserID"] =  username
                return redirect(url_for('home'))
            else:
                flash("Login failed","danger")
                return render_template("login.html")
        else:
            flash("Login failed","danger")
            return render_template("login.html")

@app.route("/logout")
def logout():
# clear session and logout and redirect to login page
    session.clear()
    return redirect(url_for('login'))


@app.route("/search", methods=["GET","POST"])
def search():
# user can not search if not logged in
    if not session.get("LoggedUserID"):
        flash("Please Login in order to search","primary")
        return render_template("login.html")
# fetch form field
    search = request.form.get("search")
# lowercased search string and prepare for %like% operator
    query = f"%{search}%".lower()
# fetch all search results and lower all database fields on the fly
    results = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn OR LOWER(title) LIKE :title OR LOWER(author) LIKE :author",
                        {"isbn": query, "title": query, "author": query }).fetchall()
    resultscount= len(results)
# check if there are results or not
    if resultscount ==0:
        flash("No books were found, Try again", "primary")
# display results and count of results
    return render_template('search.html', results=results, resultscount=resultscount)

@app.route("/api/<string:book_isbn>")
def book_api(book_isbn):
# fetch all book information including title, autor, year, isbn, reviews count, average score by known isbn
    myapp_api = db.execute("SELECT title, author, year, books.isbn AS isbn, COUNT(review_id) AS rcount,\
                            coalesce(AVG(review_stars),0) AS raverage  FROM books LEFT JOIN reviews ON\
                            books.isbn = reviews.isbn WHERE books.isbn = :isbn GROUP BY\
                            title, author, year, books.isbn",
                            {"isbn": book_isbn}).fetchone()
# handle json response if isbn is invalid
    if myapp_api is None:
        return jsonify({"error": "Invalid isbn"}), 404
    return jsonify({
              "title": myapp_api.title,
              "author": myapp_api.author,
# convert year from string to integer
              "year": int(myapp_api.year),
              "isbn": myapp_api.isbn,
              "review_count": myapp_api.rcount,
# convert average score to float and round it to 1 decimal value
              "average_score": float(round(myapp_api.raverage,1))
          })
