import streamlit as st
import hashlib
import re
import sqlite3
from datetime import datetime
import docx

# -------- SAFE OPTIONAL IMPORTS --------
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None
# -------- PAGE CONFIG --------
st.set_page_config("Resume Analyzer Pro", "📊", layout="wide")

# -------- DATABASE --------
def db():
    return sqlite3.connect("resume_analyzer.db", check_same_thread=False)

def init_db():
    c = db().cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            match_score REAL,
            ats_score INTEGER,
            created TEXT
        )
    """)
    c.connection.commit()

init_db()

# -------- AUTH --------
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def login(u,p):
    c=db().cursor()
    c.execute("SELECT password FROM users WHERE username=?", (u,))
    r=c.fetchone()
    return r and r[0]==hash_pw(p)

def register(u,p):
    try:
        c=db().cursor()
        c.execute("INSERT INTO users VALUES (?,?)", (u,hash_pw(p)))
        c.connection.commit()
        return True
    except:
        return False

# -------- FILE READ --------
def read_pdf(f):
    if not pdfplumber: return ""
    text=""
    with pdfplumber.open(f) as pdf:
        for p in pdf.pages:
            if p.extract_text(): text+=p.extract_text()
    return text

def read_docx(f):
    return "\n".join(p.text for p in docx.Document(f).paragraphs)

# -------- NLP --------
def keywords(t):
    words=re.sub(r"[^a-zA-Z ]"," ",t.lower()).split()
    stop={"the","and","is","are","to","of","in","for","with","on"}
    return set(w for w in words if w not in stop and len(w)>2)

# -------- ATS --------
def ats(resume,jd):
    score=0; details=[]
    sections=["experience","education","skills","summary","projects"]
    found=[s for s in sections if s in resume.lower()]
    pts=min(len(found)*6,30); score+=pts
    details.append(("Sections",f"{len(found)}/5",pts))

    rkw,jkw=keywords(resume),keywords(jd)
    ratio=len(rkw&jkw)/len(jkw) if jkw else 0
    pts=30 if ratio>=.5 else 20 if ratio>=.3 else 10
    score+=pts
    details.append(("Keywords",f"{int(ratio*100)}%",pts))

    pts=10 if re.search(r"\S+@\S+\.\S+",resume) else 0
    pts+=5 if re.search(r"\d{10,}",resume) else 0
    score+=pts
    details.append(("Contact","Checked",pts))

    bullets=resume.count("-")+resume.count("•")
    pts=10 if bullets>=5 else 5
    score+=pts
    details.append(("Formatting",f"{bullets} bullets",pts))

    return min(score,100),details

# -------- SKILLS --------
def skills(resume):
    db={"Python","Java","SQL","AWS","Docker","Git","HTML","CSS","JavaScript","React"}
    out={}
    for w in resume.split():
        if w.capitalize() in db:
            out[w.capitalize()]=out.get(w.capitalize(),0)+1
    return out

# -------- AI TIPS --------
def tips(resume,jd):
    out=[]
    miss=list(keywords(jd)-keywords(resume))
    if miss: out.append("Add missing keywords: "+", ".join(miss[:6]))
    if "summary" not in resume.lower(): out.append("Add a professional summary.")
    if not re.search(r"\S+@\S+\.\S+",resume): out.append("Add email address.")
    if not re.search(r"\d{10,}",resume): out.append("Add phone number.")
    if len(resume.split())<250: out.append("Resume too short. Add more detail.")
    return out or ["Resume is well optimized."]

# -------- PDF --------
def make_pdf(score):
    if not FPDF: return None
    pdf=FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica",size=14)
    pdf.cell(0,10,"Resume Analysis Report",ln=True)
    pdf.cell(0,10,f"Match Score: {score:.1f}%",ln=True)
    return pdf.output(dest="S").encode("latin-1")

# -------- SESSION --------
if "login" not in st.session_state:
    st.session_state.login=False

# -------- LOGIN UI --------
if not st.session_state.login:
    st.title("🔐 Login")
    u=st.text_input("Username")
    p=st.text_input("Password",type="password")
    if st.button("Login"):
        if login(u,p):
            st.session_state.login=True
            st.session_state.user=u
            st.rerun()
        else: st.error("Invalid login")
    if st.button("Register"):
        if register(u,p): st.success("Account created")
        else: st.error("User exists")
    st.stop()

# -------- APP --------
st.sidebar.success(st.session_state.user)
if st.sidebar.button("Logout"):
    st.session_state.login=False
    st.rerun()

st.title("📊 Resume Analyzer Pro")

resume=st.file_uploader("Upload Resume",["pdf","docx"])
jd=st.text_area("Paste Job Description")

if st.button("Analyze"):
    if not resume or not jd:
        st.warning("Upload resume and JD")
    else:
        text=read_pdf(resume) if resume.name.endswith(".pdf") else read_docx(resume)
        match=len(keywords(text)&keywords(jd))/max(len(keywords(jd)),1)*100
        ats_score,breakdown=ats(text,jd)

        st.success(f"Match Score: {match:.1f}%")
        st.info(f"ATS Score: {ats_score}/100")

        st.subheader("ATS Breakdown")
        for a,b,c in breakdown:
            st.write(f"• {a}: {b} ({c} pts)")

        st.subheader("Skill Analysis")
        sk=skills(text)
        if sk: st.bar_chart(sk)

        st.subheader("AI Tips")
        for t in tips(text,jd): st.write("•",t)

        db().cursor().execute(
            "INSERT INTO history (username,match_score,ats_score,created) VALUES (?,?,?,?)",
            (st.session_state.user,match,ats_score,datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        db().commit()

        pdf=make_pdf(match)
        if pdf:
            st.download_button("Download PDF",pdf,"report.pdf")

st.subheader("📜 History")
c=db().cursor()
c.execute("SELECT match_score,ats_score,created FROM history WHERE username=? ORDER BY id DESC",(st.session_state.user,))
rows=c.fetchall()
if rows:
    st.table({"Match %":[r[0] for r in rows],"ATS":[r[1] for r in rows],"Date":[r[2] for r in rows]})

