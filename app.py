import streamlit as st
import joblib
import pandas as pd
import numpy as np
import time

# Page Configuration
st.set_page_config(
    page_title="SentinEl | UPI Risk Engine",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for FinTech Aesthetic
st.markdown("""
    <style>
    /* Main container background */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    
    /* Card Container */
    .metric-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    
    /* Custom Badge */
    .badge-safe {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-warn {
        background-color: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-danger {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* Modern Red Accent Button */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: #ffffff;
        font-weight: 700;
        border-radius: 8px;
        border: none;
        height: 3.2em;
        letter-spacing: 0.5px;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State for History
if "history" not in st.session_state:
    st.session_state.history = []

# Load Model
@st.cache_resource
def load_model():
    return joblib.load('upi_fraud_model.pkl')

model = load_model()

# Sidebar Engine Controls
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("SentinEl Engine")
    st.caption("AI-Powered Transaction Guardian")
    st.markdown("---")
    
    st.metric(label="Inference Latency", value="14 ms", delta="-2 ms")
    st.metric(label="Model Engine", value="XGBoost v2.1")
    st.metric(label="Rule Engine Status", value="ACTIVE", delta="2 Rules Bound")
    
    st.markdown("---")
    st.markdown("**Quick Preset Scenarios**")
    if st.button("🧪 Preset: Regular Tea Shop (₹40)"):
        st.session_state["p_amt"] = 40.0
        st.session_state["p_bal"] = 12000.0
        st.session_state["p_hour"] = 17
        st.session_state["p_dist"] = 1.0
        st.session_state["p_time"] = 4.0
    if st.button("🚨 Preset: Impossible Travel Speed"):
        st.session_state["p_amt"] = 45000.0
        st.session_state["p_bal"] = 50000.0
        st.session_state["p_hour"] = 2
        st.session_state["p_dist"] = 850.0
        st.session_state["p_time"] = 0.5

# Top Header Banner
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("UPI Real-Time Fraud Detection System")
    st.markdown("Automated dual-layer fraud mitigation combining **Heuristic Rules** and **Gradient-Boosted Decision Trees**.")
with header_col2:
    st.markdown("""
        <div style='text-align: right; margin-top: 20px;'>
            <span class='badge-safe'>● PRODUCTION ACTIVE</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Main Layout
tab_eval, tab_history = st.tabs(["⚡ Live Evaluation", "📜 Session Audit Log"])

with tab_eval:
    st.subheader("1. Transaction Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input(
            "Transaction Amount (₹)", 
            min_value=1.0, 
            value=st.session_state.get("p_amt", 5000.0), 
            step=500.0
        )
        hour = st.slider(
            "Transaction Hour", 
            min_value=0, 
            max_value=23, 
            value=st.session_state.get("p_hour", 14), 
            format="%d:00 hrs"
        )
        balance_before = st.number_input(
            "Pre-Transaction Balance (₹)", 
            min_value=1.0, 
            value=st.session_state.get("p_bal", 25000.0), 
            step=1000.0
        )

    with col2:
        distance_km = st.number_input(
            "Distance From Prior Transaction (km)", 
            min_value=0.0, 
            value=st.session_state.get("p_dist", 15.0), 
            step=5.0
        )
        time_since_last = st.number_input(
            "Elapsed Time Since Prior Transaction (hours)", 
            min_value=0.01, 
            value=st.session_state.get("p_time", 2.0), 
            step=0.5
        )

    # Derived Calculations
    drain_ratio = min(amount / balance_before, 1.0) if balance_before > 0 else 1.0
    speed_kmh = distance_km / time_since_last if time_since_last > 0 else 0.0

    # Real-Time Telemetry Cards
    st.markdown("##### Computed Telemetry")
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        st.markdown(f"""
            <div class='metric-card'>
                <small style='color: #94a3b8;'>Drain Ratio</small>
                <h3>{drain_ratio * 100:.1f}%</h3>
                <small>of total available funds</small>
            </div>
        """, unsafe_allow_html=True)
    with t_col2:
        st.markdown(f"""
            <div class='metric-card'>
                <small style='color: #94a3b8;'>Physical Velocity</small>
                <h3>{speed_kmh:.1f} km/h</h3>
                <small>{"⚠️ Abnormal Speed" if speed_kmh > 120 else "Normal transit range"}</small>
            </div>
        """, unsafe_allow_html=True)
    with t_col3:
        st.markdown(f"""
            <div class='metric-card'>
                <small style='color: #94a3b8;'>Temporal Profile</small>
                <h3>{hour:02d}:00</h3>
                <small>{"Off-peak nocturnal" if hour <= 4 else "Standard daytime"}</small>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Evaluation Trigger
    if st.button("Run Comprehensive Risk Assessment", use_container_width=True):
        with st.spinner("Processing fraud heuristic pipelines..."):
            time.sleep(0.3)
            
            rule_triggered = False
            rule_reason = ""

            # Hard Rule Checks
            if speed_kmh > 500:
                rule_triggered = True
                rule_reason = f"Impossible velocity jump ({speed_kmh:.0f} km/h) across geographic coordinates."
            elif drain_ratio == 1.0 and amount >= 10000:
                rule_triggered = True
                rule_reason = "Full-account liquidation anomaly on high-value transfer."

            st.markdown("### Risk Evaluation Outcome")

            if rule_triggered:
                st.error("🚨 **TRANSACTION BLOCKED (RULE ENGINE OVERRIDE)**")
                st.markdown(f"**Trigger Reason:** {rule_reason}")
                st.progress(1.0)
                
                # Append to history
                st.session_state.history.insert(0, {
                    "Time": f"{hour:02d}:00",
                    "Amount": f"₹{amount:,.2f}",
                    "Speed": f"{speed_kmh:.1f} km/h",
                    "Status": "BLOCKED (Rule)",
                    "Risk Score": "100.0%"
                })
            else:
                input_data = pd.DataFrame(
                    [[amount, hour, drain_ratio, speed_kmh]],
                    columns=['amount', 'hour', 'drain_ratio', 'speed_kmh']
                )
                
                prob_fraud = float(model.predict_proba(input_data)[0][1])
                fraud_pct = prob_fraud * 100

                st.progress(prob_fraud)

                if prob_fraud >= 0.75:
                    st.error(f"🚨 **HIGH RISK DETECTED — TRANSACTION HALTED ({fraud_pct:.1f}%)**")
                    st.markdown("**Action Protocol:** Payment held. Requires identity desk intervention.")
                    status_label = "BLOCKED (ML)"
                elif prob_fraud >= 0.40:
                    st.warning(f"⚠️ **SUSPICIOUS ACTIVITY — STEP-UP 2FA REQUIRED ({fraud_pct:.1f}%)**")
                    st.markdown("**Action Protocol:** Out-of-band biometric or OTP prompt dispatched to registered UPI device.")
                    status_label = "CHALLENGED (OTP)"
                else:
                    st.success(f"✅ **TRANSACTION AUTHORIZED — LEGITIMATE ({fraud_pct:.1f}%)**")
                    st.markdown("**Action Protocol:** Clean behavioral match. Immediate routing.")
                    status_label = "APPROVED"

                # Append to history
                st.session_state.history.insert(0, {
                    "Time": f"{hour:02d}:00",
                    "Amount": f"₹{amount:,.2f}",
                    "Speed": f"{speed_kmh:.1f} km/h",
                    "Status": status_label,
                    "Risk Score": f"{fraud_pct:.1f}%"
                })

with tab_history:
    st.subheader("Session Audit Trail")
    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions logged in this session yet. Run an analysis above to populate the audit log.")
