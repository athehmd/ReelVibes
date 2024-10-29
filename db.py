# Module Imports
import mariadb
import sys
import os


# Connect to MariaDB Platform
try:
    mydb = mariadb.connect(
        user="root",
        password=os.environ["mariadbpassword"], #replace {os.environ["mariadbpassword"]} with your own mariadbpassword
        host="127.0.0.1",
        port=3306,
        database="reelvibes1"
    )
    
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

def get_db():
    return mydb;

