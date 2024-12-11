# ReelVibes

# Database Setup:

1. Install HeidiSQL/MySQLWorkbench
2. Open connection to a server with ports matching database connection (lines 50-60) in app.py.
3. Create database called reelvibes, if asked use utf8mb4_unicode_520_ci.
4. Copy create_database_tables.SQL into reelvibes query and execute (make sure tables are created)
5. Change database connection password in app.py to your database connection password

# Application Usage:

1. Within terminal, navigate to directory containing ReelVibes.

2. Once there, create Virtual Environment
```
python -m virtualenv venv
```
Where venv is the name of your virtual environment.

3. Activate Virtual Environment
```
venv\scripts\activate
```

4. Install Requirements
```
pip install -r requirements.txt
```

5. Run Application
```
python app.py
```
