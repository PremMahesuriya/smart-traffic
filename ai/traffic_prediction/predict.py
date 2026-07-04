"""Traffic prediction — Phase 8."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


FEATURES = ["hour", "day_of_week", "is_holiday", "vehicle_count", "weather_code"]
TARGET = "vehicle_count_future"
HORIZONS = {"10min": 1, "30min": 3, "1hour": 6}  # steps ahead


def train_model(df: pd.DataFrame, model_type: str = "random_forest"):
    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if model_type == "linear":
        model = LinearRegression()
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42)

    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    return model, score


def predict_traffic(model, current_features: dict) -> dict:
    X = pd.DataFrame([current_features])[FEATURES]
    prediction = int(model.predict(X)[0])
    return {"predicted_vehicles": prediction, "features_used": current_features}


def main():
    parser = argparse.ArgumentParser(description="Train traffic prediction model")
    parser.add_argument("--data", required=True, help="CSV with historical traffic data")
    parser.add_argument("--model-type", choices=["linear", "random_forest"], default="random_forest")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    model, score = train_model(df, args.model_type)
    print(f"Model R² score: {score:.4f}")


if __name__ == "__main__":
    main()
