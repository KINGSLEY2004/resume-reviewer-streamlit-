import streamlit as st
import google.generativeai as genai
import os
import pdfplumber
import json
from datetime import datetime

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
        border-radius: 8px;
        text-align: center;
        margin: 1em 0;
    }
    .improvement-box {
        background-color: #1E3A2E;
        padding: 1.2em;
        border-radius: 10px;
        border-left: 5px solid #28A745;
        margin-bottom: 1em;
    }
    .gap-box {
        background-color: #3A1E1E;
        padding: 1.2em;
        border-radius: 10px;
        border-left: 5px solid #DC3545;
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
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting PDF text: {str(e)}")
        return ""

def get_detailed_resume_feedback(resume_text, job_role, job_description=None):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) specialist and senior technical recruiter with 10+ years of experience. 
    Analyze the following resume for the target job role: {job_role}
    
    Resume Content:
    {resume_text}
    
    {"Job Description: " + job_description if job_description else ""}
    
    Please provide a comprehensive analysis in the following JSON format:
    {{
        "overall_score": <score out of 100>,
        "section_scores": {{
            "contact_info": <score out of 100>,
            "summary": <score out of 100>,
            "experience": <score out of 100>,
            "education": <score out of 100>,
            "skills": <score out of 100>,
            "formatting": <score out of 100>
        }},
        "strengths": [
            "List of specific strengths found in the resume"
        ],
        "gaps_and_improvements": [
            "List of specific gaps and areas for improvement"
        ],
        "missing_keywords": [
            "Keywords relevant to {job_role} that are missing"
        ],
        "formatting_issues": [
            "Specific formatting or structure issues"
        ],
        "tailoring_suggestions": [
            "Specific suggestions to tailor for {job_role}"
        ],
        "detailed_feedback": {{
            "contact_info": "Detailed feedback on contact information section",
            "summary": "Detailed feedback on professional summary/objective",
            "experience": "Detailed feedback on work experience section",
            "education": "Detailed feedback on education section",
            "skills": "Detailed feedback on skills section",
            "projects": "Detailed feedback on projects section if present"
        }},
        "action_items": [
            "Specific actionable items to improve the resume"
        ]
    }}
    
    Make sure to provide specific, actionable feedback tailored to the {job_role} position.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating feedback: {str(e)}")
        return None

def generate_improved_resume(resume_text, job_role, feedback_json):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Based on the feedback provided, create an improved version of the resume for the {job_role} position.
    
    Original Resume:
    {resume_text}
    
    Feedback Summary:
    {feedback_json.get('action_items', [])}
    
    Please provide an improved version of the resume that addresses the key issues identified.
    Format it as a clean, professional resume with proper sections and formatting.
    Focus on making it more ATS-friendly and tailored to the {job_role} position.
    
    Return only the improved resume content, properly formatted.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating improved resume: {str(e)}")
        return None

def compare_with_job_description(resume_text, job_description):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Compare the following resume with the job description and provide a match analysis.
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Provide analysis in JSON format:
    {{
        "match_percentage": <percentage match>,
        "matched_skills": ["list of skills that match"],
        "missing_skills": ["list of required skills not found in resume"],
        "experience_alignment": "How well experience aligns with job requirements",
        "recommendations": ["specific recommendations to improve match"]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error comparing with job description: {str(e)}")
        return None

def initialize_session_state():
    if 'feedback_history' not in st.session_state:
        st.session_state.feedback_history = []
    if 'current_resume' not in st.session_state:
        st.session_state.current_resume = ""

# ==========================
# STREAMLIT UI
# ==========================
initialize_session_state()

# Sidebar
with st.sidebar:
    st.header("📋 Configuration")
    
    # Privacy Disclaimer
    st.warning("🔒 **Privacy Notice**: Your resume is processed securely and not stored permanently. AI analysis is used for feedback generation only.")
    
    # Job Role Selection
    job_roles = [
        "Data Scientist", "Software Engineer", "Product Manager", "Data Analyst",
        "Machine Learning Engineer", "Full Stack Developer", "DevOps Engineer",
        "Business Analyst", "UX/UI Designer", "Project Manager", "Marketing Manager",
        "Sales Representative", "Financial Analyst", "HR Specialist", "Other"
    ]
    
    selected_job_role = st.selectbox("🎯 Select Target Job Role", job_roles)
    
    if selected_job_role == "Other":
        custom_job_role = st.text_input("Enter custom job role:")
        job_role = custom_job_role if custom_job_role else "General"
    else:
        job_role = selected_job_role
    
    st.write(f"**Selected Role:** {job_role}")
    
    # Feedback History
    if st.session_state.feedback_history:
        st.header("📊 Feedback History")
        for i, entry in enumerate(st.session_state.feedback_history[-3:], 1):
            st.write(f"**{i}.** {entry['job_role']} - Score: {entry['score']}/100")

# Main Content
st.title("🚀 Smart Resume Reviewer")
st.markdown("*Get AI-powered feedback to optimize your resume for any job role*")

# Input Methods
tab1, tab2 = st.tabs(["📎 Upload Resume", "✍️ Paste Resume Text"])

resume_text = ""

with tab1:
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF or TXT)", 
        type=["pdf", "txt"],
        help="Upload your resume in PDF or text format for analysis"
    )
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = uploaded_file.read().decode("utf-8")
        
        st.success(f"✅ File uploaded successfully! ({len(resume_text)} characters extracted)")

with tab2:
    resume_text = st.text_area(
        "Paste your resume text here:",
        height=300,
        placeholder="Copy and paste your complete resume text here..."
    )

# Job Description (Optional)
job_description_expander = st.expander("🎯 Add Job Description (Optional - for better tailoring)", expanded=False)
with job_description_expander:
    job_description = st.text_area(
        "Paste the job description here:",
        height=200,
        placeholder="Paste the complete job description to get more targeted feedback..."
    )

if not job_description:
    job_description = None

# Analysis Section
if resume_text.strip():
    st.session_state.current_resume = resume_text
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        analyze_button = st.button("🔍 Analyze Resume", type="primary")
    
    with col2:
        if job_description:
            compare_button = st.button("⚖️ Compare with Job")
        else:
            compare_button = False
    
    with col3:
        improve_button = st.button("✨ Generate Improved Version")
    
    # Main Analysis
    if analyze_button:
        with st.spinner("🔄 Analyzing your resume... This may take a moment"):
            feedback = get_detailed_resume_feedback(resume_text, job_role, job_description)
            
            if feedback:
                try:
                    # Try to parse as JSON
                    feedback_json = json.loads(feedback.replace("```json", "").replace("```", ""))
                    
                    # Store in session state
                    st.session_state.feedback_history.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'job_role': job_role,
                        'score': feedback_json.get('overall_score', 0)
                    })
                    
                    # Display Results
                    st.success("✅ Analysis Complete!")
                    
                    # Overall Score
                    overall_score = feedback_json.get('overall_score', 0)
                    st.markdown(f"""
                    <div class="score-box">
                        <h2>Overall Resume Score</h2>
                        <h1 style="color: {'#28A745' if overall_score >= 70 else '#FFC107' if overall_score >= 50 else '#DC3545'};">
                            {overall_score}/100
                        </h1>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Section Scores
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📊 Section Scores")
                        section_scores = feedback_json.get('section_scores', {})
                        for section, score in section_scores.items():
                            st.metric(
                                label=section.replace('_', ' ').title(),
                                value=f"{score}/100"
                            )
                    
                    with col2:
                        st.subheader("💪 Key Strengths")
                        strengths = feedback_json.get('strengths', [])
                        for strength in strengths[:5]:
                            st.success(f"✅ {strength}")
                    
                    # Gaps and Improvements
                    st.subheader("🎯 Areas for Improvement")
                    gaps = feedback_json.get('gaps_and_improvements', [])
                    for gap in gaps:
                        st.markdown(f"""
                        <div class="gap-box">
                            ⚠️ {gap}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Missing Keywords
                    if feedback_json.get('missing_keywords'):
                        st.subheader("🔍 Missing Keywords")
                        keywords = feedback_json.get('missing_keywords', [])
                        st.info(f"**Consider adding these keywords:** {', '.join(keywords)}")
                    
                    # Detailed Feedback
                    st.subheader("📝 Detailed Section Feedback")
                    detailed = feedback_json.get('detailed_feedback', {})
                    
                    for section, feedback_text in detailed.items():
                        with st.expander(f"{section.replace('_', ' ').title()} Feedback"):
                            st.write(feedback_text)
                    
                    # Action Items
                    st.subheader("✅ Action Items")
                    actions = feedback_json.get('action_items', [])
                    for i, action in enumerate(actions, 1):
                        st.markdown(f"**{i}.** {action}")
                    
                except json.JSONDecodeError:
                    # Fallback to plain text display
                    st.subheader("📋 Resume Feedback")
                    st.markdown(f"""
                    <div class="feedback-box">
                    {feedback.replace(chr(10), "<br>")}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Job Description Comparison
    if compare_button and job_description:
        with st.spinner("⚖️ Comparing with job description..."):
            comparison = compare_with_job_description(resume_text, job_description)
            
            if comparison:
                st.subheader("⚖️ Job Match Analysis")
                try:
                    comp_json = json.loads(comparison.replace("```json", "").replace("```", ""))
                    
                    match_pct = comp_json.get('match_percentage', 0)
                    st.markdown(f"""
                    <div class="score-box">
                        <h3>Job Match Score</h3>
                        <h2 style="color: {'#28A745' if match_pct >= 70 else '#FFC107' if match_pct >= 50 else '#DC3545'};">
                            {match_pct}%
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**✅ Matched Skills:**")
                        for skill in comp_json.get('matched_skills', []):
                            st.success(skill)
                    
                    with col2:
                        st.write("**❌ Missing Skills:**")
                        for skill in comp_json.get('missing_skills', []):
                            st.error(skill)
                    
                    st.write("**📊 Experience Alignment:**")
                    st.info(comp_json.get('experience_alignment', ''))
                    
                    st.write("**💡 Recommendations:**")
                    for rec in comp_json.get('recommendations', []):
                        st.write(f"• {rec}")
                        
                except json.JSONDecodeError:
                    st.write(comparison)
    
    # Generate Improved Resume
    if improve_button:
        if 'feedback_history' in st.session_state and st.session_state.feedback_history:
            with st.spinner("✨ Generating improved resume version..."):
                # Use the most recent feedback
                improved_resume = generate_improved_resume(resume_text, job_role, {})
                
                if improved_resume:
                    st.subheader("✨ Improved Resume Version")
                    st.markdown(f"""
                    <div class="improvement-box">
                    <pre style="white-space: pre-wrap; font-family: 'Times New Roman', serif;">
{improved_resume}
                    </pre>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Download option (as text)
                    st.download_button(
                        label="📥 Download Improved Resume",
                        data=improved_resume,
                        file_name=f"improved_resume_{job_role.lower().replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
        else:
            st.warning("Please analyze your resume first to generate an improved version.")

else:
    st.info("👆 Please upload your resume or paste your resume text to get started!")

# Footer
st.markdown("---")
st.markdown("*Built with ❤️ using Streamlit and Google Gemini AI*")
