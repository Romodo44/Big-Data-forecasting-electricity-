from fastapi import FastAPI, Query
import pandas as pd
from pathlib import Path
import traceback
import os
import numpy as np

app = FastAPI()

GOLD_PATH = Path("/opt/lakehouse/gold/timeseries")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/timeseries")
def timeseries(
    zone: str = "FR",
    start: str | None = Query(None),
    end: str | None = Query(None),
):
    debug = {}
    try:
        debug["cwd"] = os.getcwd()
        debug["gold_path"] = str(GOLD_PATH)
        debug["exists"] = GOLD_PATH.exists()
        debug["is_dir"] = GOLD_PATH.is_dir()
        debug["files"] = [p.name for p in GOLD_PATH.glob("*")] if GOLD_PATH.exists() else []

        df = pd.read_parquet(GOLD_PATH)
        debug["df_shape"] = df.shape
        debug["df_columns"] = df.columns.tolist()

        df = df[df["zone"] == zone]
        debug["after_zone_filter"] = df.shape

        df["ts_hour"] = pd.to_datetime(df["ts_hour"], errors="coerce")

        if start:
            df = df[df["ts_hour"] >= pd.to_datetime(start)]
        if end:
            df = df[df["ts_hour"] <= pd.to_datetime(end)]

        # Nettoyage JSON (NaN / inf)
        df = df.replace([np.inf, -np.inf], np.nan)

        # Convert ts_hour en string ISO (safe JSON)
        out = df.sort_values("ts_hour").tail(2000).copy()
        out["ts_hour"] = out["ts_hour"].dt.strftime("%Y-%m-%dT%H:%M:%S")

        # Remplace NaN -> None (JSON OK)
        out = out.where(pd.notnull(out), None)

        debug["final_shape"] = out.shape

        return {"debug": debug, "data": out.to_dict(orient="records")}

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "debug": debug,
        }


PRED_PATH = Path("/opt/lakehouse/gold/predictions/predictions.parquet")

@app.get("/predictions")
def predictions(zone: str = "FR"):
    if not PRED_PATH.exists():
        return {"data": []}

    df = pd.read_parquet(PRED_PATH)

    df = df[df["zone"] == zone]
    df["ts_hour"] = pd.to_datetime(df["ts_hour"])
    df = df.sort_values("ts_hour")

    df["ts_hour"] = df["ts_hour"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    df = df.where(pd.notnull(df), None)

    return {
        "start_prediction": df["ts_hour"].iloc[0] if not df.empty else None,
        "data": df.to_dict(orient="records")
    }

