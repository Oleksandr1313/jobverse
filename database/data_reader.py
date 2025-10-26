import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

HOST = os.getenv("DB_HOST")
DATABASE = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
PORT = int(os.getenv("DB_PORT", 5432))

def get_conn():
    """Establish a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT
    )

def fetch_jobs(limit=None):
    """Fetch all jobs from the database. Optionally limit the number of rows."""
    conn = get_conn()
    cursor = conn.cursor()
    query = "SELECT id, job_title, company, location, description, source_url FROM jobs ORDER BY id DESC"
    if limit:
        query += f" LIMIT {limit}"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
