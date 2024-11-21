from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import logging
from bcrypt import hashpw, checkpw, gensalt
import random

# Constants
FAILURE = 1
EXIT = 2
SUCCESS = 0

app = Flask(__name__)
app.secret_key = 'password'  # Required for Flask-Login
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root1234@localhost/reelvibes1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create log file
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

# User class for Flask-Login
class User(UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html', title='Home Page')


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
        user = User.query.filter_by(username=username).first()
        if user and checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            return redirect('/')
        else:
            flash('Login Failed. Check your credentials.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        else:
            hashed_password = hashpw(password.encode('utf-8'), gensalt())
            new_user = User(username=username, password=hashed_password.decode('utf-8'))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/recommend')
@login_required
def recommend():
    return render_template('recommend.html', title='Recommendations')

@app.route('/choose_service')
def choose_service():
    return render_template('choose_service.html')

@app.route('/genre_selection')
def genre_selection():
    return render_template('genre_selection.html')  # Template for the genre selection page
    

@app.route('/Age_range.html')
def age_range():
    return render_template('Age_range.html')

@app.route('/year_of_release.html')
def year_of_release():
    age = request.args.get('age', 'All')  # Default to 'All' if no parameter is provided
    return render_template('year_of_release.html', age=age)

@app.route('/movie_selection.html')
def movie_selection():
    # Get query parameters for age and start year
    age = request.args.get('age', 'All')  # Default to 'All' if no age is provided
    start_year = request.args.get('start_year', 1954)  # Default to 1954 if no start year is provided
    
    # You can pass these parameters to the template for further use
    return render_template('movie_selection.html', age=age, start_year=start_year)

@app.route('/random_movie')
def random_movie():
    return render_template('random_movie.html')



if __name__ == "__main__":
    db.create_all()  # This line will create all tables based on the models declared
    app.run(debug=True)
