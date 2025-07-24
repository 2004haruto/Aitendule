import os
import requests
import urllib3
from dotenv import load_dotenv

# SSL警告を無効化（ローカル用途）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# .env読み込み
load_dotenv()
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

def search_pixabay_image(query: str) -> str:
    """
    Pixabay API を使って画像を1件だけ取得し、画像URLを返す。
    """
    if not PIXABAY_API_KEY:
        print("❌ Pixabay APIキーが設定されていません (.env の PIXABAY_API_KEY を確認してください)")
        return ""

    # 前処理: 全角スペース → 半角、最大3語に制限
    safe_query = query.replace("　", " ").strip()
    keywords = safe_query.split()
    limited_query = " ".join(keywords[:3])  # 最大3語

    if not limited_query:
        print("⚠️ 空の検索クエリです")
        return ""

    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": limited_query,  # requestsが自動でURLエンコード
        "image_type": "photo",
        "safesearch": "true",
        "per_page": 3
    }

    try:
        print(f"🔍 Pixabay 検索クエリ: {limited_query}")
        response = requests.get(url, params=params, verify=False)
        if response.status_code != 200:
            print(f"❗ APIエラー (ステータスコード: {response.status_code})")
            print(f"🔴 エラーレスポンス本文: {response.text}")
            return ""
        data = response.json()
        if data.get("hits"):
            return data["hits"][0].get("webformatURL", "")
        else:
            print("❌ 画像が見つかりませんでした")
            return ""
    except Exception as e:
        print("Pixabay API error:", e)
        return ""
