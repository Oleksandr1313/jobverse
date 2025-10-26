import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("DB_HOST")
DATABASE = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
PORT = int(os.getenv("DB_PORT"))

try:
    conn = psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print("Testing...")
    print("Connected to:", cursor.fetchone())
    conn.close()
except psycopg2.OperationalError as e:
    print("Connection failed:", e)
