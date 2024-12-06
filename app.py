from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import logging
from bcrypt import hashpw, checkpw, gensalt
import random
import os
import dotenv
import requests

# Constants
FAILURE = 1
EXIT = 2
SUCCESS = 0

dotenv.load_dotenv()


app = Flask(__name__)
app.secret_key = 'password'  # Required for Flask-Login
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/reelvibes1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
TMDB_API_KEY = os.getenv("TMDB_API_KEY") # Get API Key from .env file 
BEARER_TOKEN = os.getenv("BEARER_TOKEN") # READ TOKEN

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

# ---- MOVIE API ENDPOINT ------
def fetch_tmdb_movie(provider=None, genre=None, rating=None, year_range=None):
    url = "https://api.themoviedb.org/3/discover/movie"

    print(f"Using BEARER_TOKEN: {BEARER_TOKEN}")

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "accept": "application/json"
    }

    params = {
        "include_adult": "false",
        "include_video": "false",
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": 1,
    }

    if provider:
        params["watch_provider"] = provider
    if genre:
        params["with_genres"] = genre
    if rating:
        params["certification"] = rating
    if year_range and len(year_range) == 2:
        params["primary_release_date.gte"] = f"{year_range[0]}-01-01"
        params["primary_release_date.lte"] = f"{year_range[1]}-12-31"


    try:
        # Make the request to the TMDb API
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()  # Return parsed JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from TMDb API: {e}")
        return None
    
# Map movie genre to ID
def genre_mapping():
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Map genre names to their IDs
        genre_mapping = {genre['name'].lower(): genre['id'] for genre in data['genres']}
        return genre_mapping
    except requests.exceptions.RequestException as e:
        print(f"Error fetching genres: {e}")
        return None

@app.route('/genre_selection', methods=['GET'])
def genre_selection():
    service = request.args.get('service')  # Get the selected service from the query string
    print(f"Selected Service: {service}")  # Debugging output
    return render_template('genre_selection.html', service=service)

# Service Mapping
def service_mapping():
    url = "https://api.themoviedb.org/3/watch/providers/movie?language=en-US"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Map provider names to their IDs
        provider_mapping = {provider['provider_name'].lower(): provider['provider_id'] for provider in data['results']}
        return provider_mapping
    except requests.exceptions.RequestException as e:
        print(f"Error fetching service: {e}")
        return None
    
@app.route('/choose_service', methods=['GET'])
def choose_service():
    service = request.args.get('service')
    print (f"Selected Service: {service}")
    return render_template('choose_service.html')

# -- Age Rating---

@app.route('/Age_range.html', methods=['GET'])
def age_range():
    service = request.args.get('service')
    genres = request.args.get('genres')

    print(f"Service: {service}")
    print(f"Genre: {genres}")
    return render_template('Age_range.html', service=service, genres=genres)

# --- ----

@app.route('/recommend')
@login_required
def recommend():
    return render_template('recommend.html', title='Recommendations')


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
    provider = "8"  # Example: Netflix (use the actual ID for Netflix)
    genre = "28"  # Example: Action (use the genre ID for Action)
    min_rating = 7.0  # Minimum rating of 7.0
    year_range = (2000, 2020)  # Movies from 2000 to 2020

    movies = fetch_tmdb_movie(provider, genre, min_rating, year_range)
    if movies:
        for movie in movies.get("results", []):
            print(f"{movie['title']} ({movie['release_date']}) - Rating: {movie['vote_average']}")
    with app.app_context():
        db.create_all()
    app.run()