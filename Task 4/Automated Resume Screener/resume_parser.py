import re
from typing import Dict, List

def extract_text_from_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)

def extract_text_from_pdf(path: str) -> str:
    import pdfplumber
    texts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            texts.append(page.extract_text() or "")
    return "\n".join(texts)

def extract_text(path: str) -> str:
    path_lower = path.lower()
    if path_lower.endswith('.pdf'):
        return extract_text_from_pdf(path)
    if path_lower.endswith('.docx'):
        return extract_text_from_docx(path)
    # fallback: read raw
    with open(path, 'rb') as f:
        try:
            return f.read().decode('utf-8', errors='ignore')
        except Exception:
            return ''

def parse_years_experience(text: str) -> float:
    # Find patterns like '5 years', '5+ years', 'more than 3 years'
    nums = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)", text, flags=re.I)
    nums = [float(n) for n in nums]
    if nums:
        return max(nums)
    # look for 'X-year' patterns
    nums2 = re.findall(r"(\d+(?:\.\d+)?)-year", text, flags=re.I)
    nums2 = [float(n) for n in nums2]
    if nums2:
        return max(nums2)
    return 0.0

def match_education(text: str, education_list: List[str]) -> List[str]:
    found = []
    tl = text.lower()
    for ed in education_list:
        if ed.lower() in tl:
            found.append(ed)
    return found

def score_text(text: str, criteria: Dict) -> Dict:
    """Return scoring info: keyword matches, skills matches, years, education matches, score"""
    tl = text.lower()
    keywords = [k.strip().lower() for k in criteria.get('keywords', '').split(',') if k.strip()]
    skills = [s.strip().lower() for s in criteria.get('skills', '').split(',') if s.strip()]
    min_years = float(criteria.get('min_years') or 0)
    education = criteria.get('education', '')

    kw_found = [k for k in keywords if k in tl]
    skills_found = [s for s in skills if s in tl]
    years = parse_years_experience(text)
    edu_list = [e.strip() for e in education.split(',') if e.strip()]
    edu_found = match_education(text, edu_list) if edu_list else []

    # simple scoring
    score = 0
    score += 5 * len(kw_found)
    score += 3 * len(skills_found)
    # experience bonus (capped)
    score += min(years, 10) * 2
    if edu_found:
        score += 10
    # penalize if below minimum years
    if years < min_years:
        score -= 10

    return {
        'keywords_found': kw_found,
        'skills_found': skills_found,
        'years': years,
        'education_found': edu_found,
        'score': round(score, 2)
    }
