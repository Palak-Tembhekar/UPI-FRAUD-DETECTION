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
# 2. PROFILES
# ==========================================
PROFESSIONS = {
    "College Student": {"balance": 3500.0, "avg_spend": 120.0},
    "Salaried Employee": {"balance": 65000.0, "avg_spend": 750.0},
    "Small Retailer / Kirana": {"balance": 180000.0, "avg_spend": 8500.0},
    "Wholesale Merchant / SME": {"balance": 750000.0, "avg_spend": 38000.0},
    "Other (Custom Profile)": {"balance": 25000.0, "avg_spend": 1500.0}
}

# ==========================================
# 3. SEQUENTIAL INVESTIGATION PIPELINE
# ==========================================
def investigate_transaction(amount, balance, avg_spend, hour_24, tx_count_10m, is_new_device, is_new_payee, distance_km, time_gap_sec):
    investigation_log = []
    anomaly_flags = []
    
    # 1. Deterministic Checks
    if amount <= 0:
        return {
            "tier": "REJECTED", "status": "INVALID_AMOUNT", "score": 1.0,
            "reason": "Amount must be greater than zero.",
            "log": ["Check 1: Failed. Amount must be positive."],
            "drain_ratio": 0, "amount_to_avg": 0, "speed_kmh": 0
        }

    if amount > balance:
        return {
            "tier": "REJECTED", "status": "INSUFFICIENT_FUNDS", "score": 1.0,
            "reason": f"Declined: Entered amount (₹{amount:,.2f}) is higher than your balance (₹{balance:,.2f}).",
            "log": ["Check 1: Failed. Not enough balance in account."],
            "drain_ratio": amount / (balance + 1e-5), "amount_to_avg": amount / (avg_spend + 1e-5), "speed_kmh": 0
        }

    if time_gap_sec < 1.0 and tx_count_10m <= 1:
        return {
            "tier": "TIER_1_PASS", "status": "DEDUPLICATED", "score": 0.03,
            "reason": "Accidental double-click filtered. You will be charged only once.",
            "log": ["Check 1: Passed. Duplicate tap filtered."],
            "drain_ratio": amount / (balance + 1e-5), "amount_to_avg": amount / (avg_spend + 1e-5), "speed_kmh": 0
        }

    investigation_log.append("Check 1: Balance & basics OK (Sufficient funds, positive amount).")

    # Metrics
    drain_ratio = float(amount) / (float(balance) + 1e-5)
    amount_to_avg = float(amount) / (float(avg_spend) + 1e-5)
    hours_elapsed = max(float(time_gap_sec) / 3600.0, 0.0001)
    speed_kmh = float(distance_km) / hours_elapsed

    # 2. Speed Check
    if speed_kmh > 300.0 and distance_km > 20.0:
        investigation_log.append(f"Check 2: Speed ALERT ({speed_kmh:,.0f} km/h). Impossible to travel {distance_km:.0f} km this fast.")
        anomaly_flags.append("IMPOSSIBLE_SPEED")
    else:
        investigation_log.append(f"Check 2: Speed OK ({speed_kmh:,.0f} km/h - normal travel).")

    # 3. Account Drain Check
    if drain_ratio > 0.65:
        investigation_log.append(f"Check 3: Drain ALERT (Attempting to spend {drain_ratio*100:.1f}% of total balance).")
        anomaly_flags.append("HIGH_DRAIN")
    else:
        investigation_log.append(f"Check 3: Drain OK ({drain_ratio*100:.1f}% of balance).")

    # 4. Spending Habit Check
    if amount_to_avg > 3.5:
        investigation_log.append(f"Check 4: Spending Spike ({amount_to_avg:.1f}x higher than your usual average).")
        anomaly_flags.append("SPENDING_SPIKE")
    else:
        investigation_log.append(f"Check 4: Spending Normal ({amount_to_avg:.1f}x of usual average).")

    # 5. Device Token Check
    if is_new_device:
        investigation_log.append("Check 5: Device ALERT (Payment from a new or unrecognized phone).")
        anomaly_flags.append("NEW_DEVICE")
    else:
        investigation_log.append("Check 5: Device OK (Recognized trusted phone).")

    # 6. Time & Payee Check
    off_hours = hour_24 in [0, 1, 2, 3, 4, 23]
    if off_hours:
        investigation_log.append(f"Check 6: Timing Notice (Late night transaction at {hour_24:02d}:00 hrs).")
        anomaly_flags.append("OFF_HOURS")
    else:
        investigation_log.append(f"Check 6: Timing OK (Daytime transaction at {hour_24:02d}:00 hrs).")

    if is_new_payee:
        investigation_log.append("Check 6: Payee Notice (First-time payment to this person).")
        anomaly_flags.append("NEW_PAYEE")
    else:
        investigation_log.append("Check 6: Payee OK (Known contact you paid before).")

    # 7. Model Inference & Exact Score Harmonization
    n_expected = getattr(scaler, "n_features_in_", 8)
    if n_expected == 8:
        features = np.array([[amount, amount_to_avg, drain_ratio, hour_24, tx_count_10m, 1 if is_new_device else 0, speed_kmh, time_gap_sec]])
    else:
        features = np.array([[amount, amount_to_avg, drain_ratio, hour_24, tx_count_10m, 1 if is_new_device else 0, distance_km, speed_kmh, time_gap_sec]])

    scaled_feats = scaler.transform(features)
    rf_risk = float(model.predict_proba(scaled_feats)[0][1])

    # Dynamic Synthesis: Never leave suspicious actions at 0%
    score = rf_risk
    if "IMPOSSIBLE_SPEED" in anomaly_flags:
        score = 0.99
    elif "HIGH_DRAIN" in anomaly_flags and "NEW_DEVICE" in anomaly_flags:
        score = 0.96
    elif len(anomaly_flags) >= 3:
        score = max(score, 0.72)
    elif len(anomaly_flags) == 2:
        score = max(score, 0.52)
    elif len(anomaly_flags) == 1 and ("HIGH_DRAIN" in anomaly_flags or "SPENDING_SPIKE" in anomaly_flags):
        score = max(score, 0.42)
    else:
        score = max(score, 0.05)

    if not is_new_device and not is_new_payee:
        score = min(score, 0.55)

    score = min(score, 0.99)
    investigation_log.append(f"Summary: Evaluation complete. Final Risk Score: {score*100:.1f}%.")

    # Arbitration
    if score >= 0.90:
        tier = "TIER_3_COOLING"
        status = "CRITICAL_RISK_BLOCK"
        reason = f"Payment Blocked: High risk detected across multiple checks ({', '.join(anomaly_flags)}). Transaction stopped to safeguard your balance."
    elif score >= 0.35 or len(anomaly_flags) >= 1:
        tier = "TIER_2_CHALLENGE"
        status = "SUSPICIOUS_PAYMENT_FROZEN"
        reason = f"Suspicious Activity Detected: Triggered by ({', '.join(anomaly_flags)}). Payment temporarily frozen pending OTP verification."
    else:
        tier = "TIER_1_PASS"
        status = "INSTANT_APPROVAL"
        reason = "All checks cleared safely. Payment approved."

    return {
        "tier": tier,
        "status": status,
        "score": score,
        "drain_ratio": drain_ratio,
        "amount_to_avg": amount_to_avg,
        "speed_kmh": speed_kmh,
        "reason": reason,
        "log": investigation_log,
        "flags": anomaly_flags
    }

# ==========================================
# 4. STREAMLIT DUAL-TAB UI
# ==========================================
st.title("Intelligent UPI Fraud Mitigation Engine")
st.markdown("**Pre-ML Rules + Behavioral Random Forest + Adaptive Mitigation**")

tab_viva, tab_sim = st.tabs(["Viva Manual Evaluation", "Production App Simulator"])

# -------------------------------------------------------------
# TAB 1: VIVA MANUAL EVALUATION
# -------------------------------------------------------------
with tab_viva:
    st.subheader("Manual Testing Panel")
    
    sel_prof = st.selectbox("Select Profession Profile:", list(PROFESSIONS.keys()))
    prof = PROFESSIONS[sel_prof]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Payment Details**")
        v_amount = st.number_input("Transaction Amount (₹)", min_value=1.0, value=float(prof['avg_spend'] * 2), step=100.0)
        v_balance = st.number_input("Account Balance (₹)", min_value=1.0, value=float(prof['balance']), step=500.0)
        v_avg_spend = st.number_input("Usual Average Spend (₹)", min_value=1.0, value=float(prof['avg_spend']), step=50.0)
        v_payee_status = st.selectbox("Payee History", ["Known / Frequently Paid Contact", "New / Unverified Payee"]) == "New / Unverified Payee"

        st.markdown("**Time of Transaction**")
        t1, t2, t3 = st.columns([1.2, 1.2, 1.2])
        with t1:
            hour_12 = st.selectbox("Hour", list(range(1, 13)), index=11, key="v_h")
        with t2:
            minute_val = st.selectbox("Minute", ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"], index=6, key="v_m")
        with t3:
            meridiem = st.radio("AM / PM", ["AM", "PM"], horizontal=True, index=0, key="v_ap")

        if meridiem == "AM":
            v_hour = 0 if hour_12 == 12 else hour_12
        else:
            v_hour = 12 if hour_12 == 12 else hour_12 + 12
            
        st.caption(f"Selected Time: **{hour_12}:{minute_val} {meridiem}** (24h: {v_hour:02d}:{minute_val})")

    with c2:
        st.markdown("**Location & Phone Context**")
        v_dist = st.number_input("Distance from Last Transaction (km)", min_value=0.0, value=50.0, step=5.0)
        
        st.markdown("**Time Gap Since Last Payment**")
        g1, g2 = st.columns([1, 1])
        with g1:
            g_val = st.number_input("Value", min_value=0.1, value=30.0, step=1.0, key="v_gv")
        with g2:
            g_unit = st.selectbox("Unit", ["Minutes", "Seconds", "Hours"], index=0, key="v_gu")
        
        if g_unit == "Minutes":
            v_gap = g_val * 60.0
        elif g_unit == "Hours":
            v_gap = g_val * 3600.0
        else:
            v_gap = g_val

        v_tx_count = st.number_input("Number of Payments in Last 10 Mins", min_value=0, max_value=10, value=1)
        v_device = st.selectbox("Phone Used", ["Trusted Phone (Known)", "New / Unrecognized Phone"], index=0) == "New / Unrecognized Phone"

    if st.button("Run Verification Pipeline", type="primary"):
        st.session_state['viva_res'] = investigate_transaction(
            amount=v_amount,
            balance=v_balance,
            avg_spend=v_avg_spend,
            hour_24=v_hour,
            tx_count_10m=v_tx_count,
            is_new_device=v_device,
            is_new_payee=v_payee_status,
            distance_km=v_dist,
            time_gap_sec=v_gap
        )
        st.session_state['viva_inputs'] = {
            "amount": v_amount,
            "balance": v_balance,
            "avg_spend": v_avg_spend,
            "prof": sel_prof,
            "payee_type": "New Payee" if v_payee_status else "Known Payee"
        }

    if 'viva_res' in st.session_state:
        res = st.session_state['viva_res']
        tier = res['tier']
        score = res.get('score', 0.0)

        st.markdown("---")
        if tier == "TIER_1_PASS":
            st.success(f"**STATUS: {res['status']}** | Risk Score: **{score*100:.1f}%**")
        elif tier == "TIER_2_CHALLENGE":
            st.warning(f"**STATUS: {res['status']}** | Risk Score: **{score*100:.1f}%**")
            st.info("⏸️ **Payment Frozen:** Held for safety. Enter the 4-digit SMS OTP to approve.")
            
            otp_col1, otp_col2 = st.columns([1, 2])
            with otp_col1:
                entered_otp = st.text_input("Enter 4-digit OTP (Mock: 4921):", max_chars=4, key="v_otp")
            with otp_col2:
                st.write("")
                st.write("")
                if st.button("Verify OTP & Release Funds", key="v_sub_otp"):
                    if entered_otp == "4921":
                        st.success("✅ OTP Verified! Payment approved.")
                    else:
                        st.error("❌ Wrong OTP. Payment remains frozen.")
        else:
            st.error(f"**STATUS: {res['status']}** | Risk Score: **{score*100:.1f}%**")

        st.info(f"**Reason:** {res['reason']}")

        # Simplified Investigation Log
        with st.expander("🔍 Step-by-Step Security Investigation", expanded=True):
            for log_entry in res.get('log', []):
                st.write(f"- {log_entry}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Account Drain", f"{res.get('drain_ratio', 0)*100:.1f}%")
        m2.metric("Spike vs Average", f"{res.get('amount_to_avg', 0):.1f}x")
        m3.metric("Transit Speed", f"{res.get('speed_kmh', 0):,.0f} km/h")
        m4.metric("Risk Score", f"{score*100:.1f}%")

        if tier in ["TIER_2_CHALLENGE", "TIER_3_COOLING", "REJECTED"]:
            st.markdown("---")
            st.markdown("### 🚨 Emergency Response Actions")
            
            e1, e2, e3 = st.columns(3)
            with e1:
                st.markdown("**1. Cyber Police Helpline**")
                st.markdown("Call **1930** immediately.")
                st.link_button("cybercrime.gov.in", "https://cybercrime.gov.in")

            with e2:
                st.markdown("**2. Beneficiary Lock**")
                if st.button("Request Account Freeze", key="viva_lien"):
                    st.success("Freeze notice sent to beneficiary bank switch.")

            with e3:
                st.markdown("**3. Bank Dispute File**")
                v_in = st.session_state['viva_inputs']
                report_txt = f"""OFFICIAL FRAUD DISPUTE NOTICE
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
UTR Ref: 429184{int(time.time())%1000000:06d}
Amount: INR {v_in['amount']:,.2f}
Profile: {v_in['prof']}
Recipient: {v_in['payee_type']}
Verdict: {res['status']} (Risk: {score*100:.1f}%)
Reason: {res['reason']}
Statutory Basis: Filed under RBI Customer Protection Framework."""
                
                st.download_button(
                    label="Download Dispute Report (.txt)",
                    data=report_txt,
                    file_name=f"Dispute_Report_{int(time.time())}.txt",
                    key="viva_download"
                )

# -------------------------------------------------------------
# TAB 2: PRODUCTION APP SIMULATOR
# -------------------------------------------------------------
with tab_sim:
    st.subheader("Mobile Payment Simulator")

    sim_user_col, sim_env_col = st.columns([1, 1])
    with sim_user_col:
        s_prof_name = st.selectbox("Current User Profile:", list(PROFESSIONS.keys()), key="sim_user")
        s_user = PROFESSIONS[s_prof_name]
        st.markdown(f"**Balance:** `₹{s_user['balance']:,.2f}` | **Usual Spend:** `₹{s_user['avg_spend']:,.2f}`")

    with sim_env_col:
        st.markdown("**Live Threat Context**")
        sim_call = st.checkbox("Active Phone Call with Unknown Caller")
        sim_link = st.checkbox("Payment Opened from SMS / WhatsApp Link")

    st.markdown("---")
    
    mobile_col, backend_col = st.columns([1.2, 1])
    
    with mobile_col:
        st.markdown("#### 📱 UPI Checkout")
        payee = st.text_input("Receiver UPI ID", "chai_point@upi")
        pay_amount = st.number_input("Amount to Pay (₹)", min_value=1.0, value=40.0, step=10.0)
        s_payee_new = st.selectbox("Receiver Contact Type", ["Known / Frequently Paid Contact", "New / First-Time Receiver"], index=0) == "New / First-Time Receiver"

        is_threat = sim_call or sim_link
        proceed_permitted = True

        if is_threat:
            st.error("⚠️ **SCAM WARNING (Impersonation / Digital Arrest Risk)**")
            st.markdown(
                "> **Warning:** You are on an unknown call or link. "
                "Police, customs, and banks **NEVER** ask you to pay money to unblock accounts or avoid arrest."
            )
            confirm_override = st.checkbox("I know this receiver and want to proceed anyway.")
            proceed_permitted = confirm_override

        pay_clicked = st.button("Pay Now", type="primary", disabled=not proceed_permitted)

    with backend_col:
        st.markdown("#### ⚙️ Bank Backend Server")
        st.caption("Live checks running behind the scenes.")
        backend_status_box = st.empty()
        backend_status_box.info("Waiting for user to initiate payment...")

    if pay_clicked:
        with backend_status_box.container():
            st.write("1. Payment request received.")
            st.write("2. Running 6-point fraud verification...")
            
            dist_val = 500.0 if pay_amount > 20000 else 1.5
            gap_val = 1800.0 if pay_amount > 20000 else 2400.0
            burst_val = 4 if pay_amount > 20000 else 0
            new_dev_flag = True if pay_amount > 20000 else False

            b_res = investigate_transaction(
                amount=pay_amount,
                balance=s_user['balance'],
                avg_spend=s_user['avg_spend'],
                hour_24=datetime.now().hour,
                tx_count_10m=burst_val,
                is_new_device=new_dev_flag,
                is_new_payee=s_payee_new,
                distance_km=dist_val,
                time_gap_sec=gap_val
            )

            st.session_state['sim_res'] = b_res
            st.session_state['sim_tx_details'] = {"amount": pay_amount, "payee": payee, "prof": s_prof_name}

            st.write(f"3. Decision: **{b_res['tier']}** | Final Risk: **{b_res.get('score', 0)*100:.1f}%**")
            with st.expander("Backend Audit Trail", expanded=False):
                for l in b_res.get('log', []):
                    st.write(f"- {l}")

    if 'sim_res' in st.session_state:
        b_res = st.session_state['sim_res']
        sim_dt = st.session_state['sim_tx_details']
        
        st.markdown("---")
        if b_res['tier'] == "TIER_1_PASS":
            st.success(f"✅ **Payment Successful!** ₹{sim_dt['amount']:,.2f} sent to `{sim_dt['payee']}`.")
        elif b_res['tier'] == "TIER_2_CHALLENGE":
            st.warning(f"⚠️ **Payment Frozen on Hold:** Unusual activity detected. Enter the OTP sent to your phone.")
            st.info(f"**Reason:** {b_res['reason']}")
            
            s_otp_col1, s_otp_col2 = st.columns([1, 2])
            with s_otp_col1:
                s_entered_otp = st.text_input("Enter 4-digit OTP (Mock: 4921):", max_chars=4, key="sim_otp")
            with s_otp_col2:
                st.write("")
                st.write("")
                if st.button("Submit OTP & Complete Payment", key="sim_sub_otp"):
                    if s_entered_otp == "4921":
                        st.success(f"✅ OTP Verified! ₹{sim_dt['amount']:,.2f} transferred to {sim_dt['payee']}.")
                    else:
                        st.error("❌ Wrong OTP. Payment remains frozen.")
        else:
            st.error(f"🚫 **Payment Blocked by Bank Security:** {b_res['reason']}")
            st.info(f"🔔 **Security Notification:** 'Debit of ₹{sim_dt['amount']:,.2f} to {sim_dt['payee']} was blocked to protect your funds.'")

            st.markdown("---")
            st.markdown("### 🚨 Immediate Emergency Actions")
            
            e1, e2, e3 = st.columns(3)
            with e1:
                st.markdown("**1. Cyber Cell Helpline**")
                st.markdown("Call **1930** immediately.")
                st.link_button("cybercrime.gov.in", "https://cybercrime.gov.in")

            with e2:
                st.markdown("**2. Account Freeze**")
                if st.button("Freeze Beneficiary Account", key="sim_lien"):
                    st.success("Lien request sent to beneficiary bank switch.")

            with e3:
                st.markdown("**3. Bank Dispute Notice**")
                report_text = f"""OFFICIAL FRAUD DISPUTE NOTICE
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
UTR Number: 429184{int(time.time())%1000000:06d}
Beneficiary: {sim_dt['payee']}
Amount: INR {sim_dt['amount']:,.2f}
Profile: {sim_dt['prof']}
Verdict: {b_res['status']}
Reason: {b_res['reason']}
Statutory Basis: Filed under RBI Zero-Liability Framework."""
                
                st.download_button(
                    label="Download Dispute Report (.txt)",
                    data=report_text,
                    file_name=f"Dispute_Report_{int(time.time())}.txt",
                    key="sim_download"
                )
