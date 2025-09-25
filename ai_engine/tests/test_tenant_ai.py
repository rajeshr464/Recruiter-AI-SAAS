# ai_engine/tests/test_tenant_ai.py

import unittest
import pandas as pd
from ai_engine.ml_models import tenant_ai

class TestTenantAI(unittest.TestCase):
    def setUp(self):
        self.tenant_id = 99
        X = pd.DataFrame({'a': [1, 2, 3, 4], 'b': [4, 3, 2, 1]})
        y = pd.Series([0, 1, 1, 0])
        tenant_ai.clone_global_model_for_tenant(self.tenant_id)
        tenant_ai.train_tenant_model(self.tenant_id, X, y)

    def test_tenant_model_loading(self):
        model = tenant_ai.load_tenant_model(self.tenant_id)
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, 'predict_proba'))

    def test_predict_job_fit(self):
        score = tenant_ai.predict_job_fit(self.tenant_id, [2, 3])
        self.assertTrue(0 <= score <= 1)
