import os
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import joblib

from ml_logic.data import create_training_data  # data.py の関数をimport

# ✅ モデル保存先を train.py の位置基準に固定
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(CURRENT_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def prepare_and_train_models_by_category(training_data):
    df = pd.DataFrame([x[0] for x in training_data])
    df["label"] = [x[1] for x in training_data]
    df["temp_bin"] = df["temperature"].apply(lambda x: str(int(float(x) // 5)))

    for category in df["category"].unique():
        subset = df[df["category"] == category]
        if subset.empty:
            print(f"スキップ: {category}（データが空）")
            continue

        X = subset.drop(["label", "category", "temperature"], axis=1)
        y = subset["label"]

        print(f"\n--- [{category}] ---", flush=True)
        print(y.value_counts(), flush=True)

        categorical_features = ["weather", "user_id", "month", "day", "hour", "weekday", "temp_bin"]

        preprocessor = ColumnTransformer(
            transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)]
        )

        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        clf = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", XGBClassifier(
                use_label_encoder=False,
                eval_metric="mlogloss",
                random_state=42
            )),
        ])

        if len(subset) < 2:
            print(f"[{category}] データ数が少ないため全データで学習", flush=True)
            clf.fit(X, y_encoded)
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            print(f"[{category}] Accuracy: {acc:.4f}")

        # ✅ 絶対パスで models に保存
        model_path = os.path.join(MODEL_DIR, f"{category}_model.pkl")
        joblib.dump((clf, le), model_path)
        print(f"✅ モデル保存: {model_path}")

if __name__ == "__main__":
    training_data = create_training_data()
    prepare_and_train_models_by_category(training_data)
