from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import logging
from bcrypt import hashpw, checkpw, gensalt
import os
import mariadb
import random

# Constants
FAILURE = 1
EXIT = 2
SUCCESS = 0

app = Flask(__name__)
app.secret_key = 'password'  # Required for Flask-Login

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Create log file
logger = logging.getLogger("mylog")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logfile.log")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Sample movie data
movies = [
    {"id": 1, "title": "Inception", "director": "Christopher Nolan", "genre": "Sci-Fi", "year": 2010},
    {"id": 2, "title": "The Matrix", "director": "Lana Wachowski", "genre": "Sci-Fi", "year": 1999},
    {"id": 3, "title": "Interstellar", "director": "Christopher Nolan", "genre": "Sci-Fi", "year": 2014},
    {"id": 4, "title": "The Grand Budapest Hotel", "director": "Wes Anderson", "genre": "Comedy", "year": 2014},
    # Add more movies as needed
]

security_questions = {
    0 : "What is your favorite film?",
    1 : "What is your mother's maiden name?",
    2 : "What is your city of birth?",
    3 : "What is your favorite food?",
    4 : "What is your childhood nickname?",
    5 : "What is your first pet's name?"
}

# Connect to the database
try:
    conn = mariadb.connect(
        user="root",
        password=os.environ["mariadbpassword"],
        host="127.0.0.1",
        port=3306,
        database="reelvibes1"
    )
except mariadb.Error as e:
    logger.error(f"Error connecting to MariaDB Platform: {e}")


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def home():
    return render_template('index.html', title='Home Page')

@app.route('/movies')
@login_required
def movies_list():
    genre = request.args.get('genre')
    year = request.args.get('year')
    director = request.args.get('director')
    filtered_movies = filter_movies(genre, year, director)
    return render_template('movies.html', movies=filtered_movies, title='Movies List')

def filter_movies(genre, year, director):
    filtered = movies
    if genre:
        filtered = [movie for movie in filtered if movie['genre'].lower() == genre.lower()]
    if year:
        filtered = [movie for movie in filtered if movie['year'] == int(year)]
    if director:
        filtered = [movie for movie in filtered if movie['director'].lower() == director.lower()]
    return filtered

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        status = login_check(username, password)
        if status == SUCCESS:
            #user = request.form['nm']
            return redirect('/')
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')  # Create an HTML template for the login page
    
def login_check(username, password) -> int:
    """System login.

    Returns:
        0 for successful.
        1 for failure.
    """
    logger.info("Login. Getting user input")

    try:
        cursor = conn.cursor()
        # collect usernames and passwords
        user_search = "SELECT username, password FROM users WHERE username=%s AND password=%s"
        hashed_pw = hashpw(password.encode('utf-8'), gensalt())
        logger.info("Collect username and password")
        cursor.execute(user_search, (username, hashed_pw))
        logger.info(f"{username} is a member.")
        logger.info("User logged in.")
        cursor.close()
        return SUCCESS
    
    except mariadb.Error as err:
        logger.error("Pw/Username doesn't exist. Execution halt.")
        logger.error(f"Execution halt {err}")

        return FAILURE

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        sec_quest_id = request.form['security_question']
        security_answer = request.form['security_answer']
        status = register_check(username, password, sec_quest_id, security_answer)
        
        if status == EXIT:
            flash("Username already exists. Please try another or try logging in.")
            logger.info("FLASH")
            return redirect('/register')
        
        if status != FAILURE:
            # Successful register, you can redirect the user to the login page or any other page
            return redirect('/login')
    return render_template('register.html', questions=security_questions)

def register_check(username, password, sec_quest_id, security_answer) -> str:
    logger.info("Gathering username.")
    
    logger.info("Gathering cursor.")
    cursor = conn.cursor()
    
    if login_check(username, password) == SUCCESS:
        return EXIT
    
    # first, hash the password for the user before storing
    logger.info("Hashing user password.")
    hashed_pw = hashpw(password.encode('utf-8'), gensalt())
    insert_user = "INSERT INTO users (username, password, security_question_id, security_answer, created_at) VALUES (%s, %s, %s, %s, NOW())"
    user_data = (username, hashed_pw, sec_quest_id, security_answer)

    # execute and commit
    try:
        logger.info("Insert new user into the database.")

        cursor.execute(insert_user, user_data)
        cursor.close()
        conn.commit()
        
    except mariadb.Error as err:
        logger.error(f"Failed to insert: {err}")
        return 'FAILURE'
    
    logger.info("User created.")
    return 'SUCCESS'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
