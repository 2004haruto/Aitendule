from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from crud import get_latest_location
from ml_logic.recommend import recommend_all
from ml_logic.data import fetch_weather
from ml_logic.textgen import generate_advice_and_keywords
from ml_logic.pixabay import search_pixabay_image  # ✅ 1枚取得に変更
from datetime import datetime
from dotenv import load_dotenv
from routes import save_choice

load_dotenv()

router = APIRouter(prefix="/api/v1")

class SuggestRequest(BaseModel):
    user_id: int

@router.post("/suggest")
def suggest(req: SuggestRequest):
    # 最新位置情報取得
    location = get_latest_location(req.user_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # 天気情報取得
    weather_data = fetch_weather(location["latitude"], location["longitude"])
    if not weather_data:
        raise HTTPException(status_code=500, detail="Weather fetch failed")
    
    print("✅ 天気情報:", weather_data)

    # 特徴量作成
    features = weather_data.copy()
    features["user_id"] = req.user_id
    now = datetime.now()
    features.update({
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "weekday": now.weekday(),
    })
    
    features["temp_bin"] = str(int(float(features["temperature"]) // 5))

    # 推論実行（服装カテゴリごと）
    recommendations = recommend_all(features)

    # アドバイス文 + 画像キーワード生成（Gemini使用）
    temperature = float(weather_data["temperature"])
    weather = weather_data["weather"]
    result = generate_advice_and_keywords(recommendations, temperature, weather)
    advice_text = result["advice_text"]
    image_keywords = result["image_keywords"]

    # Pixabayで画像を1枚取得
    image_url = search_pixabay_image(image_keywords)

    return {
        "recommendations": recommendations,
        "suggestion_text": advice_text,
        "image_keywords": image_keywords,
        "image_url": image_url,  # ✅ 単数
        "temperature": weather_data.get("temperature"),
        "weather": weather_data.get("weather")
    }

# FastAPIアプリ登録
app = FastAPI()
app.include_router(router)
app.include_router(save_choice.router)