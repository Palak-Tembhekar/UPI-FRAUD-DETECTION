import streamlit as st
import numpy as np
import pandas as pd
import pickle
import os
import time
from datetime import datetime

# Page Layout
st.set_page_config(page_title="Intelligent UPI Fraud Mitigation Engine", page_icon="🛡️", layout="wide")

# ==========================================
# 1. AUTO-LOAD MODEL & SCALER
# ==========================================
@st.cache_resource
def load_artifacts():
    # Looks for 'upi_fraud_model (3).pkl' first, then fallback to original name
    model_filename = 'upi_fraud_model (3).pkl' if os.path.exists('upi_fraud_model (3).pkl') else 'upi_fraud_model.pkl'
    scaler_filename = 'scaler (3).pkl' if os.path.exists('scaler (3).pkl') else 'scaler.pkl'
    
    with open(model_filename, 'rb') as f:
        model = pickle.load(f)
    with open(scaler_filename, 'rb') as f:
        scaler = pickle.load(f)
    return model, scaler

model, scaler = load_artifacts()

# ==========================================
# 2. USER PERSONAS
# ==========================================
USER_PERSONAS = {
    "College Student (Daily Low Spends)": {
        "name": "Palak",
        "balance": 12000.0,
        "avg_spend": 250.0,
        "trusted_device": True,
        "last_city": "Kamptee",
        "tx_count_10m": 0,
        "last_tx_time_gap": 1800.0
    },
    "Wholesale Merchant (High Volume Cashflow)": {
        "name": "Sharma Textiles",
        "balance": 450000.0,
        "avg_spend": 35000.0,
        "trusted_device": True,
        "last_city": "Nagpur",
        "tx_count_10m": 1,
        "last_tx_time_gap": 300.0
    },
    "Compromised Account (Victim Under Attack)": {
        "name": "Aakash Verma",
        "balance": 85000.0,
        "avg_spend": 300.0,
        "trusted_device": False,
        "last_city": "Mumbai",
        "tx_count_10m": 4,
        "last_tx_time_gap": 0.8
    }
}

# ==========================================
# 3. PIPELINE EVALUATION
# ==========================================
def evaluate_transaction(amount, balance, avg_spend, hour, tx_count_10m, is_new_device, velocity_kmh, inter_arrival_sec):
    if inter_arrival_sec < 1.0 and tx_count_10m <= 1:
        return {
            "status": "APPROVED_DEDUPLICATED",
            "score": 0.05,
            "reason": "Duplicate transaction filtered (Hardware/Network stutter detected). Single charge authorized."
        }

    drain_ratio = amount / (balance + 1e-5)
    if amount > balance:
        return {
            "status": "DECLINED_INSUFFICIENT_FUNDS",
            "score": 1.0,
            "reason": "Transaction amount exceeds current account balance."
        }

    amount_to_avg = amount / (avg_spend + 1e-5)
    features = np.array([[
        amount,
        amount_to_avg,
        drain_ratio,
        hour,
        tx_count_10m,
        1 if is_new_device else 0,
        velocity_kmh,
        inter_arrival_sec
    ]])

    scaled_features = scaler.transform(features)
    risk_score = float(model.predict_proba(scaled_features)[0][1])

    if is_new_device and drain_ratio > 0.7:
        risk_score = max(risk_score, 0.92)

    if risk_score > 0.70:
        status = "BLOCKED_FRAUD"
    elif risk_score > 0.35:
        status = "STEP_UP_CHALLENGE"
    else:
        status = "APPROVED"

    return {
        "status": status,
        "score": risk_score,
        "drain_ratio": drain_ratio,
        "amount_to_avg": amount_to_avg
    }

# ==========================================
# 4. STREAMLIT DUAL-TAB UI
# ==========================================
st.title("Intelligent UPI Fraud Mitigation Engine")
st.markdown("**Hybrid Telemetry Firewall + Random Forest Behavioral Classifier**")

tab1, tab2 = st.tabs(["Production Simulator (Automated Mock)", "Viva Evaluation (Manual Testing)"])

# -------------------------------------------------------------
# TAB 1: PRODUCTION SIMULATOR
# -------------------------------------------------------------
with tab1:
    col_user, col_threat = st.columns([1, 1])
    with col_user:
        selected_persona_name = st.selectbox("Select Active User Account:", list(USER_PERSONAS.keys()))
        persona = USER_PERSONAS[selected_persona_name]
        st.info(f"**Account Holder:** {persona['name']} | **Balance:** ₹{persona['balance']:,.2f} | **Avg Spend:** ₹{persona['avg_spend']:,.2f}")

    with col_threat:
        st.markdown("**Simulated Environmental Threat Vectors:**")
        active_call = st.checkbox("Active Phone Call with Unknown Number Detected", value=False)
        link_opened = st.checkbox("Payment Triggered via External Link (SMS / Telegram / WhatsApp)", value=False)

    if active_call or link_opened:
        st.warning(
            "⚠️ **Digital Arrest / Phishing Warning:** Legitimate enforcement, banks, and courier agencies never demand money transfers over a phone call or chat link. Do NOT enter your UPI PIN if instructed by an unknown caller."
        )

    st.markdown("---")
    st.subheader("Select a Payment Scenario to Test (Simulated QR Code)")

    qr_col1, qr_col2, qr_col3 = st.columns(3)
    preset_tx = None

    with qr_col1:
        st.markdown("☕ **Local Chai & Breakfast**")
        st.caption("P2M Micro-payment")
        if st.button("Pay ₹40 to `chaipoint@upi`"):
            preset_tx = {"amount": 40.0, "receiver": "chaipoint@upi", "velocity": 5.0}

    with qr_col2:
        st.markdown("🛍️ **Festival Clothing Store**")
        st.caption("Festival In-Store Purchase")
        if st.button("Pay ₹8,500 to `ethnicwear@okhdfc`"):
            preset_tx = {"amount": 8500.0, "receiver": "ethnicwear@okhdfc", "velocity": 15.0}

    with qr_col3:
        st.markdown("⚠️ **Emergency Transfer / Unknown Account**")
        st.caption("High-Value Drain Vector")
        if st.button("Pay ₹78,000 to `secure_escrow_agent@ybl`"):
            preset_tx = {"amount": 78000.0, "receiver": "secure_escrow_agent@ybl", "velocity": 900.0}

    if preset_tx:
        current_hour = datetime.now().hour
        result = evaluate_transaction(
            amount=preset_tx['amount'],
            balance=persona['balance'],
            avg_spend=persona['avg_spend'],
            hour=current_hour,
            tx_count_10m=persona['tx_count_10m'],
            is_new_device=not persona['trusted_device'],
            velocity_kmh=preset_tx['velocity'],
            inter_arrival_sec=persona['last_tx_time_gap']
        )

        st.markdown("### Transaction Authorization Result")
        score = result['score']

        if result['status'] == "APPROVED":
            st.success(f"Payment Authorized: ₹{preset_tx['amount']:,.2f} to {preset_tx['receiver']}. Risk Score: {score*100:.1f}%")
        elif result['status'] == "STEP_UP_CHALLENGE":
            st.warning(f"Step-Up Authentication Required. Risk Score: {score*100:.1f}%. Biometric verification required due to unusual spending ratio.")
        else:
            st.error(f"Transaction Blocked: High Fraud Probability ({score*100:.1f}%). Account safety lock engaged.")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Risk Score", f"{score*100:.1f}%")
        m2.metric("Drain Ratio", f"{(preset_tx['amount']/persona['balance'])*100:.1f}%")
        m3.metric("Spend vs Avg", f"{(preset_tx['amount']/persona['avg_spend']):.1f}x")
        m4.metric("Device State", "Untrusted Device" if not persona['trusted_device'] else "Trusted Device")

        if score > 0.70 or active_call:
            st.markdown("---")
            st.error("🚨 **Incident Mitigation & Cyber-Response Suite**")
            inc_col1, inc_col2 = st.columns([1, 1])
            with inc_col1:
                st.markdown("**Emergency Assistance:**")
                st.markdown("📞 **National Cyber Crime Helpline:** Dial **1930** immediately.")
                st.markdown("🌐 **Official Reporting Portal:** [cybercrime.gov.in](https://cybercrime.gov.in)")
                if st.button("Simulate Emergency NPCI Freeze on Receiver Account"):
                    st.success("Automated Request Dispatched to NPCI Central Switch: Lien requested on beneficiary account.")

            with inc_col2:
                st.markdown("**Official Bank Dispute Documentation:**")
                report_content = f"""OFFICIAL INCIDENT REPORT - ELECTRONIC PAYMENT DISPUTE
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Reference UTR: 429184{int(time.time())%1000000:06d}
Beneficiary UPI VPA: {preset_tx['receiver']}
Transaction Amount: INR {preset_tx['amount']}
Risk Probability: {score*100:.2f}%
Originating Account: {persona['name']}
Flagged Vectors: Drain Ratio: {(preset_tx['amount']/persona['balance']):.2f}, Spikes: {(preset_tx['amount']/persona['avg_spend']):.1f}x
Declaration: Filed under RBI Circular on Customer Protection - Limiting Liability in Unauthorized Electronic Banking Transactions.
"""
                st.download_button(
                    label="Download Official Bank Incident Report (.txt)",
                    data=report_content,
                    file_name=f"UPI_Fraud_Report_{int(time.time())}.txt",
                    mime="text/plain"
                )

# -------------------------------------------------------------
# TAB 2: VIVA EVALUATION (MANUAL INPUTS)
# -------------------------------------------------------------
with tab2:
    st.subheader("Manual Parameter Verification (Viva Testing)")
    st.caption("Directly adjust mathematical features to evaluate the Random Forest model and rule engine.")

    v_col1, v_col2 = st.columns(2)
    with v_col1:
        v_amount = st.number_input("Transaction Amount (₹)", min_value=1.0, value=25000.0, step=500.0)
        v_balance = st.number_input("Account Balance (₹)", min_value=1.0, value=30000.0, step=1000.0)
        v_avg_spend = st.number_input("Historical Average Spend (₹)", min_value=1.0, value=400.0, step=50.0)
        v_hour = st.slider("Hour of Day (24-Hour Clock)", 0, 23, 2)

    with v_col2:
        v_tx_10m = st.number_input("Transactions in Last 10 Minutes (Frequency)", min_value=0, max_value=10, value=4)
        v_new_device = st.selectbox("Device Status", options=["Trusted Device (0)", "Unrecognized/New Device (1)"]) == "Unrecognized/New Device (1)"
        v_velocity = st.number_input("Calculated Geo-Velocity (km/h)", min_value=0.0, value=650.0, step=50.0)
        v_inter_arrival = st.number_input("Inter-arrival Time (seconds since last tx)", min_value=0.1, value=0.8, step=0.5)

    if st.button("Evaluate Transaction Parameters"):
        v_result = evaluate_transaction(
            amount=v_amount,
            balance=v_balance,
            avg_spend=v_avg_spend,
            hour=v_hour,
            tx_count_10m=v_tx_10m,
            is_new_device=v_new_device,
            velocity_kmh=v_velocity,
            inter_arrival_sec=v_inter_arrival
        )

        v_score = v_result['score']
        st.markdown("### Model Verdict")
        if v_result['status'] == "APPROVED":
            st.success(f"Status: APPROVED | Fraud Probability: {v_score*100:.2f}%")
        elif v_result['status'] == "STEP_UP_CHALLENGE":
            st.warning(f"Status: STEP-UP CHALLENGE | Fraud Probability: {v_score*100:.2f}%")
        else:
            st.error(f"Status: BLOCKED / FRAUD | Fraud Probability: {v_score*100:.2f}%")

        st.json({
            "Risk Score": f"{v_score*100:.2f}%",
            "Account Drain Ratio": f"{v_result.get('drain_ratio', 0)*100:.2f}%",
            "Amount vs Average Multiplier": f"{v_result.get('amount_to_avg', 0):.2f}x",
            "Engine Decision": v_result['status']
        })
