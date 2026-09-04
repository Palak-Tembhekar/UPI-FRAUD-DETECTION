import streamlit as st
import joblib
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="UPI Shield | Intelligent Mitigation Gateway",
    page_icon="🛡️",
    layout="wide"
)

# Custom Theme Styling
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f1f5f9; }
    .metric-container {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: #ffffff;
        font-weight: 700;
        border-radius: 8px;
        height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

# Load Model
@st.cache_resource
def load_model():
    return joblib.load('upi_fraud_model.pkl')

model = load_model()

# State Management
if "eval_state" not in st.session_state:
    st.session_state.eval_state = None
if "pending_data" not in st.session_state:
    st.session_state.pending_data = {}

st.title("🛡️ UPI Intelligent Fraud Mitigation Engine")
st.caption("Hybrid Gate: Multi-Flag Deterministic Firewall + Behavioral Random Forest")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ User Profile Baseline")
    user_avg_spend = st.number_input("Typical Historical Spend (₹)", min_value=10.0, value=2000.0, step=100.0)
    is_whitelisted = st.checkbox("Payee in Verified / Frequent Contacts", value=False)
    sim_compromised = st.checkbox("Simulate Screen Share / SIM Swap Alert", value=False)
    st.markdown("---")
    st.markdown("**Engine Specifications:**")
    st.write("• Model: Calibrated Random Forest")
    st.write("• Layer 1: Multi-Flag Firewall")
    st.write("• Layer 2: Behavioral Probability Inference")
    st.write("• Layer 3: Risk-Adaptive Verification")

# 1. Input Layout
st.subheader("1. Transaction Parameters")
col1, col2 = st.columns(2)

with col1:
    amount = st.number_input("Transfer Amount (₹)", min_value=1.0, value=8000.0, step=100.0)
    hour = st.slider("Transaction Hour", min_value=0, max_value=23, value=23, format="%d:00 hrs")
    balance_before = st.number_input("Account Balance Prior to Transfer (₹)", min_value=1.0, value=8000.0, step=100.0)

with col2:
    distance_km = st.number_input("Distance from Previous Location (km)", min_value=0.0, value=50.0, step=10.0)
    time_since_last = st.number_input("Time Elapsed Since Last Transfer (hours)", min_value=0.01, value=1.0, step=0.5)

# Derived Telemetry
drain_ratio = min(amount / balance_before, 1.0) if balance_before > 0 else 1.0
speed_kmh = distance_km / time_since_last if time_since_last > 0 else 0.0
amount_deviation = amount / user_avg_spend

# Telemetry Displays
st.markdown("---")
st.subheader("2. Behavioral Telemetry")
t1, t2, t3 = st.columns(3)
with t1:
    st.markdown(f"<div class='metric-container'><small>Account Drain</small><h3>{drain_ratio:.1%}</h3></div>", unsafe_allow_html=True)
with t2:
    st.markdown(f"<div class='metric-container'><small>Velocity</small><h3>{speed_kmh:.1f} km/h</h3></div>", unsafe_allow_html=True)
with t3:
    st.markdown(f"<div class='metric-container'><small>Spend vs Baseline</small><h3>{amount_deviation:.1f}x</h3></div>", unsafe_allow_html=True)

st.markdown("---")

# Execution Engine
if st.button("Evaluate Transaction Risk", use_container_width=True):
    st.session_state.eval_state = None

    # LAYER 1: MULTI-FLAG DETERMINISTIC FIREWALL
    # Hard Block only triggers when multiple anomalies converge simultaneously
    flag_speed = speed_kmh >= 250.0
    flag_drain = drain_ratio >= 0.90
    flag_surge = amount_deviation >= 3.0
    flag_nocturnal = hour in [0, 1, 2, 3, 4, 22, 23]
    
    total_flags = sum([flag_speed, flag_drain, flag_surge, flag_nocturnal])
    
    if (total_flags >= 3 and not is_whitelisted) or sim_compromised:
        st.session_state.eval_state = "HARD_BLOCK"
        reasons = []
        if flag_speed: reasons.append(f"Impossible Velocity ({speed_kmh:.0f} km/h)")
        if flag_drain: reasons.append(f"Severe Balance Drain ({drain_ratio:.0%})")
        if flag_surge: reasons.append(f"Spike Factor ({amount_deviation:.1f}x)")
        if flag_nocturnal: reasons.append("Off-Hour Nocturnal Execution")
        if sim_compromised: reasons.append("Remote Access Tool / SIM Anomaly Detected")
        st.session_state.pending_data = {"reasons": " + ".join(reasons)}
    else:
        # LAYER 2: MACHINE LEARNING RISK INFERENCE
        input_data = pd.DataFrame(
            [[amount, hour, drain_ratio, speed_kmh, amount_deviation]],
            columns=['amount', 'hour', 'drain_ratio', 'speed_kmh', 'amount_deviation']
        )
        
        prob_raw = float(model.predict_proba(input_data)[0][1])
        
        # Moderate friction for solitary drain or late hours
        if drain_ratio >= 0.90 and not is_whitelisted:
            prob_raw = max(prob_raw, 0.45)
            
        if is_whitelisted:
            prob_raw = max(0.0, prob_raw - 0.25)
            
        prob_pct = prob_raw * 100.0

        # LAYER 3: RISK-ADAPTIVE 3-TIER OUTCOMES
        if prob_raw >= 0.75:
            st.session_state.eval_state = "COOLING_PERIOD"
            st.session_state.pending_data = {"score": prob_pct, "amount": amount}
        elif prob_raw >= 0.35:
            st.session_state.eval_state = "CHALLENGE_2FA"
            st.session_state.pending_data = {"score": prob_pct}
        else:
            st.session_state.eval_state = "APPROVED"
            st.session_state.pending_data = {"score": prob_pct}

# Display Engine Verdicts
if st.session_state.eval_state == "HARD_BLOCK":
    st.error("🚨 **TRANSACTION TERMINATED: MULTI-FLAG CRITICAL INTERCEPT**")
    st.write(f"**Triggered Criteria:** {st.session_state.pending_data['reasons']}")
    st.progress(1.0)

elif st.session_state.eval_state == "COOLING_PERIOD":
    st.warning(f"⏳ **TRANSACTION PLACED IN A 2-HOUR COOLING PERIOD ({st.session_state.pending_data['score']:.1f}% Risk)**")
    st.write(f"To safeguard your funds against potential social engineering, a token transfer of ₹2,000 has been cleared. The remaining ₹{st.session_state.pending_data['amount'] - 2000:,.2f} is queued for settlement after mandatory hold.")
    st.progress(min(1.0, st.session_state.pending_data['score'] / 100.0))

elif st.session_state.eval_state == "CHALLENGE_2FA":
    st.info(f"⚠️ **ELEVATED ACTIVITY DETECTED ({st.session_state.pending_data['score']:.1f}% Risk): STEP-UP VERIFICATION**")
    st.write("A 6-digit cryptographic verification code has been dispatched to your primary banking device.")
    st.progress(min(1.0, st.session_state.pending_data['score'] / 100.0))
    
    otp_input = st.text_input("Enter 6-Digit Verification Code:", max_chars=6, placeholder="e.g. 849201")
    if st.button("Authenticate & Release Payment"):
        if len(otp_input) == 6 and otp_input.isdigit():
            st.success("✅ **Authentication Succeeded. Payment Cleared and Settled.**")
        else:
            st.error("❌ Invalid authorization code. Please enter 6 numeric digits.")

elif st.session_state.eval_state == "APPROVED":
    st.success(f"✅ **TRANSACTION APPROVED: IMMEDIATE SETTLEMENT ({st.session_state.pending_data['score']:.1f}%)**")
    st.write("Behavioral telemetry matches clean profile baseline.")
    st.progress(max(0.05, st.session_state.pending_data['score'] / 100.0))
