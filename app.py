import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

# Firebase DB (value-only)
FIREBASE_URL = (
    "https://ecg-monitoring-a2dd2-default-rtdb."
    "asia-southeast1.firebasedatabase.app/ecg_data.json"
)

FS = 360  # Sampling frequency (Hz)

st.set_page_config(page_title="Real-Time ECG Monitoring", layout="wide")
st.title("📈 Real-Time ECG Monitoring")

SAMPLES = st.slider("Number of samples to display", 500, 5000, 2000)
REFRESH = st.slider("Refresh interval (seconds)", 1, 5, 1)

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

        df = df.tail(SAMPLES).reset_index(drop=True)

        # Generate time locally (Fs-based)
        time_axis = np.arange(len(df)) / FS

        plot_df = pd.DataFrame({
            "Time (s)": time_axis,
            "ECG": df["value"]
        }).set_index("Time (s)")

        with placeholder.container():
            st.line_chart(plot_df["ECG"], height=400)
    else:
        st.warning("Waiting for ECG data...")

    time.sleep(REFRESH)
