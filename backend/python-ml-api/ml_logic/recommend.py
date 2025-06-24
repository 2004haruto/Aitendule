import os
import joblib
import pandas as pd
from typing import Dict, Any, Optional

# List of categories with models
CATEGORIES = ["bottoms", "shoes", "outer", "tops", "accessory"]

# Order of features used during training
FEATURE_ORDER = ["weather", "user_id", "month", "day", "hour", "weekday", "temperature"]

def load_model(category: str) -> Optional[Any]:
    """
    Load the trained model pipeline for the specified category.
    
    Args:
        category (str): The clothing category (e.g., "tops", "bottoms").
    
    Returns:
        Trained Pipeline object or None if not found.
    """
    model_path = f"models/{category}_model.pkl"
    if not os.path.exists(model_path):
        print(f"[Warning] Model file not found: {model_path}")
        return None
    return joblib.load(model_path)

def recommend_for_category(category: str, features: Dict[str, Any]) -> Optional[str]:
    """
    Predict the recommended clothing item for a given category.

    Args:
        category (str): The clothing category.
        features (dict): Dictionary containing feature values.

    Returns:
        str: Predicted clothing item name or None if model not found.
    """
    model = load_model(category)
    if model is None:
        return None

    try:
        input_data = {key: str(features[key]) for key in FEATURE_ORDER}
    except KeyError as e:
        print(f"[Error] Missing required feature: {e}")
        return None

    df = pd.DataFrame([input_data])
    prediction = model.predict(df)
    return prediction[0]

def recommend_all(features: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Get clothing recommendations for all categories.

    Args:
        features (dict): Dictionary of input features.

    Returns:
        dict: Mapping from category to recommended item name.
    """
    return {
        category: recommend_for_category(category, features)
        for category in CATEGORIES
    }

# CLI test
if __name__ == "__main__":
    sample_input = {
        "temperature": 20,
        "weather": "clear",
        "user_id": 1,
        "month": 6,
        "day": 3,
        "hour": 14,
        "weekday": 2,
    }

    results = recommend_all(sample_input)
    for category, item in results.items():
        print(f"{category}: {item}")
