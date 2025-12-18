import streamlit as st
import requests
import pandas as pd
import time

# Firebase DB URL (ecg_data node)
FIREBASE_URL = "https://ecg-monitoring-a2dd2-default-rtdb.asia-southeast1.firebasedatabase.app/ecg_data.json"

st.set_page_config(page_title="Real-Time ECG Monitor", layout="wide")
st.title("📈 Real-Time ECG Monitoring")

# User controls
SAMPLES = st.slider("Number of samples to display", 500, 5000, 1500)
REFRESH = st.slider("Refresh interval (seconds)", 1, 5, 1)

@st.cache_data(ttl=1)
def fetch_data():
    response = requests.get(FIREBASE_URL)
    if response.status_code != 200:
        return pd.DataFrame()
    data = response.json()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data).T
    return df

placeholder = st.empty()

while True:
    df = fetch_data()

    if not df.empty:
        df["time_ms"] = pd.to_numeric(df["time_ms"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

        df = df.dropna()
        df = df.sort_values("time_ms")
        df = df.tail(SAMPLES)

        df["time_sec"] = df["time_ms"] / 1000.0
        df = df.set_index("time_sec")

        with placeholder.container():
            st.line_chart(df["value"], height=400)
    else:
        st.warning("Waiting for ECG data...")

    time.sleep(REFRESH)
