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

FS = 360                 # Sampling frequency (Hz)
WINDOW_SEC = 5           # ECG window length (seconds)
WINDOW_SAMPLES = FS * WINDOW_SEC

REFRESH = 0.5            # UI refresh (seconds)

# ---------- STREAMLIT UI ----------
st.set_page_config(layout="wide")
st.title("🫀 Real-Time ECG Monitoring (5s Window)")
st.markdown("Displaying latest **5 seconds** of ECG data")

@st.cache_data(ttl=1)
def fetch_data():
    r = requests.get(FIREBASE_URL)
    if r.status_code != 200 or not r.json():
        return pd.DataFrame()
    return pd.DataFrame(r.json()).T

placeholder = st.empty()

while True:
    df = fetch_data()

    if not df.empty and "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()

        # Ensure we have enough samples
        if len(df) >= WINDOW_SAMPLES:
            # Take last 5 seconds
            df = df.tail(WINDOW_SAMPLES).reset_index(drop=True)

            # Generate time axis (0 → 5 sec)
            time_axis = np.linspace(
                0, WINDOW_SEC, WINDOW_SAMPLES, endpoint=False
            )

            plot_df = pd.DataFrame({
                "Time (s)": time_axis,
                "ECG": df["value"]
            }).set_index("Time (s)")

            with placeholder.container():
                st.line_chart(plot_df["ECG"], height=450)
        else:
            st.info(
                f"Collecting data... "
                f"({len(df)}/{WINDOW_SAMPLES} samples)"
            )
    else:
        st.warning("Waiting for ECG data...")

    time.sleep(REFRESH)
