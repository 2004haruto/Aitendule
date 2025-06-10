from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from crud import get_latest_location
from ml_logic.recommend import recommend_all
from ml_logic.data import fetch_weather

# ルーターを作成
router = APIRouter(prefix="/api/v1")

class SuggestRequest(BaseModel):
    user_id: int

@router.post("/suggest")
def suggest(req: SuggestRequest):
    location = get_latest_location(req.user_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    weather_data = fetch_weather(location["latitude"], location["longitude"])
    if not weather_data:
        raise HTTPException(status_code=500, detail="Weather fetch failed")

    recommendations = recommend_all(req.user_id, weather_data)
    return {"recommendations": recommendations}

# FastAPI本体にルーターを登録
app = FastAPI()
app.include_router(router)
