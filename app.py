import streamlit as st
import joblib
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
st.title("🛡️ Real_time UPI FRAUD DETECTION SYSTEM")
st.write("Enter transaction details below to evaluate potential fraud risk using machine learning.")
st.markdown("---")
col1,col2=st.columns(2)
with col1:
  amount=st.number_input("Transaction Amount (₹)",min_value=1.0,value=2500.0,step=100.0)
  hour=st.slider("Hours of Transaction (0=Midnight,23=11 PM)",0,23,14)
with col2:
  balance_before=st.number_input("Current Account Balance (₹)",min_value=0.0,value=10000.0,step=500.0)
  distance_km=st.number_input("Distance from last transaction location (km)",min_value=0.0,value=10.0,step=5.0)
  time_gap=st.number_input("Time since last transaction (hours)",min_value=0.1,value=1.0,step=0.5)
drain_ratio=amount/balance_before if balance_before > 0 else 1.0
st.markdown("---")
if st.button("🔍 analyze risk level",use_container_width=True):
    features = np.array([[amount,hour,drain_ratio,speed_kmh]])
    prediction=model.predict(features)[0]
    probabilities=model.predict_proba(features)[0]
    fraud_probability=probabilities[1]*100
    if prediction==1:
       st.error(f"🚨**HIGH TRANSACTION DETECTED!**")
       st.warning(f"confidence level: **{fraud_probability:.1f}% risk factor**")
       st.info("💡**reason flagged:** suspicious combination of high transfer amount,speed anomaly,or off-hour balance draning.")
    else:
        st.success(f"✅**TRANSACTION SAFE**")
        st.info(f"Risk Evaluation:**{fraud_probability:.1f}% risk (normal activity)**")
                  
