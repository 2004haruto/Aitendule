import os
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

from ml_logic.data import create_training_data  # data.py の関数をimport


def prepare_and_train_models_by_category(training_data):
    # 保存先ディレクトリの作成
    os.makedirs("models", exist_ok=True)

    # DataFrame に変換
    df = pd.DataFrame([x[0] for x in training_data])
    df["label"] = [x[1] for x in training_data]

    # カテゴリごとにモデルを学習
    for category in df["category"].unique():
        subset = df[df["category"] == category]
        if subset.empty:
            print(f"スキップ: {category}（データが空）")
            continue

        X = subset.drop("label", axis=1)
        y = subset["label"]

        categorical_features = ["weather", "user_id", "month", "day", "hour", "weekday"]
        numeric_features = ["temperature"]

        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
                ("num", "passthrough", numeric_features),
            ]
        )

        clf = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=100, random_state=42)),
        ])

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"[{category}] Accuracy: {accuracy:.4f}")

        model_path = f"models/{category}_model.pkl"
        joblib.dump(clf, model_path)
        print(f"モデル保存: {model_path}")


if __name__ == "__main__":
    training_data = create_training_data()
    prepare_and_train_models_by_category(training_data)
