# ai_engine/ml_models/tenant_ai.py

import joblib
from sklearn.ensemble import RandomForestClassifier
import os

GLOBAL_MODEL_PATH = "models/global/global_ai_model.pkl"
TENANT_MODEL_DIR = "models/tenants"

def clone_global_model_for_tenant(tenant_id):
    """
    Clone the global candidate model for a new tenant.
    Returns the model file path for database reference.
    """
    # Load global model
    global_model = joblib.load(GLOBAL_MODEL_PATH)
    # Path for tenant model
    tenant_model_path = os.path.join(TENANT_MODEL_DIR, f"tenant_{tenant_id}_ai_model.pkl")
    os.makedirs(TENANT_MODEL_DIR, exist_ok=True)
    joblib.dump(global_model, tenant_model_path)
    return tenant_model_path

def load_tenant_model(tenant_id):
    """
    Load the tenant-specific model for job matching.
    Falls back to global model if tenant model missing.
    """
    tenant_model_path = os.path.join(TENANT_MODEL_DIR, f"tenant_{tenant_id}_ai_model.pkl")
    if not os.path.isfile(tenant_model_path):
        # Fallback to global model
        return joblib.load(GLOBAL_MODEL_PATH)
    return joblib.load(tenant_model_path)

def train_tenant_model(tenant_id, X, y):
    """
    Retrain tenant model with local job matching feedback.
    X -- features for job-candidate pairs
    y -- job fit labels (e.g., short-list vs. reject)
    """
    model = RandomForestClassifier()
    model.fit(X, y)
    tenant_model_path = os.path.join(TENANT_MODEL_DIR, f"tenant_{tenant_id}_ai_model.pkl")
    joblib.dump(model, tenant_model_path)
    return model

def predict_job_fit(tenant_id, features):
    """
    Predict the candidate-job fit probability using tenant AI model.
    Falls back to global model if tenant model missing.
    features -- 1D array-like feature vector
    """
    model = load_tenant_model(tenant_id)
    score = model.predict_proba([features])[0][1]  # Probability of 'fit' class
    return score

# Example usage:
# model_path = clone_global_model_for_tenant(tenant_id)
# model = train_tenant_model(tenant_id, X, y)
# score = predict_job_fit(tenant_id, candidate_job_features)
