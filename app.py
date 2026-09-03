import streamlit as st
import joblib
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="UPI Shield | Fraud Mitigation Gateway", page_icon="🛡️", layout="wide")

# Styling
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

# Session State for Evaluation and Step-Up Flow
if "eval_state" not in st.session_state:
    st.session_state.eval_state = None
if "pending_data" not in st.session_state:
    st.session_state.pending_data = {}

st.title("🛡️ UPI Intelligent Fraud Mitigation Engine")
st.caption("Hybrid System: Deterministic Firewall + Random Forest Behavioral Profiling")

# Sidebar
with st.sidebar:
    st.header("⚙️ User Spending Baseline")
    user_avg_spend = st.number_input("Typical Historical Spend (₹)", min_value=100.0, value=2500.0, step=500.0)
    is_whitelisted = st.checkbox("Payee is in Saved / Verified Contacts", value=False)
    st.markdown("---")
    st.markdown("**Engine Specifications:**")
    st.write("• Model: Scikit-Learn Random Forest")
    st.write("• Architecture: Hybrid Rule-ML Engine")
    st.write("• Dataset: IEEE-CIS Financial Benchmark")

# Form Inputs
st.subheader("1. Transaction Parameters")
col1, col2 = st.columns(2)
with col1:
    amount = st.number_input("Transfer Amount (₹)", min_value=1.0, value=4500.0, step=500.0)
    hour = st.slider("Transaction Hour", min_value=0, max_value=23, value=15, format="%d:00 hrs")
    balance_before = st.number_input("Account Balance Prior to Transfer (₹)", min_value=1.0, value=20000.0, step=1000.0)

with col2:
    distance_km = st.number_input("Distance from Previous Location (km)", min_value=0.0, value=8.0, step=5.0)
    time_since_last = st.number_input("Time Elapsed Since Last Transfer (hours)", min_value=0.01, value=2.0, step=0.5)

# Derived Telemetry & Behavioral Deltas
drain_ratio = min(amount / balance_before, 1.0) if balance_before > 0 else 1.0
speed_kmh = distance_km / time_since_last if time_since_last > 0 else 0.0
amount_deviation = amount / user_avg_spend

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

# Execution Button
if st.button("Evaluate Transaction Risk", use_container_width=True):
    st.session_state.eval_state = None

    # LAYER 1: DETERMINISTIC PRE-ML FIREWALL
    rule_blocked = False
    block_reason = ""

    if speed_kmh > 500:
        rule_blocked = True
        block_reason = f"Impossible velocity jump ({speed_kmh:.0f} km/h) across geographic coordinates."
    elif drain_ratio == 1.0 and amount >= 10000 and not is_whitelisted:
        rule_blocked = True
        block_reason = "100% account liquidation pattern detected on an unverified recipient."

    if rule_blocked:
        st.session_state.eval_state = "HARD_BLOCK"
        st.session_state.pending_data = {"reason": block_reason}
    else:
        # LAYER 2: RANDOM FOREST INFERENCE
        input_data = pd.DataFrame(
            [[amount, hour, drain_ratio, speed_kmh, amount_deviation]],
            columns=['amount', 'hour', 'drain_ratio', 'speed_kmh', 'amount_deviation']
        )
        
        prob_raw = float(model.predict_proba(input_data)[0][1])
        if is_whitelisted:
            prob_raw = max(0.0, prob_raw - 0.20)
            
        prob_pct = prob_raw * 100

        # LAYER 3: 3-TIER RISK ASSIGNMENT
        if prob_raw >= 0.75:
            st.session_state.eval_state = "ML_BLOCK"
            st.session_state.pending_data = {"score": prob_pct}
        elif prob_raw >= 0.40:
            st.session_state.eval_state = "CHALLENGE_2FA"
            st.session_state.pending_data = {"score": prob_pct}
        else:
            st.session_state.eval_state = "APPROVED"
            st.session_state.pending_data = {"score": prob_pct}

# Display Results
if st.session_state.eval_state == "HARD_BLOCK":
    st.error("🚨 **TRANSACTION BLOCKED: HEURISTIC FIREWALL OVERRIDE**")
    st.write(f"**Violation:** {st.session_state.pending_data['reason']}")
    st.progress(1.0)

elif st.session_state.eval_state == "ML_BLOCK":
    st.error(f"🚨 **HIGH RISK DETECTED: TRANSACTION DECLINED ({st.session_state.pending_data['score']:.1f}%)**")
    st.write("Reason: Telemetry diverges significantly from standard baseline profiles.")
    st.progress(st.session_state.pending_data['score'] / 100.0)

elif st.session_state.eval_state == "CHALLENGE_2FA":
    st.warning(f"⚠️ **SUSPICIOUS ACTIVITY ({st.session_state.pending_data['score']:.1f}% Risk): SECONDARY MFA REQUIRED**")
    st.info("Transaction routed to Step-Up Authentication. A 6-digit OTP has been dispatched to the user's UPI device.")
    st.progress(st.session_state.pending_data['score'] / 100.0)
    
    otp_input = st.text_input("Enter 6-Digit OTP to authorize payment:", max_chars=6, placeholder="e.g. 739201")
    if st.button("Verify OTP & Process Payment"):
        if len(otp_input) == 6 and otp_input.isdigit():
            st.success("✅ **OTP Verified Successfully! Payment Cleared and Settled.**")
        else:
            st.error("❌ Invalid verification code. Please input a valid 6-digit numeric OTP.")

elif st.session_state.eval_state == "APPROVED":
    st.success(f"✅ **TRANSACTION APPROVED: LOW RISK ({st.session_state.pending_data['score']:.1f}%)**")
    st.write("Action: Immediate settlement. Behavioral indicators match clean usage patterns.")
    st.progress(st.session_state.pending_data['score'] / 100.0)
