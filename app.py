from flask import Flask, render_template, request
import os
import pdfplumber
import spacy

# Step 1: Set up app and folders
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Step 2: Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Step 3: Extract text from uploaded PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

# Step 4: Compare resume to job description
def get_match_score(resume_text, jd_text):
    resume_doc = nlp(resume_text.lower())
    jd_doc = nlp(jd_text.lower())

    resume_words = set(token.text for token in resume_doc if token.is_alpha)
    jd_words = set(token.text for token in jd_doc if token.is_alpha)

    match_count = len(resume_words & jd_words)
    score = (match_count / len(jd_words)) * 100 if jd_words else 0
    return round(score, 2)

# Step 5: Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return "❌ No file part"

    file = request.files['resume']
    if file.filename == '':
        return "❌ No file selected"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    resume_text = extract_text_from_pdf(filepath)

    with open("job_description.txt", "r") as f:
        jd_text = f.read()

    score = get_match_score(resume_text, jd_text)

    return render_template('result.html', text=resume_text, score=score)

# Step 6: Run the app
if __name__ == '__main__':
    app.run(debug=True)
