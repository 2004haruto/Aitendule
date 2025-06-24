import joblib
import os
import pandas as pd
from datetime import datetime
from ml_logic.data import fetch_weather  # 必要に応じて正しいパスに変更

# カテゴリ一覧（必要に応じて調整）
CATEGORIES = ["tops", "bottoms", "shoes", "outer", "accessory"]

# API起動時にモデルをロードしておく（1回だけ読み込む）
MODELS = {}
for category in CATEGORIES:
    model_path = f"models/{category}_model.pkl"
    if os.path.exists(model_path):
        MODELS[category] = joblib.load(model_path)
    else:
        print(f"⚠ モデルが見つかりません: {model_path}")

def recommend_clothing(user_id, lat, lon):
    weather = fetch_weather(lat, lon)
    if not weather:
        return []

    now = datetime.now()
    base_features = {
        "temperature": weather["temperature"],
        "weather": weather["weather"],
        "user_id": user_id,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "weekday": now.weekday(),
    }

    recommendations = {}

    for category, model in MODELS.items():
        features = {**base_features, "category": category}
        df = pd.DataFrame([features])
        prediction = model.predict(df)[0]
        recommendations[category] = prediction

    return recommendations
