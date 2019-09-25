import os
import requests
import json

from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, jsonify, session, redirect, flash, url_for
from flask_session import Session
from sqlalchemy import table, column, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helper import apology, login_required, lookup
from flask_wtf import FlaskForm

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)  

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
#postgres://username:password@host:5432/db
engine = create_engine("postgres://veufgqrqcdagor:7705973df1ee8412f8adf05f713f3a4c2692d3f79fe7df60101315add082c144@ec2-54-225-95-183.compute-1.amazonaws.com:5432/d6ap38ig08mt8t")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return render_template("register.error.html", message="must provide email")

        # Query database for email
        emailCheck = db.execute("SELECT * FROM users WHERE email = :email",
                          {"email":request.form.get("email")}).fetchone()

        # Check if email already exist
        if emailCheck:
            return render_template("register.error.html", message="email already exist")

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("register.error.html", message="must provide username")

        # Query database for username
        userCheck = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username":request.form.get("username")}).fetchone()

        # Check if username already exist
        if userCheck:
            return render_template("register.error.html", message="Username already exist")
        
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("register.error.html", message="must provide password")

        # Ensure confirmation wass submitted 
        elif not request.form.get("confirmation"):
            return render_template("register.error.html", message="must confirm password")

        # Check passwords are equal
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("register.error.html", message="passwords didn't match")
        
        # Hash user's password to store in DB
        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        
        # Insert register into DB
        db.execute("INSERT INTO users (email, username, password) VALUES (:email, :username, :password)",
                            {"email":request.form.get("email"),
                            "username":request.form.get("username"),
                             "password":hashedPassword})

        # Commit changes to database
        db.commit()

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

    
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        # Ensure username was submitted
        if not request.form.get("email"):
            return render_template("login.error.html", message="must provide email")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.error.html", message="you must provide a password!")

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                            {"email": email})
        
        result = rows.fetchone()

        # Ensure email exists and password is correct
        if result == None or not check_password_hash(result[3], request.form.get("password")):
            return render_template("login.error.html", message="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = result[0]
        session["user_email"] = result[1]
        session["user_username"] = result[2]
        session["user_password"] = result[3]
        session['logged_in'] = True

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect("/")


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    return render_template('search.html')

@app.route('/booksresult', methods=['GET', 'POST'])
@login_required
def booksresult():
    
    if request.method == "GET":
        return render_template("search.html")

    if request.method == "POST":
        # Check book id was provided
        if not request.form.get("book"):
            flash('you must provide a book!')
            return redirect(url_for('search'))
                
        query = "%" + request.form.get("book") + "%"

        # Capitalize all words of input for search
        query = query.title()
            
        rows = db.execute("SELECT * FROM books WHERE isbn LIKE :query OR title LIKE :query OR author LIKE :query LIMIT 15",
                                {"query": query})
            
        # Books not founded
        if rows.rowcount == 0:
            flash("we can't find books with that description!")
            return redirect(url_for('search'))
        # Fetch all the results
        books = rows.fetchall()

        return render_template("search.result.html", books=books)

@app.route('/bookPage/<id>', methods=['GET', 'POST'])
@login_required
def bookPage(id):

    if request.method == "GET":
        # Define current username
        currentUser = session["user_username"]

        booksPage = db.execute("SELECT * FROM books WHERE id = :id",{"id": id}).fetchall()

        # Get reviews from other users on current book
        rows = db.execute("SELECT * FROM reviews WHERE book_id = :id",{"id": id})
        reviews = rows.fetchall()

        # Make sure user submit one time
        allowed = True
        for rev in reviews:
            if rev.username == session["user_username"]:
                allowed = False
        # Get Info from api       
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "r8xDam9QywwKlplVQCuUKg", "isbns": "9781632168146"})
        print(res.json())
        isbn=res.json()['books'][0]['isbn']
        average_rating=res.json()['books'][0]['average_rating']
        ratings_count=res.json()['books'][0]['work_ratings_count']
    
        viewes = True
        if reviews :
            viewes = False
        
        return render_template("bookPage.html",book=booksPage, reviews=reviews,allowed=allowed, average_rating=average_rating, ratings_count=ratings_count, isbn=isbn, viewes=viewes)        

    if request.method == "POST":
        # Define current username
        currentUser = session["user_username"]

        booksPage = db.execute("SELECT * FROM books WHERE id = :id",{"id": id}).fetchall()
        
        # Insert data to review table
        db.execute("INSERT INTO reviews (username, rate, review, book_id) VALUES (:username, :rate, :review, :book_id)",
                            {"username": currentUser,
                            "rate":request.form.get("rate"),
                            "review":request.form.get("review"),
                            "book_id": id})
        # Commit changes to database
        db.commit()
        
        # Get reviews from other users on current book
        rows = db.execute("SELECT * FROM reviews WHERE book_id = :id",{"id": id})
        reviews = rows.fetchall()
        db.commit()


        return render_template("bookPage.html",book=booksPage, reviews=reviews)


@app.route('/api/<isbn>', methods=['GET'])
@login_required
def api_call(isbn):    

    data=db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
    if data==None:
        return render_template('404.html')
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "r8xDam9QywwKlplVQCuUKg", "isbns": "9781632168146"})
    average_rating=res.json()['books'][0]['average_rating']
    work_ratings_count=res.json()['books'][0]['work_ratings_count']

    x = {
    "title": data.title,
    "author": data.author,
    "year": data.year,
    "isbn": res.json()['books'][0]['isbn'],
    "review_count": work_ratings_count,
    "average_score": average_rating
    }
    api=json.dumps(x)
    return render_template("api.json",api=api)

@app.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    if request.method == "GET":
        return render_template("setting.html")

    if request.method == "POST":
        password = request.form.get('newpassword')
        email = session["user_email"]
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                            {"email": email})
        
        result = rows.fetchone()
        if result == None or not check_password_hash(result[3], request.form.get("password")):
            flash("invalid password!")
            return redirect(url_for('setting'))
        hashedPassword = generate_password_hash(request.form.get("newpassword"), method='pbkdf2:sha256', salt_length=8)
        db.execute(
                    "UPDATE users SET password = :password where id= :user_id",
                    {"password":hashedPassword, 'user_id' : session["user_id"]})
        db.commit()
        return render_template("setting.html")

if __name__ == '__main__':
    app.run()        