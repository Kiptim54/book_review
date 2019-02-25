


import os
from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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
    print("hey")
    title="Results | Book Review"
    name=request.form.get('book')
    # name="Krondor: The Betrayal"
    sql="SELECT * FROM books WHERE title ILIKE :title"
    print(" onestep")
    results=db.execute(sql, {"title":name})
    print(type(results))
    return render_template('results.html', title=title, results=results, search=name)
