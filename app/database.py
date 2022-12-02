import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import time

load_dotenv("venv/.env")

db_user = os.getenv('DB_USR')
db_pass = os.getenv('DB_PASS')

while True:
    try: 
        conn = psycopg2.connect(host = 'localhost', database='fastapi',
        user = db_user, password = db_pass, cursor_factory=RealDictCursor) ##RealDictCursor gives column name and value as dict
        cursor = conn.cursor()
        print('DB connection successful')
        break
    except Exception as error:
        print(f"Connecting to DB failed: {error}")
        time.sleep(2)

def create_user_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS users (email VARCHAR (255) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL);")
    conn.commit()
    print("table created")