import streamlit as st
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()

HOST = os.getenv("DB_HOST")
DATABASE = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
PORT = os.getenv("DB_PORT")

# Page config
st.set_page_config(
    page_title="JobVerse Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- DATABASE CONNECTION ----
def get_conn():
    return psycopg2.connect(
        host=HOST, database=DATABASE, user=USER, password=PASSWORD, port=PORT
    )

@st.cache_data(ttl=600)
def load_data():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM jobs ORDER BY id DESC;", conn)
    conn.close()
    return df

# ---- MAIN APP ----
st.title("💼 JobVerse – Job Market Dashboard")
st.markdown("Explore the latest scraped jobs from **Indeed** and **Glassdoor** in a modern interface.")

df = load_data()

if df.empty:
    st.warning("No jobs found in the database. Try running the scraper first.")
else:
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    selected_company = st.sidebar.selectbox("Filter by Company", ["All"] + sorted(df["company"].dropna().unique().tolist()))
    selected_location = st.sidebar.selectbox("Filter by Location", ["All"] + sorted(df["location"].dropna().unique().tolist()))

    filtered_df = df.copy()
    if selected_company != "All":
        filtered_df = filtered_df[filtered_df["company"] == selected_company]
    if selected_location != "All":
        filtered_df = filtered_df[filtered_df["location"] == selected_location]

    st.markdown(f"### Showing {len(filtered_df)} Job Results")

    # ---- STYLING ----
    st.markdown("""
        <style>
        .job-card {
            background-color: #f8f9fa;
            padding: 1.2rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
            transition: all 0.2s ease-in-out;
        }
        .job-card:hover {
            background-color: #f1f3f6;
            transform: translateY(-2px);
        }
        .job-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1e88e5;
        }
        .company-badge {
            background-color: #e3f2fd;
            color: #1565c0;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.85rem;
            margin-right: 0.5rem;
        }
        .job-location {
            color: #555;
            font-size: 0.9rem;
        }
        .job-desc {
            margin-top: 0.8rem;
            font-size: 0.9rem;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

    # ---- DISPLAY JOB CARDS ----
    for _, row in filtered_df.iterrows():
        with st.container():
            st.markdown(f"""
                <div class="job-card">
                    <div class="job-title">{row['job_title'] or 'No Title'}</div>
                    <div style="margin-top:4px;">
                        <span class="company-badge">{row['company'] or 'Unknown Company'}</span>
                        <span class="job-location">📍 {row['location'] or 'N/A'}</span>
                    </div>
                    <div class="job-desc">
                        {row['description'][:250] + '...' if row['description'] and len(row['description']) > 250 else row['description'] or ''}
                    </div>
                    <a href="{row['source_url']}" target="_blank">🔗 View job posting</a>
                </div>
            """, unsafe_allow_html=True)

