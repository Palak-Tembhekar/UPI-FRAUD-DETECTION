import streamlit as st
import joblib
import pandas as pd
import numpy as np
st.set_page_config(page_title="UPI FRAUD DETECTOR",page_icon="🛡️",layout="centered")
st.markdown("""
   <style>
   .main {
       background-color: #0e1117;
   }
   .stButton>button {
       width: 100%;
       background-color: #ff4b4b;
       color:white;
       font-weight:bold;
       border-radius:8px;
       height:3em;
    }
    </style>
""",unsafe_allow_html=True)
with st.sidebar:
     st.header("⚙️System Status")
     st.success("Model:XGBoost Classifier Loaded")
     st.info("System Engine:active")
     st.markdown("---")
     st.markdown("**Projected Metrics:**")
     st.metric(label="Fraud Detection Rate",value="98.2%")
@st.cache_resource
def load_model():
  return joblib.load('upi_fraud_model.pkl')
model=load_model()
st.header("📥Transaction Details")
st.title("🛡️ Real_time UPI FRAUD DETECTION SYSTEM")
st.write("Enter transaction details below to evaluate potential fraud risk level using machine learning and Rule-Based Defence.")
st.markdown("---")
col1,col2=st.columns(2)
with col1:
  amount=st.number_input("Transaction Amount (₹)",min_value=1.0,value=5000.0,step=500.0)
  hour=st.slider("Hours of Transaction (0=Midnight,14=2PM)",0,23,14)
  balance_before = st.number_input("Current Account Balance(₹)",min_value=1.0,value=2500.0,step=1000.0)
with col2:
  distance_km=st.number_input("Distance from last transaction location (km)",min_value=0.0,value=10.0,step=5.0)
  time_since_last=st.number_input("Time since last transaction (hours)",min_value=0.01,value=2.0,step=0.5)
drain_ratio=min(amount/balance_before , 1.0)if balance_before > 0 else 1.0
speed_kmh=distance_km/time_since_last if time_since_last > 0 else 0.0
st.markdown("---")
st.subheader("📊 Feature Analysis")
st.write(f"* **Drain Ratio:** '{drain_ratio:.2%}'of total balance")
st.write(f"* **Calculated Travel Speed:'{speed_kmh:.1}km/hr'")
st.markdown("---")
if st.button("🔍 analyze risk level",use_container_width=True):
    rule_triggered = False
    rule_reason = ""
    if speed_kmh > 500:
       rule_triggered = True
       rule_reason = f"Impossible location jump detected! Calculated travel speed is {speed_kmh:.0f} km/h."
    elif drain_ratio == 1.0 and amount >= 10000:
       rule_triggered = True
       rule_reason = "Critical Account Drain: Attempting to clear 100% of account balance on a large amount."
    if rule_triggered:
       st.error(f"🚨 **HIGH RISK - TRANSACTION BLOCKED (Rule Override)**")
       st.write(f"**Reason:** {rule_reason}")
       st.progress(1.0)
    else:
       input_data = pd.DataFrame([[amount,hour,drain_ratio,speed_kmh]],
                                 columns=['amount','hour','drain_ratio','speed_kmh'])
       prob_fraud = model.predict_proba(input_data)[0][1]
       fraud_pct = prob_fraud * 100
       st.subheader("🎯 Risk Assessment Result")
       st.write(f"**Fraud Risk Score:** '{prob_fraud *100:.1f}%'")
       st.progress(float(prob_fraud))
        if prob_fraud >= 0.75:
            st.error(f"🚨**HIGH TRANSACTION DETECTED - TRANSACTION BLOCKED**")
            st.warning("Action Taken: Payment haltered. High probability of fraudulent activity.")
            st.warning(f"confidence level: **{fraud_pct:.1f}% risk factor**")
        elif prob_fraud >= 0.40:
            st.warning("⚠️ **SUSPICIOUS TRANSACTION - SECONDARY VERIFICATION REQUIRED**")
            st.info("Action Taken: sent 2FA OTP to registered mobile number for step-up authentication.")
            st.info("💡**reason flagged:** suspicious combination of high transfer amount,speed anomaly,or off-hour balance draning.")
        else:
            st.success(f"✅**TRANSACTION APPROVED - SAFE**")
            st.info(f"Risk Evaluation:**{fraud_pct:.1f}% risk (normal activity)**")
            st.write("Action Taken: Instant approval. Normal behavioural pattern.")
                  
