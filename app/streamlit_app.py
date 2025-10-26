import streamlit as st
import pandas as pd

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.data_reader import fetch_jobs

st.set_page_config(page_title="Job Market Dashboard", layout="wide")
st.title("Job Market Dashboard")
st.markdown("Browse the latest Data Scientist and Software Developer jobs in Winnipeg!")

# Fetch jobs
jobs = fetch_jobs()

if not jobs:
    st.info("No jobs found in the database yet.")
else:
    # Convert to DataFrame
    df = pd.DataFrame(jobs, columns=["ID", "Job Title", "Company", "Location", "Description", "Source URL"])

    # Interactive table
    st.dataframe(df, use_container_width=True)

    # Optional: add filters
    st.sidebar.header("Filters")
    companies = st.sidebar.multiselect("Filter by Company", options=df["Company"].unique())
    locations = st.sidebar.multiselect("Filter by Location", options=df["Location"].unique())

    filtered_df = df
    if companies:
        filtered_df = filtered_df[filtered_df["Company"].isin(companies)]
    if locations:
        filtered_df = filtered_df[filtered_df["Location"].isin(locations)]

    st.subheader(f"Filtered Jobs ({len(filtered_df)})")
    st.dataframe(filtered_df, use_container_width=True)

    # Show job descriptions when clicked
    st.subheader("Job Details")
    job_id = st.number_input("Enter Job ID to see description", min_value=int(df["ID"].min()), max_value=int(df["ID"].max()), step=1)
    job_row = df[df["ID"] == job_id]
    if not job_row.empty:
        st.markdown(f"**Job Title:** {job_row['Job Title'].values[0]}")
        st.markdown(f"**Company:** {job_row['Company'].values[0]}")
        st.markdown(f"**Location:** {job_row['Location'].values[0]}")
        st.markdown(f"**Description:** {job_row['Description'].values[0]}")
        st.markdown(f"[Source URL]({job_row['Source URL'].values[0]})")
