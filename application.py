import os
from flask import Flask, session, render_template, request, redirect, flash, url_for
from flask_bootstrap import Bootstrap
from flask_session import Session
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
bootstrap= Bootstrap(app)

# reading defined defined variables
from dotenv import load_dotenv
load_dotenv()


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
    title="Home Page | Book Review"
    return render_template('index.html', title=title)

@app.route('/books')
def display_books():
    title="Books | Book Review"
    books=db.execute('SELECT * FROM books LIMIT 30').fetchall()
    return render_template('books.html', title=title, books=books)

@app.route('/search', methods=['POST'])
def search_books():
    title="Results | Book Review"
    name=request.form.get('book')
    # name="Krondor: The Betrayal"
    sql="SELECT * FROM books WHERE title ILIKE :title"
    results=db.execute(sql, {"title":name})
    return render_template('results.html', title=title, results=results, search=name)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    title="Book Review | SignUP"
    if request.method=='GET':
        return render_template('signup.html', title=title)
    else:
        username=request.form.get('username')
        password=request.form.get('password')
        email=request.form.get('email')
        hashed_password= generate_password_hash(password)
        db.execute(''' 
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username VARCHAR NOT NULL,
            password VARCHAR NOT NULL,
            email VARCHAR NOT NULL
            );
        ''')
        db.execute('INSERT INTO users(username, password, email) VALUES(:username, :password, :email)', {"username":username, "password":hashed_password, "email":email})
        db.commit()
        flash('successfully signed up. Please log in')
        return redirect(url_for('login'))



@app.route('/login', methods=['POST', 'GET'])
def login():
    title="Book Reviews | Login"
    if request.method=='GET':
        return render_template('login.html')
    else:
        email=request.form.get('email')
        password=request.form.get('password')
        user=db.execute('SELECT * FROM users WHERE email= :email', {"email": email}).fetchone()
        print(user)
        if check_password_hash(user.password, password):
            flash(f'Logged in as {user.username}!')
            return redirect(url_for('index'))
        else:
            flash('Incorrect password try again')
            return redirect(url_for('login'))

        
