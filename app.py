import streamlit as st
import hashlib
import re
import pdfplumber
import docx
from fpdf import FPDF

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Resume Analyzer Pro", page_icon="📊", layout="wide")

# ---------------- BASIC STYLE ----------------
st.markdown("""
<style>
.stApp { background-color:#f5f6fa; }
.login-box {
    background:white; padding:30px; border-radius:10px;
    max-width:400px; margin:auto; box-shadow:0 0 10px #ccc;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {
        "admin": hashlib.sha256("admin123".encode()).hexdigest()
    }

# ---------------- AUTH ----------------
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login(user, pw):
    return user in st.session_state.users and st.session_state.users[user] == hash_pw(pw)

def register(user, pw):
    if user in st.session_state.users:
        return False
    st.session_state.users[user] = hash_pw(pw)
    return True

# ---------------- FILE TEXT ----------------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            if p.extract_text():
                text += p.extract_text()
    return text

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

# ---------------- KEYWORDS ----------------
def keywords(text):
    words = re.sub(r"[^a-zA-Z ]"," ",text.lower()).split()
    stop = {"the","and","is","are","to","of","in","for","with","on"}
    return set(w for w in words if w not in stop and len(w) > 2)

# ---------------- PDF REPORT ----------------
def make_pdf(score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0,10,"Resume Analysis Report",ln=True,align="C")
    pdf.ln(10)
    pdf.cell(0,10,f"Match Score: {score:.2f}%",ln=True)
    return pdf.output(dest="S").encode("latin-1")

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.markdown("<div class='login-box'><h2>Login</h2></div>", unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(u,p):
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Register"):
        if register(u,p):
            st.success("Registered! Login now.")
        else:
            st.error("User exists")

# ---------------- MAIN APP ----------------
def main_app():
    st.title("📊 Resume Analyzer Pro")

    resume = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf","docx"])
    jd = st.text_area("Paste Job Description")

    if st.button("Analyze"):
        if not resume or not jd:
            st.warning("Upload resume and JD")
            return

        if resume.name.endswith(".pdf"):
            resume_text = read_pdf(resume)
        else:
            resume_text = read_docx(resume)

        rkw = keywords(resume_text)
        jkw = keywords(jd)

        score = (len(rkw & jkw) / max(len(jkw),1)) * 100

        st.success(f"Match Score: {score:.2f}%")

        pdf = make_pdf(score)
        st.download_button("Download PDF Report", pdf, "report.pdf")

# ---------------- ROUTER ----------------
if not st.session_state.logged_in:
    login_page()
else:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    main_app()
