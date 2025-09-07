import streamlit as st
import google.generativeai as genai
import os
import pdfplumber
import json
from datetime import datetime
import io
from fpdf import FPDF

# ==========================
# CONFIG
# ==========================
# Replace with your Gemini API key
GEMINI_API_KEY = "AIzaSyDf1E4BZcebrZjTMwlgYhkwIcUi6N-KKFo"
genai.configure(api_key=GEMINI_API_KEY)

# Set Streamlit page config
st.set_page_config(
    page_title="Smart Resume Reviewer",
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
    .score-box {
        background-color: #2D2D2D;
        padding: 1em;
        border-radius: 10px;
        border: 2px solid #EB1F28;
        text-align: center;
        margin: 1em 0;
    }
    .strength-box {
        background-color: #1B3B36;
        padding: 0.8em;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin-bottom: 0.5em;
    }
    .weakness-box {
        background-color: #3B1B1B;
        padding: 0.8em;
        border-radius: 8px;
        border-left: 4px solid #F44336;
        margin-bottom: 0.5em;
    }
    .improvement-box {
        background-color: #2D2A1B;
        padding: 0.8em;
        border-radius: 8px;
        border-left: 4px solid #FF9800;
        margin-bottom: 0.5em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================
# HELPER FUNCTIONS
# ==========================
def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""
    return text.strip()

def get_comprehensive_resume_feedback(resume_text, job_role, job_description=""):
    """Get comprehensive feedback using Gemini AI"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    You are an expert technical recruiter and career coach. Review the following resume for the position of {job_role}.
    
    Resume Content:
    {resume_text}
    
    {"Job Description: " + job_description if job_description else ""}
    
    Please provide a comprehensive analysis in JSON format with the following structure:
    {{
        "overall_score": {{
            "score": [number out of 10],
            "explanation": "brief explanation of the score"
        }},
        "section_scores": {{
            "contact_info": [score out of 10],
            "summary": [score out of 10],
            "experience": [score out of 10],
            "education": [score out of 10],
            "skills": [score out of 10],
            "formatting": [score out of 10]
        }},
        "strengths": [
            "strength 1",
            "strength 2",
            "strength 3"
        ],
        "weaknesses": [
            "weakness 1",
            "weakness 2",
            "weakness 3"
        ],
        "missing_keywords": [
            "keyword 1",
            "keyword 2",
            "keyword 3"
        ],
        "detailed_feedback": {{
            "contact_info": "feedback on contact information",
            "summary": "feedback on professional summary",
            "experience": "feedback on work experience",
            "education": "feedback on education section",
            "skills": "feedback on skills section",
            "formatting": "feedback on overall formatting"
        }},
        "improvement_suggestions": [
            "suggestion 1",
            "suggestion 2",
            "suggestion 3",
            "suggestion 4",
            "suggestion 5"
        ],
        "job_alignment": {{
            "alignment_score": [number out of 10],
            "alignment_feedback": "how well the resume aligns with the job role"
        }}
    }}
    
    Ensure your response is valid JSON format only.
    """
    
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip())
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return generate_fallback_feedback(resume_text, job_role, job_description)
    except Exception as e:
        st.error(f"Error generating feedback: {str(e)}")
        return None

def generate_fallback_feedback(resume_text, job_role, job_description=""):
    """Fallback feedback generation if JSON parsing fails"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    You are an expert technical recruiter. Review the following resume for the position of {job_role}.
    
    Resume:
    {resume_text}
    
    {"Job Description: " + job_description if job_description else ""}
    
    Provide structured feedback covering:
    1. Overall Assessment (with score out of 10)
    2. Strengths
    3. Areas for Improvement
    4. Missing Keywords/Skills
    5. Specific Section Feedback
    6. Job Alignment Analysis
    """
    
    try:
        response = model.generate_content(prompt)
        return {"fallback_feedback": response.text}
    except Exception as e:
        return {"error": f"Could not generate feedback: {str(e)}"}

def generate_improved_resume(resume_text, job_role, feedback_data):
    """Generate an improved version of the resume"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Based on the feedback provided, create an improved version of the resume for the {job_role} position.
    
    Original Resume:
    {resume_text}
    
    Improvement Areas:
    - Missing keywords: {', '.join(feedback_data.get('missing_keywords', []))}
    - Suggestions: {', '.join(feedback_data.get('improvement_suggestions', []))}
    
    Please provide an improved version that:
    1. Incorporates relevant keywords
    2. Improves formatting and structure
    3. Enhances clarity and impact
    4. Maintains truthfulness to the original content
    
    Return only the improved resume text.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating improved resume: {str(e)}"

def create_pdf_report(feedback_data, resume_text, job_role):
    """Create a PDF report of the feedback"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Resume Review Report - {job_role}", ln=True, align='C')
    pdf.ln(10)
    
    # Overall Score
    pdf.set_font("Arial", 'B', 14)
    if 'overall_score' in feedback_data:
        pdf.cell(0, 10, f"Overall Score: {feedback_data['overall_score']['score']}/10", ln=True)
        pdf.ln(5)
    
    # Strengths
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Strengths:", ln=True)
    pdf.set_font("Arial", size=10)
    for strength in feedback_data.get('strengths', []):
        pdf.cell(0, 8, f"• {strength}", ln=True)
    pdf.ln(5)
    
    # Areas for Improvement
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Areas for Improvement:", ln=True)
    pdf.set_font("Arial", size=10)
    for weakness in feedback_data.get('weaknesses', []):
        pdf.cell(0, 8, f"• {weakness}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================
# SESSION STATE INITIALIZATION
# ==========================
if 'feedback_history' not in st.session_state:
    st.session_state.feedback_history = []
if 'current_feedback' not in st.session_state:
    st.session_state.current_feedback = None

# ==========================
# MAIN APPLICATION
# ==========================

# Privacy Disclaimer
with st.sidebar:
    st.markdown("### 🔒 Privacy Notice")
    st.info("Your resume data is processed securely and not stored permanently. AI analysis is used to provide feedback.")
    
    st.markdown("### 📊 Feedback History")
    if st.session_state.feedback_history:
        for i, item in enumerate(st.session_state.feedback_history):
            if st.button(f"Review {i+1} - {item['job_role']}", key=f"history_{i}"):
                st.session_state.current_feedback = item['feedback']

# Main Title
st.title("🎯 Smart Resume Reviewer")
st.markdown("**Get AI-powered feedback to optimize your resume for specific job roles**")

# Create two columns for input
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📄 Resume Input")
    
    # Resume input options
    input_method = st.radio("Choose input method:", ["Upload File", "Paste Text"])
    
    resume_text = ""
    
    if input_method == "Upload File":
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "txt"])
        
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(uploaded_file)
            else:
                resume_text = uploaded_file.read().decode("utf-8")
    else:
        resume_text = st.text_area("Paste your resume text here:", height=300)

with col2:
    st.subheader("🎯 Job Details")
    
    # Job role selection
    common_roles = [
        "Data Scientist", "Software Engineer", "Product Manager", 
        "Marketing Manager", "Business Analyst", "UX Designer",
        "DevOps Engineer", "Sales Manager", "HR Manager", "Other"
    ]
    
    job_role_option = st.selectbox("Select target job role:", common_roles)
    
    if job_role_option == "Other":
        job_role = st.text_input("Enter custom job role:")
    else:
        job_role = job_role_option
    
    # Optional job description
    job_description = st.text_area("Job description (optional):", height=150, 
                                 placeholder="Paste the job description here to get more targeted feedback...")

# Analysis Section
if resume_text and job_role:
    st.subheader("📄 Resume Preview")
    with st.expander("View extracted resume text", expanded=False):
        st.text_area("Resume Content", resume_text, height=200, disabled=True)
    
    # Analysis buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Analyze Resume", type="primary"):
            with st.spinner("Analyzing your resume... Please wait ⏳"):
                feedback = get_comprehensive_resume_feedback(resume_text, job_role, job_description)
                
                if feedback and 'error' not in feedback:
                    st.session_state.current_feedback = feedback
                    
                    # Add to history
                    st.session_state.feedback_history.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'job_role': job_role,
                        'feedback': feedback
                    })
                    
                    st.success("✅ Analysis Complete!")
                else:
                    st.error("❌ Analysis failed. Please try again.")
    
    with col2:
        if st.button("📈 Generate Improved Resume") and st.session_state.current_feedback:
            with st.spinner("Generating improved resume..."):
                improved_resume = generate_improved_resume(resume_text, job_role, st.session_state.current_feedback)
                st.session_state.improved_resume = improved_resume
    
    with col3:
        if st.button("📄 Download Report") and st.session_state.current_feedback:
            text_report = create_text_report(st.session_state.current_feedback, resume_text, job_role)
            st.download_button(
                label="Download Text Report",
                data=text_report,
                file_name=f"resume_review_{job_role.lower().replace(' ', '_')}.txt",
                mime="text/plain"
            )

# Display Feedback
if st.session_state.current_feedback:
    feedback = st.session_state.current_feedback
    
    if 'fallback_feedback' in feedback:
        # Display fallback feedback
        st.subheader("📊 Resume Analysis")
        st.markdown(f"""
        <div class="feedback-box">
        {feedback['fallback_feedback'].replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Display structured feedback
        st.subheader("📊 Resume Analysis Results")
        
        # Overall Score
        if 'overall_score' in feedback:
            score = feedback['overall_score']['score']
            st.markdown(f"""
            <div class="score-box">
            <h2>Overall Score: {score}/10</h2>
            <p>{feedback['overall_score']['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Section Scores
        if 'section_scores' in feedback:
            st.subheader("📈 Section-wise Scores")
            cols = st.columns(3)
            section_items = list(feedback['section_scores'].items())
            
            for i, (section, score) in enumerate(section_items):
                with cols[i % 3]:
                    st.metric(section.replace('_', ' ').title(), f"{score}/10")
        
        # Strengths, Weaknesses, and Improvements in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("✅ Strengths")
            for strength in feedback.get('strengths', []):
                st.markdown(f"""
                <div class="strength-box">
                {strength}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("⚠️ Areas for Improvement")
            for weakness in feedback.get('weaknesses', []):
                st.markdown(f"""
                <div class="weakness-box">
                {weakness}
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            st.subheader("💡 Suggestions")
            for suggestion in feedback.get('improvement_suggestions', []):
                st.markdown(f"""
                <div class="improvement-box">
                {suggestion}
                </div>
                """, unsafe_allow_html=True)
        
        # Missing Keywords
        if feedback.get('missing_keywords'):
            st.subheader("🔍 Missing Keywords")
            keywords = feedback['missing_keywords']
            keyword_html = " ".join([f"<span style='background-color: #EB1F28; padding: 4px 8px; border-radius: 4px; margin: 2px; display: inline-block;'>{kw}</span>" for kw in keywords])
            st.markdown(keyword_html, unsafe_allow_html=True)
        
        # Detailed Section Feedback
        if 'detailed_feedback' in feedback:
            st.subheader("📝 Detailed Section Feedback")
            
            for section, detail in feedback['detailed_feedback'].items():
                with st.expander(f"{section.replace('_', ' ').title()} Feedback"):
                    st.write(detail)
        
        # Job Alignment
        if 'job_alignment' in feedback:
            st.subheader("🎯 Job Role Alignment")
            alignment = feedback['job_alignment']
            st.metric("Alignment Score", f"{alignment['alignment_score']}/10")
            st.write(alignment['alignment_feedback'])

# Display Improved Resume
if 'improved_resume' in st.session_state:
    st.subheader("📝 Improved Resume")
    st.text_area("Enhanced Resume", st.session_state.improved_resume, height=400)
    
    # Download improved resume
    st.download_button(
        label="📥 Download Improved Resume",
        data=st.session_state.improved_resume,
        file_name=f"improved_resume_{job_role.lower().replace(' ', '_')}.txt",
        mime="text/plain"
    )

# Footer
st.markdown("---")
st.markdown("**Made with ❤️ using Streamlit and Google Gemini AI**")
st.markdown("*Tip: For best results, ensure your resume is well-formatted and includes relevant experience for the target role.*")
