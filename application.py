from dotenv import load_dotenv
import os
from flask import Flask, session, render_template, request, redirect, flash, url_for, escape
from flask_bootstrap import Bootstrap
from flask_session import Session
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
bootstrap = Bootstrap(app)

# reading defined defined variables
load_dotenv()

secret_key = os.getenv('SECRET_KEY')
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
    title = "Home Page | Book Review"
    if 'username' in session:
        user = session['username']
        return render_template('index.html', title=title, user=user)
    else:
        return render_template('index.html', title=title)



@app.route('/books')
def display_books():
    title = "Books | Book Review"
    user=session['username']
    books = db.execute('SELECT * FROM books LIMIT 30').fetchall()
    return render_template('books.html', title=title, books=books, user=user)


@app.route('/search', methods=['POST'])
def search_books():
    title = "Results | Book Review"
    name = request.form.get('book')
    # name="Krondor: The Betrayal"
    sql = "SELECT * FROM books WHERE title ILIKE :title"
    results = db.execute(sql, {"title": name})
    return render_template('results.html', title=title, results=results, search=name)


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
            session['email'] = user.email
            session['username'] = user.username
            flash(f'Logged In!')
            return redirect(url_for('index'))
        else:
            flash('Incorrect password try again', 'error')
            return redirect(url_for('login'))


            
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('logged out')
    return redirect(url_for('index'))