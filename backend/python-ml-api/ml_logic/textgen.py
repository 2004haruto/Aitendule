import os
import random
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# アドバイス文を生成（日本語）
def generate_advice_text(recommendations: dict, temperature: float, weather: str) -> str:
    prompt = (
        "以下の情報をもとに、自然な日本語の服装アドバイス文を1〜2文で生成してください。\n"
        f"気温: {temperature}℃\n"
        f"天気: {weather}\n"
        f"提案された服装: {recommendations}\n"
        "気温や天気と矛盾しないように注意しつつ、季節感のある親しみやすい表現でお願いします。"
    )
    response = model.generate_content(prompt)
    return response.text.strip()

# 画像検索用キーワードを生成（英語・整形・最大3語）
def generate_image_keywords(advice_text: str, max_keywords: int = 3) -> str:
    prompt = (
        "以下の服装アドバイス文をもとに、Pixabayで画像検索するための英単語を3〜5語、スペース区切りで抽出してください。\n"
        f"{advice_text}\n"
        "例: jeans jacket sneakers\n"
        "出力はキーワードのみ。記号・番号・文は不要。"
    )
    response = model.generate_content(prompt)
    raw_output = response.text.strip()

    # 🔧 英単語のみにフィルタ（記号や番号除去）
    words = re.findall(r'\b[a-zA-Z]+\b', raw_output.lower())
    keywords = random.sample(words, min(len(words), max_keywords))
    return " ".join(keywords)

# アドバイス文 + 画像キーワードをまとめて返す関数
def generate_advice_and_keywords(recommendations: dict, temperature: float, weather: str) -> dict:
    advice = generate_advice_text(recommendations, temperature, weather)
    keywords = generate_image_keywords(advice)
    return {
        "advice_text": advice,
        "image_keywords": keywords,
        "recommendation_items": recommendations
    }
