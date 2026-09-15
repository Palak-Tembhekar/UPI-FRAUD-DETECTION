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
# 3. SEQUENTIAL MULTI-FACTOR INVESTIGATION
# ==========================================
def investigate_transaction(amount, balance, avg_spend, hour_24, tx_count_10m, is_new_device, is_new_payee, distance_km, time_gap_sec):
    investigation_log = []
    anomaly_flags = []
    
    # -------------------------------------------------------------
    # STAGE 1: DETERMINISTIC PRE-CHECKS
    # -------------------------------------------------------------
    if amount <= 0:
        return {
            "tier": "REJECTED",
            "status": "INVALID_AMOUNT",
            "score": 1.0,
            "reason": "Amount must be strictly positive.",
            "log": ["STAGE 1: Failed. Non-positive transaction value."],
            "drain_ratio": 0, "amount_to_avg": 0, "speed_kmh": 0
        }

    if amount > balance:
        return {
            "tier": "REJECTED",
            "status": "INSUFFICIENT_FUNDS",
            "score": 1.0,
            "reason": f"Declined: Requested amount (₹{amount:,.2f}) exceeds available balance (₹{balance:,.2f}).",
            "log": ["STAGE 1: Failed. Transaction amount exceeds available liquidity."],
            "drain_ratio": amount / (balance + 1e-5), "amount_to_avg": amount / (avg_spend + 1e-5), "speed_kmh": 0
        }

    if time_gap_sec < 1.0 and tx_count_10m <= 1:
        return {
            "tier": "TIER_1_PASS",
            "status": "DEDUPLICATED",
            "score": 0.03,
            "reason": "Hardware lag deduplicated. Single debit authorized.",
            "log": ["STAGE 1: Cleared. Idempotency deduplication engaged for rapid repeat click."],
            "drain_ratio": amount / (balance + 1e-5), "amount_to_avg": amount / (avg_spend + 1e-5), "speed_kmh": 0
        }

    investigation_log.append("STAGE 1: Deterministic parameters validated (Funds available, positive value, non-duplicate).")

    # Derived Metrics
    drain_ratio = float(amount) / (float(balance) + 1e-5)
    amount_to_avg = float(amount) / (float(avg_spend) + 1e-5)
    hours_elapsed = max(float(time_gap_sec) / 3600.0, 0.0001)
    speed_kmh = float(distance_km) / hours_elapsed

    # -------------------------------------------------------------
    # STAGE 2: KINEMATIC & GEO-VELOCITY AUDIT
    # -------------------------------------------------------------
    if speed_kmh > 300.0 and distance_km > 20.0:
        investigation_log.append(f"STAGE 2 [ANOMALY]: Impossible transit velocity ({speed_kmh:,.0f} km/h over {distance_km:.0f} km).")
        anomaly_flags.append("IMPOSSIBLE_SPEED")
    else:
        investigation_log.append(f"STAGE 2: Geo-velocity cleared ({speed_kmh:,.1f} km/h - physically feasible).")

    # -------------------------------------------------------------
    # STAGE 3: BEHAVIORAL LIQUIDITY DRAIN AUDIT
    # -------------------------------------------------------------
    if drain_ratio > 0.70:
        investigation_log.append(f"STAGE 3 [ANOMALY]: High account drain ({drain_ratio*100:.1f}% of total balance).")
        anomaly_flags.append("HIGH_DRAIN")
    else:
        investigation_log.append(f"STAGE 3: Drain ratio within normal threshold ({drain_ratio*100:.1f}%).")

    # -------------------------------------------------------------
    # STAGE 4: HISTORICAL SPEND BASELINE AUDIT
    # -------------------------------------------------------------
    if amount_to_avg > 4.0:
        investigation_log.append(f"STAGE 4 [ANOMALY]: Spending surge ({amount_to_avg:.1f}x historical average).")
        anomaly_flags.append("SURGE_MULTIPLIER")
    else:
        investigation_log.append(f"STAGE 4: Spend surge within standard deviation ({amount_to_avg:.1f}x average).")

    # -------------------------------------------------------------
    # STAGE 5: HARDWARE TOKEN & IDENTITY AUDIT
    # -------------------------------------------------------------
    if is_new_device:
        investigation_log.append("STAGE 5 [ANOMALY]: Device token mismatch (Unrecognized / New hardware).")
        anomaly_flags.append("NEW_DEVICE")
    else:
        investigation_log.append("STAGE 5: Authenticated on registered trusted hardware token.")

    # -------------------------------------------------------------
    # STAGE 6: TEMPORAL & BENEFICIARY PROXIMITY AUDIT
    # -------------------------------------------------------------
    temporal_flag = hour_24 in [0, 1, 2, 3, 4, 23]
    if temporal_flag:
        investigation_log.append(f"STAGE 6: Off-hour transaction ({hour_24:02d}:00 hrs).")
    else:
        investigation_log.append(f"STAGE 6: Standard daylight banking window ({hour_24:02d}:00 hrs).")

    if is_new_payee:
        investigation_log.append("STAGE 6 [CONTEXT]: Recipient is an unverified / first-time beneficiary.")
        anomaly_flags.append("NEW_PAYEE")
    else:
        investigation_log.append("STAGE 6 [CONTEXT]: Recipient is an established frequent contact.")

    # -------------------------------------------------------------
    # STAGE 7: SYNTHESIS & ML CORRELATION
    # -------------------------------------------------------------
    n_expected = getattr(scaler, "n_features_in_", 8)
    if n_expected == 8:
        features = np.array([[amount, amount_to_avg, drain_ratio, hour_24, tx_count_10m, 1 if is_new_device else 0, speed_kmh, time_gap_sec]])
    else:
        features = np.array([[amount, amount_to_avg, drain_ratio, hour_24, tx_count_10m, 1 if is_new_device else 0, distance_km, speed_kmh, time_gap_sec]])

    scaled_feats = scaler.transform(features)
    rf_risk = float(model.predict_proba(scaled_feats)[0][1])

    # Multi-Factor Score Synthesis
    score = rf_risk
    if "IMPOSSIBLE_SPEED" in anomaly_flags:
        score = max(score, 0.99)
    if "HIGH_DRAIN" in anomaly_flags and "NEW_DEVICE" in anomaly_flags:
        score = max(score, 0.95)
    if "NEW_DEVICE" in anomaly_flags and "NEW_PAYEE" in anomaly_flags and temporal_flag:
        score = max(score, 0.91)

    # Contextual Damping: Trusted device and known contact temper false positives
    if not is_new_device and not is_new_payee:
        score = min(score, 0.65)

    score = min(score, 0.99)
    investigation_log.append(f"STAGE 7: Cross-vector synthesis complete. Correlated score: {score*100:.1f}%.")

    # -------------------------------------------------------------
    # DECISION ARBITRATION
    # -------------------------------------------------------------
    if score >= 0.90:
        tier = "TIER_3_COOLING"
        status = "CRITICAL_RISK_BLOCK"
        reason = f"CRITICAL FRAUD LOCK: Correlated anomalies detected across {len(anomaly_flags)} vectors ({', '.join(anomaly_flags)}). Transaction blocked to prevent total account loss."
    elif score >= 0.35 or len(anomaly_flags) >= 2:
        tier = "TIER_2_CHALLENGE"
        status = "SUSPICIOUS_PAYMENT_FROZEN"
        reason = f"SUSPICIOUS ACTIVITY: Multi-factor audit identified risk vectors ({', '.join(anomaly_flags) if anomaly_flags else 'Surge anomaly'}). Payment held for 2FA OTP verification."
    else:
        tier = "TIER_1_PASS"
        status = "INSTANT_APPROVAL"
        reason = "All 6 telemetry verification stages cleared. Transaction approved."

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
        st.markdown("**Financial & Recipient Parameters**")
        v_amount = st.number_input("Transaction Amount (₹)", min_value=1.0, value=float(prof['avg_spend'] * 2), step=100.0)
        v_balance = st.number_input("Account Balance (₹)", min_value=1.0, value=float(prof['balance']), step=500.0)
        v_avg_spend = st.number_input("Baseline Average Spend (₹)", min_value=1.0, value=float(prof['avg_spend']), step=50.0)
        v_payee_status = st.selectbox("Recipient Account History", ["Known / Frequent Contact (Previously Paid)", "New / Unverified Payee (First-Time Transfer)"]) == "New / Unverified Payee (First-Time Transfer)"

        st.markdown("**Time of Transaction (12-Hour Format)**")
        t_col1, t_col2, t_col3 = st.columns([1.2, 1.2, 1.2])
        with t_col1:
            hour_12 = st.selectbox("Hour", list(range(1, 13)), index=11, key="v_h")
        with t_col2:
            minute_val = st.selectbox("Minute", ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"], index=6, key="v_m")
        with t_col3:
            meridiem = st.radio("AM / PM", ["AM", "PM"], horizontal=True, index=0, key="v_ap")

        if meridiem == "AM":
            v_hour = 0 if hour_12 == 12 else hour_12
        else:
            v_hour = 12 if hour_12 == 12 else hour_12 + 12
            
        st.caption(f"Selected: **{hour_12}:{minute_val} {meridiem}** (24h Equivalent: **{v_hour:02d}:{minute_val}**)")

    with c2:
        st.markdown("**Behavioral & Hardware Telemetry**")
        v_dist = st.number_input("Distance from Last Transaction Location (km)", min_value=0.0, value=50.0, step=5.0)
        
        st.markdown("**Inter-Arrival Time Gap**")
        g1, g2 = st.columns([1, 1])
        with g1:
            g_val = st.number_input("Time Gap Value", min_value=0.1, value=30.0, step=1.0, key="v_gv")
        with g2:
            g_unit = st.selectbox("Unit", ["Minutes", "Seconds", "Hours"], index=0, key="v_gu")
        
        if g_unit == "Minutes":
            v_gap = g_val * 60.0
        elif g_unit == "Hours":
            v_gap = g_val * 3600.0
        else:
            v_gap = g_val

        v_tx_count = st.number_input("Transaction Count in Last 10 Minutes", min_value=0, max_value=10, value=1)
        v_device = st.selectbox("Device Token State", ["Trusted Device (Known)", "Unrecognized / New Device"], index=0) == "Unrecognized / New Device"

    if st.button("Run Full Investigation Pipeline", type="primary"):
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
            st.success(f"**STATUS: {res['status']}** | Risk Score: **{score*100:.2f}%**")
        elif tier == "TIER_2_CHALLENGE":
            st.warning(f"**STATUS: {res['status']}** | Risk Score: **{score*100:.2f}%**")
            st.info("⏸️ **Payment Frozen on Hold:** This transaction is held for safety. Enter the 4-digit SMS OTP to release funds.")
            
            otp_col1, otp_col2 = st.columns([1, 2])
            with otp_col1:
                entered_otp = st.text_input("Enter 4-digit Security OTP (Mock: 4921):", max_chars=4, key="v_otp")
            with otp_col2:
                st.write("")
                st.write("")
                if st.button("Submit OTP & Release Funds", key="v_sub_otp"):
                    if entered_otp == "4921":
                        st.success("✅ OTP Verified! Hold released. Payment processed successfully.")
                    else:
                        st.error("❌ Invalid OTP. Hold maintained.")
        else:
            st.error(f"**STATUS: {res['status']}** | Risk Score: **{score*100:.2f}%**")

        st.info(f"**Reason for Decision:** {res['reason']}")

        # Investigation Diagnostic Log
        with st.expander("🔍 Sequential Investigation Audit Trail", expanded=True):
            for log_entry in res.get('log', []):
                st.write(f"- {log_entry}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Drain Ratio", f"{res.get('drain_ratio', 0)*100:.1f}%")
        m2.metric("Surge Multiplier", f"{res.get('amount_to_avg', 0):.1f}x")
        m3.metric("Calculated Speed", f"{res.get('speed_kmh', 0):,.1f} km/h")
        m4.metric("Model Probability", f"{score*100:.1f}%")

        if tier in ["TIER_2_CHALLENGE", "TIER_3_COOLING", "REJECTED"]:
            st.markdown("---")
            st.markdown("### 🚨 Emergency Incident Response Suite")
            
            e1, e2, e3 = st.columns(3)
            with e1:
                st.markdown("**1. Cyber Crime Helpline**")
                st.markdown("Dial **1930** immediately.")
                st.link_button("National Cyber Crime Portal", "https://cybercrime.gov.in")

            with e2:
                st.markdown("**2. NPCI Central Switch Lien**")
                if st.button("Simulate Beneficiary Account Lien", key="viva_lien"):
                    st.success("Automated freeze signal dispatched to beneficiary bank switch.")

            with e3:
                st.markdown("**3. Bank Dispute Documentation**")
                v_in = st.session_state['viva_inputs']
                report_txt = f"""OFFICIAL FRAUD DISPUTE NOTICE - ELECTRONIC BANKING
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
UTR Reference: 429184{int(time.time())%1000000:06d}
Evaluated Amount: INR {v_in['amount']:,.2f}
Account Profile: {v_in['prof']}
Recipient Status: {v_in['payee_type']}
Risk Evaluation: {res['status']} (Risk Probability: {score*100:.2f}%)
Telemetry Reason: {res['reason']}
Statutory Basis: Filed under RBI Circular on Customer Protection - Limiting Liability in Unauthorized Electronic Transactions."""
                
                st.download_button(
                    label="Download Bank Dispute Report (.txt)",
                    data=report_txt,
                    file_name=f"Viva_Dispute_{int(time.time())}.txt",
                    key="viva_download"
                )

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
        s_payee_new = st.selectbox("Beneficiary History", ["Known / Frequently Paid Contact", "New / Unsaved Payee"], index=0) == "New / Unsaved Payee"

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
            st.write("2. Executing multi-stage forensic investigation...")
            
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

            st.write(f"3. Decision Engine Tier: **{b_res['tier']}** | Risk Score: **{b_res.get('score', 0)*100:.2f}%**")
            with st.expander("Backend Audit Trail", expanded=False):
                for l in b_res.get('log', []):
                    st.write(f"- {l}")

    if 'sim_res' in st.session_state:
        b_res = st.session_state['sim_res']
        sim_dt = st.session_state['sim_tx_details']
        
        st.markdown("---")
        if b_res['tier'] == "TIER_1_PASS":
            st.success(f"✅ **Payment Successful!** ₹{sim_dt['amount']:,.2f} transferred to `{sim_dt['payee']}`.")
        elif b_res['tier'] == "TIER_2_CHALLENGE":
            st.warning(f"⚠️ **Payment Frozen on Hold:** Unusual spending activity detected. An OTP challenge has been dispatched to verify authorization.")
            st.info(f"**Reason:** {b_res['reason']}")
            
            s_otp_col1, s_otp_col2 = st.columns([1, 2])
            with s_otp_col1:
                s_entered_otp = st.text_input("Enter 4-digit Security OTP (Mock: 4921):", max_chars=4, key="sim_otp")
            with s_otp_col2:
                st.write("")
                st.write("")
                if st.button("Submit OTP & Complete Payment", key="sim_sub_otp"):
                    if s_entered_otp == "4921":
                        st.success(f"✅ OTP Verified! Hold released. ₹{sim_dt['amount']:,.2f} sent to {sim_dt['payee']}.")
                    else:
                        st.error("❌ Invalid OTP. Payment remains frozen.")
        else:
            st.error(f"🚫 **Transaction Blocked by Bank Security:** {b_res['reason']}")
            st.info(f"🔔 **Security Alert Dispatched:** 'Attempted debit of ₹{sim_dt['amount']:,.2f} to {sim_dt['payee']} was blocked to protect your account.'")

            st.markdown("---")
            st.markdown("### 🚨 Immediate Incident Response Protocol")
            
            e1, e2, e3 = st.columns(3)
            with e1:
                st.markdown("**1. National Cyber Crime Desk**")
                st.markdown("Dial **1930** immediately.")
                st.link_button("National Cyber Portal", "https://cybercrime.gov.in")

            with e2:
                st.markdown("**2. Inter-Bank Switch Freeze**")
                if st.button("Request Recipient Account Lien", key="sim_lien"):
                    st.success("Automated lien dispatch transmitted to beneficiary bank switch.")

            with e3:
                st.markdown("**3. Bank Dispute Documentation**")
                report_text = f"""OFFICIAL FRAUD DISPUTE NOTICE - ELECTRONIC BANKING
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
UTR Number: 429184{int(time.time())%1000000:06d}
Beneficiary VPA: {sim_dt['payee']}
Attempted Amount: INR {sim_dt['amount']:,.2f}
Originating Profile: {sim_dt['prof']}
Decision Flag: {b_res['status']}
Reason: {b_res['reason']}
Statutory Basis: Filed under RBI Circular on Limiting Customer Liability in Unauthorized Electronic Banking Transactions (Zero-Liability Framework)."""
                
                st.download_button(
                    label="Download Bank Dispute Report (.txt)",
                    data=report_text,
                    file_name=f"Bank_Dispute_{int(time.time())}.txt",
                    key="sim_download"
                )
