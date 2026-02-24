import streamlit as st
import pdfplumber
import docx
import re

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
    
    /* File Uploader */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 20px;
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
    
    /* Cards */
    .css-1r6slb0 {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Success Box */
    .stSuccess {
        background: linear-gradient(135deg, #11998e, #38ef7d) !important;
        border-radius: 15px;
        padding: 20px;
        color: white;
    }
    
    /* Error Box */
    .stError {
        background: linear-gradient(135deg, #eb3349, #f45c43) !important;
        border-radius: 15px;
        padding: 20px;
        color: white;
    }
    
    /* Warning Box */
    .stWarning {
        background: linear-gradient(135deg, #f2994a, #f2c94c) !important;
        border-radius: 15px;
        padding: 15px;
    }
    
    /* Columns */
    .css-1r6slb0 {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Divider */
    hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
        border-radius: 5px;
    }
    
    /* Custom Card Styling */
    .match-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 25px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin: 10px 0;
    }
    
    .score-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 20px;
        padding: 30px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* Keyword Pills */
    .keyword-pill {
        display: inline-block;
        background: linear-gradient(45deg, #4facfe, #00f2fe);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        font-size: 14px;
        font-weight: bold;
    }
    
    .keyword-pill-missing {
        background: linear-gradient(45deg, #fa709a, #fee140);
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

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
            st.error("❌ Unsupported file format! Please upload PDF or DOCX.")
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
        'year', 'years', 'experience', 'team', 'like', 'new', 'good', 'great'
    }
    
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    unique_keywords = list(set(keywords))
    
    return unique_keywords[:top_n]

# --- 3. Analysis Logic ---

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
        
    return matched, missing, score, resume_set, jd_set

# --- 4. Main Interface ---

def main():
    st.set_page_config(
        page_title="Resume Analyzer Pro",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1>🎯 Resume Keyword Analyzer</h1>
        <p style="color: white; font-size: 20px;">Upload your resume & paste job description to check your match score!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Create columns
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
            padding: 20px;
            border-radius: 20px;
            margin-bottom: 20px;
        ">
            <h2 style="color: #333; margin: 0;">📋 Job Description</h2>
        </div>
        """, unsafe_allow_html=True)
        
        jd_text = st.text_area(
            "Paste the Job Description here:",
            height=300,
            placeholder="e.g., We are looking for a Python Developer with SQL, React, and AWS experience..."
        )
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
            padding: 20px;
            border-radius: 20px;
            margin-bottom: 20px;
        ">
            <h2 style="color: #333; margin: 0;">📄 Upload Resume</h2>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose your resume (PDF or DOCX)",
            type=["pdf", "docx"]
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Centered Analyze Button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        analyze_btn = st.button("🔍 Analyze My Resume")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Results Section
    if analyze_btn:
        if uploaded_file is None or not jd_text:
            st.warning("⚠️ Please upload a resume and enter job description!")
        else:
            with st.spinner("🔄 Analyzing your resume..."):
                resume_text = get_text(uploaded_file)
                
                if resume_text:
                    matched, missing, score, resume_set, jd_set = analyze_resume(resume_text, jd_text)
                    
                    # Score Display
                    st.markdown(f"""
                    <div class="score-card">
                        <h1 style="font-size: 72px; margin: 0;">{score:.0f}%</h1>
                        <p style="font-size: 24px; margin: 10px 0;">Match Score</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Progress Bar
                    st.progress(int(score))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Matched and Missing Keywords
                    result_col1, result_col2 = st.columns(2)
                    
                    with result_col1:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #11998e, #38ef7d);
                            padding: 25px;
                            border-radius: 20px;
                            color: white;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        ">
                            <h3 style="margin: 0; color: white;">✅ Matched Keywords ({len(matched)})</h3>
                            <p style="font-size: 14px; opacity: 0.9;">These keywords were found in your resume!</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if matched:
                            matched_list = ", ".join(sorted(matched))
                            st.info(matched_list)
                        else:
                            st.write("No matches found 😔")
                    
                    with result_col2:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #eb3349, #f45c43);
                            padding: 25px;
                            border-radius: 20px;
                            color: white;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        ">
                            <h3 style="margin: 0; color: white;">❌ Missing Keywords ({len(missing)})</h3>
                            <p style="font-size: 14px; opacity: 0.9;">Add these keywords to improve your chances!</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if missing:
                            missing_list = ", ".join(sorted(missing))
                            st.error(missing_list)
                        else:
                            st.success("Perfect match! 🎉")
                    
                    # Tips Section
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if score < 50:
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #ff6b6b, #feca57);
                            padding: 20px;
                            border-radius: 15px;
                            text-align: center;
                        ">
                            <h3 style="margin: 0;">💡 Tips to Improve</h3>
                            <p>Add more relevant keywords from the job description to your resume!</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif score < 80:
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #feca57, #48dbfb);
                            padding: 20px;
                            border-radius: 15px;
                            text-align: center;
                        ">
                            <h3 style="margin: 0;">👍 Good Job!</h3>
                            <p>You're close! Add a few more keywords to increase your chances.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #11998e, #38ef7d);
                            padding: 20px;
                            border-radius: 15px;
                            text-align: center;
                        ">
                            <h3 style="margin: 0;">🎉 Excellent Match!</h3>
                            <p>Your resume matches the job description very well!</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                else:
                    st.error("❌ Could not extract text from the resume. Try a different file.")

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: white; opacity: 0.7;">
        <p>Made with ❤️ | Resume Keyword Analyzer</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
