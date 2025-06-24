from db import get_connection
from datetime import datetime
import requests
import os

def fetch_weather(lat, lon):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY is not set in environment variables")
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ja"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "weather": data["weather"][0]["main"].lower()  # ex: "clear", "rain"
        }
    except Exception as e:
        print(f"天気情報の取得に失敗: {e}")
        return None

def create_training_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.user_id, c.clothing_item_name, c.created_at, i.category
        FROM user_clothing_choices c
        JOIN clothing_items i ON c.clothing_item_name = i.name
        ORDER BY c.created_at
    """)
    choices = cursor.fetchall()

    training_data = []

    for choice in choices:
        try:
            user_id = choice["user_id"]
            chosen_item = choice["clothing_item_name"]
            category = choice["category"]
            choice_time = choice["created_at"]

            # 最新の位置情報を取得（選択時点以前）
            cursor.execute("""
                SELECT * FROM user_locations
                WHERE user_id=%s AND created_at <= %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id, choice_time))
            location = cursor.fetchone()
            if not location:
                continue

            weather = fetch_weather(location["latitude"], location["longitude"])
            if not weather:
                continue

            features = {
                "temperature": weather["temperature"],
                "weather": weather["weather"],  # ← 数値ではなく文字列
                "user_id": user_id,
                "month": choice_time.month,
                "day": choice_time.day,
                "hour": choice_time.hour,
                "weekday": choice_time.weekday(),
                "category": category,
            }

            training_data.append((features, chosen_item))
        except Exception as e:
            print(f"データ処理中にエラー: {e}")
            continue

    conn.close()
    return training_data
