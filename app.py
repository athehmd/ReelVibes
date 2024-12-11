from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import logging, datetime
from bcrypt import hashpw, checkpw, gensalt
import os
import dotenv
import mysql.connector
import random, requests, typing 
from typing import Optional
from datetime import timedelta

# Constants
FAILURE = 1
EXIT = 2
SUCCESS = 0

dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = 'password'  # Required for Flask-Login
BEARER_TOKEN = os.getenv("BEARER_TOKEN") # READ TOKEN
app.jinja_env.filters['upper'] = str.upper

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

# API Endpoint Shortcuts
base_url = "https://api.themoviedb.org/3/"

headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "accept": "application/json"
}
movie_endpoint = f"{base_url}search/movie"
popular_endpoint = f"{base_url}movie/popular?language=en-US&page=1"

our_Recommendations = ["Rush Hour",
                      "Inception",
                      "The Grand Budapest Hotel",
                      "The Big Short",
                      "Interstellar",
                      "The Matrix",
]

#             Example: 
# query = request.form[query] <- gets query from html webpage
# response = requests.get(movie_endpoint, headers=headers, params={"query": query})
#
# if response.status_code == 200:
#     data = response.json()
#     print(data)
# else:
#     print(f"Error: {response.status_code}")

# Connect to the database
conn = None
try:
    conn = mysql.connector.connect(
        user="root",
        password=os.environ.get("mariadbpassword"),
        host="127.0.0.1",
        port=3306,
        database="reelvibes"
    )
except mysql.connector.Error as e:
    logger.error(f"Error connecting to DB Platform: {e}")

if conn != None:
    cursor = conn.cursor()
else:
    logger.error(f"cursor is none")

# User class for Flask-Login

class User(UserMixin):
    def __init__(self, user_id: str, username: str):
        self.id = user_id
        self.username = username
    
    def getId(self):
        return self.username
    
    @staticmethod
    def get_user_by_id(conn, user_id: str) -> Optional['User']:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                return User(str(user_data['id']), user_data['username'])
            return None
        except mysql.connector.Error as err:
            logger.error(f"Error fetching user by ID: {err}")
            return None
    
    @staticmethod
    def get_user_by_username(conn, username: str) -> Optional['User']:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                return User(str(user_data['id']), user_data['username'])
            return None
        except mysql.connector.Error as err:
            logger.error(f"Error fetching user by username: {err}")
            return None

# Update the user loader function
@login_manager.user_loader
def load_user(user_id):
    try:
        local_conn = mysql.connector.connect(
            user="root",
            password=os.environ.get("mariadbpassword"),
            host="127.0.0.1",
            port=3306,
            database="reelvibes"
        )
        user = User.get_user_by_id(local_conn, user_id)
        local_conn.close()
        return user
    except mysql.connector.Error as err:
        logger.error(f"Error in user loader: {err}")
        return None

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    current_username = current_user.getId()
    if request.method == 'POST':
        try:
            local_conn = mysql.connector.connect(
                user="root",
                password=os.environ.get("mariadbpassword"),
                host="127.0.0.1",
                port=3306,
                database="reelvibes"
            )
            new_username = request.form.get('new-username')
            confirm_username = request.form.get('confirm-username')
            if new_username == confirm_username:
                cursor = local_conn.cursor(dictionary=True)
                cursor.execute("UPDATE users SET username = %s WHERE username = %s", (new_username, current_username))
                if cursor.rowcount > 0:
                    local_conn.commit()
                    return redirect(url_for('profile'))
                cursor.close()
                local_conn.close()
        except mysql.connector.Error as err:
            logger.error(f"Error in user loader: {err}")
        
    return(render_template('profile.html', username=current_username))

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    username = current_user.getId()
    try:
        local_conn = mysql.connector.connect(
            user="root",
            password=os.environ.get("mariadbpassword"),
            host="127.0.0.1",
            port=3306,
            database="reelvibes"
        )
        cursor = local_conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        if cursor.rowcount > 0:
            local_conn.commit()
            return redirect(url_for('home'))
        cursor.close()
        local_conn.close()
    except mysql.connector.Error as err:
        logger.error(f"Error in user loader: {err}")
        return None
        

@app.route('/')
def home():
    url = "https://api.themoviedb.org/3/movie/popular?language=en-US"
    url2 = "https://api.themoviedb.org/3/discover/movie"
    url_details = "https://api.themoviedb.org/3/movie/{movie_id}"
    url_certification = "https://api.themoviedb.org/3/movie/{movie_id}/release_dates"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }
    params = {
        "include_adult": "false",
        "include_video": "false",
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": 1,
        "watch_region": "US",
        "region": "US",
        "certification_country": "US",
        "with_genres": 16
    }
    
    all_movies = []
    
    page, page2 = 1, 1
    
    while page < 4:
        response = requests.get(f"{url}&page={page}", headers=headers)  # Append page to URL
        if response.status_code == 200:
            movies = response.json().get('results', [])
            all_movies.extend(movies)  # Use extend to add all movies from this page
            
            # Check if there are more pages to fetch
            total_pages = response.json().get('total_pages', 0)
            if page >= total_pages:
                break
            page += 1
        else:
            print(f"Error fetching page {page}")
            break
    
    all_movies = all_movies[:23]
    while page2 < 3:
        params["page"] = page2  # Set the page parameter for animated movies request
        response = requests.get(url2, headers=headers, params=params)  # Append page to URL
        if response.status_code == 200:
            movies = response.json().get('results', [])
            all_movies.extend(movies)  # Use extend to add all movies from this page
            
            # Check if there are more pages to fetch
            total_pages = response.json().get('total_pages', 0)
            if page2 >= total_pages:
                break
            page2 += 1
        else:
            print(f"Error fetching page {page2}")
            break
    
    for i in range(min(len(all_movies), 40)):
        movie_id = all_movies[i].get('id')  # Get the movie ID
        if movie_id:
            response = requests.get(url_details.format(movie_id=movie_id), headers=headers)
            response2 = requests.get(url_certification.format(movie_id=movie_id), headers=headers)
            if response.status_code == 200:
                movie_details = response.json()
                runtime = movie_details.get('runtime', None)  # Fetch runtime from details
                
                all_movies[i]['runtime'] = runtime  # Map runtime to the respective movie
            else:
                print(f"Failed to fetch runtime for movie ID {movie_id}: {response.status_code}")
            if response2.status_code == 200:
                release_dates = response2.json().get('results', [])
                us_certification = None
                for entry in release_dates:
                    if entry.get('iso_3166_1') == "US":  # Look for US certifications
                        us_release_dates = entry.get('release_dates', [])
                        for release in us_release_dates:
                            certification = release.get('certification')
                            if certification:  # Check if certification is not empty
                                us_certification = certification
                                break  # Stop once a valid certification is found
                        break  # Stop checking other countries once US is processed
                all_movies[i]['certification'] = us_certification  # Map certification to the respective movie
            else:
                print(f"Failed to fetch certification for movie ID {movie_id}: {response2.status_code}")
        else:
            print(f"Missing movie ID at index {i}")
    
    return render_template('home.html', movies=all_movies)

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
        form_type = request.form.get('form_type')
        if form_type == 'login':  # Handle login form 
            username = request.form['username']
            password = request.form['password']
            remember = request.form.get('remember_me', 'off')
            status = login_check(username, password, remember)
            if status == SUCCESS:
                #user = request.form['nm']
                flash("Login Success!")
                return redirect('/')
            else:
                return render_template('login.html')
        elif form_type == 'register':  # Handle registration form
            username = request.form['username']
            password = request.form['password']
            sec_quest_id = request.form['security_question']
            security_answer = request.form['security_answer']
            status = register_check(username, password, sec_quest_id, security_answer)
            
            if status == EXIT:
                flash("Username already exists. Please try another or try logging in.")
                logger.info("FLASH")
                return redirect('/login')
            
            if status != FAILURE:
                # Successful register, you can redirect the user to the login page or any other page
                return redirect('/login')
    else:
        return render_template('login.html', questions=security_questions)  # Create an HTML template for the login page
    
def login_check(username, password, remember='off') -> int:
    """System login.

    Returns:
        0 for successful.
        1 for failure.
    """
    logger.info("Login. Getting user input")

    try:
        cursor = conn.cursor(dictionary=True)  # Configure the cursor
        # collect usernames and passwords
        user_search = "SELECT username, password, id FROM users WHERE username=%s"
        logger.info("Collect username and password")
        cursor.execute(user_search, (username,)) 
        result = cursor.fetchone()
        logger.info(f"Username: {result['username']}, Password Hash: {result['password']}")
                
        if result['username']:
            stored_password = result['password']  # Retrieved from DB as a string
            if checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                logger.info(f"{username} is a member.")
                user = User(str(result['id']), username)
                if remember == 'on':
                    login_user(user, remember=True, duration=timedelta(days=1)) # Keeps user logged in for one day
                    logger.info("User logged in. Remember Me True.")
                else:
                    login_user(user) # User will be logged out when browser is closed
                    logger.info("User logged in. Remember Me False.")
                
                
                cursor.close()
                
                return SUCCESS
            else:
                logger.error("Pw doesn't match. Execution halt.")
                return FAILURE
        else:
            logger.error("Username doesn't match. Execution halt.")
            return FAILURE
    
    except mysql.connector.Error as err:
        logger.error("Pw/Username doesn't exist. Execution halt.")
        logger.error(f"Execution halt {err}")

        return FAILURE

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         sec_quest_id = request.form['security_question']
#         security_answer = request.form['security_answer']
#         status = register_check(username, password, sec_quest_id, security_answer)
        
#         if status == FAILURE:
#             flash("Username already exists. Please try another or try logging in.")
#             logger.info("FLASH : Username already exists. Please try another or try logging in.")
#             return redirect('/register')
        
#         if status != FAILURE:
#             # Successful register, you can redirect the user to the login page or any other page
#             return redirect('/login')
#     return render_template('register.html', questions=security_questions)

def register_check(username, password, sec_quest_id, security_answer) -> str:
    logger.info("Gathering username.")
    
    logger.info("Gathering cursor.")
    #cursor = conn.cursor()
    
    logger.info("CHECKING USERNAME TO SEE IF ALREADY EXISTS.")
    cursor.execute("SELECT username FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()
    if result != None:
        logger.info("USERNAME ALR EXISTS AND THUS WE ARE NOT REGISTERING.")
        return EXIT
    
    # first, hash the password for the user before storing
    logger.info("Hashing user password.")
    hashed_pw = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
    insert_user = "INSERT INTO users (username, password, security_question_id, security_answer, created_at) VALUES (%s, %s, %s, %s, NOW())"
    user_data = (username, hashed_pw, sec_quest_id, security_answer)

    # execute and commit
    try:
        logger.info("Insert new user into the database.")

        cursor.execute(insert_user, user_data)
        cursor.close()
        conn.commit()
        
    except mysql.connector.Error as err:
        logger.error(f"Failed to insert: {err}")
        return 'FAILURE'
    
    logger.info("User created.")
    return 'SUCCESS'

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    security_question = None
    if request.method == 'POST':
        username = request.form['username']
        action = request.form.get('action')
        logger.info(f"Username received: {username}")
        
        try:
            # Establish a new connection for this request
            local_conn = mysql.connector.connect(
                user="root",
                password=os.environ.get("mariadbpassword"),
                host="127.0.0.1",
                port=3306,
                database="reelvibes"
            )
            cursor = local_conn.cursor()
            
            # Handle fetching the security question
            if action == 'fetch_question':
                find_sec_Q = "SELECT security_question_id FROM users WHERE username = %s"
                cursor.execute(find_sec_Q, (username,))
                sec_Q = cursor.fetchone()
                
                if sec_Q:
                    question_id = sec_Q[0]
                    security_question = security_questions.get(question_id, "Unknown security question")
                else:
                    flash("User not found", "error")
                    return render_template('forgot.html', title='Forgot')
            
            # Handle security answer submission
            elif action == 'submit_answer':
                # First, get the security question again to display it
                find_sec_Q = "SELECT security_question_id FROM users WHERE username = %s"
                cursor.execute(find_sec_Q, (username,))
                sec_Q = cursor.fetchone()
                
                if sec_Q:
                    question_id = sec_Q[0]
                    security_question = security_questions.get(question_id, "Unknown security question")
                    
                    # Now handle the security answer
                    security_answer = request.form['security_answer']
                    if security_answer:
                        find_sec_Q_answer = "SELECT security_answer FROM users WHERE username = %s"
                        cursor.execute(find_sec_Q_answer, (username,))
                        stored_sec_Q_answer = cursor.fetchone()
                        
                        if stored_sec_Q_answer and stored_sec_Q_answer[0] == security_answer:
                            return redirect(url_for('reset', username=username))
                        else:
                            flash("Wrong security question answer, please try again.", "error")
                    else:
                        flash("Please provide a security answer.", "error")
                else:
                    flash("User not found", "error")
                    
        except mysql.connector.Error as err:
            logger.error(f"Failed to find security question: {err}")
            flash("Failed to find security question. Ensure user exists.")
            
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn.is_connected():
                conn.close()
                
    return render_template('forgot.html', title='Forgot', security_question=security_question)

@app.route('/reset', methods=['GET', 'POST']) #Reset Password Page
def reset():
    username = request.args.get('username')  # Retrieve username from query string
    if request.method == 'POST':
        newPassword = request.form["newPassword"]
        confirmPassword = request.form["confirmPassword"]
        if newPassword == confirmPassword:
            logger.info("Confirmed password match.")
            local_conn = mysql.connector.connect(
                user="root",
                password=os.environ.get("mariadbpassword"),
                host="127.0.0.1",
                port=3306,
                database="reelvibes"
            )
            cursor = local_conn.cursor()
            hashedNewPassword = hashpw(newPassword.encode('utf-8'), gensalt()).decode('utf-8')
            resetPasswordQuery = "UPDATE users SET password = %s WHERE username = %s;"
            try: 
                cursor.execute(resetPasswordQuery, (hashedNewPassword, username))
                cursor.close()
                conn.commit()
                find_user_id = "SELECT id FROM users WHERE username = %s"
                cursor.execute(find_user_id, (username,))
                local_conn.commit()
                logger.info("Password update in database.")
                user_id = cursor.fetchone()
                if user_id:  # Ensure user exists
                    logger.info(f"User found with ID: {user_id['id']}")
                    user = User(str(user_id['id']), username)
                    login_user(user)
                    logger.info("User logged in after password reset.")
                    return redirect(url_for('/'))
                else:
                    logger.error("User not found after password update.")
                    flash("User not found. Please try again.", "error")
                    return redirect(url_for('reset', username=username))
            except: 
                logger.error("Failed to execute new password update.")
                flash("Failed to execute new password update. Try Again")
                return redirect(url_for('reset', username=username))
        else:
            logger.error("Passwords do not match")
            flash("Passwords do not match. Try Again.")
            return redirect(url_for('reset', username=username))
            
    return render_template('reset.html', title='Reset', username=username)

@app.route('/recommend')
@login_required
def recommend():
    return render_template('recommend.html', title='Recommendations')



@app.route('/choose_service', methods=['GET', 'POST'])
def choose_service():
    session.pop('temp_list', None)
    session['temp_list'] = {"service": [], "genres": [], "rating": [], "year": []}
    
    if request.method == 'POST':
        service = None
        
        if 'button_id' in request.form:
            service = request.form['button_id']
        
        if not service:
            service = request.form.get('button_id')
        
        if not service:
            for key, value in request.form.items():
                if key.startswith('button_id'):
                    service = value
                    break

        #service = request.form.get('button_id', "all_button")
        if service:
            session['temp_list']['service'] = [service]
            session.modified = True
            logger.info(f"temp list: {session['temp_list']}")
            return redirect(url_for('genre_selection'))
        else:
            logger.error("Failed to find streaming service.")
            flash("Failed to find streaming service. Try Again")
            
    return render_template('choose_service.html', title='Choose Service')

@app.route('/genre_selection', methods=['GET', 'POST'])
def genre_selection():
    if request.method == 'POST':
        if 'temp_list' in session:
            selected_genres = request.form.get('selected_genres', '')
            genre_list = selected_genres.split(',') if selected_genres else []
            session['temp_list']['genres'] = genre_list
            session.modified = True
            logger.info(f"temp list: {session['temp_list']}")
            
            if 'done_button' in request.form:
                return redirect(url_for('age_range'))

    return render_template('genre_selection.html')  # Template for the genre selection page
    
@app.route('/Age_range.html', methods=['GET', 'POST'])
def age_range():
    if request.method == 'POST':
        if 'temp_list' in session:
            selected_ratings = request.form.get('selected_ratings', '')
            ratings_list = selected_ratings.split(',') if selected_ratings else []
            session['temp_list']['rating'] = ratings_list
            session.modified = True
            logger.info(f"temp list: {session['temp_list']}")
            # Always redirect to the next step, `year_of_release`
            return redirect(url_for('year_of_release'))
            #if 'done_button' in request.form:
            #    return redirect(url_for('year_of_release'))
            
    return render_template('Age_range.html')

@app.route('/year_of_release.html', methods=['GET', 'POST'])
def year_of_release():
    if request.method == 'POST':
        start_year = request.form.get('start_year')
        try:
            start_year = int(start_year) if start_year else None
        except ValueError:
            start_year = None
        
        # If temp_list exists in session, update it
        if 'temp_list' in session:
            if start_year:
                years = [start_year, datetime.datetime.now().year]
            else:
                years = [1950, datetime.datetime.now().year]

        session['temp_list']['year'] = years
        session.modified = True
        logger.info(f"temp list after year of release: {session['temp_list']}")
        return redirect(url_for('movie_selection'))
        
    return render_template('year_of_release.html')

@app.route('/movie_selection.html', methods=['GET', 'POST'])
def movie_selection():
    # Extract service_ids (from providers)
    service_ids = [
        id_ for service in session['temp_list']['service']
        if (result := service_mapping(service)) is not None
        for id_ in (result[0] or {}).values()  # Extract values from the 'providers' dictionary
    ]
    # Extract omit IDs as a flat list of integers
    omit_ids = [
        id_ for service in session['temp_list']['service']
        if (result := service_mapping(service)) is not None and result[1]  # Check for non-None 'omits'
        for id_ in result[1].values()  # Extract values from the 'omits' dictionary
    ]
    genre = []  # Initialize an empty dictionary to hold all genres and their IDs
    for genres in session['temp_list']['genres']:
        result = genre_mapping(genres)  # Returns {'drama': 18} or {}
        if result:  # Check if result is not empty
            genre.extend(result.values())  # Add the key-value pair(s) from result to genre
    #genre = ",".join(str(gid) for gid in genre_ids if gid)  # Combine genre IDs into a single string
    age = session['temp_list']['rating'] if 'rating' in session['temp_list'] else []    
    start_year = session['temp_list']['year']
    # Convert lists to comma-separated strings for API
    provider_str = ','.join(map(str, service_ids)) if service_ids else None
    omit_str = ','.join(map(str, omit_ids)) if omit_ids else None
    genre_str = ','.join(map(str, genre)) if genre else None
    age_str = ','.join(age) if age else None
    
    logger.info(f"Providers: {provider_str}")
    logger.info(f"Omit Providers: {omit_str}")
    logger.info(f"Genres: {genre_str}")
    logger.info(f"Ratings: {age_str}")
    logger.info(f"Year Range: {start_year[0]}--{start_year[1]}")
    
    # Fetch movies from TMDB with converted parameters
    output = fetch_tmdb_movie(
        provider=provider_str, 
        omit=omit_str, 
        genre=genre_str, 
        rating=age_str, 
        year_range=start_year
    )
    filtered_movies = output.get('results', []) if output else []
    if output: logger.info(f"Fetched {len(output.get('results', []))} movies ::::: {output.get('results', [])}")
    # If not enough movies from filter, supplement with predefined movies
    if len(filtered_movies) < 6:
        # Fetch additional movie details for predefined titles
        predefined_movie_details = Recommendation_Fetcher(our_Recommendations)
        
        # Combine and deduplicate movies
        combined_movies = filtered_movies + [
            movie for movie in predefined_movie_details 
            if movie not in filtered_movies
        ]
        
        # Truncate to 6 movies
        final_movies = combined_movies[:6]
    else:
        final_movies = filtered_movies
    #logger.info(f"final_movies ::::: {final_movies}")
    return render_template('movie_selection.html', movies=final_movies, our_Recommendations=our_Recommendations)

# ---- MOVIE API ENDPOINT ------
def fetch_tmdb_movie(provider=None, omit=None, genre=None, rating=None, year_range=None):
    url = "https://api.themoviedb.org/3/discover/movie"

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
        "watch_region": "US",
        "region": "US",
        "certification_country": "US"
    }

    if provider:
        params["with_watch_providers"] = provider
    if omit:
        params["without_watch_providers"] = omit
    if genre:
        params["with_genres"] = genre
    if rating:
        params["certification"] = rating
    if year_range and len(year_range) == 2:
        params["primary_release_date.gte"] = f"{year_range[0]}-01-01"
        params["primary_release_date.lte"] = f"{year_range[1]}-12-31"

    try:
        # Make the request to the TMDb API
        logger.info(f"API Params: {params}")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from TMDb API: {e}")
        return None

def Recommendation_Fetcher(movie_titles):
    all_movie_results = []
    
    for title in movie_titles:
        url = "https://api.themoviedb.org/3/search/movie"
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "accept": "application/json"
        }
        
        params = {
            "query": title,
            "language": "en-US",
            "page": 1,
            "include_adult": "false"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # If results exist, take the first match
            if data.get('results'):
                # Sort results by popularity and take the top result
                top_result = sorted(data['results'], 
                                    key=lambda x: x.get('popularity', 0), 
                                    reverse=True)[0]
                all_movie_results.append(top_result)
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching for '{title}': {e}")
    
    return all_movie_results
    

# Service Mapping
def service_mapping(provider):
    url = "https://api.themoviedb.org/3/watch/providers/movie?language=en-US"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        omits, providers = None, None
        provider_mapping = {provider['provider_name'].lower(): provider['provider_id'] for provider in data['results']}
        if provider == "netflix-button":
            providers = {'netflix': provider_mapping.get('netflix')}
        elif provider == "hulu-button":
            providers = {'hulu': provider_mapping.get('hulu')}
        elif provider == "third-party-button":
            omits = {'hulu': provider_mapping.get('hulu'), 
                     'netflix': provider_mapping.get('netflix')
            }
            providers = None
        elif provider == "all-button":
            providers = ""
        else:
            print(f"Error fetching service: {e}")
            return None
        
        # Map provider names to their IDs
        return providers, omits
    except requests.exceptions.RequestException as e:
        print(f"Error fetching service: {e}")
        return None
    
def genre_mapping(genre):
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
        genre_mapping = {g['name'].lower(): g['id'] for g in data['genres']}

        # Filter by input genre if provided
        if genre:
            genre_id = genre_mapping.get(genre.lower())
            return {genre: genre_id} if genre_id else {}
        return genre_mapping
    except requests.exceptions.RequestException as e:
        print(f"Error fetching genres: {e}")
        return None

@app.route('/random_movie')
def random_movie():
    url = "https://api.themoviedb.org/3/movie/top_rated?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }

    # Fetch popular movies
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        movies = response.json().get('results', [])
        if movies:
            # Pick a random movie from the list
            random_movie = random.choice(movies)
            return render_template('random_movie.html', movie=random_movie)
        else:
            logger.error("No movies found.")
    else:
        logger.error(f"Error fetching movies: {response.status_code}")
        return render_template('random_movie.html')


if __name__ == "__main__":
    app.run(debug=True)
