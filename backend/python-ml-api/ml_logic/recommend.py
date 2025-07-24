import os
import joblib
import pandas as pd
from typing import Dict, Any, Optional, Tuple

# モデルを持つカテゴリ一覧
CATEGORIES = ["bottoms", "shoes", "outer", "tops", "accessory"]

# 学習時に使った特徴量の順序
FEATURE_ORDER = ["weather", "user_id", "month", "day", "hour", "weekday", "temp_bin"]

def load_model(category: str) -> Optional[Tuple[Any, Any]]:
    model_path = f"models/{category}_model.pkl"
    if not os.path.exists(model_path):
        print(f"⚠ モデルファイルが見つかりません: {model_path}")
        return None

    try:
        bundle = joblib.load(model_path)
        if isinstance(bundle, dict):
            return bundle["model"], bundle["label_encoder"]
        elif isinstance(bundle, tuple) and len(bundle) == 2:
            return bundle[0], bundle[1]
        else:
            print(f"❌ 想定外のモデル形式 [{category}]")
            return None
    except Exception as e:
        print(f"❌ モデル読み込み失敗 [{category}]: {e}")
        return None
    
def recommend_for_category(category: str, features: Dict[str, Any]) -> Optional[str]:
    """
    特定カテゴリに対する服の推薦を返す

    Returns:
        予測された服の名称 または None
    """
    model_bundle = load_model(category)
    if model_bundle is None:
        return None

    pipeline, label_encoder = model_bundle

    try:
        input_data = {
            "weather": str(features["weather"]),
            "user_id": str(features["user_id"]),
            "month": str(features["month"]),
            "day": str(features["day"]),
            "hour": str(features["hour"]),
            "weekday": str(features["weekday"]),
            "temp_bin": str(int(float(features["temperature"]) // 5)),
        }
    except KeyError as e:
        print(f"❌ 必要な特徴量が不足: {e}")
        return None

    df = pd.DataFrame([input_data])
    try:
        pred_index = pipeline.predict(df)[0]
        pred_label = label_encoder.inverse_transform([pred_index])[0]
        return pred_label
    except Exception as e:
        print(f"❌ 推論失敗 [{category}]: {e}")
        return None

def recommend_all(features: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    全カテゴリに対して服の推薦を行う

    Returns:
        {カテゴリ: 推薦されたアイテム名} の辞書
    """
    return {
        category: recommend_for_category(category, features)
        for category in CATEGORIES
    }

# CLIテスト用
if __name__ == "__main__":
    sample_input = {
        "temperature": 26.5,
        "weather": "clear",
        "user_id": 1,
        "month": 7,
        "day": 13,
        "hour": 15,
        "weekday": 6,
    }

    print("🧪 推薦結果サンプル：\n")
    results = recommend_all(sample_input)
    for category, item in results.items():
        print(f"{category}: {item}")
