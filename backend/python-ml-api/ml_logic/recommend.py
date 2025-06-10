import joblib
import pandas as pd

CATEGORIES = ["bottoms", "shoes", "outer", "tops", "accessory"]

def load_model(category):
    model_path = f"models/{category}_model.pkl"
    try:
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        print(f"モデルファイルが見つかりません: {model_path}")
        return None

def recommend_for_category(category, features):
    model = load_model(category)
    if model is None:
        return None
    df = pd.DataFrame([features])
    prediction = model.predict(df)
    return prediction[0]

def recommend_all(features):
    recommendations = {}
    for category in CATEGORIES:
        item = recommend_for_category(category, features)
        recommendations[category] = item
    return recommendations

# 使い方例
if __name__ == "__main__":
    sample_features = {
        "temperature": 20,
        "weather": "clear",  # 学習時にエンコードされていれば文字列でもOK
        "user_id": 1,
        "month": 6,
        "day": 3,
        "hour": 14,
        "weekday": 2,
    }

    recs = recommend_all(sample_features)
    for cat, item in recs.items():
        print(f"{cat}: {item}")
