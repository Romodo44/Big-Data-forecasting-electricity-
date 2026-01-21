# /opt/spark/jobs/prediction/train_xgb.py

import pandas as pd
from pathlib import Path
import joblib
from xgboost import XGBRegressor

# CONFIG 
GOLD_PATH = Path("/opt/lakehouse/gold/timeseries")
MODEL_PATH = Path("/opt/lakehouse/gold/model_xgb.pkl")

FEATURES = [
    "temp_c",
    "rain_mm",
    "wind_ms",
    "hour",
    "dayofweek",
    "month",
    "is_weekend",
    "is_winter",
]

TARGET = "load_mw"

#LOAD DATA 
df = pd.read_parquet(GOLD_PATH)
df["ts_hour"] = pd.to_datetime(df["ts_hour"])
df = df.sort_values("ts_hour")

# FEATURE ENGINEERING
df["hour"] = df["ts_hour"].dt.hour
df["dayofweek"] = df["ts_hour"].dt.dayofweek
df["month"] = df["ts_hour"].dt.month
df["is_weekend"] = (df["dayofweek"] >=5 ).astype(int)
df["is_winter"] = df["month"].isin([12, 1, 2]).astype(int)

df = df.dropna(subset=FEATURES + [TARGET])

# TRAIN / TEST SPLIT
split_date = df["ts_hour"].quantile(0.8)

train_df = df[df["ts_hour"] <= split_date]
test_df  = df[df["ts_hour"] > split_date]

X_train = train_df[FEATURES]
y_train = train_df[TARGET]

#  MODEL 
model = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
)

model.fit(X_train, y_train)

#  SAVE MODEL
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(model, MODEL_PATH)

print(f"✅ Model trained and saved to {MODEL_PATH}")
print(f"Train size: {len(train_df)} | Test size: {len(test_df)}")
