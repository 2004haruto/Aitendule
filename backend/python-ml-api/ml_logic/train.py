import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

from ml_logic.data import create_training_data  # data.py の関数をimport

def prepare_and_train_model(training_data):
    features_list = [x[0] for x in training_data]
    labels = [x[1] for x in training_data]

    df = pd.DataFrame(features_list)
    df["label"] = labels

    X = df.drop("label", axis=1)
    y = df["label"]

    categorical_features = ["weather", "user_id", "month", "day", "hour", "weekday", "category"]
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
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")

    joblib.dump(clf, "clothing_recommender.pkl")

    return clf

if __name__ == "__main__":
    training_data = create_training_data()
    prepare_and_train_model(training_data)
