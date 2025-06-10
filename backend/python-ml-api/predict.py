import joblib
from datetime import datetime

# 学習済みモデルをロード（API起動時にロードしておくのが効率的）
model = joblib.load("clothing_recommender.pkl")

def recommend_clothing(user_id, lat, lon):
    weather = fetch_weather(lat, lon)
    if not weather:
        return []

    now = datetime.now()
    features = {
        "temperature": weather["temperature"],
        "weather": weather["weather"],
        "user_id": user_id,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "weekday": now.weekday(),
    }
    df = pd.DataFrame([features])

    preds = model.predict(df)
    return preds.tolist()
