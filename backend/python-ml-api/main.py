from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from crud import get_latest_location
from ml_logic.recommend import recommend_all
from ml_logic.data import fetch_weather
from ml_logic.textgen import generate_description  # 🔥 追加：自然文生成モジュール
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ルーターを作成
router = APIRouter(prefix="/api/v1")

class SuggestRequest(BaseModel):
    user_id: int

@router.post("/suggest")
def suggest(req: SuggestRequest):
    # ユーザーの最新位置情報を取得
    location = get_latest_location(req.user_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # 天気情報を取得
    weather_data = fetch_weather(location["latitude"], location["longitude"])
    if not weather_data:
        raise HTTPException(status_code=500, detail="Weather fetch failed")

    # 特徴量を構成
    features = weather_data.copy()
    features["user_id"] = req.user_id

    # 現在日時を特徴量として追加
    now = datetime.now()
    features["month"] = now.month
    features["day"] = now.day
    features["hour"] = now.hour
    features["weekday"] = now.weekday()

    # 推論を実行
    recommendations = recommend_all(features)

    # 🔥 自然な提案文を生成（Gemini APIなどを使用）
    suggestion_text = generate_description(recommendations)

    # 🔁 フロントに両方返す
    return {
        "recommendations": recommendations,
        "suggestion_text": suggestion_text
    }

# FastAPIアプリを作成してルーターを登録
app = FastAPI()
app.include_router(router)
