import streamlit as st
import google.generativeai as genai
import os
import pdfplumber

# ==========================
# CONFIG
# ==========================
# Replace with your Gemini API key
GEMINI_API_KEY = "AIzaSyDf1E4BZcebrZjTMwlgYhkwIcUi6N-KKFo"
genai.configure(api_key=GEMINI_API_KEY)

# Set Streamlit page config
st.set_page_config(
    page_title="AI Resume Feedback",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================
# CUSTOM CSS (Dark Theme with Your Colors)
# ==========================
st.markdown(
    """
    <style>
    body {
        background-color: #1A1A1A;
        color: #E0E0E0;
    }
    .stApp {
        background-color: #1A1A1A;
    }
    h1, h2, h3, h4 {
        color: #FFFFFF !important;
    }
    .stButton>button {
        background-color: #EB1F28;
        color: #FFFFFF;
        border-radius: 8px;
        padding: 0.6em 1em;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FF5A1F;
        color: #FFFFFF;
    }
    .css-10trblm {
        color: #E0E0E0 !important;
    }
    .stTextArea textarea {
        background-color: #262626;
        color: #FFFFFF;
        border-radius: 6px;
    }
    .stFileUploader label {
        color: #FF5A1F !important;
        font-weight: bold;
    }
    .feedback-box {
        background-color: #262626;
        padding: 1.2em;
        border-radius: 10px;
        border-left: 5px solid #EB1F28;
        margin-bottom: 1em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================
# HELPER FUNCTIONS
# ==========================
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def get_resume_feedback(resume_text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    You are an expert technical recruiter. Review the following resume content
    and provide structured, professional feedback.

    Resume:
    {resume_text}

    Please give feedback in this format:
    1. General Comments (Format, Structure, Contact Info)
    2. Education Feedback
    3. Project Feedback
    4. Skills Feedback
    5. Final Tips
    """
    response = model.generate_content(prompt)
    return response.text

# ==========================
# STREAMLIT UI
# ==========================
st.title("📄 AI Resume Feedback App")

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

if uploaded_file:
    # Extract text
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = uploaded_file.read().decode("utf-8")

    st.subheader("📄 Extracted Resume Text")
    st.text_area("Resume Content", resume_text, height=200)

    if st.button("🚀 Get AI Feedback"):
        with st.spinner("Analyzing your resume... Please wait ⏳"):
            feedback = get_resume_feedback(resume_text)

        st.success("✅ Feedback Generated!")

        st.markdown(f"""
        <div class="feedback-box">
        {feedback.replace("\n", "<br>")}
        </div>
        """, unsafe_allow_html=True)  
