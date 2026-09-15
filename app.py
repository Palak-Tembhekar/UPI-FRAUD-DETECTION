import streamlit as st
import numpy as np
import pandas as pd
import pickle
import os
import time
from datetime import datetime

st.set_page_config(page_title="Intelligent UPI Fraud Mitigation Engine", page_icon="🛡️", layout="wide")

# ==========================================
# 1. LOAD ARTIFACTS
# ==========================================
@st.cache_resource
def load_artifacts():
    model_name = 'upi_fraud_model (3).pkl' if os.path.exists('upi_fraud_model (3).pkl') else 'upi_fraud_model.pkl'
    scaler_name = 'scaler (3).pkl' if os.path.exists('scaler (3).pkl') else 'scaler.pkl'
    with open(model_name, 'rb') as f:
        model = pickle.load(f)
    with open(scaler_name, 'rb') as f:
        scaler = pickle.load(f)
    return model, scaler

model, scaler = load_artifacts()

# ==========================================
# 2. AUTO-CALIBRATING PROFILES
# ==========================================
PROFESSIONS = {
    "College Student": {"balance": 3500.0, "avg_spend": 120.0},
    "Salaried Employee": {"balance": 65000.0, "avg_spend": 750.0},
    "Small Retailer / Kirana": {"balance": 180000.0, "avg_spend": 8500.0},
    "Wholesale Merchant / SME": {"balance": 750000.0, "avg_spend": 38000.0},
    "Other (Custom Profile)": {"balance": 25000.0, "avg_spend": 1500.0}
}

# ==========================================
# 3. 3-STAGE HYBRID BACKEND ENGINE
# ==========================================
def evaluate_transaction_backend(amount, balance, avg_spend, hour_24, tx_count_10m, is_new_device, distance_km, time_gap_sec):
    # Calculate fundamental metrics
    drain_ratio = float(amount) / (float(balance) + 1e-5)
    amount_to_avg = float(amount) / (float(avg_spend) + 1e-5)
    
    # Safe calculation of speed in km/h
    hours_elapsed = max(float(time_gap_sec) / 3600.0, 0.0001)
    speed_kmh = float(distance_km) / hours_elapsed

    # -------------------------------------------------------------
    # LAYER 1: DETERMINISTIC PRE-ML FIREWALL (STRICT ENFORCEMENT)
    # -------------------------------------------------------------
    if amount <= 0:
        return {"tier": "REJECTED", "status": "INVALID_AMOUNT", "score": 1.0, "reason": "Amount must be strictly positive.", "drain_ratio": 0, "amount_to_avg": 0, "speed_kmh": 0}

    if amount > balance:
        return {"tier": "REJECTED", "status": "INSUFFICIENT_FUNDS", "score": 1.0, "reason": f"Amount (₹{amount:,.2f}) exceeds current balance (₹{balance:,.2f}).", "drain_ratio": drain_ratio, "amount_to_avg": amount_to_avg, "speed_kmh": speed_kmh}

    # Deduplication check
    if time_gap_sec < 1.0 and tx_count_10m <= 1:
        return {"tier": "TIER_1_PASS", "status": "DEDUPLICATED", "score": 0.03, "reason": "Rapid multi-click filtered (Hardware lag). Single charge permitted.", "drain_ratio": drain_ratio, "amount_to_avg": amount_to_avg, "speed_kmh": speed_kmh}

    # Impossible Travel Speed (Anything over 250 km/h is physically impossible by road/train)
    if speed_kmh > 250.0 and distance_km > 20.0:
        return {
            "tier": "TIER_3_COOLING",
            "status": "IMPOSSIBLE_GEO_VELOCITY",
            "score": 0.99,
            "drain_ratio": drain_ratio,
            "amount_to_avg": amount_to_avg,
            "speed_kmh": speed_kmh,
            "reason": f"CRITICAL: Impossible travel speed ({speed_kmh:,.0f} km/h). {distance_km:.0f} km in {hours_elapsed*60:.0f} mins indicates severe geo-spoofing or account theft."
        }

    # Severe Account Drain + New Device
    if is_new_device and drain_ratio > 0.65:
        return {
            "tier": "TIER_3_COOLING",
            "status": "CRITICAL_ACCOUNT_DRAIN",
            "score": 0.98,
            "drain_ratio": drain_ratio,
            "amount_to_avg": amount_to_avg,
            "speed_kmh": speed_kmh,
            "reason": f"CRITICAL: Unrecognized device attempting to drain {drain_ratio*100:.1f}% of total account balance."
        }

    # -------------------------------------------------------------
    # LAYER 2: RANDOM FOREST ML INFERENCE
    # -------------------------------------------------------------
    n_expected = getattr(scaler, "n_features_in_", 8)
    if n_expected == 8:
        features = np.array([[
            amount,
            amount_to_avg,
            drain_ratio,
            hour_24,
            tx_count_10m,
            1 if is_new_device else 0,
            speed_kmh,
            time_gap_sec
        ]])
    else:
        features = np.array([[
            amount,
            amount_to_avg,
            drain_ratio,
            hour_24,
            tx_count_10m,
            1 if is_new_device else 0,
            distance_km,
            speed_kmh,
            time_gap_sec
        ]])

    scaled_feats = scaler.transform(features)
    risk_score = float(model.predict_proba(scaled_feats)[0][1])

    # Dynamic Weight Calibration
    if is_new_device:
        risk_score += 0.25
    if hour_24 in [0, 1, 2, 3, 4, 23]:
        risk_score += 0.20
    if tx_count_10m >= 3:
        risk_score += 0.25
    if drain_ratio > 0.60:
        risk_score += 0.25

    risk_score = min(risk_score, 0.99)

    # -------------------------------------------------------------
    # LAYER 3: ADAPTIVE MITIGATION POLICY
    # -------------------------------------------------------------
    if risk_score >= 0.60:
        tier = "TIER_3_COOLING"
        status = "CRITICAL_RISK_BLOCK"
        reason = f"High fraud risk ({risk_score*100:.1f}%). Multi-vector anomaly flagged: Off-hours + high drain ratio + device anomaly."
    elif risk_score >= 0.30:
        tier = "TIER_2_CHALLENGE"
        status = "STEP_UP_2FA"
        reason = f"Moderate suspicion ({risk_score*100:.1f}%). Spending surge ({amount_to_avg:.1f}x baseline) requires 2FA confirmation."
    else:
        tier = "TIER_1_PASS"
        status = "INSTANT_APPROVAL"
        reason = "Normal behavioral telemetry. Transaction cleared."

    return {
        "tier": tier,
        "status": status,
        "score": risk_score,
        "drain_ratio": drain_ratio,
        "amount_to_avg": amount_to_avg,
        "speed_kmh": speed_kmh,
        "reason": reason
    }

# ==========================================
# 4. STREAMLIT DUAL-TAB UI
# ==========================================
st.title("Intelligent UPI Fraud Mitigation Engine")
st.markdown("**Deterministic Firewall + Behavioral Random Forest + Adaptive Mitigation**")

tab_viva, tab_sim = st.tabs(["Viva Manual Evaluation", "Production App Simulator"])

# -------------------------------------------------------------
# TAB 1: VIVA MANUAL EVALUATION
# -------------------------------------------------------------
with tab_viva:
    st.subheader("Manual Telemetry Verification")
    
    sel_prof = st.selectbox("Select Profession Profile:", list(PROFESSIONS.keys()))
    prof = PROFESSIONS[sel_prof]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Financial Parameters**")
        v_amount = st.number_input("Transaction Amount (₹)", min_value=1.0, value=float(prof['avg_spend'] * 2), step=100.0)
        v_balance = st.number_input("Account Balance (₹)", min_value=1.0, value=float(prof['balance']), step=500.0)
        v_avg_spend = st.number_input("Baseline Average Spend (₹)", min_value=1.0, value=float(prof['avg_spend']), step=50.0)
        
        st.markdown("**Time of Transaction (12-Hour Format)**")
        t_col1, t_col2, t_col3 = st.columns([1.2, 1.2, 1.2])
        with t_col1:
            hour_12 = st.selectbox("Hour", list(range(1, 13)), index=11)  # Default 12
        with t_col2:
            minute_val = st.selectbox("Minute", ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"], index=6)
        with t_col3:
            meridiem = st.radio("AM / PM", ["AM", "PM"], horizontal=True, index=0)  # Default AM

        # Exact 24-Hour Conversion: 12 AM is 0, 12 PM is 12
        if meridiem == "AM":
            v_hour = 0 if hour_12 == 12 else hour_12
        else:
            v_hour = 12 if hour_12 == 12 else hour_12 + 12
            
        st.caption(f"Selected: **{hour_12}:{minute_val} {meridiem}** (24h Equivalent: **{v_hour:02d}:{minute_val}**)")

    with c2:
        st.markdown("**Behavioral & Hardware Telemetry**")
        v_dist = st.number_input("Distance from Last Transaction Location (km)", min_value=0.0, value=400.0, step=10.0)
        
        st.markdown("**Inter-Arrival Time Gap**")
        g1, g2 = st.columns([1, 1])
        with g1:
            g_val = st.number_input("Time Gap Value", min_value=0.1, value=30.0, step=1.0)
        with g2:
            g_unit = st.selectbox("Unit", ["Minutes", "Seconds", "Hours"], index=0)
        
        # Rigorous conversion to seconds
        if g_unit == "Minutes":
            v_gap = g_val * 60.0
        elif g_unit == "Hours":
            v_gap = g_val * 3600.0
        else:
            v_gap = g_val

        v_tx_count = st.number_input("Transaction Count in Last 10 Minutes", min_value=0, max_value=10, value=3)
        v_device = st.selectbox("Device Token State", ["Unrecognized / New Device", "Trusted Device (Known)"], index=0) == "Unrecognized / New Device"

    if st.button("Run Verification Pipeline", type="primary"):
        res = evaluate_transaction_backend(
            amount=v_amount,
            balance=v_balance,
            avg_spend=v_avg_spend,
            hour_24=v_hour,
            tx_count_10m=v_tx_count,
            is_new_device=v_device,
            distance_km=v_dist,
            time_gap_sec=v_gap
        )

        st.markdown("---")
        tier = res['tier']
        score = res.get('score', 0.0)

        if tier == "TIER_1_PASS":
            st.success(f"**STATUS: {res['status']}** | Risk Score: **{score*100:.2f}%**")
        elif tier == "TIER_2_CHALLENGE":
            st.warning(f"**STATUS: {res['status']}** | Risk Score: **{score*100:.2f}%**")
        else:
            st.error(f"**STATUS: {res['status']}** | Risk Score: **{score*100:.2f}%**")

        st.info(f"**Engine Rationale:** {res['reason']}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Drain Ratio", f"{res.get('drain_ratio', 0)*100:.1f}%")
        m2.metric("Surge Multiplier", f"{res.get('amount_to_avg', 0):.1f}x")
        m3.metric("Calculated Speed", f"{res.get('speed_kmh', 0):,.1f} km/h")
        m4.metric("Model Probability", f"{score*100:.1f}%")

# -------------------------------------------------------------
# TAB 2: PRODUCTION APP SIMULATOR
# -------------------------------------------------------------
with tab_sim:
    st.subheader("Mobile Payment Simulation")

    sim_user_col, sim_env_col = st.columns([1, 1])
    with sim_user_col:
        s_prof_name = st.selectbox("Active Account Profile:", list(PROFESSIONS.keys()), key="sim_user")
        s_user = PROFESSIONS[s_prof_name]
        st.markdown(f"**Account Balance:** `₹{s_user['balance']:,.2f}` | **Normal Daily Spend:** `₹{s_user['avg_spend']:,.2f}`")

    with sim_env_col:
        st.markdown("**Simulated Context Flags**")
        sim_call = st.checkbox("Active Phone Call with Unknown Caller")
        sim_link = st.checkbox("App Opened via External Chat/SMS Link")

    st.markdown("---")
    
    mobile_col, backend_col = st.columns([1.2, 1])
    
    with mobile_col:
        st.markdown("#### 📱 UPI Checkout Interface")
        payee = st.text_input("Payee Virtual Payment Address (VPA)", "chai_point@upi")
        pay_amount = st.number_input("Enter Amount to Transfer (₹)", min_value=1.0, value=40.0, step=10.0)

        is_threat = sim_call or sim_link
        proceed_permitted = True

        if is_threat:
            st.error("⚠️ **CRITICAL PRE-PAYMENT WARNING (Potential Impersonation Scam)**")
            st.markdown(
                "> **CAUTION:** An active unknown phone call or external link is detected. "
                "Police, bank managers, and customs **NEVER** request money transfers over the phone."
            )
            confirm_override = st.checkbox("I verify this recipient personally and wish to proceed under my own discretion.")
            proceed_permitted = confirm_override

        pay_clicked = st.button("Authorize & Pay", type="primary", disabled=not proceed_permitted)

    with backend_col:
        st.markdown("#### ⚙️ Bank Switch Server (Backend)")
        st.caption("Live background inspection log invisible to the end-user.")
        backend_status_box = st.empty()
        backend_status_box.info("Awaiting payment initiation from client device...")

    if pay_clicked:
        with backend_status_box.container():
            st.write("1. Incoming payload received from mobile client.")
            st.write("2. Resolving account baseline and telemetry variables...")
            
            dist_val = 250.0 if pay_amount > 20000 else 1.5
            gap_val = 1.2 if pay_amount > 20000 else 2400.0
            burst_val = 4 if pay_amount > 20000 else 0
            new_dev_flag = True if pay_amount > 20000 else False

            b_res = evaluate_transaction_backend(
                amount=pay_amount,
                balance=s_user['balance'],
                avg_spend=s_user['avg_spend'],
                hour_24=datetime.now().hour,
                tx_count_10m=burst_val,
                is_new_device=new_dev_flag,
                distance_km=dist_val,
                time_gap_sec=gap_val
            )

            st.write(f"3. Decision Engine Tier: **{b_res['tier']}** | Risk Score: **{b_res.get('score', 0)*100:.2f}%**")
            st.json({
                "Firewall Rationale": b_res['reason'],
                "Calculated Drain": f"{b_res.get('drain_ratio', 0)*100:.1f}%",
                "Speed": f"{b_res.get('speed_kmh', 0):,.1f} km/h"
            })

        st.markdown("---")
        if b_res['tier'] == "TIER_1_PASS":
            st.success(f"✅ **Payment Successful!** ₹{pay_amount:,.2f} transferred to `{payee}`.")
        elif b_res['tier'] == "TIER_2_CHALLENGE":
            st.warning(f"⚠️ **Payment Paused for Step-Up Verification:** Unusual spending surge. Enter 6-digit biometric OTP sent to your registered SIM.")
        else:
            st.error(f"🚫 **Transaction Declined for Security:** Unusual activity detected. To protect your funds, ₹{pay_amount:,.2f} was not debited.")
            st.info(f"🔔 **Security Notification Dispatched:** 'Attempted debit of ₹{pay_amount:,.2f} to {payee} was intercepted by bank security.'")

            st.markdown("---")
            st.markdown("### 🚨 Immediate Incident Response Protocol")
            
            e1, e2, e3 = st.columns(3)
            with e1:
                st.markdown("**1. National Cyber Crime Desk**")
                st.markdown("Dial **1930** immediately.")
                st.link_button("National Cyber Portal", "https://cybercrime.gov.in")

            with e2:
                st.markdown("**2. Inter-Bank Switch Freeze**")
                if st.button("Request Recipient Account Lien"):
                    st.success("Automated lien dispatch transmitted to beneficiary bank switch.")

            with e3:
                st.markdown("**3. Bank Dispute Documentation**")
                report_text = f"""OFFICIAL FRAUD DISPUTE NOTICE - ELECTRONIC BANKING
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
UTR Number: 429184{int(time.time())%1000000:06d}
Beneficiary VPA: {payee}
Attempted Amount: INR {pay_amount:,.2f}
Originating Profile: {s_prof_name}
Decision Flag: {b_res['status']}
Telemetry Vectors: Spend Surge {b_res.get('amount_to_avg', 0):.1f}x, Drain Ratio {b_res.get('drain_ratio', 0)*100:.1f}%
Statutory Basis: Filed under RBI Circular on Limiting Customer Liability in Unauthorized Electronic Banking Transactions (Zero-Liability Framework)."""
                
                st.download_button(
                    label="Download Bank Dispute Report (.txt)",
                    data=report_text,
                    file_name=f"Bank_Dispute_{int(time.time())}.txt"
                )
