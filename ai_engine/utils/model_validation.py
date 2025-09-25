# ai_engine/utils/model_validation.py

def validate_classification_model(model, X_test, y_test, min_accuracy=0.7):
    """
    Validate classification model, ensuring minimum accuracy.
    Returns bool, actual accuracy.
    """
    accuracy = model.score(X_test, y_test)
    is_valid = accuracy >= min_accuracy
    return is_valid, accuracy

def is_model_file_valid(path, loader):
    """
    Check if a model file exists and loads without error.
    loader: function to load model (e.g., joblib.load)
    """
    try:
        model = loader(path)
        return True
    except Exception:
        return False
