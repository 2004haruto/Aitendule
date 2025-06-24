import os
import time
import mysql.connector
import pandas as pd
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from datetime import datetime

CATEGORY_NAME_MAP = {
    "トップス": "tops",
    "ボトムス": "bottoms",
    "シューズ": "shoes",
    "アウター": "outer",
    "アクセサリー": "accessory",
}

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
            print(f"[DB connection failed {i+1}/{retries}] {e}")
            time.sleep(delay)
    raise Exception("DB connection failed after retries")

def fetch_training_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.user_id, i.name AS clothing_item_name, c.created_at, i.category
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
        }
        label = row["clothing_item_name"]
        data_by_category[category].append((features, label))
    return data_by_category

def save_training_data_as_csv(data_by_category, output_path="models/training_data.csv"):
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
    print(f"📁 Exported training data to {output_path}（{len(df)} 件）")


def train_and_save_models(data_by_category):
    os.makedirs("models", exist_ok=True)
    for category, data in data_by_category.items():
        if not data:
            print(f"Skip: {category} (no data)")
            continue

        df = pd.DataFrame([x[0] for x in data])
        df["label"] = [x[1] for x in data]

        X = df.drop(columns=["label"])
        y = df["label"]

        categorical_features = ["user_id", "month", "day", "hour", "weekday"]
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
            ]
        )

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
        ])

        if len(df) < 2:
            print(f"[{category}] Not enough data to split. Training with full data.")
            pipeline.fit(X, y)
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            print(f"[{category}] Accuracy: {acc:.4f}")

        filename_category = CATEGORY_NAME_MAP.get(category, category)
        model_path = f"models/{filename_category}_model.pkl"
        joblib.dump(pipeline, model_path)
        print(f"✅ Saved model: {model_path}")

if __name__ == "__main__":
    print("🚀 Fetching training data from DB...")
    raw_data = fetch_training_data()

    if not raw_data:
        print("⚠ No training data found. Exiting.")
        exit(1)

    print("🧹 Preparing data...")
    data_by_category = prepare_data(raw_data)
    
    print("📊 カテゴリ別データ数：")
    for category, items in data_by_category.items():
        print(f"- {category}: {len(items)} 件")


    print("📦 Saving training data to CSV...")
    save_training_data_as_csv(data_by_category)

    print("🧠 Training models by category...")
    train_and_save_models(data_by_category)

    print("✅ Training complete.")
