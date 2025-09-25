# ai_engine/tests/test_features.py

import unittest
from ai_engine.ml_models import features

class TestFeatures(unittest.TestCase):
    def test_extract_resume_features(self):
        sample_resume = """
        John Doe
        Email: john@example.com
        Phone: +1-555-123-4567
        Experienced Python and Django Developer 
        Bachelor of Science, University of Example
        Skills: python, django, rest, sql
        """
        output = features.extract_resume_features(sample_resume)
        self.assertIn('name', output)
        self.assertIn('email', output)
        self.assertIn('phone', output)
        self.assertIn('skills', output)
        self.assertTrue('python' in output['skills'])
        self.assertTrue('django' in output['skills'])
        self.assertTrue(output['email'] == 'john@example.com')

    def test_skill_extraction(self):
        doc = features.nlp("Expert in Python, Django, Kubernetes, and SQL.")
        skills = features.extract_skills(doc)
        self.assertIn("python", skills)
        self.assertIn("django", skills)
