import streamlit as st
import subprocess
import os
from pathlib import Path

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jobs_app import render_jobs_section
from analyzer_app import render_analyzer_section

# --- Page setup ---
st.set_page_config(
    page_title="JobVerse Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load CSS ---
styles_file_path = Path(r"C:\MainFolder\PortfolioProjects\job_market_dashboard\jobverse\styles\main.css")
with open(styles_file_path, "r", encoding="utf-8") as styles_read:
    styles = styles_read.read()
st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)

# --- Header ---
st.title("JOBVERSE")

# --- Sidebar ---
if st.sidebar.button("🔄 Refresh Jobs"):
    with st.spinner("Scraping new jobs..."):
        subprocess.run(["python", "scraper.py"])
    st.success("Jobs updated! Reload the page to see new results.")

# --- Split Layout ---
col1, col2 = st.columns([2, 1])  # left wider than right

with col1:
    render_jobs_section()

with col2:
    render_analyzer_section()
