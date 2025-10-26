import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("DB_HOST")
DATABASE = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
PORT = int(os.getenv("DB_PORT", 5432)) 

def get_conn():
    return psycopg2.connect(
        host=HOST, database=DATABASE, user=USER, password=PASSWORD, port=PORT
    )

def create_tables():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id SERIAL PRIMARY KEY,
        job_title TEXT,
        company TEXT,
        location TEXT,
        description TEXT,
        source_url TEXT,
        UNIQUE(job_title, company, location)
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def insert_job(job_data):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (job_title, company, location, description, source_url)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (job_title, company, location) DO NOTHING;
    """, (
        job_data.get("job_title"),
        job_data.get("company"),
        job_data.get("location"),
        job_data.get("description"),
        job_data.get("source_url")
    ))
    conn.commit()
    cursor.close()
    conn.close()
