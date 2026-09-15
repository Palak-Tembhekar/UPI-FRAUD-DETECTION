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
# 1. HIGH-CONTRAST, LARGE-FONT CSS THEME
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 18px !important;
        color: #000000 !important;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Input Labels and Text */
    p, span, label, .stMarkdown {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #000000 !important;
    }
    
    /* Top Header Bar */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        padding: 16px 28px;
        border-radius: 18px;
        border: 2px solid #CBD5E1;
        margin-bottom: 24px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
    }
    .brand-title {
        font-size: 1.35rem;
        font-weight: 900;
        color: #000000;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-badge {
        font-size: 0.8rem;
        background: #DBEAFE;
        color: #1D4ED8;
        padding: 3px 10px;
        border-radius: 8px;
        font-weight: 800;
    }
    .user-pill {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #F1F5F9;
        border: 2px solid #94A3B8;
        padding: 6px 16px;
        border-radius: 24px;
        font-weight: 800;
        color: #000000;
    }
    
    /* Main Cards */
    .custom-card {
        background: #FFFFFF;
        border-radius: 18px;
        border: 2px solid #CBD5E1;
        padding: 24px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
        margin-bottom: 22px;
    }
    .card-header-bar {
        font-weight: 900;
        font-size: 1.3rem;
        color: #000000;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Verification Button */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #E11D48 0%, #BE123C 100%) !important;
        color: #FFFFFF !important;
        font-size: 1.25rem !important;
        font-weight: 900 !important;
        border-radius: 14px !important;
        padding: 16px 32px !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(225, 29, 72, 0.35) !important;
        width: 100% !important;
        margin-top: 14px !important;
    }

    /* Bento Metric Tiles */
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-top: 14px;
    }
    .bento-tile {
        border-radius: 14px;
        padding: 16px 18px;
        border: 2px solid #CBD5E1;
    }
    .tile-drain { background: #FAF5FF; border-color: #D8B4FE; }
    .tile-spike { background: #EFF6FF; border-color: #93C5FD; }
    .tile-speed { background: #F0FDF4; border-color: #86EFAC; }
    .tile-risk  { background: #FFFBEB; border-color: #FDE68A; }
    
    .tile-lbl {
        font-size: 0.85rem;
        font-weight: 800;
        color: #1E293B;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .tile-val {
        font-size: 1.7rem;
        font-weight: 900;
    }
    
    /* Checklist Steps */
    .step-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 10px;
        background: #F8FAFC;
        border: 2px solid #E2E8F0;
    }
    .step-title {
        font-weight: 900;
        font-size: 1.05rem;
        color: #000000;
    }
    .step-sub {
        font-size: 0.9rem;
        font-weight: 700;
        color: #334155;
    }
    .pill-ok {
        background: #DCFCE7;
        color: #166534;
        font-weight: 900;
        font-size: 0.85rem;
        padding: 6px 14px;
        border-radius: 10px;
        border: 1px solid #86EFAC;
    }
    .pill-alert {
        background: #FEE2E2;
        color: #991B1B;
        font-weight: 900;
        font-size: 0.85rem;
        padding: 6px 14px;
        border-radius: 10px;
        border: 1px solid #FCA5A5;
    }

    /* Large Prominent OTP Box */
    .otp-container {
        background: #FFFFFF;
        border: 2px solid #F59E0B;
        border-radius: 16px;
        padding: 20px;
        margin-top: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. TOP NAVBAR & HERO
# ==========================================
st.markdown("""
<div class="top-header">
    <div class="brand-title">
        <span>🛡️ UPI Shield</span>
        <span class="brand-badge">v2.0</span>
        <span style="color:#64748B; font-weight:700; font-size:1rem; margin-left:8px;">| Intelligent Fraud Mitigation Gateway</span>
    </div>
    <div style="display:flex; align-items:center; gap:24px;">
        <div style="font-size:0.95rem; font-weight:800; color:#16A34A; display:flex; align-items:center; gap:8px;">
            <span style="width:10px; height:10px; background:#16A34A; border-radius:50%; display:inline-block;"></span>
            Bank Switch Online
        </div>
        <div class="user-pill">
            <span style="background:#2563EB; color:#FFF; border-radius:50%; width:28px; height:28px; display:inline-flex; align-items:center; justify-content:center; font-size:0.85rem;">P</span>
            <span>Palak (AI Engineer)</span>
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
# 4. ROBUST EVALUATION ENGINE
# ==========================================
def run_investigation(amount, balance, avg_spend, hour_24, tx_count, is_new_device, is_new_payee, dist_km, gap_sec):
    drain_ratio = float(amount) / (float(balance) + 1e-5)
    amount_to_avg = float(amount) / (float(avg_spend) + 1e-5)
    hours_elapsed = max(float(gap_sec) / 3600.0, 0.0001)
    speed_kmh = float(dist_km) / hours_elapsed

    flags = []
    log = []

    # 1. Deterministic Checks
    if amount <= 0:
        return {"tier": "REJECTED", "status": "INVALID AMOUNT", "score": 1.0, "reason": "Amount must be strictly positive.", "drain_ratio": 0, "amount_to_avg": 0, "speed_kmh": 0, "log": [("Balance & basics", "Failed: Amount <= 0", "ALERT")], "flags": ["INVALID"]}

    if amount > balance:
        log.append(("1. Balance & Liquidity", f"FAILED: Amount ₹{amount:,.0f} exceeds balance ₹{balance:,.0f}", "ALERT"))
        return {"tier": "REJECTED", "status": "INSUFFICIENT FUNDS", "score": 1.0, "reason": f"Amount (₹{amount:,.2f}) exceeds available balance (₹{balance:,.2f}).", "drain_ratio": drain_ratio, "amount_to_avg": amount_to_avg, "speed_kmh": speed_kmh, "log": log, "flags": ["OVERDRAW"]}
    else:
        log.append(("1. Balance & Liquidity", "Sufficient balance verified.", "OK"))

    # 2. Velocity Check
    if speed_kmh > 300.0 and dist_km > 20.0:
        log.append(("2. Travel Speed", f"ALERT: Impossible speed ({speed_kmh:,.0f} km/h).", "ALERT"))
        flags.append("IMPOSSIBLE SPEED")
    else:
        log.append(("2. Travel Speed", f"{speed_kmh:,.0f} km/h (Physically feasible).", "OK"))

    # 3. Account Drain Check
    if drain_ratio > 0.65:
        log.append(("3. Balance Drain", f"ALERT: High drain ({drain_ratio*100:.1f}% of total funds).", "ALERT"))
        flags.append("HIGH DRAIN")
    else:
        log.append(("3. Balance Drain", f"{drain_ratio*100:.1f}% of balance (Safe).", "OK"))

    # 4. Spending Surge
    if amount_to_avg > 3.5:
        log.append(("4. Spend Baseline", f"ALERT: Surge of {amount_to_avg:.1f}x historical average.", "ALERT"))
        flags.append("SPENDING SPIKE")
    else:
        log.append(("4. Spend Baseline", f"{amount_to_avg:.1f}x baseline (Normal spend habit).", "OK"))

    # 5. Device Integrity
    if is_new_device:
        log.append(("5. Device Token", "ALERT: Unrecognized hardware token.", "ALERT"))
        flags.append("NEW DEVICE")
    else:
        log.append(("5. Device Token", "Recognized trusted handset.", "OK"))

    # 6. Timing Window
    if hour_24 in [0, 1, 2, 3, 4, 23]:
        log.append(("6. Timing Window", f"NOTICE: Late night transaction ({hour_24:02d}:00 hrs).", "ALERT"))
        flags.append("OFF-HOURS")
    else:
        log.append(("6. Timing Window", f"Standard daylight window ({hour_24:02d}:00 hrs).", "OK"))

    # 7. Payee Status
    if is_new_payee:
        log.append(("7. Recipient Trust", "NOTICE: First-time transfer to new contact.", "ALERT"))
        flags.append("NEW PAYEE")
    else:
        log.append(("7. Recipient Trust", "Established contact previously transacted with.", "OK"))

    # Machine Learning Inference
    n_expected = getattr(scaler, "n_features_in_", 8)
    if n_expected == 8:
        feats = np.array([[amount, amount_to_avg, drain_ratio, hour_24, tx_count, 1 if is_new_device else 0, speed_kmh, gap_sec]])
    else:
        feats = np.array([[amount, amount_to_avg, drain_ratio, hour_24, tx_count, 1 if is_new_device else 0, dist_km, speed_kmh, gap_sec]])
    
    scaled = scaler.transform(feats)
    rf_risk = float(model.predict_proba(scaled)[0][1])

    # Dynamic Score Harmonization (Prevents 0.0% Glitch)
    if "IMPOSSIBLE SPEED" in flags:
        score = 0.99
    elif "HIGH DRAIN" in flags and "NEW DEVICE" in flags:
        score = 0.96
    elif len(flags) >= 3:
        score = max(rf_risk, 0.76)
    elif len(flags) >= 1:
        score = max(rf_risk, 0.52)
    else:
        score = min(max(rf_risk, 0.05), 0.18)

    # Threshold Arbitration
    if score >= 0.90:
        tier = "TIER_3_COOLING"
        status = "CRITICAL RISK, BLOCKED"
        reason = f"Payment Blocked: High risk detected ({', '.join(flags)}). Transaction terminated to protect funds."
    elif score >= 0.35 or len(flags) >= 1:
        tier = "TIER_2_CHALLENGE"
        status = "SUSPICIOUS PAYMENT, FROZEN"
        reason = f"Suspicious Activity Detected: Triggered by {', '.join(flags)}. Payment held on security freeze pending OTP verification."
    else:
        tier = "TIER_1_PASS"
        status = "INSTANT APPROVAL"
        reason = "All security telemetry checks verified safely. Transaction cleared."

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
# 5. STREAMLIT UI
# ==========================================
tab_manual, tab_prod = st.tabs(["📋 Manual Testing Panel", "📱 Production App Simulator"])

with tab_manual:
    st.markdown("""
    <div class="custom-card">
        <div class="card-header-bar">
            <span>📋 Manual Testing Panel</span>
        </div>
    """, unsafe_allow_html=True)

    c_in1, c_in2 = st.columns(2)

    with c_in1:
        st.markdown("**1. Select Profession Profile**")
        sel_prof = st.selectbox("", list(PROFESSIONS.keys()), label_visibility="collapsed")
        prof = PROFESSIONS[sel_prof]

        st.markdown("**2. Payment Details**")
        st.markdown("**Transaction Amount (₹)**")
        in_amount = st.number_input("Transaction Amount", min_value=1.0, value=10000.0, step=500.0, label_visibility="collapsed")
        
        st.markdown("**Account Balance (₹)**")
        in_balance = st.number_input("Account Balance", min_value=1.0, value=float(prof['balance']), step=1000.0, label_visibility="collapsed")
        
        st.markdown("**Usual Average Spend (₹)**")
        in_avg = st.number_input("Usual Average Spend", min_value=1.0, value=float(prof['avg_spend']), step=100.0, label_visibility="collapsed")
        
        st.markdown("**Payee History**")
        in_payee_new = st.selectbox("Payee History", ["Known / Frequently Paid Contact", "New / Unverified Payee"], index=0, label_visibility="collapsed") == "New / Unverified Payee"

    with c_in2:
        st.markdown("**3. Location & Phone Context**")
        st.markdown("**Distance from Last Transaction (km)**")
        in_dist = st.number_input("Distance from Last Transaction (km)", min_value=0.0, value=50.0, step=5.0, label_visibility="collapsed")

        st.markdown("**Time Gap Since Last Payment**")
        g_val_col, g_unit_col = st.columns([1, 1])
        with g_val_col:
            in_gap_val = st.number_input("Value", min_value=0.1, value=30.0, step=1.0, label_visibility="collapsed")
        with g_unit_col:
            in_gap_unit = st.selectbox("Unit", ["Minutes", "Seconds", "Hours"], index=0, label_visibility="collapsed")

        st.markdown("**Number of Payments in Last 10 Mins**")
        in_tx_count = st.number_input("Payments in 10 Mins", min_value=0, max_value=10, value=1, label_visibility="collapsed")

        st.markdown("**Phone Used**")
        in_device = st.selectbox("Phone Used", ["Trusted Phone (Known)", "New / Unrecognized Phone"], index=0, label_visibility="collapsed") == "New / Unrecognized Phone"

    # Time of Transaction Row
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**4. Time of Transaction**")
    t_c1, t_c2, t_c3, t_c4 = st.columns([1, 1, 1.2, 2.5])
    with t_c1:
        st.caption("**Hour**")
        h_12 = st.selectbox("Hour", list(range(1, 13)), index=11, label_visibility="collapsed")
    with t_c2:
        st.caption("**Minute**")
        m_val = st.selectbox("Minute", ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"], index=6, label_visibility="collapsed")
    with t_c3:
        st.caption("**AM / PM**")
        ampm = st.radio("AM/PM", ["AM", "PM"], horizontal=True, index=0, label_visibility="collapsed")
    with t_c4:
        st.write("")
        st.markdown(f"**Selected Time:** `{h_12}:{m_val} {ampm}`")

    calc_gap_sec = in_gap_val * 60.0 if in_gap_unit == "Minutes" else (in_gap_val * 3600.0 if in_gap_unit == "Hours" else in_gap_val)
    calc_hour_24 = (0 if h_12 == 12 else h_12) if ampm == "AM" else (12 if h_12 == 12 else h_12 + 12)

    st.markdown("</div>", unsafe_allow_html=True)

    btn_trigger = st.button("Run Verification Pipeline", type="primary")

    if btn_trigger or 'res_data' not in st.session_state:
        st.session_state['res_data'] = run_investigation(
            in_amount, in_balance, in_avg, calc_hour_24, in_tx_count, in_device, in_payee_new, in_dist, calc_gap_sec
        )
        st.session_state['v_inputs'] = {"amount": in_amount, "prof": sel_prof, "payee": "New Payee" if in_payee_new else "Known Contact"}

    res = st.session_state['res_data']
    tier = res['tier']
    score = res['score']

    # ---------------------------------------------
    # DYNAMIC STATUS BAR (POINTS 3 & 4)
    # ---------------------------------------------
    if tier == "TIER_1_PASS":
        box_bg = "#ECFDF5"
        box_border = "#10B981"
        txt_color = "#047857"
        right_badge_txt = "● Low Risk (Passed)"
        right_badge_bg = "#D1FAE5"
    elif tier == "TIER_2_CHALLENGE":
        box_bg = "#FFFBEB"
        box_border = "#F59E0B"
        txt_color = "#B45309"
        right_badge_txt = "● Medium Risk (Frozen)"
        right_badge_bg = "#FDE68A"
    else:
        box_bg = "#FEF2F2"
        box_border = "#EF4444"
        txt_color = "#B91C1C"
        right_badge_txt = "● High Risk (Blocked)"
        right_badge_bg = "#FECACA"

    st.markdown(f"""
    <div style="background:{box_bg}; border:2px solid {box_border}; border-radius:16px; padding:16px 24px; display:flex; justify-content:space-between; align-items:center; margin-bottom:24px;">
        <div style="font-weight:900; font-size:1.25rem; color:{txt_color};">
            STATUS: {res['status']}
        </div>
        <div style="display:flex; gap:14px; align-items:center;">
            <span style="background:#FFFFFF; border:2px solid {box_border}; color:{txt_color}; font-weight:900; font-size:1rem; padding:6px 16px; border-radius:20px;">
                Risk Score: {score*100:.1f}%
            </span>
            <span style="background:{right_badge_bg}; color:{txt_color}; font-weight:900; font-size:1rem; padding:6px 16px; border-radius:20px;">
                {right_badge_txt}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------
    # CONDITIONAL DASHBOARD SPLIT (POINTS 6 & 7)
    # ---------------------------------------------
    col_left, col_right = st.columns([1.15, 1])

    with col_left:
        # If Instant Approval, show clean verified badge instead of Frozen box
        if tier == "TIER_1_PASS":
            st.markdown("""
            <div class="custom-card" style="border:2px solid #10B981; background:#F0FDF4;">
                <div style="font-size:1.3rem; font-weight:900; color:#166534; display:flex; align-items:center; gap:10px;">
                    ✅ Transaction Cleared & Safe
                </div>
                <div style="font-size:1.05rem; font-weight:700; color:#15803D; margin-top:8px;">
                    No anomalous telemetry detected. Payment was instantly authorized without challenge.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # If Suspicious/Frozen, show Large Prominent OTP Box
        elif tier == "TIER_2_CHALLENGE":
            st.markdown("""
            <div class="otp-container">
                <div style="font-size:1.3rem; font-weight:900; color:#DC2626; display:flex; align-items:center; gap:10px;">
                    ⏸️ Payment Frozen
                </div>
                <div style="font-size:1.05rem; font-weight:700; color:#000000; margin-top:4px;">
                    Held for safety. Enter the 4-digit SMS OTP to approve release of funds.
                </div>
            </div>
            """, unsafe_allow_html=True)

            otp_c1, otp_c2 = st.columns([1.8, 1])
            with otp_c1:
                st.markdown("**Enter 4-Digit Security OTP (Mock: 4921):**")
                user_otp = st.text_input("Enter 4-digit Security OTP", max_chars=4, label_visibility="collapsed", placeholder="Enter 4-digit OTP here")
            with otp_c2:
                st.write("")
                st.write("")
                if st.button("Verify & Release Funds", key="v_otp_btn"):
                    if user_otp == "4921":
                        st.success("✅ OTP Verified! Payment approved and funds released.")
                    else:
                        st.error("❌ Invalid OTP. Hold maintained.")

            # Reason Card
            st.markdown(f"""
            <div class="custom-card" style="border:2px solid #F59E0B; margin-top:14px;">
                <div style="font-size:1.2rem; font-weight:900; color:#B45309; margin-bottom:8px;">⚠️ Decision Reason</div>
                <div style="font-size:1.05rem; font-weight:700; color:#000000; line-height:1.5;">
                    {res['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        else: # TIER_3_COOLING
            st.markdown(f"""
            <div class="custom-card" style="border:2px solid #EF4444; background:#FEF2F2;">
                <div style="font-size:1.3rem; font-weight:900; color:#DC2626; margin-bottom:8px;">🚫 Transaction Terminated</div>
                <div style="font-size:1.05rem; font-weight:700; color:#991B1B; line-height:1.5;">
                    {res['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Behavioral Metrics Bento Grid
        st.markdown(f"""
        <div class="custom-card" style="margin-top:14px;">
            <div class="card-header-bar">📊 Behavioral Metrics Summary</div>
            <div class="summary-grid">
                <div class="bento-tile tile-drain">
                    <div class="tile-lbl">Account Drain</div>
                    <div class="tile-val" style="color:#7E22CE;">{res['drain_ratio']*100:.1f}%</div>
                </div>
                <div class="bento-tile tile-spike">
                    <div class="tile-lbl">Spike Ratio</div>
                    <div class="tile-val" style="color:#1D4ED8;">{res['amount_to_avg']:.1f}x</div>
                </div>
                <div class="bento-tile tile-speed">
                    <div class="tile-lbl">Travel Speed</div>
                    <div class="tile-val" style="color:#15803D;">{res['speed_kmh']:,.0f} <span style="font-size:0.9rem;">km/h</span></div>
                </div>
                <div class="bento-tile tile-risk">
                    <div class="tile-lbl">Risk Score</div>
                    <div class="tile-val" style="color:#B45309;">{score*100:.1f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # Step-by-Step Checklist
        st.markdown("""
        <div class="custom-card">
            <div class="card-header-bar">🔍 Security Investigation (Step-by-Step)</div>
        """, unsafe_allow_html=True)

        for name, detail, state in res['log']:
            pill_class = "pill-ok" if state == "OK" else "pill-alert"
            st.markdown(f"""
            <div class="step-item">
                <div>
                    <div class="step-title">{name}</div>
                    <div class="step-sub">{detail}</div>
                </div>
                <span class="{pill_class}">▲ {state}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------
    # EMERGENCY RESPONSE ACTIONS (POINT 5)
    # ---------------------------------------------
    st.markdown("""
    <div class="custom-card" style="margin-top:10px;">
        <div class="card-header-bar" style="color:#B91C1C;">
            <span>🚨 Emergency Response Actions</span>
        </div>
        <div style="font-size:1rem; font-weight:700; color:#475569; margin-bottom:16px;">
            Take immediate action to secure the account, dispatch liens, or report incidents under RBI regulations.
        </div>
    """, unsafe_allow_html=True)

    e_c1, e_c2, e_c3 = st.columns(3)

    with e_c1:
        st.markdown("**1. Cyber Police Helpline**")
        st.markdown("Immediate national escalation: Dial **1930**")
        st.link_button("🌐 Open cybercrime.gov.in", "https://cybercrime.gov.in")

    with e_c2:
        st.markdown("**2. Beneficiary Account Lock**")
        st.markdown("Send urgent freeze signal to switch.")
        if st.button("🔒 Request Account Freeze", key="v_freeze_btn"):
            st.success("✅ Lien notice dispatched to beneficiary bank switch.")

    with e_c3:
        st.markdown("**3. Bank Dispute File**")
        st.markdown("Statutory Zero-Liability dossier.")
        v_in = st.session_state['v_inputs']
        report_txt = f"""OFFICIAL ELECTRONIC FRAUD DISPUTE DOSSIER
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
UTR Reference: 429184{int(time.time())%1000000:06d}
Amount Evaluated: INR {v_in['amount']:,.2f}
Account Profile: {v_in['prof']}
Recipient Status: {v_in['payee']}
Final Verdict: {res['status']}
Calculated Risk: {score*100:.1f}%
Reason: {res['reason']}
Statutory Authority: Filed under RBI Circular on Limiting Customer Liability in Unauthorized Electronic Transactions."""
        st.download_button(
            label="📄 Download Dispute Report (.txt)",
            data=report_txt,
            file_name=f"Dispute_Report_{int(time.time())}.txt",
            key="v_download_btn"
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 6. PRODUCTION APP SIMULATOR TAB
# ==========================================
with tab_prod:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("📱 Production Checkout Mode: Switch here to demonstrate client-side checkout context.")
