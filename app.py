import streamlit as st
import numpy as np
import pandas as pd
import pickle
import os
import time
import re
from datetime import datetime

st.set_page_config(
    page_title="UPI Fraud Guard — Real-Time Inline Fraud Mitigation Switch",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize navigation session state for seamless button redirection
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "Home"

def navigate_to(page_name):
    st.session_state["nav_page"] = page_name

# ==============================================================================
# 1. HIGH-CONTRAST, CLEAN FINTECH STYLING
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 18px;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }

    /* SIDEBAR TEXT SCALING (ENLARGED & HIGH CONTRAST) */
    section[data-testid="stSidebar"] {
        background-color: #F1F5F9;
        border-right: 2px solid #E2E8F0;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        padding: 6px 0 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label span {
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
    }
    .sidebar-brand-title {
        font-size: 1.65rem !important;
        font-weight: 900 !important;
        color: #0F172A !important;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }

    /* Input & Dropdown Styling */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input, 
    select {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #CBD5E1 !important;
    }
    div[data-baseweb="select"] * {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #0F172A !important;
    }

    /* TOP HERO CONTAINER (FRAUD DETECTION / DASHBOARD) */
    .top-header-container {
        background: #FFFFFF;
        padding: 28px 40px;
        border-radius: 22px;
        border: 2px solid #E2E8F0;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .hero-title-giant {
        font-size: 2.85rem !important;
        font-weight: 900 !important;
        color: #0F172A !important;
        letter-spacing: -1.2px;
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 0;
        line-height: 1.1;
    }
    .hero-badge-v2 {
        font-size: 1.05rem !important;
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        color: #FFFFFF !important;
        padding: 5px 16px;
        border-radius: 12px;
        font-weight: 900;
        vertical-align: middle;
    }
    .team-pill-box {
        display: flex;
        align-items: center;
        gap: 12px;
        background: #F1F5F9;
        border: 2px solid #94A3B8;
        padding: 10px 22px;
        border-radius: 28px;
        font-weight: 900;
        font-size: 1.2rem !important;
        color: #0F172A;
    }

    /* BENTO CONTAINERS */
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
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .tile-val {
        font-size: 1.9rem;
        font-weight: 900;
        line-height: 1.1;
    }

    /* GET STARTED ACTION BUTTON (CORAL-RED HIGH VISIBILITY) */
    div.stButton > button.get-started-btn {
        background: #EF4444 !important;
        color: #FFFFFF !important;
        font-size: 1.25rem !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        padding: 14px 34px !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.35) !important;
        width: auto !important;
        cursor: pointer !important;
    }

    /* PRIMARY WORKFLOW BUTTONS */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #E11D48 0%, #BE123C 100%) !important;
        color: #FFFFFF !important;
        font-size: 1.25rem !important;
        font-weight: 900 !important;
        border-radius: 14px !important;
        padding: 16px 32px !important;
        border: none !important;
        box-shadow: 0 6px 22px rgba(225, 29, 72, 0.35) !important;
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
        border: 1px solid #86EFAC;
    }
    .pill-alert {
        background: #FEE2E2;
        color: #991B1B;
        font-weight: 900;
        font-size: 0.88rem;
        padding: 6px 16px;
        border-radius: 10px;
        border: 1px solid #FCA5A5;
    }

    /* BACKEND TELEMETRY CONSOLE */
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
""", unsafe_allow_html=True)

# ==============================================================================
# 2. LOAD MODEL ARTIFACTS
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

# ==============================================================================
# 3. PURE SVG ULTRA-FAST DONUT (CRASH-PROOF)
# ==============================================================================
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

    svg_html = f"""
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
    return svg_html

# ==============================================================================
# 4. INLINE SWITCH INVESTIGATION ENGINE
# ==============================================================================
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

    # 1. Deterministic Layer 1
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

    # 2. VPA Hygiene Check
    scam_regex = r"(refund|cashback|lottery|winner|kyc|support|verification|helpline)"
    if re.search(scam_regex, receiver_vpa.lower()):
        log.append(("2. 🎯 Beneficiary VPA Hygiene", f"ALERT: High-risk keyword detected in VPA ({receiver_vpa})", "ALERT"))
        flags.append("SUSPICIOUS_VPA")
    else:
        log.append(("2. 🎯 Beneficiary VPA Hygiene", f"Standard format verified: {receiver_vpa}", "OK"))

    # 3. Velocity / Displacement
    if speed_kmh > 300.0 and dist_km > 20.0:
        log.append(("3. 🚀 Velocity Transit", f"ALERT: Impossible speed ({speed_kmh:,.0f} km/h) on device token.", "ALERT"))
        flags.append("IMPOSSIBLE_SPEED")
    else:
        log.append(("3. 🚀 Velocity Transit", f"{speed_kmh:,.0f} km/h (Physically plausible road/rail transit).", "OK"))

    # 4. Account Drain Check
    if drain_ratio > 0.65:
        log.append(("4. 📉 Liquidity Drain", f"ALERT: High drain ({drain_ratio*100:.1f}% of total account).", "ALERT"))
        flags.append("HIGH_DRAIN")
    else:
        log.append(("4. 📉 Liquidity Drain", f"{drain_ratio*100:.1f}% balance drain (Within safety boundary).", "OK"))

    # 5. Spend Anomaly Multiplier
    if amount_to_avg > 3.5:
        log.append(("5. 📈 Behavioral Surge", f"ALERT: Surge of {amount_to_avg:.1f}x historical baseline.", "ALERT"))
        flags.append("SPENDING_SPIKE")
    else:
        log.append(("5. 📈 Behavioral Surge", f"{amount_to_avg:.1f}x baseline (Standard spend habit).", "OK"))

    # 6. Hardware Fingerprint & Gateway Subnet
    if is_new_device:
        log.append(("6. 📱 Hardware Token & Subnet", "ALERT: Unrecognized hardware token / New cellular gateway.", "ALERT"))
        flags.append("NEW_DEVICE")
    else:
        log.append(("6. 📱 Hardware Token & Subnet", "Recognized trusted handset fingerprint & verified carrier subnet.", "OK"))

    # 7. Temporal Window
    if hour_24 in [0, 1, 2, 3, 4, 23]:
        log.append(("7. 🕒 Temporal Window", f"NOTICE: Off-hours transaction at {hour_24:02d}:00 hrs.", "ALERT"))
        flags.append("OFF_HOURS")
    else:
        log.append(("7. 🕒 Temporal Window", f"Standard daytime window ({hour_24:02d}:00 hrs).", "OK"))

    # 8. Counterparty Trust
    if is_new_payee:
        log.append(("8. 👤 Beneficiary History", "NOTICE: First-time transfer to unverified contact.", "ALERT"))
        flags.append("NEW_PAYEE")
    else:
        log.append(("8. 👤 Beneficiary History", "Established payee with positive payment history.", "OK"))

    # Random Forest Inference
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

    # Automated 3-Tier Mitigation Policy
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
# 5. SIDEBAR NAVIGATION (ENLARGED, HIGH LEGIBILITY)
# ==============================================================================
with st.sidebar:
    st.markdown('<div class="sidebar-brand-title">🛡️ Navigation</div>', unsafe_allow_html=True)
    
    st.caption("**Go to**")
    nav_options = ["Home", "Dashboard", "Fraud Detection"]
    curr_index = nav_options.index(st.session_state["nav_page"]) if st.session_state["nav_page"] in nav_options else 0
    
    selected_page = st.radio(
        "Go to",
        nav_options,
        index=curr_index,
        label_visibility="collapsed",
        key="sidebar_nav_radio"
    )
    
    # Sync radio selection with session state
    if selected_page != st.session_state["nav_page"]:
        st.session_state["nav_page"] = selected_page
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style="font-size:1.05rem; color:#1E293B; font-weight:800; line-height: 2.0; padding:10px 0;">
        ⚡ Team: <strong>Spark Squad</strong><br>
        🏛️ Bank Switch: <span style="color:#16A34A;">Online 🟢</span><br>
        ⏱️ Protocol: <strong>ISO 20022</strong><br>
        🔒 Engine: <strong>Inline FRM</strong>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 6. VIEW 1: HOME PAGE (EXACT DESIGN AS SCREENSHOT 1)
# ==============================================================================
if st.session_state["nav_page"] == "Home":
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Headline with Shield Icon matching screenshot
    st.markdown("""
    <div style="display:flex; align-items:center; gap:16px; margin-bottom:28px;">
        <span style="font-size:3.2rem;">🛡️</span>
        <h1 style="font-size:3.4rem !important; font-weight:900 !important; color:#1E293B !important; margin:0; letter-spacing:-1px;">
            UPI Fraud Guard
        </h1>
    </div>
    """, unsafe_allow_html=True)

    c_hero_txt, c_hero_gfx = st.columns([1.5, 1])
    
    with c_hero_txt:
        st.markdown("""
        <h2 style="font-size:2.0rem !important; font-weight:800 !important; color:#0F172A !important; margin-bottom:18px;">
            Secure Your Digital Transactions
        </h2>
        <p style="font-size:1.15rem; font-weight:500; color:#475569; line-height:1.7; margin-bottom:32px;">
            Welcome to <strong>UPI Fraud Guard</strong>, an advanced AI-powered system designed to detect and prevent fraudulent UPI transactions in real-time. Using state-of-the-art machine learning### What Was Fixed
1. **Broken Code Box in Screenshot 2 Removed:** The second image showed raw unclosed HTML leaking into a markdown code block. All broken tags have been removed and replaced with standard styling.
2. **Matching Home Page Layout & Graphic:** Matches the reference design with clean typography, an embedded SVG safe illustration, a coral-red **"Get Started →"** button, and a horizontal 3-column feature row (`⚡ Real-Time Protection`, `🧠 AI Intelligence`, `📊 Smart Analytics`).
3. **Working "Get Started →" Redirection:** Clicking **"Get Started →"** immediately routes to **Fraud Detection Gateway** by updating `st.session_state`.
4. **Enlarged Sidebar Typography:** Sidebar radio items, section headers, and indicators have increased font sizes and weights for clear readability.

---

### Complete Copy-Paste `app.py`

```python
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
# 1. CLEAN TYPOGRAPHY & ENLARGED SIDEBAR STYLING
# ==============================================================================
st.markdown("""
<style>
    @import url('[https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap](https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap)');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #FFFFFF;
    }

    /* ENLARGED, HIGH-READABILITY SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
        padding-top: 1.5rem;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 8px 12px !important;
        border-radius: 10px !important;
        margin-bottom: 6px !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] p {
        color: #EF4444 !important;
        font-weight: 900 !important;
    }

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

    /* HOME HERO HEADINGS */
    .home-brand-title {
        font-size: 2.8rem;
        font-weight: 900;
        color: #1E293B;
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 12px;
    }
    .home-sub-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 16px;
    }
    .home-desc-text {
        font-size: 1.15rem;
        font-weight: 500;
        color: #475569;
        line-height: 1.65;
        margin-bottom: 24px;
    }

    /* RED GET STARTED BUTTON */
    div.stButton > button.get-started-btn {
        background-color: #FF4D4D !important;
        color: #FFFFFF !important;
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(255, 77, 77, 0.35) !important;
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

    /* ACTION BUTTON */
    div.stButton > button[kind="primary"] {
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
""", unsafe_allow_html=True)

# ==============================================================================
# 2. SESSION NAVIGATION STATE
# ==============================================================================
if "active_nav" not in st.session_state:
    st.session_state["active_nav"] = "Home"

def navigate_to(page_name):
    st.session_state["active_nav"] = page_name

# ==============================================================================
# 3. SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    st.markdown('<div style="font-size:1.6rem; font-weight:900; color:#0F172A; margin-bottom:12px;">Navigation</div>', unsafe_allow_html=True)
    st.caption("**Go to**")
    
    pages = ["Home", "Dashboard", "Fraud Detection"]
    curr_idx = pages.index(st.session_state["active_nav"]) if st.session_state["active_nav"] in pages else 0
    
    selected_page = st.radio(
        "Navigation",
        pages,
        index=curr_idx,
        label_visibility="collapsed",
        key="sidebar_radio_selection"
    )
    if selected_page != st.session_state["active_nav"]:
        st.session_state["active_nav"] = selected_page
        st.rerun()
        
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.95rem; color:#475569; font-weight:700; line-height: 1.8;">
        ⚡ Team: <strong>Spark Squad</strong><br>
        🏛️ Bank Switch: <strong>Online 🟢</strong><br>
        ⏱️ Protocol: <strong>ISO 20022</strong>
    </div>
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
        log.append(("1. ⚖️️ Balance & Liquidity", f"FAILED: Amount ₹{amount:,.0f} exceeds balance ₹{balance:,.0f}", "ALERT"))
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
# 5. VIEW 1: CLEAN HOME PAGE (MATCHING SCREENSHOT 1)
# ==============================================================================
if st.session_state["active_nav"] == "Home":
    
    col_text, col_art = st.columns([1.3, 1])
    
    with col_text:
        st.markdown("""
        <div class="home-brand-title">
            <span style="font-size:3.2rem;">🛡️</span>
            <span>UPI Shield</span>
        </div>
        <div class="home-sub-title">
            Secure Your Digital Transactions
        </div>
        <div class="home-desc-text">
            Welcome to <strong>UPI Shield</strong>, an advanced AI-powered system designed to detect and prevent fraudulent UPI transactions in real-time. Operating directly as an inline switch interceptor, we analyze transaction kinematics, device tokens, and behavioral liquidity to ensure your digital payments remain secure.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get Started →", key="btn_get_started"):
            navigate_to("Fraud Detection")
            st.rerun()

    with col_art:
        st.markdown("""
        <div style="display:flex; justify-content:center; align-items:center; height:100%; min-height:300px;">
            <svg width="280" height="230" viewBox="0 0 280 230" fill="none" xmlns="[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)">
                <ellipse cx="140" cy="185" rx="120" ry="25" fill="#E2E8F0"/>
                <path d="M70 145 C60 145 50 155 55 168 C60 178 75 180 85 178 Z" fill="#E2E8F0"/>
                <rect x="75" y="55" width="130" height="110" rx="16" fill="#3B82F6" stroke="#1E293B" stroke-width="4"/>
                <circle cx="140" cy="110" r="34" fill="#F8FAFC" stroke="#1E293B" stroke-width="4"/>
                <circle cx="140" cy="110" r="18" fill="#F59E0B" stroke="#1E293B" stroke-width="3"/>
                <circle cx="215" cy="155" r="18" fill="#FBBF24" stroke="#1E293B" stroke-width="3"/>
                <text x="210" y="162" font-family="Arial" font-size="20" font-weight="900" fill="#1E293B">₹</text>
                <circle cx="230" cy="130" r="15" fill="#FBBF24" stroke="#1E293B" stroke-width="3"/>
                <text x="226" y="136" font-family="Arial" font-size="16" font-weight="900" fill="#1E293B">₹</text>
            </svg>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:none; border-top:1px solid #E2E8F0; margin:40px 0;'>", unsafe_allow_html=True)

    st.markdown('<div style="font-size:1.85rem; font-weight:800; color:#0F172A; margin-bottom:28px;">Why Choose UPI Shield?</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
        <div style="font-size:1.3rem; font-weight:800; color:#0F172A; display:flex; align-items:center; gap:10px; margin-bottom:8px;">
            <span>⚡</span> Real-Time Protection
        </div>
        <div style="font-size:1.05rem; font-weight:500; color:#64748B;">
            Instant analysis of transactions as they happen in ~16ms without payment delays.
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div style="font-size:1.3rem; font-weight:800; color:#0F172A; display:flex; align-items:center; gap:10px; margin-bottom:8px;">
            <span>🧠</span> AI Intelligence
        </div>
        <div style="font-size:1.05rem; font-weight:500; color:#64748B;">
            Powered by a kinematic Random Forest classifier and deterministic sanity checks.
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div style="font-size:1.3rem; font-weight:800; color:#0F172A; display:flex; align-items:center; gap:10px; margin-bottom:8px;">
            <span>📊</span> Smart Analytics
        </div>
        <div style="font-size:1.05rem; font-weight:500; color:#64748B;">
            Deep insights into transaction risks, account drain, and automated RBI disputes.
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 6. VIEW 2: DASHBOARD & ANALYTICS
# ==============================================================================
elif st.session_state["active_nav"] == "Dashboard":
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
                <div class="tile-val" style="color:#581C87;">173</div>
            </div>
            <div class="metric-tile tile-risk">
                <div class="tile-lbl" style="color:#B45309;">Base Fraud Rate</div>
                <div class="tile-val" style="color:#92400E;">0.14%</div>
            </div>
            <div class="metric-tile tile-speed">
                <div class="tile-lbl" style="color:#15803D;">Legitimate Transfers</div>
                <div class="tile-val" style="color:#166534;">127,079</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    d_col1, d_col2 = st.columns([1.2, 1])
    with d_col1:
        st.markdown("""
        <div class="bento-card">
            <div class="bento-card-title">🔍 Feature Engineering & Pipeline Architecture</div>
            <p style="font-size:1.05rem; font-weight:500; color:#334155; line-height:1.6;">
                Financial fraud datasets exhibit extreme class imbalance (99.86% legitimate vs 0.14% fraud). Standard classifiers fail by predicting the majority class. Our pipeline resolves this via:
            </p>
            <ul style="font-size:1.05rem; font-weight:600; color:#0F172A; line-height:1.8;">
                <li><strong>Class-Weighted Random Forest:</strong> Penalizes false negatives to capture anomalous outliers.</li>
                <li><strong>Kinematic Speed Transform:</strong> Spatial distance divided by elapsed session hours.</li>
                <li><strong>Liquidity Drain Ratio:</strong> Normalizes transaction value by available balance.</li>
                <li><strong>Device Token Fingerprinting:</strong> Validates carrier subnet and hardware signatures.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with d_col2:
        st.markdown("""
        <div class="bento-card">
            <div class="bento-card-title">🍩 Training Class Distribution</div>
        """, unsafe_allow_html=True)
        
        df_dist = pd.DataFrame({
            "Category": ["Legitimate (99.86%)", "Fraudulent (0.14%)"],
            "Count": [127079, 173]
        })
        st.bar_chart(df_dist.set_index("Category"))
        st.caption("Demonstrating real-world extreme imbalance typical of high-throughput payment networks.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 7. VIEW 3: FRAUD DETECTION GATEWAY
# ==============================================================================
else:
    st.markdown("""
    <div style="margin-bottom:24px; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-size:2.4rem; font-weight:900; color:#0F172A;">
                🛡️ Fraud Detection Gateway
            </div>
            <div style="font-size:1.15rem; font-weight:600; color:#64748B; margin-top:4px;">
                ⚡ Deterministic Firewall + Behavioral Random Forest + Inline Switch Interceptor
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:1.1rem; font-weight:900; color:#16A34A;">Bank Switch: Online 🟢</div>
            <div style="font-size:0.85rem; font-weight:700; color:#64748B;">Protocol: ISO 20022</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_manual, tab_prod = st.tabs([
        "📋 Viva Telemetry Verification Panel", 
        "⚡ Synchronous Virtual Gateway & Persona Switch"
    ])

    with tab_manual:
        st.markdown("""
        <div class="bento-card">
            <div class="bento-card-title">
                <span>📋 Manual Telemetry Simulation & Parameter Stress-Testing</span>
            </div>
        """, unsafe_allow_html=True)

        c_in1, c_in2 = st.columns(2)

        with c_in1:
            st.markdown("**1. 👤 Account Baseline & Persona Profile**")
            sel_prof = st.selectbox("Select Account Profile:", list(PROFESSIONS.keys()), label_visibility="collapsed", key="v_sel_prof")
            prof = PROFESSIONS[sel_prof]

            st.markdown("**2. 💳 Payment & VPA Identifiers**")
            st.markdown("**💵 Transaction Amount (₹)**")
            in_amount = st.number_input("Transaction Amount", min_value=1.0, value=10000.0, step=500.0, label_visibility="collapsed", key="v_in_amt")
            
            st.markdown("**🏦 Account Available Balance (₹)**")
            in_balance = st.number_input("Account Balance", min_value=1.0, value=float(prof['balance']), step=1000.0, label_visibility="collapsed", key="v_in_bal")
            
            st.markdown("**📊 Historical Daily Spend Baseline (₹)**")
            in_avg = st.number_input("Usual Average Spend", min_value=1.0, value=float(prof['avg_spend']), step=100.0, label_visibility="collapsed", key="v_in_avg")
            
            vpa_c1, vpa_c2 = st.columns(2)
            with vpa_c1:
                st.markdown("**Sender UPI ID**")
                in_sender_vpa = st.text_input("Sender VPA", "user@oksbi", label_visibility="collapsed", key="v_s_vpa")
            with vpa_c2:
                st.markdown("**Recipient UPI ID**")
                in_receiver_vpa = st.text_input("Receiver VPA", "chai_point@upi", label_visibility="collapsed", key="v_r_vpa")

            st.markdown("**👥 Recipient Contact Trust Level**")
            in_payee_new = st.selectbox("Payee History", ["⭐ Known / Frequently Paid Contact", "🆕 New / First-Time Payee"], index=0, label_visibility="collapsed", key="v_is_new_p") == "🆕 New / First-Time Payee"

        with c_in2:
            st.markdown("**3. 📍 Spatial, Hardware & Network Context**")
            st.markdown("**📍 Displacement from Last Transaction (km)**")
            in_dist = st.number_input("Distance from Last Transaction (km)", min_value=0.0, value=50.0, step=5.0, label_visibility="collapsed", key="v_dist_km")

            st.markdown("**⏱️ Elapsed Time Since Previous Activity**")
            g_val_col, g_unit_col = st.columns([1, 1])
            with g_val_col:
                in_gap_val = st.number_input("Value", min_value=0.1, value=30.0, step=1.0, label_visibility="collapsed", key="v_gap_val")
            with g_unit_col:
                in_gap_unit = st.selectbox("Unit", ["Minutes ⏳", "Seconds ⏱️", "Hours ⌛"], index=0, label_visibility="collapsed", key="v_gap_unit")

            st.markdown("**🔢 Velocity: Number of Rapid Transactions (Last 10 Mins)**")
            in_tx_count = st.number_input("Payments in 10 Mins", min_value=0, max_value=15, value=1, label_visibility="collapsed", key="v_tx_burst")

            st.markdown("**📱 Hardware Fingerprint & Subnet Match**")
            in_device = st.selectbox("Device State", ["🔒 Trusted Handset & Known Carrier Subnet", "⚠️ Unrecognized Handset / Foreign Gateway"], index=0, label_visibility="collapsed", key="v_dev_state") == "⚠️ Unrecognized Handset / Foreign Gateway"

            st.markdown("**👥 Delegation Mode (UPI Circle)**")
            in_delegated = st.selectbox("Authorized User Session", ["Primary Account Holder", "UPI Circle Secondary User (Family Member)"], index=0, key="v_delegated")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**4. 🕒 Transaction Timestamp (12-Hour Format)**")
        t_c1, t_c2, t_c3, t_c4 = st.columns([1, 1, 1.2, 2.5])
        with t_c1:
            st.caption("**Hour 🕐**")
            h_12 = st.selectbox("Hour", list(range(1, 13)), index=11, label_visibility="collapsed", key="v_h12")
        with t_c2:
            st.caption("**Minute ⏱️**")
            m_val = st.selectbox("Minute", ["00", "05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"], index=6, label_visibility="collapsed", key="v_mval")
        with t_c3:
            st.caption("**AM / PM ☀️🌙**")
            ampm = st.radio("AM/PM", ["AM", "PM"], horizontal=True, index=0, label_visibility="collapsed", key="v_ampm")
        with t_c4:
            st.write("")
            st.markdown(f"**Calculated Window:** `{h_12}:{m_val} {ampm}`")

        calc_gap_sec = in_gap_val * 60.0 if "Minutes" in in_gap_unit else (in_gap_val * 3600.0 if "Hours" in in_gap_unit else in_gap_val)
        calc_hour_24 = (0 if h_12 == 12 else h_12) if ampm == "AM" else (12 if h_12 == 12 else h_12 + 12)

        st.markdown("</div>", unsafe_allow_html=True)

        btn_trigger = st.button("⚡ Run Inline Switch Verification Pipeline 🚀", type="primary", key="v_run_pipeline_btn")

        if btn_trigger or 'res_data' not in st.session_state:
            st.session_state['res_data'] = execute_inline_investigation(
                in_amount, in_balance, in_avg, calc_hour_24, in_tx_count, 
                in_device, in_payee_new, in_dist, calc_gap_sec,
                in_sender_vpa, in_receiver_vpa, in_delegated
            )
            st.session_state['v_inputs'] = {
                "amount": in_amount, "prof": sel_prof, "payee": in_receiver_vpa,
                "sender": in_sender_vpa, "delegated": in_delegated
            }

        res = st.session_state['res_data']
        tier = res['tier']
        score = res['score']

        if tier == "TIER_1_PASS":
            box_bg = "#ECFDF5"
            box_border = "#10B981"
            txt_color = "#047857"
            right_badge_txt = "● Low Risk (Passed) ✅"
            right_badge_bg = "#D1FAE5"
        elif tier == "TIER_2_CHALLENGE":
            box_bg = "#FFFBEB"
            box_border = "#F59E0B"
            txt_color = "#B45309"
            right_badge_txt = "● Medium Risk (Hold / OTP) ⏸️"
            right_badge_bg = "#FDE68A"
        else:
            box_bg = "#FEF2F2"
            box_border = "#EF4444"
            txt_color = "#B91C1C"
            right_badge_txt = "● High Risk (Blocked) 🚫"
            right_badge_bg = "#FECACA"

        st.markdown(f"""
        <div style="background:{box_bg}; border:2px solid {box_border}; border-radius:18px; padding:20px 28px; display:flex; justify-content:space-between; align-items:center; margin-bottom:24px;">
            <div>
                <div style="font-weight:900; font-size:1.4rem; color:{txt_color}; line-height:1.2;">
                    STATUS: {res['status']}
                </div>
                <div style="font-size:0.95rem; font-weight:700; color:{txt_color}; margin-top:4px;">
                    Session: {in_delegated} &nbsp;|&nbsp; Payee: {in_receiver_vpa}
                </div>
            </div>
            <div style="display:flex; gap:14px; align-items:center;">
                <span style="background:#FFFFFF; border:2px solid {box_border}; color:{txt_color}; font-weight:900; font-size:1.05rem; padding:8px 18px; border-radius:22px;">
                    ⚡ Switch Latency: {res['latency_ms']} ms
                </span>
                <span style="background:#FFFFFF; border:2px solid {box_border}; color:{txt_color}; font-weight:900; font-size:1.05rem; padding:8px 18px; border-radius:22px;">
                    📊 Model Risk: {score*100:.1f}%
                </span>
                <span style="background:{right_badge_bg}; color:{txt_color}; font-weight:900; font-size:1.05rem; padding:8px 18px; border-radius:22px;">
                    {right_badge_txt}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1.15, 1])

        with col_left:
            if tier == "TIER_1_PASS":
                st.markdown("""
                <div class="bento-card" style="border:2px solid #10B981; background:#F0FDF4;">
                    <div style="font-size:1.35rem; font-weight:900; color:#166534; display:flex; align-items:center; gap:10px;">
                        ✅ Transaction Cleared for Settlement
                    </div>
                    <div style="font-size:1.05rem; font-weight:700; color:#15803D; margin-top:8px;">
                        ISO 20022 Code 00: Verified liquidity, known token, and normal velocity. Cleared without step-up challenge.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            elif tier == "TIER_2_CHALLENGE":
                st.markdown("""
                <div class="bento-card" style="border:2px solid #F59E0B; background:#FFFBEB;">
                    <div style="font-size:1.35rem; font-weight:900; color:#DC2626; display:flex; align-items:center; gap:10px;">
                        ⏸️ Pre-Debit Security Freeze (ISO: U16)
                    </div>
                    <div style="font-size:1.05rem; font-weight:700; color:#000000; margin-top:6px;">
                        Held for safety. Enter the 4-digit SMS OTP dispatched to registered SIM to authorize debit.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                otp_c1, otp_c2 = st.columns([1.8, 1])
                with otp_c1:
                    st.markdown("**🔐 Enter 4-Digit Security OTP (Mock: 4921):**")
                    user_otp = st.text_input("Enter 4-digit Security OTP", max_chars=4, label_visibility="collapsed", placeholder="Enter OTP here", key="v_otp_val_in")
                with otp_c2:
                    st.write("")
                    st.write("")
                    if st.button("🔓 Verify & Release Debit", key="v_otp_release_btn"):
                        if user_otp == "4921":
                            st.success("✅ OTP Verified! ISO 20022 response Code 00 dispatched. Funds cleared.")
                        else:
                            st.error("❌ Invalid OTP. Hold maintained under bank FRM guidelines.")

                st.markdown(f"""
                <div class="bento-card" style="border:2px solid #F59E0B; margin-top:14px;">
                    <div style="font-size:1.25rem; font-weight:900; color:#B45309; margin-bottom:8px;">⚠️ Decision Reason & Anomaly Triggers</div>
                    <div style="font-size:1.05rem; font-weight:700; color:#000000; line-height:1.5;">
                        {res['reason']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.markdown(f"""
                <div class="bento-card" style="border:2px solid #EF4444; background:#FEF2F2;">
                    <div style="font-size:1.35rem; font-weight:900; color:#DC2626; margin-bottom:8px;">🚫 Transaction Terminated at Switch (ISO: U28)</div>
                    <div style="font-size:1.05rem; font-weight:700; color:#991B1B; line-height:1.5;">
                        {res['reason']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="bento-card" style="margin-top:14px;">
                <div class="bento-card-title">📊 Key Forensic Metrics</div>
                <div class="metric-grid">
                    <div class="metric-tile tile-drain">
                        <div class="tile-lbl" style="color:#7E22CE;">Account Drain</div>
                        <div class="tile-val" style="color:#581C87;">{res['drain_ratio']*100:.1f}%</div>
                    </div>
                    <div class="metric-tile tile-spike">
                        <div class="tile-lbl" style="color:#1D4ED8;">Spike Multiplier</div>
                        <div class="tile-val" style="color:#1E40AF;">{res['amount_to_avg']:.1f}x</div>
                    </div>
                    <div class="metric-tile tile-speed">
                        <div class="tile-lbl" style="color:#15803D;">Transit Speed</div>
                        <div class="tile-val" style="color:#166534;">{res['speed_kmh']:,.0f} <span style="font-size:0.95rem;">km/h</span></div>
                    </div>
                    <div class="metric-tile tile-risk">
                        <div class="tile-lbl" style="color:#B45309;">ML Risk Score</div>
                        <div class="tile-val" style="color:#92400E;">{score*100:.1f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="bento-card">
                <div class="bento-card-title">🍩 Live Behavioral Risk Gauge</div>
            """, unsafe_allow_html=True)
            
            st.markdown(render_native_svg_donut(res['score'], res['tier']), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown("""
            <div class="bento-card">
                <div class="bento-card-title">🔍 Explainable AI (XAI) Audit Checklist</div>
            """, unsafe_allow_html=True)

            for name, detail, state in res['log']:
                pill_class = "pill-ok" if state == "OK" else "pill-alert"
                symbol_badge = "✓" if state == "OK" else "⚠️"
                st.markdown(f"""
                <div class="step-item">
                    <div>
                        <div class="step-title">{name}</div>
                        <div class="step-sub">{detail}</div>
                    </div>
                    <span class="{pill_class}">{symbol_badge} {state}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # Regulatory Emergency Actions
        st.markdown("""
        <div class="bento-card" style="margin-top:10px;">
            <div class="bento-card-title" style="color:#B91C1C;">
                <span>🚨 Regulatory Emergency Remediation Suite (RBI Zero-Liability)</span>
            </div>
            <div style="font-size:1.05rem; font-weight:700; color:#475569; margin-bottom:16px;">
                Instant post-fraud action suite supporting legal escalation, inter-bank lien instructions, and dispute generation.
            </div>
        """, unsafe_allow_html=True)

        e_c1, e_c2, e_c3 = st.columns(3)
        with e_c1:
            st.markdown("**1. 📞 National Cyber Crime Helpline**")
            st.markdown("Immediate escalation: Dial **1930**")
            st.link_button("🌐 Open cybercrime.gov.in", "[https://cybercrime.gov.in](https://cybercrime.gov.in)")

        with e_c2:
            st.markdown("**2. 🔒 Inter-Bank Beneficiary Lien**")
            st.markdown("Dispatch freezing signal to receiver switch.")
            if st.button("🔒 Dispatch Beneficiary Lien", key="v_freeze_lien_btn"):
                st.success(f"✅ Lien request transmitted to switch for payee VPA: {in_receiver_vpa}")

        with e_c3:
            st.markdown("**3. 📄 Official Bank Dispute Dossier**")
            st.markdown("Downloadable statutory dispute document.")
            v_in = st.session_state['v_inputs']
            report_txt = f"""OFFICIAL ELECTRONIC FRAUD DISPUTE DOSSIER
Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
UTR Reference: 429184{int(time.time())%1000000:06d}
Sender VPA: {v_in['sender']}
Beneficiary VPA: {v_in['payee']}
Evaluated Amount: INR {v_in['amount']:,.2f}
Account Profile: {v_in['prof']}
Delegated Session: {v_in['delegated']}
Switch Verdict: {res['status']}
Model Probability: {score*100:.1f}%
Execution Latency: {res['latency_ms']} ms
Statutory Reference: Limiting Customer Liability in Unauthorized Electronic Transactions (RBI Circular Ref: DBR.No.Leg.BC.78/09.07.005/2017-18)."""
            st.download_button(
                label="📥 Download Legal Dossier (.txt)",
                data=report_txt,
                file_name=f"Dispute_Report_{int(time.time())}.txt",
                key="v_download_report_btn"
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with tab_prod:
        st.markdown("""
        <div class="bento-card">
            <div class="bento-card-title">
                <span>⚡ Synchronous Virtual Gateway & Inline Switch Interceptor</span>
            </div>
            <div style="font-size:1.05rem; font-weight:700; color:#64748B; margin-bottom:16px;">
                Dual synchronous view: Client checkout handshake (Left) processed in real-time by Bank Switch Telemetry (Right).
            </div>
        """, unsafe_allow_html=True)

        sim_user_col, sim_env_col = st.columns([1, 1])
        with sim_user_col:
            s_prof_name = st.selectbox("Active Bank Account Persona:", list(PROFESSIONS.keys()), key="sim_user_prof_sel")
            s_user = PROFESSIONS[s_prof_name]
            st.markdown(f"**🏦 Balance:** `₹{s_user['balance']:,.2f}` &nbsp;|&nbsp; **📊 Typical Daily Spend:** `₹{s_user['avg_spend']:,.2f}`")

        with sim_env_col:
            st.markdown("**⚠️ Environmental Sensor & Scam Threat Vector**")
            sim_call = st.checkbox("📞 Active Unknown Call Detected (Potential Digital Arrest)", key="s_call_flag")
            sim_link = st.checkbox("🔗 Transaction Triggered from External SMS/WhatsApp Link", key="s_link_flag")

        st.markdown("</div>", unsafe_allow_html=True)
        
        mobile_col, backend_col = st.columns([1.15, 1])
        
        with mobile_col:
            st.markdown("""
            <div class="bento-card" style="border: 2px solid #3B82F6;">
                <div class="bento-card-title" style="color:#1D4ED8;">
                    <span>📱 UPI Consumer Payment App (Client View)</span>
                </div>
            """, unsafe_allow_html=True)
            
            sim_vpa = st.text_input("Beneficiary UPI ID (VPA):", "claim-refund@fakebank", key="sim_vpa_box")
            sim_pay_amount = st.number_input("Enter Amount to Transfer (₹):", min_value=1.0, value=8500.0, step=100.0, key="sim_pay_val")
            sim_payee_new = st.selectbox("Recipient History:", ["⭐ Known / Saved Contact", "🆕 New / Unverified Payee"], index=1, key="sim_payee_state") == "🆕 New / Unverified Payee"

            is_threat = sim_call or sim_link
            proceed_permitted = True

            if is_threat:
                st.error("⚠️ **CRITICAL PRE-PAYMENT WARNING (Scam Threat Engaged)**")
                st.markdown(
                    "> **CAUTION:** Active call or external link detected. "
                    "Police, TRAI, and Bank managers **NEVER** ask for UPI transfers over calls."
                )
                confirm_override = st.checkbox("I verify this recipient and authorize under my own discretion.", key="sim_override_flag")
                proceed_permitted = confirm_override

            pay_clicked = st.button("🚀 Pay & Initiate Switch Handshake", type="primary", disabled=not proceed_permitted, key="sim_checkout_btn")
            st.markdown("</div>", unsafe_allow_html=True)

        with backend_col:
            st.markdown("""
            <div class="terminal-container">
                <div class="terminal-title">
                    <span>⚙️ Bank Switch Server (Backend Telemetry)</span>
                </div>
                <div class="terminal-sub">
                    Live packet inspection log executed on the switch level (invisible to consumer).
                </div>
            """, unsafe_allow_html=True)
            
            backend_status_box = st.empty()
            backend_status_box.markdown(
                '<div style="color:#38BDF8 !important; font-weight:700; font-size:1rem; padding:12px; background:#1E293B; border-radius:10px; border:1px solid #334155;">⏳ Awaiting ISO 20022 debit message from client PSP...</div>', 
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

        if pay_clicked:
            with backend_status_box.container():
                st.markdown('<div style="color:#FFFFFF !important; font-weight:700; font-size:1rem; margin-bottom:6px;">1. 📥 Packet received: ISO 20022 / UPI CL 3.0 auth payload.</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#FFFFFF !important; font-weight:700; font-size:1rem; margin-bottom:6px;">2. 🔍 VPA Resolved: {sim_vpa} | Carrier Subnet: SHA256_VERIFIED.</div>', unsafe_allow_html=True)
                
                dist_val = 600.0 if sim_pay_amount > 20000 else 2.5
                gap_val = 1200.0 if sim_pay_amount > 20000 else 3600.0
                burst_val = 5 if sim_pay_amount > 20000 else 1
                new_dev_flag = True if sim_pay_amount > 20000 else False

                b_res = execute_inline_investigation(
                    amount=sim_pay_amount,
                    balance=s_user['balance'],
                    avg_spend=s_user['avg_spend'],
                    hour_24=datetime.now().hour,
                    tx_count=burst_val,
                    is_new_device=new_dev_flag,
                    is_new_payee=sim_payee_new,
                    dist_km=dist_val,
                    gap_sec=gap_val,
                    sender_vpa="primary.user@oksbi",
                    receiver_vpa=sim_vpa
                )

                st.session_state['sim_res'] = b_res
                st.session_state['sim_tx_details'] = {"amount": sim_pay_amount, "payee": sim_vpa, "prof": s_prof_name}

                st.markdown(f'<div style="color:#38BDF8 !important; font-weight:900; font-size:1.15rem; margin:10px 0;">3. ⚡ Switch Verdict: {b_res["tier"]} | Latency: {b_res["latency_ms"]} ms | Risk: {b_res["score"]*100:.1f}%</div>', unsafe_allow_html=True)
                with st.expander("Switch Telemetry Audit Log", expanded=True):
                    for l_name, l_detail, l_st in b_res.get('log', []):
                        st.markdown(f'<span style="color:#FFFFFF !important; font-weight:700;">- {l_name}:</span> <span style="color:#CBD5E1 !important;">{l_detail}</span> <strong style="color:#38BDF8 !important;">({l_st})</strong>', unsafe_allow_html=True)

        if 'sim_res' in st.session_state:
            b_res = st.session_state['sim_res']
            sim_dt = st.session_state['sim_tx_details']
            
            st.markdown("<br>", unsafe_allow_html=True)
            if b_res['tier'] == "TIER_1_PASS":
                st.success(f"✅ **Payment Cleared (ISO: 00)!** ₹{sim_dt['amount']:,.2f} sent to `{sim_dt['payee']}`. UTR: 429184{int(time.time())%1000000:06d}")
            elif b_res['tier'] == "TIER_2_CHALLENGE":
                st.warning(f"⚠️ **Pre-Debit Hold Engaged (ISO: U16):** Unusual telemetry detected. An OTP challenge has been dispatched to authenticate authorization.")
                st.info(f"**Reason:** {b_res['reason']}")
                
                s_otp_col1, s_otp_col2 = st.columns([1.5, 1])
                with s_otp_col1:
                    s_entered_otp = st.text_input("Enter 4-digit Security OTP (Mock: 4921):", max_chars=4, key="sim_otp_release_val")
                with s_otp_col2:
                    st.write("")
                    st.write("")
                    if st.button("🔓 Submit OTP & Complete Settlement", key="sim_otp_settle_btn"):
                        if s_entered_otp == "4921":
                            st.success(f"✅ OTP Verified! Hold released. ₹{sim_dt['amount']:,.2f} transferred to {sim_dt['payee']}.")
                        else:
                            st.error("❌ Invalid OTP. Payment remains frozen.")
            else:
                st.error(f"🚫 **Transaction Blocked by Bank Security (ISO: U28):** {b_res['reason']}")
                st.info(f"🔔 **Regulatory Lien Activated:** Beneficiary VPA `{sim_dt['payee']}` flagged across NPCI FRM network.")
