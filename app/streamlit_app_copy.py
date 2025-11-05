import streamlit as st
import pandas as pd
import subprocess
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_manager import fetch_jobs


from pathlib import Path
styles_file_path = Path("C:\MainFolder\PortfolioProjects\job_market_dashboard\jobverse\styles\main.css")
with open(styles_file_path, "r", encoding="utf-8") as styles_read:
    styles = styles_read.read()


st.set_page_config(
    page_title="JobVerse Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)

# ---- MAIN APP ----
st.title("💼 JobVerse")
st.markdown("Explore the latest jobs from **Indeed**")

# Sidebar refresh button
if st.sidebar.button("🔄 Refresh Jobs"):
    with st.spinner("Scraping new jobs..."):
        subprocess.run(["python", "scraper.py"])  # run your scraper
    st.success("Jobs updated! Reload the page to see new results.")

# Load jobs
rows = fetch_jobs()
df = pd.DataFrame(rows, columns=["id", "job_title", "company", "location", "description", "source_url"])

df = df.dropna(subset=["job_title", "company", "location"])
df = df[~df["company"].str.upper().isin(["NA", "N/A"])]
df = df[~df["location"].str.upper().isin(["NA", "N/A"])]
df = df[~df["job_title"].str.upper().isin(["NA", "N/A"])]


if df.empty:
    st.warning("No jobs found in the database.")
else:
    st.sidebar.header("🔍 Filters")
    selected_company = st.sidebar.selectbox("Filter by Company", ["All"] + sorted(df["company"].dropna().unique().tolist()))
    selected_location = st.sidebar.selectbox("Filter by Location", ["All"] + sorted(df["location"].dropna().unique().tolist()))

    filtered_df = df.copy()
    if selected_company != "All":
        filtered_df = filtered_df[filtered_df["company"] == selected_company]
    if selected_location != "All":
        filtered_df = filtered_df[filtered_df["location"] == selected_location]

    st.markdown(f"### Showing {len(filtered_df)} Job Results")

    for _, row in filtered_df.iterrows():
        job_title = row['job_title'] or "No Title"
        company = row['company'] or "Unknown Company"
        location = row['location'] or "N/A"
        description = row['description'] or "No description provided."
        source_url = row['source_url'] or "#"

        st.markdown(f"""
            <div class="job-card">
                <div class="job-title">{job_title}</div>
                <div>
                    <span class="company-badge">{company}</span>
                    <span class="job-location">📍 {location}</span>
                </div>
                <div class="job-desc">{description[:300] + '...' if len(description) > 300 else description}</div>
                <a href="{source_url}" target="_blank" class="job-link">🔗 View Job Posting</a>
            </div>
        """, unsafe_allow_html=True)