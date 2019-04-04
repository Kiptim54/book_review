from dotenv import load_dotenv
import os
from flask import Flask, session, render_template, request, redirect, flash, url_for, escape
from flask_bootstrap import Bootstrap
from flask_session import Session
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from werkzeug.contrib.cache import SimpleCache




app = Flask(__name__)
bootstrap = Bootstrap(app)
cache = SimpleCache()
# reading defined defined variables
load_dotenv()

secret_key = os.getenv('SECRET_KEY')
key=os.getenv('key')
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
def index():
    title = "Home | Book Review"    
    books = cache.get('books')
    if books is None:
        books=db.execute('SELECT * FROM books LIMIT 10').fetchall()
        cache.set('books', books)
    if 'username' in session:
        user = session['username']
        return render_template('index.html', title=title, user=user, books=books)
    
    return render_template('index.html', title=title, books=books)




@app.route('/books')
def display_books():
    title = "Books | Book Review"
    books = cache.get('books')
    if books is None:
        books = db.execute('SELECT * FROM books LIMIT 30').fetchall()
        cache.set('books', books)
    if 'username' in session:
        user = session['username']
        return render_template('books.html', title=title, books=books, user=user)

    return render_template('books.html', title=title, books=books)




@app.route('/search', methods=['POST'])
def search_books():
    title = "Results | Book Review"
    search_term=request.form.get('search_term')
    # name = request.form.get('book')
    # isbn=request.form.get('isbn')
    # name="Krondor: The Betrayal"
    sql = "SELECT * FROM books WHERE isbn=:isbn OR title ILIKE :author OR author ILIKE :author"
    results = db.execute(sql, {"title": f"%{search_term}%", "isbn":search_term, "author":f"%{search_term}%"})
    return render_template(f'results.html', title=title, results=results, search=search_term)




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    title = "Book Review | SignUp"
    if request.method == 'GET':
        return render_template('signup.html', title=title)
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        hashed_password = generate_password_hash(password)
        db.execute(''' 
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username VARCHAR NOT NULL,
            password VARCHAR NOT NULL,
            email VARCHAR NOT NULL
            );
        ''')
        db.execute('INSERT INTO users(username, password, email) VALUES(:username, :password, :email)', {
                   "username": username, "password": hashed_password, "email": email})
        db.commit()
        flash('successfully signed up. Please log in')
        return redirect(url_for('login'))



@app.route('/login', methods=['POST', 'GET'])
def login():
    title = "Book Reviews | Login"
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.execute(
            'SELECT * FROM users WHERE email= :email', {"email": email}).fetchone()
        if check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['logged_in']=True
            flash(f'Logged In!')
            return redirect(url_for('index'))
        else:
            flash('Incorrect password try again', 'error')
            return redirect(url_for('login'))



@app.route('/book/<isbn>/')
def book(isbn):
    title="Book Review | Book "
    isbn=isbn
    key=os.getenv('key')
    book_details=requests.get('https://www.goodreads.com/book/review_counts.json', params={"key":key, "isbns":isbn})
    results=book_details.json()
    results=results['books']
    book_details=db.execute('SELECT * FROM books WHERE isbn=:isbn', {"isbn": isbn})
    return render_template('book.html', title=title,reviews=results, book=book_details)
    


            
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)

    flash('logged out')
    return redirect(url_for('index'))