import streamlit as st
import tempfile
import fitz
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from resume_analyzer.analyzer import analyze_resume

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

def render_analyzer_section():
    st.header("Resume Analyzer")

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