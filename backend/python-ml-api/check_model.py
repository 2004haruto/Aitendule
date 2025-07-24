import joblib
import os
from sklearn.pipeline import Pipeline

CATEGORIES = ["bottoms", "shoes", "outer", "tops", "accessory"]

for category in CATEGORIES:
    path = f"models/{category}_model.pkl"
    print(f"\n🔍 カテゴリ: {category}")
    print(f"📍 モデルパス: {path}")

    if not os.path.exists(path):
        print(f"❌ モデルファイルなし: {path}")
        continue

    try:
        bundle = joblib.load(path)
    except Exception as e:
        print(f"❌ 読み込みエラー: {e}")
        continue

    if isinstance(bundle, tuple) and len(bundle) == 2:
        model, label_encoder = bundle
        print(f"📦 モデル型: {type(model)}")
        if isinstance(model, Pipeline):
            classifier = model.named_steps.get("classifier", None)
            print(f"🧠 使用分類器: {type(classifier)}")
        else:
            print("❓ モデルは Pipeline ではありません")
    else:
        print("❌ 想定外のモデル形式")
        print(f"📦 内容: {bundle}")
