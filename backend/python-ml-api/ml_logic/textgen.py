import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_description(recommendations: dict) -> str:
    prompt = (
        "以下の服装提案に基づいて、自然な日本語のアドバイス文を1〜2文で生成してください。\n"
        f"{recommendations}\n"
        "季節感や気候も考慮した親しみやすい表現でお願いします。"
    )

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)
    return response.text.strip()
