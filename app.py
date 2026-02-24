import streamlit as st
import pdfplumber
import docx
import re
from fpdf import FPDF
import hashlib

# --- Page Configuration ---
st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="📊",
    layout="wide"
)

# --- Custom CSS for Colorful Design ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Title Styling */
    h1 {
        color: #ffffff !important;
        text-align: center;
        font-size: 48px !important;
        font-weight: bold !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 30px !important;
    }
    
    /* Subheaders */
    h2, h3 {
        color: #ffd700 !important;
    }
    
    /* Text Areas */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        border: 3px solid #ff6b6b !important;
        padding: 15px;
        font-size: 16px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb);
        border: none !important;
        border-radius: 30px !important;
        padding: 15px 50px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        color: white !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 30px rgba(0,0,0,0.4);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00ff88, #00cc6a) !important;
    }
    
    /* Login Card */
    .login-card {
        background: white;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        max-width: 400px;
        margin: 0 auto;
    }
    
    /* Score Card */
    .score-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 20px;
        padding: 30px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* ATS Card */
    .ats-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 20px;
        padding: 25px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* Category Card */
    .category-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        border-radius: 15px;
        padding: 20px;
        color: #333;
        margin: 10px 0;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
        border-radius: 5px;
    }
    
    /* Input fields */
    .stTextInput input {
        border-radius: 10px;
        border: 2px solid #667eea;
        padding: 10px;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.9);
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'users' not in st.session_state:
    # Default users (you can add more)
    st.session_state.users = {
        'admin': 'admin123',
        'user': 'user123',
        'test': 'test123'
    }

# --- Hash Password Function ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Verify Password Function ---
def verify_password(password, hashed):
    return hash_password(password) == hashed

# --- Login Function ---
def login(username, password):
    if username in st.session_state.users:
        stored_password = st.session_state.users[username]
        if verify_password(password, stored_password):
            return True
    return False

# --- Register Function ---
def register(username, password):
    if username in st.session_state.users:
        return False  # User already exists
    else:
        st.session_state.users[username] = hash_password(password)
        return True

# --- Logout Function ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ''

# --- 1. Text Extraction Functions ---

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def get_text(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.pdf'):
            return extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith('.docx'):
            return extract_text_from_docx(uploaded_file)
        else:
            st.error("Unsupported file format! Please upload PDF or DOCX.")
            return ""
    return ""

# --- 2. Keyword Extraction ---

def extract_keywords_simple(text, top_n=100):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    words = text.split()
    
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
        'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as',
        'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'between', 'under', 'again', 'further', 'then', 'once', 'here',
        'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few',
        'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'just',
        'if', 'because', 'until', 'while', 'about', 'against', 'this',
        'that', 'these', 'those', 'am', 'it', 'its', 'he', 'she', 'they',
        'we', 'you', 'i', 'me', 'my', 'your', 'his', 'her', 'their', 'our',
        'what', 'which', 'who', 'whom', 'also', 'get', 'including', 'work',
        'year', 'years', 'experience', 'team', 'like', 'new', 'good', 'great',
        'working', 'job', 'role', 'position', 'company', 'responsibilities'
    }
    
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    unique_keywords = list(set(keywords))
    
    return unique_keywords[:top_n]

# --- 3. Skill Categories ---

def categorize_keywords(keywords):
    categories = {
        '🖥️ Programming Languages': [
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust',
            'php', 'swift', 'kotlin', 'typescript', 'scala', 'perl', 'r'
        ],
        '🌐 Web Technologies': [
            'html', 'css', 'react', 'angular', 'vue', 'node', 'django', 'flask',
            'spring', 'express', 'nextjs', 'jquery', 'bootstrap', 'tailwind'
        ],
        '🗄️ Databases': [
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite',
            'nosql', 'dynamodb', 'cassandra', 'firebase', 'mariadb'
        ],
        '☁️ Cloud & DevOps': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'github', 'gitlab', 'ci/cd', 'terraform', 'ansible', 'linux'
        ],
        '🤖 AI & ML': [
            'machine learning', 'deep learning', 'tensorflow', 'pytorch',
            'nlp', 'computer vision', 'neural network', 'data science',
            'artificial intelligence', 'pandas', 'numpy', 'scikit'
        ],
        '💼 Soft Skills': [
            'communication', 'leadership', 'teamwork', 'problem solving',
            'analytical', 'time management', 'project management', 'agile',
            'scrum', 'collaboration', 'presentation'
        ],
        '📊 Data & Analytics': [
            'excel', 'tableau', 'power bi', 'statistics', 'analytics',
            'visualization', 'reporting', 'dashboard', 'sql', 'etl'
        ]
    }
    
    categorized = {}
    uncategorized = []
    
    for keyword in keywords:
        found = False
        for category, skills in categories.items():
            if keyword in skills or any(skill in keyword for skill in skills):
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(keyword)
                found = True
                break
        if not found:
            uncategorized.append(keyword)
    
    return categorized, uncategorized

# --- 4. ATS Score Checker ---

def check_ats(resume_text, jd_text):
    score = 0
    checks = []
    
    # Check for required sections
    sections = ['experience', 'education', 'skills', 'summary', 'objective']
    resume_lower = resume_text.lower()
    
    found_sections = []
    for section in sections:
        if section in resume_lower:
            found_sections.append(section)
    
    if len(found_sections) >= 4:
        score += 25
        checks.append(("✅ Required Sections", f"Found: {', '.join(found_sections)}"))
    else:
        score += (len(found_sections) * 6)
        missing = set(sections) - set(found_sections)
        checks.append(("⚠️ Missing Sections", f"Missing: {', '.join(missing)}"))
    
    # Check file format
    checks.append(("✅ File Format", "PDF format is ATS-friendly"))
    score += 15
    
    # Check keyword density
    resume_keywords = set(extract_keywords_simple(resume_text))
    jd_keywords = set(extract_keywords_simple(jd_text))
    match_ratio = len(resume_keywords.intersection(jd_keywords)) / len(jd_keywords) if jd_keywords else 0
    
    if match_ratio > 0.5:
        score += 30
        checks.append(("✅ Keyword Density", "Good keyword matching"))
    elif match_ratio > 0.3:
        score += 20
        checks.append(("⚠️ Keyword Density", "Could be improved"))
    else:
        score += 10
        checks.append(("❌ Keyword Density", "Low keyword match"))
    
    # Check for contact info
    email_pattern = r'\S+@\S+\.\S+'
    phone_pattern = r'\d{10,}'
    
    has_email = bool(re.search(email_pattern, resume_text))
    has_phone = bool(re.search(phone_pattern, resume_text))
    
    if has_email and has_phone:
        score += 15
        checks.append(("✅ Contact Information", "Email and Phone found"))
    elif has_email:
        score += 10
        checks.append(("⚠️ Contact Information", "Only email found"))
    else:
        checks.append(("❌ Contact Information", "Missing contact details"))
    
    # Check for bullet points
    bullet_count = resume_text.count('•') + resume_text.count('-') + resume_text.count('*')
    if bullet_count > 5:
        score += 15
        checks.append(("✅ Formatting", "Good use of bullet points"))
    else:
        score += 5
        checks.append(("⚠️ Formatting", "Add more bullet points"))
    
    return min(score, 100), checks

# --- 5. Generate PDF Report ---

def generate_pdf_report(matched, missing, score, ats_score, categories, resume_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', size=24)
    pdf.set_text_color(102, 126, 234)
    pdf.cell(200, 20, txt="Resume Analysis Report", ln=True, align='C')
    pdf.ln(10)
    
    # Score Section
    pdf.set_font("Arial", 'B', size=16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=f"Match Score: {score:.1f}%", ln=True, align='C')
    pdf.cell(200, 10, txt=f"ATS Score: {ats_score:.1f}%", ln=True, align='C')
    pdf.ln(10)
    
    # Matched Keywords
    pdf.set_font("Arial", 'B', size=14)
    pdf.set_text_color(17, 153, 142)
    pdf.cell(200, 10, txt="Matched Keywords:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    matched_text = ", ".join(sorted(matched)) if matched else "None"
    pdf.multi_cell(0, 10, matched_text)
    pdf.ln(5)
    
    # Missing Keywords
    pdf.set_font("Arial", 'B', size=14)
    pdf.set_text_color(235, 51, 73)
    pdf.cell(200, 10, txt="Missing Keywords:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    missing_text = ", ".join(sorted(missing)) if missing else "None"
    pdf.multi_cell(0, 10, missing_text)
    pdf.ln(5)
    
    # Skill Categories
    if categories:
        pdf.set_font("Arial", 'B', size=14)
        pdf.set_text_color(102, 126, 234)
        pdf.cell(200, 10, txt="Skill Categories:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        for category, skills in categories.items():
            pdf.cell(0, 8, txt=f"- {category}: {', '.join(skills)}", ln=True)
    
    # Footer
    pdf.ln(20)
    pdf.set_font("Arial", 'I', size=10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(200, 10, txt=f"Generated by Resume Keyword Analyzer | {resume_name}", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 6. Analysis Logic ---

def analyze_resume(resume_text, jd_text):
    resume_keywords = extract_keywords_simple(resume_text)
    jd_keywords = extract_keywords_simple(jd_text)
    
    resume_set = set([k.lower() for k in resume_keywords])
    jd_set = set([k.lower() for k in jd_keywords])
    
    matched = resume_set.intersection(jd_set)
    missing = jd_set.difference(resume_set)
    
    if len(jd_set) > 0:
        score = (len(matched) / len(jd_set)) * 100
    else:
        score = 0
    
    # Get skill categories
    categorized, uncategorized = categorize_keywords(matched)
    
    # Get ATS score
    ats_score, ats_checks = check_ats(resume_text, jd_text)
    
    return matched, missing, score, categorized, ats_score, ats_checks, resume_set, jd_set

# --- 7. Login Page ---

def login_page():
    st.markdown("""
    <div style="text-align: center;
