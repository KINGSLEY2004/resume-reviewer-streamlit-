# resume-reviewer-streamlit-


Problem statement:
Smart Resume Reviewer

Problem Descriptionnn

The goal is to build an LLM-powered (Large Language Model) application that reviews resumes and offers tailored, constructive feedback for a specific job role. This tool should assist job seekers in optimizing their resumes to better align with job descriptions and industry expectations.

Key Features & Functional Requirements:

Resume Upload/Input
- Users should be able to upload resumes in PDF or text format.
- Alternatively, users can paste their resume text into a textbox.

Job Role Selection
- Users must be able to specify the target job role (e.g., Data Scientist, Product Manager).
- Optionally, allow for uploading or pasting a job description to guide the feedback.

LLM-Powered Review Engine
- Analyze structure, content, and tone
- Provide specific feedback such as:
• Missing skills or keywords relevant to the job.
• Recommendations to improve formatting or clarity.
• Highlighting redundant or vague language.
• Suggestions to tailor experience/achievements to the job role.
- Score or rate the resume on various aspects (optional).

Output Format
- Clearly structured feedback, possibly section-wise (Education, Experience, Skills, etc.)
- Optionally, generate an improved version of the resume.

User Interface:

- Web-based interface (using Streamlit, Flask, etc.).
- User-friendly experience for uploading resumes and viewing feedback.

Security & Privacy:

- Ensure uploaded resumes are not stored or exposed publicly.
- (Optional) Include a disclaimer about AI usage and privacy.

Technical Guidelines:

- Programming Language: Python (preferred)
- Models: OpenAI GPT-4, Claude, Mistral, or open-source models like LLaMA, depending on your access.
- Libraries:
• langchain, openai/anthropic SDKs, pdfminer.six, PyMuPDF or pdfplumber(for PDF parsing)
• streamlit, flask, or gradio (for UI)
• pydantic, typer, fastapi (optional, for structured code or APIs)

Bonus Features (Optional):

- Resume comparison with a job description.
- Highlighted version of resume showing strengths and gaps.
- Tracking improvements over multiple uploads.
- PDF export of the reviewed resume.
- Support for multiple languages or regions.

Problem Selected!

How to set up & run:
step1: create a folder and a create a file named app.py and paste the code in the app.py in the github i given and in the powershell install required dependencies and use command in the powershell given below :            
      cd "E:\smart_resume"
      py -m streamlit run app.py

      since before this we used streamlit for our project 


      [📄 Smart Resume Reviewer

An AI-powered web app that reviews resumes and provides structured, constructive feedback tailored to a target job role.
Built with Python, Streamlit, and Google Generative AI, this tool helps job seekers optimize their resumes to better align with job descriptions and industry expectations.

🚀 Problem Statement

Job seekers often struggle with:

Resumes missing key skills and industry keywords

Poor formatting, structure, and clarity

Generic descriptions that don’t align with specific job roles

This results in lower chances of selection, especially with ATS (Applicant Tracking Systems) and competitive job markets.

Our solution: Smart Resume Reviewer – an AI-powered app that analyzes resumes, highlights gaps, and suggests improvements, empowering job seekers to present stronger, job-ready resumes.

⚡ Features

✅ Upload resumes in PDF or TXT format
✅ Extract and display resume content for quick review
✅ Enter target job role for tailored feedback
✅ Get structured AI feedback (Education, Skills, Projects, General Comments, Final Tips)
✅ Suggestions for missing skills, formatting improvements, and alignment with job role
✅ Dark theme UI with custom colors (#1A1A1A background, red & orange accents)
✅ Privacy-first: resumes are not stored or shared
✅ Option to generate and download an improved version of the resume (future scope)

🛠️ Tech Stack

Frontend / UI → Streamlit (Python)

AI Engine → Google Generative AI (Gemini 1.5 Flash model)

PDF Parsing → pdfplumber

Styling → Custom CSS (dark theme with red/orange accents)

🖥️ How to Set Up & Run
 cd "E:\smart_resume"
  py -m streamlit run app.py
  Install Dependencies
pip install -r requirements.txt
Run the App
streamlit run app.py
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/eee61f64-b8eb-4e36-b69a-e8e36bfaef82" />

Architecture

User uploads resume (PDF/TXT)

pdfplumber extracts text → displayed on UI

User enters target job role

Resume text + job role sent to Google Gemini

AI generates structured feedback → displayed in a styled feedback box

🌍 Future Enhancements

Compare resume directly with job descriptions

Highlight missing skills inline on the resume

Multi-language support

Export improved ATS-friendly resumes in PDF/Word

Track improvements across multiple uploads

👥 Team

Kingsley Joseph M (Developer – Christ University, Bengaluru)

This is the official submission repository for Mission UpSkill India Hackathon 2025.

