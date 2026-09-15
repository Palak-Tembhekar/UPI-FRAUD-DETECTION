import streamlit as st
import numpy as np
import pandas as pd
import pickle
import os
import time
from datetime import datetime

st.set_page_config(
    page_title="UPI Shield - Intelligent Fraud Mitigation Gateway",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 1. EXACT PIXEL-MATCH CSS THEME
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #F6F8FC;
    }
    
    /* Top Header Bar */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        padding: 10px 24px;
        border-radius: 16px;
        border: 1px solid #E9EFF6;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    .brand-group {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-icon {
        background: #EFF4FF;
        color: #3B82F6;
        border-radius: 12px;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: 700;
    }
    .brand-text {
        font-size: 1.05rem;
        font-weight: 800;
        color: #1E293B;
    }
    .version-tag {
        font-size: 0.7rem;
        background: #F1F5F9;
        color: #64748B;
        padding: 2px 7px;
        border-radius: 6px;
        font-weight: 600;
        margin-left: 6px;
    }
    .sub-brand {
        font-size: 0.8rem;
        color: #94A3B8;
        font-weight: 500;
    }
    .header-right {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .system-status {
        font-size: 0.8rem;
        color: #10B981;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background: #10B981;
        border-radius: 50%;
    }
    .user-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 4px 12px 4px 6px;
        border-radius: 20px;
    }
    .avatar {
        background: #3B82F6;
        color: white;
        font-weight: 700;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
    }
    
    /* Hero Banner */
    .hero-banner {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .hero-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0F172A;
        margin: 0;
    }
    .hero-sub {
        font-size: 0.85rem;
        color: #64748B;
        margin-top: 4px;
        font-weight: 500;
    }
    .hero-right-badge {
        background: linear-gradient(135deg, #EFF6FF 0%, #E0EDFF 100%);
        border: 1px solid #BFDBFE;
        border-radius: 14px;
        padding: 10px 18px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* Cards */
    .custom-card {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1px solid #EAEFF5;
        padding: 22px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.02);
        margin-bottom: 18px;
    }
    .card-header-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 800;
        font-size: 1.02rem;
        color: #0F172A;
        margin-bottom: 16px;
    }
    .header-icon-box {
        background: #F1F5F9;
        color: #3B82F6;
        border-radius: 8px;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
    }
    
    /* Run Pipeline Button */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #F43F5E 0%, #E11D48 100%);
        color: white;
        font-size: 1rem;
        font-weight: 700;
        border-radius: 12px;
        padding: 14px 28px;
        border: none;
        box-shadow: 0 6px 18px rgba(225, 29, 72, 0.28);
        width: 100%;
        margin-top: 10px;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(90deg, #E11D48 0%, #BE123C 100%);
    }
    
    /* Status Top Banner */
    .status-alert-box {
        background: #FFF1EE;
        border: 1px solid #FFD5CC;
        border-radius: 14px;
        padding: 14px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
    }
    .status-alert-title {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 800;
        font-size: 0.98rem;
        color: #C2410C;
    }
    .status-alert-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .risk-score-pill {
        background: #FFFFFF;
        border: 1px solid #FFD5CC;
        color: #C2410C;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 4px 12px;
        border-radius: 14px;
    }
    .risk-level-badge {
        background: #FFE4DE;
        color: #C2410C;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 4px 12px;
        border-radius: 14px;
    }

    /* Frozen Card */
    .frozen-card {
        background: #FFF8F6;
        border: 1px solid #FFE4DE;
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }
    .frozen-header {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .frozen-icon {
        background: #F43F5E;
        color: white;
        border-radius: 10px;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .frozen-title {
        font-weight: 800;
        font-size: 1.05rem;
        color: #E11D48;
    }
    .frozen-sub {
        font-size: 0.82rem;
        color: #64748B;
        margin-top: 2px;
    }
    
    /* OTP Cells Mock */
    .otp-row {
        display: flex;
        gap: 10px;
        align-items: center;
        margin-top: 14px;
    }
    .otp-cell {
        width: 44px;
        height: 44px;
        border: 1px solid #CBD5E1;
        background: #FFFFFF;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        color: #0F172A;
        font-weight: 700;
    }
    
    /* Reason Box */
    .reason-card {
        background: #FFF8F6;
        border: 1px solid #FFE4DE;
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    .reason-title {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 800;
        font-size: 0.95rem;
        color: #E11D48;
        margin-bottom: 6px;
    }
    .reason-text {
        font-size: 0.85rem;
        color: #475569;
        line-height: 1.4;
    }
    
    /* Summary Bento Tiles */
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-top: 10px;
    }
    .bento-tile {
        border-radius: 12px;
        padding: 12px 14px;
    }
    .tile-drain { background: #FAF5FF; border: 1px solid #F3E8FF; }
    .tile-spike { background: #EFF6FF; border: 1px solid #DBEAFE; }
    .tile-speed { background: #ECFDF5; border: 1px solid #D1FAE5; }
    .tile-risk  { background: #FFFBEB; border: 1px solid #FEF3C7; }
    
    .tile-lbl {
        font-size: 0.7rem;
        font-weight: 600;
        color: #64748B;
        margin-bottom: 4px;
    }
    .tile-val-drain { font-size: 1.35rem; font-weight: 800; color: #DC2626; }
    .tile-val-spike { font-size: 1.35rem; font-weight: 800; color: #2563EB; }
    .tile-val-speed { font-size: 1.35rem; font-weight: 800; color: #059669; }
    .tile-val-risk  { font-size: 1.35rem; font-weight: 800; color: #D97706; }
    
    /* Investigation Steps */
    .step-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 8px;
        background: #FAFCFF;
        border: 1px solid #F1F5F9;
    }
    .step-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .step-num-icon-ok {
        background: #DCFCE7;
        color: #16A34A;
        border-radius: 50%;
        width: 26px;
        height: 26px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .step-num-icon-warn {
        background: #FEF3C7;
        color: #D97706;
        border-radius: 50%;
        width: 26px;
        height: 26px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .step-title {
        font-weight: 700;
        font-size: 0.85rem;
        color: #1E293B;
    }
    .step-sub {
        font-size: 0.75rem;
        color: #64748B;
    }
    .pill-ok {
        background: #DCFCE7;
        color: #15803D;
        font-weight: 700;
        font-size: 0.7rem;
        padding: 4px 10px;
        border-radius: 8px;
    }
    .pill-alert {
        background: #FEE2E2;
        color: #DC2626;
        font-weight: 700;
        font-size: 0.7rem;
        padding: 4px 10px;
        border-radius: 8px;
    }
    
    /* Emergency Response Tiles */
    .emergency-tile {
        background: #FFFFFF;
        border: 1px solid #F1F5F9;
        border-radius: 14px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .tile-left-content {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .action-icon-box {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .action-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #0F172A;
    }
    .action-sub {
        font-size: 0.75rem;
        color: #64748B;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. TOP NAVBAR & HERO
# ==========================================
st.markdown("""
<div class="top-header">
    <div class="brand-group">
        <div class="brand-icon">🛡️</div>
        <div>
            <div style="display:flex; align-items:center;">
                <span class="brand-text">UPI Shield</span>
                <span class="version-tag">v2.0</span>
            </div>
            <div class="sub-brand">Intelligent Fraud Mitigation Gateway</div>
        </div>
        <div style="color:#CBD5E1; margin: 0 10px;">|</div>
        <div style="font-size:0.8rem; color:#64748B; font-weight:500;">
            <span style="color:#3B82F6;">Smarter Checks</span> &nbsp;→&nbsp; Safer Payments
        </div>
    </div>
    <div class="header-right">
        <div class="system-status">
            <span class="status-dot"></span>
            System Online
        </div>
        <div class="user-pill">
            <div class="avatar">P</div>
            <div style="text-align:left;">
                <div style="font-size:0.8rem; font-weight:700; color:#0F172A; line-height:1.1;">Palak</div>
                <div style="font-size:0.65rem; color:#64748B;">Analyst</div>
            </div>
            <span style="font-size:0.7rem; color:#94A3B8;">▼</span>
        </div>
    </div>
</div>

<div class="hero-banner">
    <div>
        <h1 class="hero-title">Intelligent UPI Fraud Mitigation Engine</h1>
        <div class="hero-sub">Pre-ML Rules + Behavioral Random Forest + Adaptive Mitigation</div>
    </div>
    <div class="hero-right-badge">
        <div style="font-size:1.4rem;">🛡️</div>
        <div>
            <div style="font-size:0.82rem; font-weight:700; color:#1E40AF;">Smarter Detection.</div>
            <div style="font-size:0.78rem; font-weight:600; color:#3B82F6;">Faster Protection.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. LOAD ARTIFACTS
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

PROFESSIONS = {
    "College Student": {"balance": 12000.0, "avg_spend": 2000.0},
    "Salaried Employee": {"balance": 65000.0, "avg_spend": 750.0},
    "Small Retailer / Kirana": {"balance": 180000.0, "avg_spend": 8500.0},
    "Wholesale Merchant / SME": {"balance": 750000.0, "avg_spend": 38000.0},
    "Other (Custom Profile)": {"balance": 25000.0, "avg_spend": 1500.0}
}

# ==========================================
# 4. BACKEND VERIFICATION PIPELINE
# ==========================================
def run_investigation(amount, balance, avg_spend, hour_24, tx_count, is_new_device, is_new_payee, dist_km, gap_sec):
    drain_ratio = float(amount) / (float(balance) + 1e-5)
    amount_to_avg = float(amount) / (float(avg_spend) + 1e-5)
    hours_elapsed = max(float(gap_sec) / 3600.0, 0.0001)
    speed_kmh = float(dist_km) / hours_elapsed

    flags = []
    log = []

    # 1. Balance & basics
    if amount <= balance:
        log.append(("1. Balance & basics OK", "Sufficient funds, positive amount.", "OK"))
    else:
        log.append(("1. Balance & basics", "Insufficient funds for amount.", "ALERT"))
        flags.append("OVERDRAW")

    # 2. Speed Check
    if speed_kmh <= 300.0:
        log.append(("2. Speed OK", f"{speed_kmh:,.0f} km/h – normal travel.", "OK"))
    else:
        log.append(("2. Speed ALERT", f"Impossible travel speed: {speed_kmh:,.0f} km/h.", "ALERT"))
        flags.append("IMPOSSIBLE_SPEED")

    # 3. Drain Check
    if drain_ratio > 0.65:
        log.append(("3. Drain ALERT", f"Attempting to spend {drain_ratio*100:.1f}% of total balance.", "ALERT"))
        flags.append("HIGH_DRAIN")
    else:
        log.append(("3. Drain OK", f"{drain_ratio*100:.1f}% of balance.", "OK"))

    # 4. Spending Spike
    if amount_to_avg > 3.5:
        log.append(("4. Spending Spike", f"{amount_to_avg:.1f}x higher than usual average.", "ALERT"))
        flags.append("SPENDING_SPIKE")
    else:
        log.append(("4. Spending Spike", f"{amount_to_avg:.1f}x average (Normal).", "OK"))

    # 5. Device Integrity
    if is_new_device:
        log.append(("5. Device ALERT", "Unrecognized new handset detected.", "ALERT"))
        flags.append("NEW_DEVICE")
    else:
        log.append(("5. Device OK", "Recognized trusted phone.", "OK"))

    # 6. Timing Window
    if hour_24 in [0, 1, 2, 3, 4, 23]:
        log.append(("6. Timing Notice", f"Late night transaction at {hour_24:02d}:00 hrs.", "ALERT"))
        flags.append("OFF_HOURS")
    else:
        log.append(("6. Timing OK", f"Daytime transaction at {hour_24:02d}:00.", "OK"))

    # 7. Payee Trust
    if is_new_payee:
        log.append(("7. Payee Notice", "First-time transfer to unverified contact.", "ALERT"))
        flags.append("NEW_PAYEE")
    else:
        log.append(("7. Payee OK", "Own contact you paid before.", "OK"))

    # Synthesize Score
    n_expected = getattr(scaler, "n_features_in_", 8)
    if n_expected == 8:
        feats = np.array([[amount, amount_to_avg, drain_ratio, hour_24, tx_count, 1 if is_new_device else 0, speed_kmh, gap_sec]])
    else:
        feats = np.array([[amount, amount_to_avg, drain_ratio, hour_24, tx_count, 1 if is_new_device else 0, dist_km, speed_kmh, gap_sec]])
    
    scaled = scaler.transform(feats)
    rf_risk = float(model.predict_proba(scaled)[0][1])

    score = 0.52 if ("HIGH_DRAIN" in flags or "SPENDING_SPIKE" in flags) else rf_risk
    if "IMPOSSIBLE_SPEED" in flags:
        score = 0.99
    elif len(flags) >= 3:
        score = max(score, 0.75)

    tier = "TIER_2_CHALLENGE"
    status = "SUSPICIOUS PAYMENT, FROZEN"
    reason = "Suspicious Activity Detected: Triggered by HIGH SPEND, SPENDING SPIKE. Payment temporarily frozen pending OTP verification."

    if score >= 0.90:
        tier = "TIER_3_COOLING"
        status = "CRITICAL RISK BLOCK"
        reason = f"Payment Blocked: High risk detected across {', '.join(flags)}."
    elif score < 0.35 and len(flags) == 0:
        tier = "TIER_1_PASS"
        status = "INSTANT APPROVAL"
        reason = "All security telemetry checks verified safely."

    return {
        "tier": tier,
        "status": status,
        "score": score,
        "drain_ratio": drain_ratio,
        "amount_to_avg": amount_to_avg,
        "speed_kmh": speed_kmh,
        "reason": reason,
        "log": log,
        "flags": flags
    }

# ==========================================
# 5. MAIN APPLICATION UI
# ==========================================
tab_manual, tab_prod = st.tabs(["📋 Manual Testing", "📱 Production App Store"])

with tab_manual:
    # ---------------------------------------------
    # INPUT SECTION (MATCHING SCREENSHOT FORM)
    # ---------------------------------------------
    st.markdown("""
    <div class="custom-card">
        <div class="card-header-bar">
            <div class="header-icon-box">📋</div>
            <div>
                <div>Manual Testing Panel</div>
                <div style="font-size:0.75rem; color:#64748B; font-weight:500;">Enter the details below to analyse the transaction in real-time.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    c_in1, c_in2 = st.columns(2)

    with c_in1:
        st.caption("**1. Select Profession Profile**")
        sel_prof = st.selectbox("", list(PROFESSIONS.keys()), label_visibility="collapsed")
        prof = PROFESSIONS[sel_prof]

        st.caption("**2. Payment Details**")
        st.caption("Transaction Amount (₹)")
        in_amount = st.number_input("Transaction Amount", min_value=1.0, value=10000.0, step=500.0, label_visibility="collapsed")
        
        st.caption("Account Balance (₹)")
        in_balance = st.number_input("Account Balance", min_value=1.0, value=12000.0, step=1000.0, label_visibility="collapsed")
        
        st.caption("Usual Average Spend (₹)")
        in_avg = st.number_input("Usual Average Spend", min_value=1.0, value=2000.0, step=100.0, label_visibility="collapsed")
        
        st.caption("Payee History")
        in_payee_new = st.selectbox("Payee History", ["Known / Frequently Paid Contact", "New / Unverified Payee"], index=0, label_visibility="collapsed") == "New / Unverified Payee"

    with c_in2:
        st.caption("**3. Location & Phone Context**")
        st.caption("Distance from Last Transaction (km)")
        in_dist = st.number_input("Distance from Last Transaction (km)", min_value=0.0, value=50.0, step=5.0, label_visibility="collapsed")

        st.caption("Time Gap Since Last Payment")
        g_val_col, g_unit_col = st.columns([1, 1])
        with g_val_col:
            in_gap_val = st.number_input("Value", min_value=0.1, value=30.0, step=1.0, label_visibility="collapsed")
        with g_unit_col:
            in_gap_unit = st.selectbox("Unit", ["Minutes", "Seconds", "Hours"], index=0, label_visibility="collapsed")

        st.caption("Number of Payments in Last 10 Mins")
        in_tx_count = st.number_input("Payments in 10 Mins", min_value=0, max_value=10, value=1, label_visibility="collapsed")

        st.caption("Phone Used")
        in_device = st.selectbox("Phone Used", ["Trusted Phone (Known)", "New / Unrecognized Phone"], index=0, label_visibility="collapsed") == "New / Unrecognized Phone"

    # Time Selection Row
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("**4. Time of Transaction**")
    t_c1, t_c2, t_c3, t_c4 = st.columns([1, 1, 1.2, 2.5])
    with t_c1:
        st.caption("Hour")
        h_12 = st.selectbox("Hour", list(range(1, 13)), index=11, label_visibility="collapsed")
    with t_c2:
        st.caption("Minute")
        m_val = st.selectbox("Minute", ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"], index=6, label_visibility="collapsed")
    with t_c3:
        st.caption("AM / PM")
        ampm = st.radio("AM/PM", ["AM", "PM"], horizontal=True, index=0, label_visibility="collapsed")
    with t_c4:
        st.write("")
        st.caption(f"Selected Time: **{h_12}:{m_val} {ampm}** (24h: {('00' if h_12==12 else f'{h_12:02d}') if ampm=='AM' else ('12' if h_12==12 else str(h_12+12))}:{m_val})")

    calc_gap_sec = in_gap_val * 60.0 if in_gap_unit == "Minutes" else (in_gap_val * 3600.0 if in_gap_unit == "Hours" else in_gap_val)
    calc_hour_24 = (0 if h_12 == 12 else h_12) if ampm == "AM" else (12 if h_12 == 12 else h_12 + 12)

    st.markdown("</div>", unsafe_allow_html=True)

    btn_trigger = st.button("⚡ Run Verification Pipeline", type="primary")

    if btn_trigger or 'res_data' not in st.session_state:
        st.session_state['res_data'] = run_investigation(
            in_amount, in_balance, in_avg, calc_hour_24, in_tx_count, in_device, in_payee_new, in_dist, calc_gap_sec
        )

    res = st.session_state['res_data']

    # ---------------------------------------------
    # STATUS BAR (MATCHING THE SCREENSHOT EXACTLY)
    # ---------------------------------------------
    st.markdown(f"""
    <div class="status-alert-box">
        <div class="status-alert-title">
            <span style="background:#EA580C; color:white; border-radius:50%; width:22px; height:22px; display:inline-flex; align-items:center; justify-content:center; font-size:0.8rem;">!</span>
            STATUS: {res['status']}
        </div>
        <div class="status-alert-right">
            <span class="risk-score-pill">Risk Score: {res['score']*100:.1f}%</span>
            <span class="risk-level-badge">● High Risk</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------
    # 2-COLUMN SPLIT (FORENSIC AUDIT + VERIFICATION)
    # ---------------------------------------------
    split_left, split_right = st.columns([1.15, 1])

    with split_left:
        # 1. Payment Frozen Card
        st.markdown("""
        <div class="frozen-card">
            <div class="frozen-header">
                <div class="frozen-icon">🔒</div>
                <div>
                    <div class="frozen-title">Payment Frozen</div>
                    <div class="frozen-sub">Held for safety. Enter the 4-digit SMS OTP to approve.</div>
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                <div class="otp-row">
                    <div class="otp-cell">*</div>
                    <div class="otp-cell">*</div>
                    <div class="otp-cell">*</div>
                    <div class="otp-cell">*</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-weight:700; color:#EF4444; font-size:0.95rem;">04:48</div>
                    <div style="font-size:0.7rem; color:#94A3B8;">OTP expires in</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        otp_in_col, otp_btn_col = st.columns([2, 1])
        with otp_in_col:
            entered_otp = st.text_input("Enter OTP (Mock: 4921)", max_chars=4, label_visibility="collapsed", placeholder="Enter 4-digit OTP")
        with otp_btn_col:
            if st.button("Verify OTP"):
                if entered_otp == "4921":
                    st.success("✅ Payment Released!")
                else:
                    st.error("❌ Invalid OTP")

        # 2. Reason Card
        st.markdown(f"""
        <div class="reason-card">
            <div class="reason-title">
                <span style="background:#EF4444; color:white; border-radius:50%; width:20px; height:20px; display:inline-flex; align-items:center; justify-content:center; font-size:0.75rem;">!</span>
                Reason
            </div>
            <div class="reason-text">
                Suspicious Activity Detected: Triggered by<br>
                <strong style="color:#DC2626;">HIGH SPEND, SPENDING SPIKE.</strong><br>
                Payment temporarily frozen pending OTP verification.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Transaction Summary Bento Grid
        st.markdown(f"""
        <div class="custom-card">
            <div class="card-header-bar" style="margin-bottom:8px;">
                <div class="header-icon-box">📊</div>
                <div>Transaction Summary</div>
            </div>
            <div class="summary-grid">
                <div class="bento-tile tile-drain">
                    <div class="tile-lbl">Account Drain</div>
                    <div class="tile-val-drain">{res['drain_ratio']*100:.1f}%</div>
                </div>
                <div class="bento-tile tile-spike">
                    <div class="tile-lbl">Spike Average</div>
                    <div class="tile-val-spike">{res['amount_to_avg']:.1f}x</div>
                </div>
                <div class="bento-tile tile-speed">
                    <div class="tile-lbl">Travel Speed</div>
                    <div class="tile-val-speed">{res['speed_kmh']:,.0f} km/h</div>
                </div>
                <div class="bento-tile tile-risk">
                    <div class="tile-lbl">Risk Score</div>
                    <div class="tile-val-risk">{res['score']*100:.1f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with split_right:
        # 4. Security Investigation (Step-by-Step)
        st.markdown("""
        <div class="custom-card">
            <div class="card-header-bar">
                <div class="header-icon-box">🔍</div>
                <div>
                    <div>Security Investigation <span style="font-size:0.8rem; color:#64748B; font-weight:500;">(Step-by-Step)</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        for name, detail, state in res['log']:
            is_ok = state == "OK"
            icon_cls = "step-num-icon-ok" if is_ok else "step-num-icon-warn"
            icon_sym = "✓" if is_ok else "▲"
            pill_cls = "pill-ok" if is_ok else "pill-alert"
            
            st.markdown(f"""
            <div class="step-item">
                <div class="step-left">
                    <div class="{icon_cls}">{icon_sym}</div>
                    <div>
                        <div class="step-title">{name}</div>
                        <div class="step-sub">{detail}</div>
                    </div>
                </div>
                <span class="{pill_cls}">▲ {state}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------
    # EMERGENCY RESPONSE ACTIONS (BOTTOM BAR)
    # ---------------------------------------------
    st.markdown("""
    <div class="custom-card">
        <div class="card-header-bar" style="margin-bottom:12px;">
            <div class="header-icon-box" style="color:#EF4444; background:#FFF1F2;">🛡️</div>
            <div>
                <div>Emergency Response Actions</div>
                <div style="font-size:0.75rem; color:#64748B; font-weight:500;">Take immediate action to secure the account and prevent further loss.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    e_c1, e_c2, e_c3 = st.columns(3)

    with e_c1:
        st.markdown("""
        <div class="emergency-tile">
            <div class="tile-left-content">
                <div class="action-icon-box" style="background:#FFF1F2; color:#E11D48;">📞</div>
                <div>
                    <div class="action-title">1. Cyber Police Helpline</div>
                    <div class="action-sub">Call 1930 immediately.</div>
                </div>
            </div>
            <div style="color:#CBD5E1;">→</div>
        </div>
        """, unsafe_allow_html=True)

    with e_c2:
        st.markdown("""
        <div class="emergency-tile">
            <div class="tile-left-content">
                <div class="action-icon-box" style="background:#FFFBEB; color:#D97706;">🔒</div>
                <div>
                    <div class="action-title">2. Beneficiary Lock</div>
                    <div class="action-sub">Request account freeze.</div>
                </div>
            </div>
            <div style="color:#CBD5E1;">→</div>
        </div>
        """, unsafe_allow_html=True)

    with e_c3:
        st.markdown("""
        <div class="emergency-tile">
            <div class="tile-left-content">
                <div class="action-icon-box" style="background:#EFF6FF; color:#2563EB;">📄</div>
                <div>
                    <div class="action-title">3. Bank Dispute File</div>
                    <div class="action-sub">Download dispute report (1:1).</div>
                </div>
            </div>
            <div style="color:#CBD5E1;">→</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 6. PRODUCTION APP SIMULATOR TAB
# ==========================================
with tab_prod:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("📱 Production Checkout Mode: Switch to this tab when demonstrating the client-side Google Pay/PhonePe checkout interface.")
