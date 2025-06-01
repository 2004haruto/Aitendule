from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SuggestRequest(BaseModel):
    temp: float
    weather: str

@app.post("/suggest")
def suggest_clothing(req: SuggestRequest):
    if req.temp < 10:
        return {"items": ["コート", "長袖シャツ", "ジーンズ"]}
    elif req.temp < 20:
        if req.weather == "rainy":
            return {"items": ["カーディガン", "長袖シャツ", "レインコート"]}
        return {"items": ["カーディガン", "長袖シャツ", "ジーンズ"]}
    else:
        return {"items": ["半袖シャツ", "ショートパンツ"]}
