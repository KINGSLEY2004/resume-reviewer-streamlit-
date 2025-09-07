import os
import io
import streamlit as st
from openai import OpenAI
import fitz  # PyMuPDF

st.set_page_config(page_title="AI Resume Reviewer", page_icon="🧠", layout="centered")

# --------- Helpers ----------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            # "text" returns plain text; fast & reliable for most PDFs
            text += page.get_text("text")
    return text

def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ Add your OPENAI_API_KEY in Streamlit 'App → Settings → Secrets' (or as an env var).")
        st.stop()
    return OpenAI(api_key=api_key)

# --------- UI ----------
st.title("🧠 AI Resume Reviewer")
st.caption("Upload your resume, pick a target role, and get tailored, constructive feedback.")

col1, col2 = st.columns(2)
with col1:
    job_role = st.text_input("🎯 Target Job Role (e.g., Data Scientist, Product Manager)", "")
with col2:
    score_toggle = st.toggle("Show scores (0–100)", value=True)

job_desc = st.text_area("📋 (Optional) Paste Job Description", height=150, placeholder="Paste the JD here for more accurate, ATS-aligned feedback…")

resume_file = st.file_uploader("📄 Upload Resume (PDF or .txt)", type=["pdf", "txt"])

if st.button("Analyze Resume", type="primary"):
    if not job_role:
        st.warning("Please enter a target job role.")
        st.stop()
    if not resume_file:
        st.warning("Please upload a resume (PDF or .txt).")
        st.stop()

    # Read resume text
    with st.spinner("Extracting resume text…"):
        if resume_file.name.lower().endswith(".pdf"):
            file_bytes = resume_file.getvalue()
            resume_text = extract_text_from_pdf(file_bytes)
        else:  # .txt
            resume_text = resume_file.read().decode("utf-8", errors="ignore")

    if len(resume_text.strip()) < 50:
        st.error("Could not extract enough text from the resume. Try a different file or a selectable-text PDF.")
        st.stop()

    client = get_openai_client()

    system_prompt = f"""You are an expert resume reviewer specializing in {job_role}.
Provide concise, actionable, and section-wise feedback to improve alignment with the role and typical ATS filters.
Return Markdown with clear headings and bullet points. Keep tone supportive and specific."""

    user_prompt = f"""
=== JOB ROLE ===
{job_role}

=== JOB DESCRIPTION (Optional) ===
{job_desc if job_desc else "N/A"}

=== RESUME TEXT ===
{resume_text}

=== INSTRUCTIONS ===
1) Give **Section-wise Feedback** for: Summary/Profile, Experience, Projects, Education, Skills, Certifications, Extras.
2) List **Missing/Weak Keywords** compared to the job role/JD.
3) Point out **Vague/Redundant language** and suggest rewrites (bullet points w/ strong action verbs + metrics).
4) Formatting advice: length, order, consistency, readability for ATS.
5) If 'Show scores' is on, include a short **Scorecard** (0–100) for: Relevance, Impact (metrics), Clarity, ATS Keywords, Formatting.
6) End with a short **Tailored Summary** (3–5 bullets) of the top improvements to make right now.
"""

    with st.spinner("Reviewing resume with AI…"):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )
            feedback = resp.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI error: {e}")
            st.stop()

    # Optionally hide scorecard if toggle is off
    if not score_toggle:
        # A light filter: remove a 'Scorecard' section if present
        import re
        feedback = re.sub(r"(?is)#+\\s*scorecard.*?(?=\\n#|$)", "", feedback).strip()

    st.subheader("✅ Feedback")
    st.markdown(feedback)

    # Download feedback
    st.download_button(
        label="⬇️ Download feedback as Markdown",
        data=feedback.encode("utf-8"),
        file_name="resume_feedback.md",
        mime="text/markdown",
    )

st.markdown("---")
st.caption("Privacy: Your resume is processed in-memory for this session only. Do not share sensitive personal data.")
