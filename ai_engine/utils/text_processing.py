# ai_engine/utils/text_processing.py

import re
import string
import spacy

nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    """
    Lowercase, remove punctuation and excess whitespace.
    """
    text = text.lower()
    text = re.sub(f'[{re.escape(string.punctuation)}]', '', text)
    text = re.sub('\s+', ' ', text)
    return text.strip()

def tokenize_text(text):
    """
    Tokenize text to a list of words using spaCy.
    """
    doc = nlp(text)
    return [token.text for token in doc if not token.is_space]

def lemmatize_text(text):
    """
    Lemmatize tokens using spaCy.
    """
    doc = nlp(text)
    return [token.lemma_ for token in doc if not token.is_space]

def extract_sentences(text):
    """
    Split text into sentences using spaCy.
    """
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]
