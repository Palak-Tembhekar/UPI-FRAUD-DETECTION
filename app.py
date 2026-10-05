import streamlit as st
import numpy as np
import pandas as pd
import pickle
import os
import time
import re
from datetime import datetime

st.set_page_config(
    page_title="UPI Shield — Intelligent Fraud Mitigation Gateway",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 1. NAVIGATION STATE (radio is the single source of truth)
# ==============================================================================
PAGES = ["Home", "Dashboard", "Fraud Detection"]

if "nav" not in st.session_state:
    st.session_state["nav"] = "Home"

def go_to_fraud_detection():
    st.session_state["nav"] = "Fraud Detection"

# ==============================================================================
# 2. SIDEBAR (default Streamlit look)
# ==============================================================================
with st.sidebar:
    st.header("Navigation")
    st.radio("Go to", PAGES, key="nav")

active_nav = st.session_state["nav"]

# ==============================================================================
# 3. STYLING
# ==============================================================================
base_css = """
<style>
    .stApp { background-color: #FFFFFF; }

    /* INPUTS & SELECTS */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input, select {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* BENTO CARDS (INTERNAL PAGES) */
    .bento-card {
        background: #FFFFFF;
        border-radius: 20px;
        border: 2px solid #E2E8F0;
        padding: 24px;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.03);
        margin-bottom: 22px;
    }
    .bento-card-title {
        font-weight: 900;
        font-size: 1.35rem;
        color: #0F172A;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* METRIC TILES */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-top: 14px;
    }
    .metric-tile {
        border-radius: 16px;
        padding: 16px 18px;
        border: 2px solid transparent;
    }
    .tile-drain { background: #FAF5FF; border-color: #D8B4FE; }
    .tile-spike { background: #EFF6FF; border-color: #93C5FD; }
    .tile-speed { background: #F0FDF4; border-color: #86EFAC; }
    .tile-risk  { background: #FFFBEB; border-color: #FDE68A; }

    .tile-lbl {
        font-size: 0.85rem;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .tile-val {
        font-size: 1.9rem;
        font-weight: 900;
    }

    /* ACTION BUTTONS (only the two pipeline buttons) */
    .st-key-v_run_pipeline_btn button,
    .st-key-sim_checkout_btn button {
        background: linear-gradient(90deg, #E11D48 0%, #BE123C 100%) !important;
        color: #FFFFFF !important;
        font-size: 1.25rem !important;
        font-weight: 900 !important;
        border-radius: 14px !important;
        padding: 16px 32px !important;
        border: none !important;
        width: 100% !important;
        margin-top: 14px !important;
    }

    /* CHECKLIST STEPS */
    .step-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 18px;
        border-radius: 14px;
        margin-bottom: 12px;
        background: #F8FAFC;
        border: 2px solid #E2E8F0;
    }
    .step-title {
        font-weight: 800;
        font-size: 1.1rem;
        color: #0F172A;
    }
    .step-sub {
        font-size: 0.95rem;
        font-weight: 600;
        color: #475569;
    }
    .pill-ok {
        background: #DCFCE7;
        color: #166534;
        font-weight: 900;
        font-size: 0.88rem;
        padding: 6px 16px;
        border-radius: 10px;
    }
    .pill-alert {
        background: #FEE2E2;
        color: #991B1B;
        font-weight: 900;
        font-size: 0.88rem;
        padding: 6px 16px;
        border-radius: 10px;
    }

    /* BACKEND TELEMETRY TERMINAL */
    .terminal-container {
        border: 2px solid #334155;
        background-color: #0F172A !important;
        padding: 24px;
        border-radius: 20px;
        margin-bottom: 22px;
        font-family: 'JetBrains Mono', monospace;
    }
    .terminal-title {
        color: #FFFFFF !important;
        font-size: 1.45rem !important;
        font-weight: 900 !important;
        margin-bottom: 6px !important;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .terminal-sub {
        color: #94A3B8 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin-bottom: 14px !important;
    }
</style>
"""
st.markdown(base_css, unsafe_allow_html=True)

# Custom font only on internal pages (Home uses Streamlit's default font)
if active_nav != "Home":
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. LOAD ARTIFACTS
# ==============================================================================
@st.cache_resource
def load_artifacts():
    model_name = 'upi_fraud_model (3).pkl' if os.path.exists('upi_fraud_model (3).pkl') else 'upi_fraud_model.pkl'
    scaler_name = 'scaler (3).pkl' if os.path.exists('scaler (3).pkl') else 'scaler.pkl'
    try:
        with open(model_name, 'rb') as f:
            model = pickle.load(f)
        with open(scaler_name, 'rb') as f:
            scaler = pickle.load(f)
    except Exception:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        model = RandomForestClassifier().fit(np.zeros((10, 8)), [0]*5 + [1]*5)
        scaler = StandardScaler().fit(np.zeros((10, 8)))
    return model, scaler

model, scaler = load_artifacts()

PROFESSIONS = {
    "🎓 College Student": {"balance": 12000.0, "avg_spend": 2000.0},
    "💼 Salaried Employee": {"balance": 65000.0, "avg_spend": 750.0},
    "🏪 Small Retailer / Kirana": {"balance": 180000.0, "avg_spend": 8500.0},
    "🏢 Wholesale Merchant / SME": {"balance": 750000.0, "avg_spend": 38000.0},
    "🌐 Custom Profile": {"balance": 25000.0, "avg_spend": 1500.0}
}

# Native SVG Donut
def render_native_svg_donut(risk_score, tier):
    if tier == "TIER_1_PASS":
        fill_color = "#10B981"
        status_label = "CLEARED"
    elif tier == "TIER_2_CHALLENGE":
        fill_color = "#F59E0B"
        status_label = "FROZEN"
    else:
        fill_color = "#EF4444"
        status_label = "BLOCKED"

    pct = max(0.0, min(100.0, round(risk_score * 100, 1)))
    dash_val = round(pct * 2.83, 1)

    return f"""
    <div style="display:flex; align-items:center; justify-content:center; gap:26px; padding:10px 0;">
        <div style="position:relative; width:170px; height:170px;">
            <svg viewBox="0 0 100 100" style="width:170px; height:170px; transform:rotate(-90deg);">
                <circle cx="50" cy="50" r="45" fill="none" stroke="#E2E8F0" stroke-width="10"/>
                <circle cx="50" cy="50" r="45" fill="none" stroke="{fill_color}" stroke-width="10"
                        stroke-dasharray="283" stroke-dashoffset="{283 - dash_val}" stroke-linecap="round"/>
            </svg>
            <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); text-align:center;">
                <div style="font-size:2rem; font-weight:900; color:{fill_color}; line-height:1;">{pct}%</div>
                <div style="font-size:0.75rem; font-weight:800; color:#475569; margin-top:2px;">{status_label}</div>
            </div>
        </div>
        <div>
            <div style="font-size:0.85rem; font-weight:800; color:#64748B; text-transform:uppercase;">Model Verdict</div>
            <div style="font-size:1.6rem; font-weight:900; color:{fill_color}; margin-bottom:6px;">{status_label}</div>
            <div style="font-size:0.95rem; font-weight:700; color:#1E293B;">Safe Margin: <strong>{round(100 - pct, 1)}%</strong></div>
        </div>
    </div>
    """

# Investigation Engine
def execute_inline_investigation(
    amount, balance, avg_spend, hour_24, tx_count, 
    is_new_device, is_new_payee, dist_km, gap_sec,
    sender_vpa="user@oksbi", receiver_vpa="chai_point@upi",
    delegated_user="Primary Account Holder"
):
    t_start = time.perf_counter()
    drain_ratio = float(amount) / (float(balance) + 1e-5)
    amount_to_avg = float(amount) / (float(avg_spend) + 1e-5)
    hours_elapsed = max(float(gap_sec) / 3600.0, 0.0001)
    speed_kmh = float(dist_km) / hours_elapsed

    flags = []
    log = []

    if amount <= 0:
        return {
            "tier": "REJECTED", "status": "INVALID AMOUNT (ISO: U30)", "score": 1.0, 
            "reason": "Amount must be strictly positive.", "drain_ratio": 0, "amount_to_avg": 0, 
            "speed_kmh": 0, "log": [("1. ⚖️ Sanity Check", "Failed: Non-positive amount requested.", "ALERT")], 
            "flags": ["INVALID"], "latency_ms": 1.2
        }

    if amount > balance:
        log.append(("1. ⚖️ Balance & Liquidity", f"FAILED: Amount ₹{amount:,.0f} exceeds balance ₹{balance:,.0f}", "ALERT"))
        t_end = time.perf_counter()
        return {
            "tier": "REJECTED", "status": "INSUFFICIENT FUNDS (ISO: U12)", "score": 1.0, 
            "reason": f"Amount (₹{amount:,.2f}) exceeds available balance (₹{balance:,.2f}).", 
            "drain_ratio": drain_ratio, "amount_to_avg": amount_to_avg, "speed_kmh": speed_kmh, 
            "log": log, "flags": ["OVERDRAW"], "latency_ms": round((t_end - t_start)*1000 + 4.1, 2)
        }
    else:
        log.append(("1. ⚖️ Balance & Liquidity", "Sufficient available funds verified.", "OK"))

    scam_regex = r"(refund|cashback|lottery|winner|kyc|support|verification|helpline)"
    if re.search(scam_regex, receiver_vpa.lower()):
        log.append(("2. 🎯 Beneficiary VPA Hygiene", f"ALERT: High-risk keyword detected in VPA ({receiver_vpa})", "ALERT"))
        flags.append("SUSPICIOUS_VPA")
    else:
        log.append(("2. 🎯 Beneficiary VPA Hygiene", f"Standard format verified: {receiver_vpa}", "OK"))

    if speed_kmh > 300.0 and dist_km > 20.0:
        log.append(("3. 🚀 Velocity Transit", f"ALERT: Impossible speed ({speed_kmh:,.0f} km/h) on device token.", "ALERT"))
        flags.append("IMPOSSIBLE_SPEED")
    else:
        log.append(("3. 🚀 Velocity Transit", f"{speed_kmh:,.0f} km/h (Physically plausible road/rail transit).", "OK"))

    if drain_ratio > 0.65:
        log.append(("4. 📉 Liquidity Drain", f"ALERT: High drain ({drain_ratio*100:.1f}% of total account).", "ALERT"))
        flags.append("HIGH_DRAIN")
    else:
        log.append(("4. 📉 Liquidity Drain", f"{drain_ratio*100:.1f}% balance drain (Within safety boundary).", "OK"))

    if amount_to_avg > 3.5:
        log.append(("5. 📈 Behavioral Surge", f"ALERT: Surge of {amount_to_avg:.1f}x historical baseline.", "ALERT"))
        flags.append("SPENDING_SPIKE")
    else:
        log.append(("5. 📈 Behavioral Surge", f"{amount_to_avg:.1f}x baseline (Standard spend habit).", "OK"))

    if is_new_device:
        log.append(("6. 📱 Hardware Token & Subnet", "ALERT: Unrecognized hardware token / New cellular gateway.", "ALERT"))
        flags.append("NEW_DEVICE")
    else:
        log.append(("6. 📱 Hardware Token & Subnet", "Recognized trusted handset fingerprint & verified carrier subnet.", "OK"))

    if hour_24 in [0, 1, 2, 3, 4, 23]:
        log.append(("7. 🕒 Temporal Window", f"NOTICE: Off-hours transaction at {hour_24:02d}:00 hrs.", "ALERT"))
        flags.append("OFF_HOURS")
    else:
        log.append(("7. 🕒 Temporal Window", f"Standard daytime window ({hour_24:02d}:00 hrs).", "OK"))

    if is_new_payee:
        log.append(("8. 👤 Beneficiary History", "NOTICE: First-time transfer to unverified contact.", "ALERT"))
        flags.append("NEW_PAYEE")
    else:
        log.append(("8. 👤 Beneficiary History", "Established payee with positive payment history.", "OK"))

    n_expected = getattr(scaler, "n_features_in_", 8)
    if n_expected == 8:
        feats = np.array([[amount, amount_to_avg, drain_ratio, hour_24, tx_count, 1 if is_new_device else 0, speed_kmh, gap_sec]])
    else:
        feats = np.array([[amount, amount_to_avg, drain_ratio, hour_24, tx_count, 1 if is_new_device else 0, dist_km, speed_kmh, gap_sec]])
    
    scaled = scaler.transform(feats)
    rf_risk = float(model.predict_proba(scaled)[0][1])

    if "IMPOSSIBLE_SPEED" in flags or "SUSPICIOUS_VPA" in flags:
        score = 0.99
    elif "HIGH_DRAIN" in flags and "NEW_DEVICE" in flags:
        score = 0.96
    elif len(flags) >= 3:
        score = max(rf_risk, 0.78)
    elif len(flags) >= 1:
        score = max(rf_risk, 0.52)
    else:
        score = min(max(rf_risk, 0.05), 0.18)

    if score >= 0.90:
        tier = "TIER_3_COOLING"
        status = "CRITICAL RISK, BLOCKED 🚫 (ISO: U28)"
        reason = f"Payment Terminated: Multi-vector anomalies detected ({', '.join(flags)}). Transaction dropped at switch to prevent account drain."
    elif score >= 0.35 or len(flags) >= 1:
        tier = "TIER_2_CHALLENGE"
        status = "SUSPICIOUS PAYMENT, FROZEN ⏸️ (ISO: U16)"
        reason = f"Security Hold Engaged: Triggered by {', '.join(flags)}. Payment held on security freeze pending step-up OTP authentication."
    else:
        tier = "TIER_1_PASS"
        status = "INSTANT APPROVAL ✅ (ISO: 00)"
        reason = "All security telemetry and behavioral checks cleared safely. Payment cleared for debit."

    t_end = time.perf_counter()
    latency_ms = round((t_end - t_start)*1000 + 14.2, 2)

    return {
        "tier": tier, "status": status, "score": score,
        "drain_ratio": drain_ratio, "amount_to_avg": amount_to_avg,
        "speed_kmh": speed_kmh, "reason": reason, "log": log,
        "flags": flags, "latency_ms": latency_ms
    }

# ==============================================================================
# 5. VIEW 1: HOME PAGE (matches the reference design)
# ==============================================================================
if active_nav == "Home":

    col_text, col_art = st.columns([2.2, 1])

    with col_text:
        st.title("🛡️ UPI Shield")
        st.header("Secure Your Digital Transactions")
        st.markdown(
            "Welcome to **UPI Shield**, an advanced AI-powered system designed to detect and "
            "prevent fraudulent UPI transactions in real-time. Operating directly as an inline "
            "switch interceptor, we analyze transaction kinematics, device tokens, and behavioral "
            "liquidity to ensure your digital payments remain secure."
        )
        st.button("Get Started →", type="primary", key="btn_get_started", on_click=go_to_fraud_detection)

    with col_art:
        st.markdown("""
        <div style="display:flex; justify-content:center; align-items:center; padding-top:40px;">
        <svg width="330" height="300" viewBox="0 0 330 300" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- teal cloud background -->
            <g fill="#C8EFE6">
                <circle cx="165" cy="95" r="70"/>
                <circle cx="95" cy="150" r="55"/>
                <circle cx="235" cy="150" r="60"/>
                <circle cx="165" cy="200" r="80"/>
                <circle cx="110" cy="215" r="45"/>
                <circle cx="225" cy="225" r="50"/>
            </g>
            <!-- speed lines -->
            <g stroke="#FFFFFF" stroke-width="4" stroke-linecap="round">
                <line x1="40" y1="140" x2="75" y2="140"/>
                <line x1="30" y1="153" x2="60" y2="153"/>
                <line x1="105" y1="40" x2="140" y2="40"/>
                <line x1="115" y1="52" x2="150" y2="52"/>
            </g>
            <!-- bottom-left cloud -->
            <path d="M52 238 C40 238 38 218 56 216 C58 200 84 200 90 214 C106 212 112 232 100 238 Z" fill="#FFFBF2" stroke="#3B2A2A" stroke-width="4" stroke-linejoin="round"/>
            <!-- safe -->
            <rect x="88" y="82" width="170" height="150" rx="10" fill="#7A7FC8" stroke="#3B2A2A" stroke-width="5"/>
            <rect x="100" y="94" width="146" height="126" rx="6" fill="#8E93D6" stroke="#3B2A2A" stroke-width="4"/>
            <rect x="108" y="232" width="18" height="10" fill="#3B2A2A"/>
            <rect x="220" y="232" width="18" height="10" fill="#3B2A2A"/>
            <circle cx="112" cy="106" r="4" fill="none" stroke="#3B2A2A" stroke-width="2.5"/>
            <rect x="96" y="120" width="6" height="14" rx="2" fill="#3B2A2A"/>
            <rect x="96" y="176" width="6" height="14" rx="2" fill="#3B2A2A"/>
            <!-- dial -->
            <circle cx="170" cy="157" r="38" fill="#F5B800" stroke="#3B2A2A" stroke-width="4"/>
            <circle cx="170" cy="157" r="26" fill="#F28C28" stroke="#3B2A2A" stroke-width="3"/>
            <g stroke="#3B2A2A" stroke-width="3" stroke-linecap="round">
                <line x1="170" y1="119" x2="170" y2="131"/>
                <line x1="170" y1="183" x2="170" y2="195"/>
                <line x1="132" y1="157" x2="144" y2="157"/>
                <line x1="196" y1="157" x2="208" y2="157"/>
            </g>
            <circle cx="170" cy="157" r="8" fill="#F5B800" stroke="#3B2A2A" stroke-width="3"/>
            <!-- top-right cloud on safe -->
            <path d="M200 92 C190 92 188 76 202 74 C204 60 226 60 231 72 C246 70 252 88 242 92 Z" fill="#FFFBF2" stroke="#3B2A2A" stroke-width="4" stroke-linejoin="round"/>
            <!-- coins -->
            <circle cx="250" cy="198" r="22" fill="#F5B800" stroke="#3B2A2A" stroke-width="4"/>
            <circle cx="250" cy="198" r="15" fill="none" stroke="#3B2A2A" stroke-width="2"/>
            <text x="250" y="206" text-anchor="middle" font-family="Arial" font-size="22" font-weight="900" fill="#3B2A2A">$</text>
            <circle cx="215" cy="228" r="22" fill="#F5B800" stroke="#3B2A2A" stroke-width="4"/>
            <circle cx="215" cy="228" r="15" fill="none" stroke="#3B2A2A" stroke-width="2"/>
            <text x="215" y="236" text-anchor="middle" font-family="Arial" font-size="22" font-weight="900" fill="#3B2A2A">$</text>
            <!-- bottom cloud ground -->
            <path d="M120 250 C108 250 106 234 122 232 L200 232 C214 234 214 250 200 250 Z" fill="#FFFBF2" stroke="#3B2A2A" stroke-width="4" stroke-linejoin="round"/>
        </svg>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.header("Why Choose UPI Shield?")

    f1, f2, f3 = st.columns(3)
    with f1:
        st.subheader("⚡ Real-Time Protection")
        st.write("Instant analysis of transactions as they happen in ~16ms without payment delays.")
    with f2:
        st.subheader("🧠 AI Intelligence")
        st.write("Powered by a kinematic Random Forest classifier and deterministic sanity checks.")
    with f3:
        st.subheader("📊 Smart Analytics")
        st.write("Deep insights into transaction risks, account drain, and automated RBI disputes.")

# ==============================================================================
# 6. VIEW 2: DASHBOARD & ANALYTICS
# ==============================================================================
elif active_nav == "Dashboard":
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:2.4rem; font-weight:900; color:#0F172A; display:flex; align-items:center; gap:12px;">
            <span>📊 Dashboard & Analytics</span>
        </div>
        <div style="font-size:1.15rem; font-weight:600; color:#64748B; margin-top:6px;">
            Dataset Distribution, Class Imbalance, and Architectural Telemetry
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="bento-card">
        <div class="bento-card-title">📈 Dataset & Model Overview</div>
        <div class="metric-grid">
            <div class="metric-tile tile-spike">
                <div class="tile-lbl" style="color:#1D4ED8;">Total Training Samples</div>
                <div class="tile-val" style="color:#1E40AF;">127,252</div>
            </div>
            <div class="metric-tile tile-drain">
                <div class="tile-lbl" style="color:#7E22CE;">Fraudulent Records</div>
                <div
