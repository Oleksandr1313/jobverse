import streamlit as st
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import tempfile
import fitz
import os
import sys
import pandas as pd
import torch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.db_manager import fetch_jobs

def extract_text_from_pdf(uploaded_file):
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    pdf = fitz.open(tmp_path)
    for page in pdf:
        text += page.get_text("text")
    pdf.close()
    os.remove(tmp_path)
    return text

def summarize_resume(resume_text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(resume_text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def extract_skills(resume_text):
    keywords = [
        "python", "sql", "java", "c++", "machine learning", "deep learning",
        "data analysis", "tensorflow", "pytorch", "nlp", "cloud", "aws",
        "azure", "docker", "react", "django", "flask", "pandas", "numpy"
    ]
    found = [kw for kw in keywords if kw.lower() in resume_text.lower()]
    return list(set(found))

def match_jobs(resume_text, top_k=5):
    rows = fetch_jobs()
    jobs_df = pd.DataFrame(rows, columns=["id", "job_title", "company", "location", "description", "source_url"])
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    resume_emb = embedder.encode(resume_text, convert_to_tensor=True)
    job_embeddings = embedder.encode(jobs_df['description'].tolist(), convert_to_tensor=True)
    cos_scores = util.cos_sim(resume_emb, job_embeddings)[0]
    top_results = torch.topk(cos_scores, k=min(top_k, len(jobs_df)))
    results = []
    for idx, score in zip(top_results.indices, top_results.values):
        job = jobs_df.iloc[idx.item()]
        results.append({
            "title": job['job_title'],
            "company": job['company'],
            "location": job['location'],
            "similarity": float(score),
            "description": job['description'][:300] + "..."
        })
    return results

def analyze_resume(resume_text):
    summary = summarize_resume(resume_text)
    skills = extract_skills(resume_text)
    matched_jobs = match_jobs(resume_text)
    return summary, skills, matched_jobs

def render_analyzer_section():
    st.header("🧠 Resume Analyzer")

    uploaded_resume = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
    manual_input = st.text_area(
        "Or paste your resume text here",
        height=400,
        placeholder="Paste your resume text here for analysis..."
    )

    if st.button("Analyze Resume"):
        if uploaded_resume:
            if uploaded_resume.name.endswith(".pdf"):
                resume_text = extract_text_from_pdf(uploaded_resume)
            else:
                resume_text = uploaded_resume.read().decode("utf-8", errors="ignore")
        elif manual_input.strip():
            resume_text = manual_input.strip()
        else:
            st.warning("Please upload a resume or paste text.")
            return

        summary, skills, matched_jobs = analyze_resume(resume_text)

        st.subheader("📋 Resume Summary")
        st.write(summary)

        st.subheader("🛠️ Extracted Skills")
        st.write(", ".join(skills) if skills else "No key skills detected.")

        st.subheader("🔍 Top Matching Jobs")
        for job in matched_jobs:
            st.markdown(f"""
                <div class="job-card">
                    <div class="job-title">{job['title']}</div>
                    <div class="company-badge">{job['company']}</div>
                    <div class="job-location">{job['location']}</div>
                    <div class="job-desc">{job['description']}</div>
                    <div style="margin-top:0.5rem; font-size:0.85rem; color:#6b7280;">
                        Similarity Score: {job['similarity']:.2f}
                    </div>
                </div>
            """, unsafe_allow_html=True)