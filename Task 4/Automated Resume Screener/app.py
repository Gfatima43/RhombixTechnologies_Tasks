import os
import time
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import pandas as pd
from resume_parser import extract_text, score_text

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
REPORT_FOLDER = os.path.join(BASE_DIR, 'reports')
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Email config (using Gmail SMTP; adjust as needed)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', True)
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@resumescreener.com')
mail = Mail(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/screen', methods=['POST'])
def screen():
    # Criteria
    keywords = request.form.get('keywords', '')
    skills = request.form.get('skills', '')
    min_years = request.form.get('min_years', '0')
    education = request.form.get('education', '')
    email_to = request.form.get('email', '')

    criteria = {
        'keywords': keywords,
        'skills': skills,
        'min_years': min_years,
        'education': education
    }

    files = request.files.getlist('resumes')
    results = []

    for f in files:
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(save_path)
            text = extract_text(save_path)
            info = score_text(text, criteria)
            results.append({
                'filename': filename,
                'keywords_found': ', '.join(info['keywords_found']),
                'skills_found': ', '.join(info['skills_found']),
                'years': str(int(info['years'])) if info['years'] > 0 else '0',
                'education_found': ', '.join(info['education_found']),
                'score': info['score']
            })

    # Sort by score desc
    results_sorted = sorted(results, key=lambda r: r['score'], reverse=True)

    # Save/Update report to Excel
    report_name = 'report.xlsx'
    report_path = os.path.join(REPORT_FOLDER, report_name)
    
    # Create dataframe from current results
    df_new = pd.DataFrame(results_sorted)
    if df_new.empty:
        df_new = pd.DataFrame(columns=['filename','keywords_found','skills_found','years','education_found','score'])
    
    # Check if report exists and append to it
    if os.path.exists(report_path):
        try:
            df_existing = pd.read_excel(report_path)
            df = pd.concat([df_existing, df_new], ignore_index=True)
        except Exception as e:
            print(f"Error reading existing report: {e}")
            df = df_new
    else:
        df = df_new
    
    df.to_excel(report_path, index=False)

    # Send email alert if email provided
    email_sent = False
    if email_to:
        try:
            msg = Message(
                subject='Resume Screening Report Ready',
                recipients=[email_to],
                html=render_template('email/alert.html', count=len(results_sorted), report_link=url_for('download_report', filename=report_name, _external=True))
            )
            mail.send(msg)
            email_sent = True
        except Exception as e:
            print(f"Email send failed: {e}")

    return render_template('results.html', results=results_sorted, report_link=url_for('download_report', filename=report_name), email_sent=email_sent, email_to=email_to, criteria=criteria)

@app.route('/reports/<path:filename>')
def download_report(filename):
    return send_from_directory(REPORT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)