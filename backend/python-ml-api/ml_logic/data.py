from db import get_connection
from datetime import datetime
import requests
import os

def fetch_weather(lat, lon):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY is not set in environment variables")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ja"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return {
        "temperature": data["main"]["temp"],
        "weather": data["weather"][0]["main"].lower()
    }

def encode_weather(weather_str):
    mapping = {
        "thunderstorm": 0,  # 雷雨
        "drizzle": 1,       # 霧雨
        "rain": 2,          # 雨
        "snow": 3,          # 雪
        "clear": 4,         # 晴れ
        "clouds": 5,        # 曇り
        "mist": 6,          # 靄
        "smoke": 7,         # 煙
        "haze": 8,          # 霞
        "dust": 9,          # 埃 or 塵
        "fog": 10,          # 霧
        "sand": 11,         # 砂
        "ash": 12,          # 灰
        "squall": 13,       # スコール
        "tornado": 14       # トルネード
    }
    return mapping.get(weather_str.lower(), -1)

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
        user_id = choice["user_id"]
        chosen_item = choice["clothing_item_name"]
        category = choice["category"]
        choice_time = choice["created_at"]

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

        weather_encoded = encode_weather(weather["weather"])
        if weather_encoded == -1:
            continue

        features = {
            "temperature": weather["temperature"],
            "weather": weather_encoded,
            "user_id": user_id,
            "month": choice_time.month,
            "day": choice_time.day,
            "hour": choice_time.hour,
            "weekday": choice_time.weekday(),
            "category": category,
        }

        training_data.append((features, chosen_item))

    conn.close()
    return training_data
