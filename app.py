from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'password'  # Required for Flask-Login

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Sample movie data
movies = [
    {"id": 1, "title": "Inception", "director": "Christopher Nolan", "genre": "Sci-Fi", "year": 2010},
    {"id": 2, "title": "The Matrix", "director": "Lana Wachowski", "genre": "Sci-Fi", "year": 1999},
    {"id": 3, "title": "Interstellar", "director": "Christopher Nolan", "genre": "Sci-Fi", "year": 2014},
    {"id": 4, "title": "The Grand Budapest Hotel", "director": "Wes Anderson", "genre": "Comedy", "year": 2014},
    # Add more movies as needed
]

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
        # Simplified login logic (for demo purposes)
        user_id = request.form.get('username')
        if user_id:
            user = User(user_id)
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Simplified registration logic (for demo purposes)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
