import streamlit as st
import google.generativeai as genai
import os
import pdfplumber
from fpdf import FPDF
from sklearn.feature_extraction.text import CountVectorizer

# ==========================
# CONFIG
# ==========================
GEMINI_API_KEY = os.getenv("AIzaSyDf1E4BZcebrZjTMwlgYhkwIcUi6N-KKFo")
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(
    page_title="AI Resume Feedback",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================
# CUSTOM CSS (Dark Theme)
# ==========================
st.markdown("""
<style>
body {background-color: #1A1A1A; color: #E0E0E0;}
.stApp {background-color: #1A1A1A;}
h1,h2,h3,h4 {color: #FFFFFF !important;}
.stButton>button {background-color: #EB1F28; color: #FFFFFF; border-radius: 8px; padding: 0.6em 1em; border:none; font-weight:bold;}
.stButton>button:hover {background-color: #FF5A1F; color:#FFFFFF;}
.stTextArea textarea {background-color:#262626; color:#FFFFFF; border-radius:6px;}
.stFileUploader label {color:#FF5A1F !important; font-weight:bold;}
.feedback-box {background-color:#262626; padding:1.2em; border-radius:10px; border-left:5px solid #EB1F28; margin-bottom:1em;}
.matched {color: #00FF00; font-weight:bold;}
.missing {color: #EB1F28; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# ==========================
# HELPER FUNCTIONS
# ==========================
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_keywords(text):
    vectorizer = CountVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])
    return set(vectorizer.get_feature_names_out())

def get_resume_feedback(resume_text, job_role="", job_description=""):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    You are an expert technical recruiter. Review the following resume content
    and provide structured, professional feedback tailored to the target job role.

    Resume:
    {resume_text}

    Target Job Role: {job_role}
    Job Description: {job_description}

    Please give feedback in this format:
    1. General Comments (Format, Structure, Contact Info)
    2. Education Feedback
    3. Project Feedback
    4. Skills Feedback (highlight missing skills based on job description)
    5. Final Tips
    """
    response = model.generate_content(prompt)
    return response.text

def generate_pdf(feedback_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, feedback_text)
    pdf_file = "resume_feedback.pdf"
    pdf.output(pdf_file)
    return pdf_file

# ==========================
# STREAMLIT UI
# ==========================
st.title("📄 AI Resume Feedback App")

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

job_role = st.text_input("Target Job Role", placeholder="e.g., Software Engineer")
job_description = st.text_area(
    "Paste Job Description Here (optional)",
    placeholder="Paste detailed JD to tailor feedback...",
    height=150
)

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = uploaded_file.read().decode("utf-8")

    st.subheader("📄 Extracted Resume Text")
    st.text_area("Resume Content", resume_text, height=200)

    if st.button("🚀 Get AI Feedback"):
        with st.spinner("Analyzing your resume... Please wait ⏳"):
            feedback = get_resume_feedback(resume_text, job_role, job_description)

        st.success("✅ Feedback Generated!")

        # ==========================
        # Keyword Analysis
        # ==========================
        if job_description:
            resume_keywords = extract_keywords(resume_text)
            jd_keywords = extract_keywords(job_description)

            missing_keywords = jd_keywords - resume_keywords
            matched_keywords = jd_keywords & resume_keywords

            st.subheader("🔍 Keyword Gap Analysis")
            col1, col2 = st.columns(2)
            col1.markdown("**Matched Skills:** " + ", ".join([f"<span class='matched'>{k}</span>" for k in matched_keywords]), unsafe_allow_html=True)
            col2.markdown("**Missing Skills:** " + ", ".join([f"<span class='missing'>{k}</span>" for k in missing_keywords]), unsafe_allow_html=True)

        # ==========================
        # Section-wise Feedback Display
        # ==========================
        sections = ["General Comments", "Education Feedback", "Project Feedback", "Skills Feedback", "Final Tips"]
        for section in sections:
            with st.expander(section):
                st.markdown(f"<div class='feedback-box'>{feedback.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

        # ==========================
        # Download Buttons
        # ==========================
        st.download_button(
            label="📥 Download Feedback (Markdown)",
            data=feedback,
            file_name="resume_feedback.md",
            mime="text/markdown"
        )

        pdf_file = generate_pdf(feedback)
        st.download_button(
            label="📥 Download Feedback (PDF)",
            data=open(pdf_file, "rb"),
            file_name="resume_feedback.pdf",
            mime="application/pdf"
        )
