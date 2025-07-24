from ml_logic.pixabay import search_pixabay_image

# テスト用クエリ（例：単語1〜2個で試すと確実）
test_queries = [
    "coat",                     # 英語の単語（成功しやすい）
    "jacket sweater",           # 英語複数語
    "コート",                   # 日本語も一応OK
    "スニーカー セーター",       # 日本語複数語（失敗するかも）
    "",                         # 空文字（→""を返す想定）
]

for q in test_queries:
    print(f"\n🔍 検索キーワード: {q}")
    image_url = search_pixabay_image(q)
    print(f"📸 取得画像URL: {image_url or 'なし'}")
