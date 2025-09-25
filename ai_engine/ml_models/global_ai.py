# ai_engine/ml_models/global_ai.py

import os
import joblib
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

GLOBAL_MODEL_PATH = "models/global/global_ai_model.pkl"

def train_global_model(X, y):
    """
    Train a global RandomForest model and save it to disk.
    Args:
        X: Features (pandas DataFrame or numpy array)
        y: Labels (Series or array)
    Returns:
        Trained model object.
    """
    model = RandomForestClassifier()
    model.fit(X, y)
    os.makedirs(os.path.dirname(GLOBAL_MODEL_PATH), exist_ok=True)
    joblib.dump(model, GLOBAL_MODEL_PATH)
    return model

def load_global_model():
    """
    Loads the global candidate model from disk.
    Returns:
        Loaded model object.
    Raises:
        FileNotFoundError if the model file is missing.
    """
    if not os.path.isfile(GLOBAL_MODEL_PATH):
        raise FileNotFoundError(f"Global model not found at {GLOBAL_MODEL_PATH}")
    return joblib.load(GLOBAL_MODEL_PATH)

def predict_candidate_fit(features):
    """
    Predict candidate 'fit' probability using the global model.
    Args:
        features: 1D array-like or pd.Series for a single candidate
    Returns:
        Probability (float) of 'fit' class.
    """
    model = load_global_model()
    probability = model.predict_proba([features])[0][1]  # assumes 'fit' is class 1
    return probability
