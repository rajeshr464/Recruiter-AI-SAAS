# ai_engine/tests/test_global_ai.py

import unittest
import numpy as np
import pandas as pd
from ai_engine.ml_models import global_ai

class TestGlobalAI(unittest.TestCase):
    def test_training_and_loading(self):
        # Synthetic data for basic fit
        X = pd.DataFrame({'a': [1, 2, 3, 4], 'b': [4, 3, 2, 1]})
        y = pd.Series([0, 1, 0, 1])
        model = global_ai.train_global_model(X, y)
        self.assertIsNotNone(model)
        loaded = global_ai.load_global_model()
        self.assertIsNotNone(loaded)
        self.assertTrue(hasattr(loaded, 'predict_proba'))

    def test_predict_candidate_fit(self):
        features = [2, 3]
        score = global_ai.predict_candidate_fit(features)
        self.assertTrue(0 <= score <= 1)
