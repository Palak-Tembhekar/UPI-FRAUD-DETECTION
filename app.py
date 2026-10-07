"""
UPI Shield: inline fraud mitigation for UPI payments.
Run:  streamlit run app.py
"""
import os
import html
import hashlib
import secrets
from datetime import time as dtime

import pandas as pd
import streamlit as st

import engine

st.set_page_config(
    page_title="UPI Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

PAGES = ["Home", "Dashboard", "Fraud Detection", "Settings"]

# =============================================================================
# THEME (real light / dark switching through CSS variables)
# =============================================================================
PALETTE = {
    "light": dict(bg="#FFFFFF", surface="#F8FAFC", card="#FFFFFF", border="#E2E8F0", text="#0F172A",
                  muted="#64748B", accent="#E11D48", link="#2563EB", shadow="rgba(15,23,42,.06)",
                  ok_bg="#ECFDF5", ok_bd="#10B981", ok_tx="#047857",
                  warn_bg="#FFFBEB", warn_bd="#F59E0B", warn_tx="#B45309",
                  bad_bg="#FEF2F2", bad_bd="#EF4444", bad_tx="#B91C1C",
                  info_bg="#EFF6FF", info_bd="#93C5FD", info_tx="#1E3A8A"),
    "dark": dict(bg="#0B1220", surface="#111A2E", card="#0F1729", border="#27344F", text="#E6EDF7",
                 muted="#9AA9C2", accent="#F43F5E", link="#60A5FA", shadow="rgba(0,0,0,.45)",
                 ok_bg="#062A1E", ok_bd="#10B981", ok_tx="#6EE7B7",
                 warn_bg="#2B2008", warn_bd="#F59E0B", warn_tx="#FCD34D",
                 bad_bg="#2D0F14", bad_bd="#EF4444", bad_tx="#FCA5A5",
                 info_bg="#0E1E3D", info_bd="#3B82F6", info_tx="#BFDBFE"),
}

STATIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, .stApp, .stMarkdown, label, input, textarea, button p, [data-baseweb="tab"] p
{ font-family: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] { background: var(--bg); color: var(--text); }
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp p, .stApp li, .stApp label,
.stApp [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
.stApp [data-testid="stCaptionContainer"] p, .stApp small { color: var(--muted) !important; }
.stApp hr { border-color: var(--border); }
code { background: var(--surface) !important; color: var(--text) !important; }
a { color: var(--link); }

section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background: var(--surface) !important; }
section[data-testid="stSidebar"] { border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] div[role="radiogroup"] label { padding: 6px 10px; border-radius: 10px; }
section[data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 1.1rem; font-weight: 700; }

div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"]
{ background: var(--card) !important; border-color: var(--border) !important; border-radius: 10px !important; }
input, textarea { color: var(--text) !important; -webkit-text-fill-color: var(--text) !important; background: transparent !important; }
div[data-baseweb="select"] div, div[data-baseweb="select"] span { color: var(--text) !important; }
[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] { background: var(--surface) !important; color: var(--text) !important; }
div[data-baseweb="popover"] > div, ul[role="listbox"], li[role="option"] { background: var(--card) !important; color: var(--text) !important; }
li[role="option"]:hover, li[aria-selected="true"] { background: var(--surface) !important; }
[data-testid="stFileUploaderDropzone"] { background: var(--surface) !important; border: 1px dashed var(--border) !important; }
[data-testid="stFileUploaderDropzone"] * { color: var(--text) !important; }

button[data-baseweb="tab"] p { color: var(--muted) !important; font-weight: 700; font-size: 1.02rem; }
button[data-baseweb="tab"][aria-selected="true"] p { color: var(--accent) !important; }
div[data-baseweb="tab-highlight"] { background: var(--accent) !important; }
div[data-baseweb="tab-border"] { background: var(--border) !important; }
[data-testid="stExpander"] { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 14px !important; }
[data-testid="stExpander"] details, [data-testid="stExpander"] summary { background: transparent !important; color: var(--text) !important; }

button[data-testid="stBaseButton-primary"], button[kind="primary"] { background: var(--accent) !important; border: none !important; border-radius: 12px !important; font-weight: 800 !important; }
button[data-testid="stBaseButton-primary"] p, button[kind="primary"] p { color: #FFFFFF !important; font-weight: 800; }
button[data-testid="stBaseButton-secondary"], button[kind="secondary"], a[data-testid="stBaseLinkButton-secondary"]
{ background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; }
button[data-testid="stBaseButton-secondary"] p, button[kind="secondary"] p, a[data-testid="stBaseLinkButton-secondary"] p { color: var(--text) !important; font-weight: 700; }
button:disabled { opacity: .45 !important; }

.card { background: var(--card); border: 1px solid var(--border); border-radius: 18px; padding: 22px; margin: 0 0 18px 0; box-shadow: 0 6px 20px var(--shadow); }
.card-title { font-weight: 800; font-size: 1.25rem; color: var(--text); margin-bottom: 10px; }
.muted { color: var(--muted); }
.notice { border: 2px solid; border-radius: 16px; padding: 16px 20px; margin: 4px 0 16px 0; }
.nt { font-weight: 800; font-size: 1.2rem; margin-bottom: 4px; }
.nb { font-weight: 500; font-size: 1.0rem; line-height: 1.5; }
.chips { display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 14px 0; }
.chip { background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 6px 14px; font-weight: 700; font-size: .92rem; color: var(--text); }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; margin: 6px 0 18px 0; }
.tile { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 16px; }
.tl { font-size: .78rem; font-weight: 800; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); margin-bottom: 4px; }
.tv { font-size: 1.7rem; font-weight: 800; color: var(--text); }
.brow { display: grid; grid-template-columns: 150px 1fr 90px; align-items: center; gap: 10px; margin: 7px 0; font-size: .95rem; }
.brow .bl { color: var(--text); font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.brow .bt { background: var(--surface); border-radius: 8px; height: 16px; overflow: hidden; border: 1px solid var(--border); }
.brow .bf { height: 100%; border-radius: 8px; }
.brow .bv { color: var(--text); font-weight: 700; text-align: right; }
.tblwrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 14px; margin-bottom: 14px; }
.tbl { width: 100%; border-collapse: collapse; font-size: .92rem; }
.tbl th { text-align: left; background: var(--surface); color: var(--muted); font-weight: 800; padding: 10px 12px; white-space: nowrap; }
.tbl td { padding: 10px 12px; border-top: 1px solid var(--border); color: var(--text); white-space: nowrap; }
.pill { display: inline-block; border-radius: 999px; padding: 3px 12px; font-weight: 800; font-size: .82rem; border: 1px solid; }
.step { display: flex; justify-content: space-between; align-items: center; gap: 12px; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px 16px; margin-bottom: 8px; }
.step .sn { font-weight: 800; color: var(--text); } .step .sd { color: var(--muted); font-size: .95rem; }
.sms { background: var(--surface);
