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
# 1. CLEAN HIGH-CONTRAST CSS THEME
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #0F172A;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }

    /* Natural, Clearly Visible Input & Dropdown Text (Not Overly Bold) */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input, 
    select {
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
    }
    
    div[data-baseweb="select"] * {
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        color: #0F172A !important;
    }

    /* Command-Attention Giant Headline */
    .top-header-container {
        background: #FFFFFF;
        padding: 30px 36px;
        border-radius: 22px;
        border: 2px solid #CBD5E1;
        margin-bottom: 28px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .hero-title-main {
        font-size: 2.85rem !important;
        font-weight: 900 !important;
        color: #0F172A !important;
        line-height: 1.15;
        letter-spacing: -1px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    
    .hero-badge-prominent {
        font-size: 1.1rem !important;
        background: #2563EB;
        color: #FFFFFF !important;
        padding: 6px 16px;
        border-radius: 12px;
        font-weight: 800;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    
    .hero-sub-prominent {
        font-size: 1.18rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
        margin-top: 10px;
    }

    .team-pill-prominent {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #F8FAFC;
        border: 2px solid #64748B;
        padding: 12px 24px;
        border-radius: 30px;
        font-weight: 800;
        font-size: 1.25rem !important;
        color: #0F172A;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* Bento Cards */
    .custom-card {
        background: #FFFFFF;
        border-radius: 20px;
        border: 2px solid #CBD5E1;
        padding: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
        margin-bottom: 24px;
    }
    .card-header-bar {
        font-weight: 800;
        font-size: 1.35rem;
        color: #0F172A;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Verification Run Button */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #E11D48 0%, #BE123C 100%) !important;
        color: #FFFFFF !important;
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        border-radius: 14px !important;
        padding: 18px 36px !important;
        border: none !important;
        box-shadow: 0 6px 22px rgba(225, 29, 72, 0.35) !important;
        width: 100% !important;
        margin-top: 14px !important;
    }

    /* Metric Grid */
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
        font-size: 0.88rem;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .tile-val {
        font-size: 1.85rem;
        font-weight: 900;
    }
    
    /* Checklist Steps */
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
        font-weight: 500;
        color: #475569;
    }
    .pill-ok {
        background: #DCFCE7;
        color: #166534;
        font-weight: 800;
        font-size: 0.9rem;
        padding: 6px 16px;
        border-radius: 10px;
        border: 1px solid #86EFAC;
    }
    .pill-alert {
        background: #FEE2E2;
        color: #991B1B;
        font-weight: 800;
        font-size: 0.9rem;
        padding: 6px 16px;
        border-radius: 10px;
        border: 1px solid #FCA5A5;
    }

    .otp-container {
        background: #FFFFFF;
        border: 2px solid #F59E0B;
        border-radius: 16px;
        padding: 22px;
        margin-top: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PROMINENT HEADER BAR
# ==========================================
st.markdown("""
<div class="top-header-container">
    <div>
        <div class="hero-title-main">
            <span>🛡️ UPI Shield — Intelligent Fraud Mitigation Gateway</span>
            <span class="hero-badge-prominent">v2.0</span>
        </div>
        <div class="hero-sub-prominent">
            ⚡ Deterministic Firewall + Behavioral Random Forest + Adaptive Mitigation
        </div>
    </div>
    <div style="display:flex; align-items:center; gap:26px;">
        <div style="font-size:1.1rem; font-weight:800; color:#16A34A; display:flex; align-items:center; gap:8px;">
            <span style="width:12px; height:12px; background:#16A34A; border-radius:50%; display:inline-block;"></span>
            Bank Switch Online 🟢
        </div>
        <div class="team-pill-prominent">
            <span>⚡ Spark Squad 🚀</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
