import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_URL = "http://api:8000"

st.set_page_config(
    page_title="Electricity & Weather Dashboard",
    layout="wide"
)

st.title("⚡ Electricity consumption, weather & prediction")

# =====================
# Sidebar
# =====================
st.sidebar.header("Filters")

zone = st.sidebar.selectbox("Zone", ["FR"])

# =====================
# Load real data
# =====================
params = {"zone": zone}

with st.spinner("Loading real data..."):
    r = requests.get(f"{API_URL}/timeseries", params=params)
    r.raise_for_status()
    df = pd.DataFrame(r.json()["data"])

if df.empty:
    st.warning("No data available.")
    st.stop()

df["ts_hour"] = pd.to_datetime(df["ts_hour"])

# =====================
# Load predictions
# =====================
pred_df = None
start_pred = None

try:
    r_pred = requests.get(f"{API_URL}/predictions", params={"zone": zone})
    r_pred.raise_for_status()
    payload = r_pred.json()

    pred_df = pd.DataFrame(payload["data"])
    start_pred = payload.get("start_prediction")

    if not pred_df.empty:
        pred_df["ts_hour"] = pd.to_datetime(pred_df["ts_hour"])
except Exception:
    pred_df = None

# =====================
# Merge real + pred
# =====================
if pred_df is not None and not pred_df.empty:
    df = df.merge(
        pred_df[["ts_hour", "load_pred"]],
        on="ts_hour",
        how="left"
    )

    st.info(f"Predictions start at {start_pred}")
else:
    st.warning("Predictions not available")

# =====================
# Select ONE prediction day
# =====================
if pred_df is not None and not pred_df.empty:
    pred_df["date"] = pred_df["ts_hour"].dt.date
    available_days = sorted(pred_df["date"].unique())

    selected_day = st.sidebar.selectbox(
        "Prediction day",
        available_days,
        index=len(available_days) - 1
    )

    df_plot = df[df["ts_hour"].dt.date == selected_day].copy()
else:
    df_plot = df.copy()

# =====================
# Plot – real vs prediction (clean & readable)
# =====================
fig = go.Figure()

# Real load
fig.add_trace(go.Scatter(
    x=df_plot["ts_hour"],
    y=df_plot["load_mw"],
    mode="lines",
    name="Real load",
    line=dict(color="royalblue", width=2),
))

# Prediction
if "load_pred" in df_plot.columns and df_plot["load_pred"].notna().any():
    fig.add_trace(go.Scatter(
        x=df_plot["ts_hour"],
        y=df_plot["load_pred"],
        mode="lines",
        name="Predicted load",
        line=dict(color="firebrick", dash="dash", width=2),
    ))

fig.update_layout(
    title=f"Electricity load – {selected_day}",
    xaxis_title="Hour",
    yaxis_title="Load (MW)",
    legend=dict(orientation="h", y=1.15),
)

st.plotly_chart(fig, use_container_width=True)

# =====================
# Raw data
# =====================
with st.expander("Show raw data"):
    st.dataframe(df_plot)
