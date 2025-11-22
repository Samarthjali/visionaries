# ui.py
import streamlit as st
import requests
import numpy as np
import pandas as pd
import json
import os
from datetime import datetime

# --------- Config ----------
BACKEND_PREDICT_ENDPOINT = "http://localhost:5000/predict"  # Flask backend
HISTORY_FILE = "tx_history.json"  # local file to persist history
st.set_page_config(page_title="PhishGuard — Transaction Analyzer", layout="centered")

# --------- Helpers ----------
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def compute_signal(amount, avg, lower_mult, upper_mult):
    if amount < lower_mult * avg:
        return "green", "🟢 Below average (Safe)"
    elif amount <= upper_mult * avg:
        return "yellow", "🟡 Close to average (Monitor)"
    else:
        return "red", "🔴 Above average (Risky)"

# --------- Session state & history ----------
if "history" not in st.session_state:
    st.session_state.history = load_history()

st.title("🛡️ PhishGuard — Transaction Analyzer")
st.write("This interface learns your transaction behavior and shows a traffic-light risk signal. Each check is saved to the backend (and onto Algorand TestNet).")

# --------- User Controls ----------
amount = st.number_input("💰 Enter Transaction Amount", min_value=1.0, value=100.0, step=1.0)
# Slider for yellow band
sensitivity = st.slider("Yellow Band (%)", min_value=25, max_value=80, value=50, help="Width of the yellow band around your average")

# Reset history button
if st.button("Reset History"):
    st.session_state.history = []
    save_history([])
    st.success("Transaction history reset.")


lower_mult = 1 - (sensitivity / 100.0)
upper_mult = 1 + (sensitivity / 100.0)

# --------- Analyze button ---------
if st.button("Analyze Transaction & Store"):
    now = datetime.utcnow().isoformat()
    # compute rolling average
    amounts = [float(r["amount"]) for r in st.session_state.history] if st.session_state.history else []
    avg = float(np.mean(amounts)) if amounts else float(amount)
    
    # determine local signal
    color_key, signal_text = compute_signal(float(amount), avg, lower_mult, upper_mult)

    # call backend to store AI prediction on blockchain
    with st.spinner("Calling backend and storing prediction on blockchain..."):
        try:
            resp = requests.post(BACKEND_PREDICT_ENDPOINT, json={"amount": float(amount)}, timeout=12)
            if resp.status_code == 200:
                backend_json = resp.json()
                txid = backend_json.get("txid", "N/A")
                ai_prediction = backend_json.get("prediction", "N/A")
            else:
                txid = f"HTTP {resp.status_code}"
                ai_prediction = f"Backend error: {resp.text}"
        except Exception as e:
            txid = "ERROR"
            ai_prediction = f"Connection error: {e}"

    # save record locally
    record = {
        "timestamp": now,
        "amount": float(amount),
        "signal": signal_text,
        "ai_prediction": ai_prediction,
        "txid": txid
    }
    st.session_state.history.append(record)
    save_history(st.session_state.history)

    # display results
    if color_key == "green":
        st.success(signal_text)
    elif color_key == "yellow":
        st.warning(signal_text)
    else:
        st.error(signal_text)

    st.write(f"Your rolling average (based on {len(amounts)} prior tx): **{round(avg,2)}**")
    st.write(f"AI prediction (backend): **{ai_prediction}**")
    if txid and txid != "ERROR" and not str(txid).startswith("HTTP"):
        st.write(f"Transaction stored on chain — TXID: `{txid}`")
        st.markdown(f"[View on TestNet Explorer](https://testnet.algoexplorer.io/tx/{txid})")
    else:
        st.write(f"Blockchain storage info: `{txid}`")

# --------- Visualize history ----------
if st.session_state.history:
    st.subheader("📈 Transaction History")
    df = pd.DataFrame(st.session_state.history)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    st.dataframe(df.sort_values("timestamp", ascending=False).reset_index(drop=True))
    st.line_chart(pd.DataFrame({"amount": [r["amount"] for r in st.session_state.history]}))
    st.markdown(f"**Total checks:** {len(st.session_state.history)}  •  **Avg amount:** {round(df['amount'].mean(),2)}")
else:
    st.info("No transaction history yet. Enter some amounts and press 'Analyze Transaction & Store'.")
