import os
import time
import mysql.connector
import pandas as pd
from collections import defaultdict
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import joblib
from datetime import datetime

CATEGORY_NAME_MAP = {
    "トップス": "tops",
    "ボトムス": "bottoms",
    "シューズ": "shoes",
    "アウター": "outer",
    "アクセサリー": "accessory",
}

# モデル保存先を明示的に指定（/app/python-ml-api/models）
MODEL_DIR = os.path.join("/app/python-ml-api/models")
print(f"モデル保存先: {MODEL_DIR}")


def get_db_connection(retries=5, delay=3):
    for i in range(retries):
        try:
            return mysql.connector.connect(
                host=os.getenv("MYSQL_HOST", "db"),
                user=os.getenv("MYSQL_USER", "root"),
                password=os.getenv("MYSQL_PASSWORD", "root"),
                database=os.getenv("MYSQL_DB", "AI_Seminar_IE3B"),
                port=int(os.getenv("MYSQL_PORT", 3306))
            )
        except mysql.connector.Error as e:
            print(f"[DB connection failed {i+1}/{retries}] {e}", flush=True)
            time.sleep(delay)
    raise Exception("DB connection failed after retries")


def fetch_training_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.user_id, i.name AS clothing_item_name, c.created_at, i.category,
               c.weather, c.temperature
        FROM user_clothing_choices c
        JOIN clothing_items i ON c.clothing_id = i.clothing_id
        ORDER BY c.created_at
    """)
    results = cursor.fetchall()
    conn.close()
    return results


def prepare_data(raw_data):
    data_by_category = defaultdict(list)
    for row in raw_data:
        category = row["category"]
        dt = row["created_at"]
        features = {
            "month": str(dt.month),
            "day": str(dt.day),
            "hour": str(dt.hour),
            "weekday": str(dt.weekday()),
            "user_id": str(row["user_id"]),
            "weather": row.get("weather", "unknown"),
            "temp_bin": str(int(row.get("temperature", 0) // 2)),
        }
        label = row["clothing_item_name"]
        data_by_category[category].append((features, label))
    return data_by_category


def save_training_data_as_csv(data_by_category, output_path=os.path.join(MODEL_DIR, "training_data.csv")):
    all_records = []
    for category, data in data_by_category.items():
        for features, label in data:
            record = features.copy()
            record["label"] = label
            record["category"] = category
            all_records.append(record)

    df = pd.DataFrame(all_records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"📁 Exported training data to {output_path}（{len(df)} 件）", flush=True)


def train_and_save_models(data_by_category):
    os.makedirs(MODEL_DIR, exist_ok=True)
    for category, data in data_by_category.items():
        if not data:
            print(f"Skip: {category} (no data)", flush=True)
            continue

        print(f"\n----- [{category}] モデル学習開始 -----", flush=True)

        df = pd.DataFrame([x[0] for x in data])
        df["label"] = [x[1] for x in data]

        X = df.drop(columns=["label"])
        y = df["label"]

        print("[データラベルの内訳]", flush=True)
        print(y.value_counts(), flush=True)

        categorical_features = ["user_id", "month", "day", "hour", "weekday", "weather", "temp_bin"]
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
            ]
        )

        label_encoder = LabelEncoder()
        label_encoder.fit(y)
        y_encoded = label_encoder.transform(y)
        num_class = len(label_encoder.classes_)

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", XGBClassifier(
                use_label_encoder=False,
                eval_metric='mlogloss',
                objective="multi:softprob",
                num_class=num_class,
                random_state=42,
                max_depth=6,         # ← 木の深さ（精度向上に効く）
                learning_rate=0.1,   # ← 学習率（小さいと精度上がるが学習時間増）
                n_estimators=200     # ← 木の本数（増やすと精度UPすることも）
            ))
        ])

        if len(df) < 2:
            print("⚠️ データが1件以下のため全件で学習", flush=True)
            pipeline.fit(X, y_encoded)
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            print(f"[{category}] Accuracy: {acc:.4f}", flush=True)

            print("\n[予測結果サンプル]", flush=True)
            for i in range(min(5, len(y_test))):
                actual = label_encoder.inverse_transform([y_test[i]])[0]
                pred = label_encoder.inverse_transform([y_pred[i]])[0]
                print(f"  実際: {actual} | 予測: {pred}", flush=True)

        filename_category = CATEGORY_NAME_MAP.get(category, category)
        model_path = os.path.join(MODEL_DIR, f"{filename_category}_model.pkl")
        joblib.dump((pipeline, label_encoder), model_path)
        print(f"✅ Saved model: {model_path}", flush=True)
        print(f"----- [{category}] モデル学習終了 -----\n", flush=True)


if __name__ == "__main__":
    print("🚀 Fetching training data from DB...", flush=True)
    raw_data = fetch_training_data()

    if not raw_data:
        print("⚠ No training data found. Exiting.", flush=True)
        exit(1)

    print("🧹 Preparing data...", flush=True)
    data_by_category = prepare_data(raw_data)

    print("📊 カテゴリ別データ数：", flush=True)
    for category, items in data_by_category.items():
        print(f"- {category}: {len(items)} 件", flush=True)

    print("📦 Saving training data to CSV...", flush=True)
    save_training_data_as_csv(data_by_category)

    print("🧠 Training models by category...", flush=True)
    train_and_save_models(data_by_category)

    print("✅ Training complete.", flush=True)