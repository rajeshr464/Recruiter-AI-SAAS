import re
import spacy

# Pre-trained spaCy model for English (ensure installed via: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

# Regex patterns for basic fields
EMAIL_PATTERN = r'[a-zA-Z0-9\.\-+_]+@[a-zA-Z0-9\.\-+_]+\.[a-zA-Z]+'
PHONE_PATTERN = r'^\+?(\d[\d\s\-().]{7,}\d)$'
LINK_PATTERN = r'(https?:\/\/[^\s]+|www\.[^\s]+)'

def extract_name(doc):
    # Try to get PERSON named entities
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    # Fallback: first two Proper Nouns found
    proper_nouns = [token.text for token in doc if token.pos_ == "PROPN"]
    if proper_nouns:
        return " ".join(proper_nouns[:2])
    return None

def extract_email(text):
    match = re.search(EMAIL_PATTERN, text)
    return match.group() if match else None

def extract_phone(text):
    match = re.search(PHONE_PATTERN, text)
    return match.group() if match else None

def extract_links(text):
    return re.findall(LINK_PATTERN, text)

def extract_skills(doc):
    # Simple skills extraction: match nouns longer than 2 characters
    nouns = set([token.text.lower() for token in doc if token.pos_ in ("NOUN", "PROPN") and len(token.text) > 2])
    # Sample skills list, should load industry keywords from DB/config
    SKILLS_DB = [
        "python", "django", "react", "sql", "machine learning", "javascript",
        "docker", "kubernetes", "rest", "excel", "pandas", "tensorflow"
    ]
    skills_found = [skill for skill in SKILLS_DB if skill in nouns]
    return skills_found

def extract_education(doc):
    edu_keywords = {"bachelor", "master", "bachelors", "masters", "bachelor's", "master's", "phd", "university", "college", "degree", "school"}
    education = []
    for ent in doc.ents:
        if any(k in ent.text.lower() for k in edu_keywords):
            education.append(ent.text)
    return education

def extract_experience(text):
    # Basic pattern for years/months of experience
    exp_pattern = r'([0-9]{1,2})\s+(years?|months?)\s+(of\s+)?experience'
    match = re.search(exp_pattern, text, flags=re.IGNORECASE)
    return match.group() if match else None

def extract_resume_features(resume_text):
    """
    Extract main resume features from raw string.
    Returns dict with name, email, phone, links, skills, education, experience.
    """
    doc = nlp(resume_text)
    features = {
        "name": extract_name(doc),
        "email": extract_email(resume_text),
        "phone": extract_phone(resume_text),
        "links": extract_links(resume_text),
        "skills": extract_skills(doc),
        "education": extract_education(doc),
        "experience": extract_experience(resume_text)
    }
    return features

class ResumeFeatureExtractor:
    def __init__(self, resume_text):
        self.resume_text = resume_text

    def extract_features(self):
        return extract_resume_features(self.resume_text)

# Example usage:
# features = ResumeFeatureExtractor(resume_text).extract_features()
