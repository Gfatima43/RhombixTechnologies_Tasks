# Automated Resume Screener

Simple Resume Screening web app (Flask) that parses PDF and DOCX resumes, scores them against job criteria (keywords, skills, experience, education), and produces a shortlist and Excel report. Includes optional email alerts.

## Features

- **Upload multiple resumes** - Support for PDF and DOCX formats
- **Filter by criteria:**
  - Keywords (comma-separated)
  - Skills (comma-separated)
  - Minimum years of experience
  - Education level (High School, Diploma, Bachelor's, Master's, PhD)
- **Automatic scoring and ranking** - Resumes ranked by match score
- **Excel report export** - Results saved to `reports/report.xlsx` with all candidate data
- **Email notifications** - Get alerts when screening is complete
- **Display screening criteria** - View the filtering criteria used for each batch on the results page
- **Years extraction** - Automatically extracts and displays years of experience from resumes

## Quick Start

1. Create a Python virtual environment and activate it.

Windows (PowerShell):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

2. Open http://127.0.0.1:5000 in your browser.

## How to Use

1. **Upload Resumes** - Select one or more resume files (PDF or DOCX)
2. **Set Criteria** - Enter:
   - Keywords to search for
   - Required skills
   - Minimum years of experience
   - Education level requirement
   - Email address (optional) for results notification
3. **Screen Resumes** - Click "Screen Resumes" to analyze
4. **View Results** - See:
   - Screening criteria used
   - Table with candidate names and extracted information:
     - Keywords found
     - Skills matched
     - **Years of experience** extracted from resume
     - Education level detected
     - Overall match score
5. **Download Report** - Export results to Excel for further processing

## Email Configuration

To enable email alerts, set these environment variables before running the app:

Windows (PowerShell):
```powershell
$env:MAIL_SERVER = "smtp.gmail.com"
$env:MAIL_PORT = "587"
$env:MAIL_USE_TLS = "True"
$env:MAIL_USERNAME = "your_email@gmail.com"
$env:MAIL_PASSWORD = "your_app_password"
$env:MAIL_DEFAULT_SENDER = "noreply@resumescreener.com"
```

**For Gmail:**
1. Enable 2-Step Verification on your Google account.
2. Generate an [App Password](https://myaccount.google.com/apppasswords).
3. Use the 16-character app password in `MAIL_PASSWORD`.

Alternatively, provide your own SMTP server details.

## Project Structure

- `app.py` - Flask backend with email support and screening logic
- `resume_parser.py` - Text extraction and scoring algorithm
- `templates/` - HTML templates using Bootstrap 5
  - `index.html` - Main input form
  - `results.html` - Results display with criteria and table
  - `email/alert.html` - Email notification template
- `static/css/` - Styling
- `uploads/` - Temporary resume storage
- `reports/` - Generated Excel reports

## Excel Report

The exported Excel file (`report.xlsx`) contains the following columns:

| Column | Description |
|--------|-------------|
| **filename** | Resume filename |
| **keywords_found** | Matched keywords from the resume |
| **skills_found** | Matched skills from the resume |
| **years** | Years of experience extracted from resume |
| **education_found** | Education levels detected |
| **score** | Overall match score |

## Notes

- Resumes are temporarily stored in `uploads/` folder
- Excel reports are saved to `reports/` folder
- Each batch of screening appends new results to `report.xlsx`
- For improved parsing accuracy, consider integrating NLP libraries like spaCy or transformers
