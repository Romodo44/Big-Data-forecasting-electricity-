# /opt/spark/jobs/prediction/test_xgb.py

import pandas as pd
import joblib
from pathlib import Path

# ================= CONFIG =================
GOLD_PATH = Path("/opt/lakehouse/gold/timeseries")
MODEL_PATH = Path("/opt/lakehouse/gold/model_xgb.pkl")
PRED_PATH = Path("/opt/lakehouse/gold/predictions")

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

#LOAD DATA
df = pd.read_parquet(GOLD_PATH)
df["ts_hour"] = pd.to_datetime(df["ts_hour"])
df = df.sort_values("ts_hour")

# FEATURE ENGINEERING
df["hour"] = df["ts_hour"].dt.hour
df["dayofweek"] = df["ts_hour"].dt.dayofweek
df["month"] = df["ts_hour"].dt.month
df["is_weekend"] = df["dayofweek"] >= 5
df["is_winter"] = df["month"].isin([12, 1, 2])

df = df.dropna(subset=FEATURES)

#  LOAD MODEL
model = joblib.load(MODEL_PATH)

#  PREDICT 
df["load_pred"] = model.predict(df[FEATURES])

# ⚠️ uniquement la partie "future"
split_date = df["ts_hour"].quantile(0.8)
df_pred = df[df["ts_hour"] > split_date]

# SAVE 
PRED_PATH.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PRED_PATH / "predictions.parquet"

df_pred[[
    "ts_hour",
    "zone",
    "load_mw",
    "load_pred",
    "temp_c",
    "rain_mm",
    "wind_ms",
]].to_parquet(OUTPUT_FILE, index=False)

print(f"📈 Predictions written to {OUTPUT_FILE}")
print(f"Rows predicted: {len(df_pred)}")

