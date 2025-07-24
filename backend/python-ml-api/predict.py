import joblib
import os
import pandas as pd
from datetime import datetime
from ml_logic.data import fetch_weather  # 必要に応じて正しいパスに変更

CATEGORIES = ["tops", "bottoms", "shoes", "outer", "accessory"]

# モデル＋エンコーダーの読み込み
MODELS = {}
for category in CATEGORIES:
    model_path = f"models/{category}_model.pkl"
    if os.path.exists(model_path):
        pipeline, label_encoder = joblib.load(model_path)  # ✅ タプルとして読み込む
        MODELS[category] = {
            "model": pipeline,
            "label_encoder": label_encoder,
        }
    else:
        print(f"⚠ モデルが見つかりません: {model_path}")

def recommend_clothing(user_id, lat, lon):
    weather = fetch_weather(lat, lon)
    if not weather:
        return []

    now = datetime.now()
    base_features = {
        "temperature": float(weather["temperature"]),
        "temp_bin": str(int(temperature // 5)),
        "weather": str(weather["weather"]),
        "user_id": str(user_id),
        "month": str(now.month),
        "day": str(now.day),
        "hour": str(now.hour),
        "weekday": str(now.weekday()),
    }

    recommendations = {}

    for category, components in MODELS.items():
        model = components["model"]
        label_encoder = components["label_encoder"]

        df = pd.DataFrame([base_features])
        y_pred = model.predict(df)
        label = label_encoder.inverse_transform(y_pred)[0]
        recommendations[category] = label

    return recommendations
