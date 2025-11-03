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
    """Establish a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT
    )

def create_tables():
    """Create the jobs table if it doesn't exist."""
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
    """Insert a job into the database, skip if duplicate, then clean invalid rows."""
    conn = get_conn()
    cursor = conn.cursor()

    try:
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

    except Exception as e:
        print(f"Insert failed: {e}")
    finally:
        cursor.close()
        conn.close()

    cleanup_jobs()

def fetch_jobs(limit=None):
    """Fetch jobs from the database. Optionally limit the number of rows."""
    cleanup_jobs()
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

def cleanup_jobs():
    """Remove records with NULL or invalid values (e.g. 'NA', 'N/A')."""
    conn = get_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM jobs
            WHERE company IS NULL OR company ILIKE 'NA' OR company ILIKE 'N/A'
               OR location IS NULL OR location ILIKE 'NA' OR location ILIKE 'N/A'
               OR job_title IS NULL OR job_title ILIKE 'NA' OR job_title ILIKE 'N/A';
        """)
        conn.commit()

    except Exception as e:
        print(f"Cleanup failed: {e}")
    finally:
        cursor.close()
        conn.close()