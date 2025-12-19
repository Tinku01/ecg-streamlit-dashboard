import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

# ---------- CONFIG ----------
FIREBASE_URL = (
    "https://ecg-monitoring-a2dd2-default-rtdb."
    "asia-southeast1.firebasedatabase.app/ecg_data.json"
)

FS = 360                  # Sampling frequency (Hz)
WINDOW_SEC = 5            # Window length (seconds)
WINDOW_SAMPLES = FS * WINDOW_SEC  # 1800 samples
REFRESH = 0.5             # UI refresh (seconds)

# ---------- UI ----------
st.set_page_config(layout="wide")
st.title("🫀 Real-Time ECG (Strict 5-Second Window)")

status = st.empty()
plot_area = st.empty()

@st.cache_data(ttl=1)
def fetch_data():
    r = requests.get(FIREBASE_URL)
    if r.status_code != 200 or not r.json():
        return pd.DataFrame()
    return pd.DataFrame(r.json()).T

while True:
    df = fetch_data()

    # Validate data
    if df.empty or "value" not in df.columns:
        status.warning("Waiting for ECG data…")
        time.sleep(REFRESH)
        continue

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()

    sample_count = len(df)

    # ---- STRICT CONDITION ----
    if sample_count < WINDOW_SAMPLES:
        status.info(
            f"Collecting data… "
            f"{sample_count}/{WINDOW_SAMPLES} samples"
        )
        time.sleep(REFRESH)
        continue

    # ---- EXACT WINDOW ----
    df_window = df.tail(WINDOW_SAMPLES).reset_index(drop=True)

    # Local time axis (0 → 5 s)
    time_axis = np.arange(WINDOW_SAMPLES) / FS

    plot_df = pd.DataFrame({
        "Time (s)": time_axis,
        "ECG": df_window["value"]
    }).set_index("Time (s)")

    status.success("Displaying latest 5-second ECG window")

    with plot_area.container():
        st.line_chart(plot_df["ECG"], height=450)

    time.sleep(REFRESH)
