import streamlit as st
import pdfplumber
import docx
import re

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
            st.error("Unsupported file format. Please upload PDF or DOCX.")
            return ""
    return ""

# --- 2. Better Keyword Extraction ---

def extract_keywords_simple(text, top_n=100):
    """Extract keywords using simple word frequency (more reliable than TF-IDF)"""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters, keep only letters and spaces
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Split into words
    words = text.split()
    
    # Common stop words to ignore
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
        'what', 'which', 'who', 'whom', 'also', 'get', 'including'
    }
    
    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Get unique keywords
    unique_keywords = list(set(keywords))
    
    return unique_keywords[:top_n]

# --- 3. Analysis Logic ---

def analyze_resume(resume_text, jd_text):
    # Extract keywords from both
    resume_keywords = extract_keywords_simple(resume_text)
    jd_keywords = extract_keywords_simple(jd_text)
    
    # Convert to sets for comparison
    resume_set = set([k.lower() for k in resume_keywords])
    jd_set = set([k.lower() for k in jd_keywords])
    
    # Find matches and missing
    matched = resume_set.intersection(jd_set)
    missing = jd_set.difference(resume_set)
    
    # Calculate Score
    if len(jd_set) > 0:
        score = (len(matched) / len(jd_set)) * 100
    else:
        score = 0
        
    return matched, missing, score, resume_set, jd_set

# --- 4. The Web Interface ---

def main():
    st.set_page_config(page_title="Resume Keyword Analyzer", layout="wide")
    
    st.title("📄 Resume Keyword Analyzer")
    st.markdown("Upload your resume and paste the Job Description to see how well you match.")

    col1, col2 = st.columns(2)

    with col1:
        st.header("Job Description")
        jd_text = st.text_area("Paste Job Description here:", height=300)

    with col2:
        st.header("Upload Resume")
        uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
        
        if uploaded_file is not None:
            st.success("File Uploaded Successfully!")
            
            if st.button("Analyze Match"):
                with st.spinner("Analyzing..."):
                    resume_text = get_text(uploaded_file)
                    
                    if resume_text and jd_text:
                        matched, missing, score, resume_set, jd_set = analyze_resume(resume_text, jd_text)
                        
                        st.divider()
                        st.subheader(f"📊 Match Score: {score:.1f}%")
                        
                        st.progress(int(score))
                        
                        c1, c2 = st.columns(2)
                        
                        with c1:
                            st.success(f"✅ Matched Keywords ({len(matched)})")
                            if matched:
                                st.write(", ".join(sorted(matched)))
                            else:
                                st.write("No matches found")
                        
                        with c2:
                            st.error(f"❌ Missing Keywords ({len(missing)})")
                            if missing:
                                st.write(", ".join(sorted(missing)))
                            else:
                                st.write("Nothing missing!")
                                
                        # Debug info (optional - to see all extracted keywords)
                        with st.expander("🔍 Debug Info (See all extracted words)"):
                            st.write(f"JD Keywords ({len(jd_set)}):", sorted(jd_set))
                            st.write(f"Resume Keywords ({len(resume_set)}):", sorted(resume_set))
                                
                    else:
                        st.warning("Please enter Job Description text.")

if __name__ == "__main__":
    main()
