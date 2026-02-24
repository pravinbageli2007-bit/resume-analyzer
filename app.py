import streamlit as st
import pdfplumber
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

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
        # Check file extension
        if uploaded_file.name.endswith('.pdf'):
            return extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith('.docx'):
            return extract_text_from_docx(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload PDF or DOCX.")
            return ""
    return ""

# --- 2. Keyword Analysis Logic ---

def extract_keywords(text):
    # Use TF-IDF to find important words, ignoring common English stop words
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        # Get the scores for the words
        scores = tfidf_matrix.toarray()[0]
        
        # Create a dictionary of word: score
        word_scores = {word: score for word, score in zip(feature_names, scores)}
        
        # Sort by score (highest first) and take top 30 keywords
        sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        return [word for word, score in sorted_words[:30]]
    except ValueError:
        # Handle case where text is empty or only stop words
        return []

def analyze_resume(resume_text, jd_text):
    # Get keywords from both
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)
    
    # Clean inputs for comparison (lowercase)
    resume_set = set([k.lower() for k in resume_keywords])
    jd_set = set([k.lower() for k in jd_keywords])
    
    # Find matches and missing
    matched = resume_set.intersection(jd_set)
    missing = jd_set.difference(resume_set)
    
    # Calculate Score (Simple Percentage)
    if len(jd_set) > 0:
        score = (len(matched) / len(jd_set)) * 100
    else:
        score = 0
        
    return matched, missing, score

# --- 3. The Web Interface (Streamlit) ---

def main():
    st.set_page_config(page_title="Resume Keyword Analyzer", layout="wide")
    
    st.title("📄 Resume Keyword Analyzer")
    st.markdown("Upload your resume and paste the Job Description to see how well you match.")

    # Layout: Two Columns
    col1, col2 = st.columns(2)

    with col1:
        st.header("Job Description")
        jd_text = st.text_area("Paste Job Description here:", height=300)

    with col2:
        st.header("Upload Resume")
        uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
        
        if uploaded_file is not None:
            st.success("File Uploaded Successfully!")
            
            # Button to Analyze
            if st.button("Analyze Match"):
                with st.spinner("Analyzing..."):
                    # 1. Get Text
                    resume_text = get_text(uploaded_file)
                    
                    if resume_text and jd_text:
                        # 2. Analyze
                        matched, missing, score = analyze_resume(resume_text, jd_text)
                        
                        # 3. Display Results
                        st.divider()
                        st.subheader(f"Match Score: {score:.1f}%")
                        
                        # Progress Bar for Score
                        st.progress(int(score))
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.success(f"✅ Matched Keywords ({len(matched)})")
                            st.write(", ".join(matched))
                        
                        with c2:
                            st.error(f"❌ Missing Keywords ({len(missing)})")
                            st.write(", ".join(missing))
                    else:
                        st.warning("Please enter Job Description text.")

if __name__ == "__main__":
    main()