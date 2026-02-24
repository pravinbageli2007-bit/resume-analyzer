import streamlit as st
import pdfplumber
import docx
import re
from fpdf
import hashlib

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="📊",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
h1 { color:white; text-align:center; }
.login-card {
    background:white;
    padding:40px;
    border-radius:20px;
    max-width:400px;
    margin:auto;
    box-shadow:0 10px 30px rgba(0,0,0,.3);
}
.stButton>button {
    border-radius:30px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": hashlib.sha256("admin123".encode()).hexdigest(),
        "user": hashlib.sha256("user123".encode()).hexdigest(),
        "test": hashlib.sha256("test123".encode()).hexdigest()
    }

# ---------------- AUTH FUNCTIONS ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def login(username, password):
    if username in st.session_state.users:
        return verify_password(password, st.session_state.users[username])
    return False

def register(username, password):
    if username in st.session_state.users:
        return False
    st.session_state.users[username] = hash_password(password)
    return True

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""

# ---------------- TEXT EXTRACTION ----------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def get_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    else:
        return ""

# ---------------- KEYWORDS ----------------
def extract_keywords(text):
    text = re.sub(r"[^a-zA-Z ]", " ", text.lower())
    words = text.split()
    stop = set([
        "the","and","is","are","to","of","in","for","with","on","a","an",
        "this","that","it","as","by","from","or","be","was","were"
    ])
    return list(set(w for w in words if w not in stop and len(w) > 2))

# ---------------- ATS CHECK ----------------
def check_ats(resume, jd):
    score = 0
    checks = []

    sections = ["experience","education","skills","summary","objective"]
    found = [s for s in sections if s in resume.lower()]
    score += min(len(found) * 5, 25)

    if resume:
        score += 15
        checks.append(("✅ File Format", "PDF/DOCX detected"))

    r_kw = set(extract_keywords(resume))
    j_kw = set(extract_keywords(jd))
    match = len(r_kw & j_kw) / len(j_kw) if j_kw else 0

    if match > .5:
        score += 30
    elif match > .3:
        score += 20
    else:
        score += 10

    if re.search(r"\S+@\S+\.\S+", resume):
        score += 10
    if re.search(r"\d{10,}", resume):
        score += 5

    return min(score, 100)

# ---------------- PDF REPORT ----------------
def generate_pdf(score, ats):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(0,10,"Resume Analysis Report",ln=True,align="C")
    pdf.ln(10)
    pdf.cell(0,10,f"Match Score: {score:.1f}%",ln=True)
    pdf.cell(0,10,f"ATS Score: {ats}%",ln=True)
    return pdf.output(dest="S").encode("latin-1")

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.markdown('<div class="login-card"><h2>🔐 Login</h2></div>', unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with col2:
        if st.button("Register"):
            if register(username, password):
                st.success("Registered! Login now.")
            else:
                st.error("User exists")

# ---------------- MAIN APP ----------------
def main_app():
    st.title("📊 Resume Analyzer Pro")

    resume = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf","docx"])
    jd = st.text_area("Paste Job Description")

    if st.button("Analyze"):
        if resume and jd:
            resume_text = get_text(resume)
            score = len(set(extract_keywords(resume_text)) &
                        set(extract_keywords(jd))) / max(len(extract_keywords(jd)),1) * 100
            ats = check_ats(resume_text, jd)

            st.success(f"Match Score: {score:.1f}%")
            st.info(f"ATS Score: {ats}%")

            pdf = generate_pdf(score, ats)
            st.download_button("Download Report", pdf, "report.pdf")
        else:
            st.warning("Upload resume & paste JD")

# ---------------- ROUTER ----------------
if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()
    main_app()

