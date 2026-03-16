import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import re
import math
import zipfile
import io
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SunStripe · ERCOT Nodal Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS — Cyberpunk Neon
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ═══════════════════════════════════════════════
   SUNSTRIPE — Professional White/Red Theme
   Playfair Display (display) · DM Sans (body) · DM Mono (data)
   ═══════════════════════════════════════════════ */

:root {
  --bg:        #ffffff;
  --bg2:       #f7f7f5;
  --bg3:       #f0efec;
  --border:    #e2e0db;
  --border2:   #d0cdc6;
  --red:       #c8102e;
  --red-light: #f5e6e9;
  --red-mid:   #e8b4bc;
  --red-dark:  #8b0b1f;
  --ink:       #1a1a18;
  --ink2:      #3d3d38;
  --ink3:      #6b6b64;
  --ink4:      #9b9b92;
  --gold:      #b8860b;
  --gold-lt:   #f5f0e0;
}

/* ── Reset & Base ─────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: var(--bg) !important;
    color: var(--ink) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background-image:
        linear-gradient(90deg, rgba(200,16,46,0.025) 1px, transparent 1px),
        linear-gradient(0deg, rgba(200,16,46,0.025) 1px, transparent 1px) !important;
    background-size: 48px 48px !important;
}

/* ── Sidebar ──────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: 3px solid var(--red) !important;
    box-shadow: 4px 0 32px rgba(200,16,46,0.12) !important;
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1) !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    letter-spacing: 0.01em !important;
    padding: 6px 0 !important;
    color: rgba(255,255,255,0.7) !important;
    transition: color 0.15s !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    color: #fff !important;
}
[data-testid="stSidebar"] [aria-checked="true"] + div label,
[data-testid="stSidebar"] [data-baseweb="radio"] [aria-checked="true"] ~ * {
    color: #fff !important;
}

/* ── Page headers ─────────────────────────────── */
.page-header {
    border-bottom: 2px solid var(--ink);
    padding-bottom: 18px;
    margin-bottom: 28px;
    position: relative;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: -2px; left: 0;
    width: 60px; height: 2px;
    background: var(--red);
}
.page-header .tag {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--red);
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 8px;
    font-weight: 500;
}
.page-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    font-weight: 700;
    color: var(--ink);
    margin: 0;
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.page-header h1 span { color: var(--red); }
.page-header .ph-right {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: var(--ink4);
    text-align: right;
    letter-spacing: .08em;
    text-transform: uppercase;
}

/* ── Section labels ───────────────────────────── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: var(--ink3);
    letter-spacing: .18em;
    text-transform: uppercase;
    margin: 24px 0 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 500;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

.step-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 22px; height: 22px; border-radius: 50%;
    background: var(--red); color: #fff;
    font-family: 'DM Sans', sans-serif; font-size: 11px; font-weight: 600;
}

/* ── Cards ────────────────────────────────────── */
.osm-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 4px solid var(--red);
    border-radius: 2px;
    padding: 18px 22px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    position: relative;
}
.osm-card .oc-title {
    font-family: 'Playfair Display', serif;
    font-size: 16px;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 14px;
    letter-spacing: -0.01em;
}
.osm-card .oc-grid { display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 10px; }
.osm-card .oc-item .oc-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 9px; color: var(--ink4);
    letter-spacing: .14em; text-transform: uppercase;
}
.osm-card .oc-item .oc-val {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px; font-weight: 500; color: var(--ink2); margin-top: 3px;
}

.ercot-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 4px solid var(--ink);
    border-radius: 2px;
    padding: 18px 22px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.ercot-card h3 {
    font-family: 'Playfair Display', serif;
    font-size: 16px; font-weight: 600;
    color: var(--ink); margin: 0 0 14px;
    letter-spacing: -0.01em;
}
.dg { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 12px; }
.di .dl {
    font-family: 'DM Mono', monospace;
    font-size: 9px; color: var(--ink4);
    letter-spacing: .14em; text-transform: uppercase;
}
.di .dv {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px; font-weight: 500; color: var(--ink2); margin-top: 3px;
}

/* ── Tags / Pills ─────────────────────────────── */
.tag-row { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
.tag-bus  { display:inline-block; padding:3px 10px; border-radius:2px; font-family:'DM Mono',monospace; font-size:10px; font-weight:500; background: var(--red-light); border:1px solid var(--red-mid); color: var(--red-dark); }
.tag-zone { display:inline-block; padding:3px 10px; border-radius:2px; font-family:'DM Mono',monospace; font-size:10px; background: #e8f0fe; border:1px solid #a8c0f0; color: #1a3a7a; }
.tag-psse { display:inline-block; padding:3px 10px; border-radius:2px; font-family:'DM Mono',monospace; font-size:10px; background: var(--bg3); border:1px solid var(--border2); color: var(--ink2); }
.tag-hub  { display:inline-block; padding:3px 10px; border-radius:2px; font-family:'DM Mono',monospace; font-size:10px; background: var(--gold-lt); border:1px solid #d4a820; color: var(--gold); font-weight:600; }
.tag-rn   { display:inline-block; padding:3px 10px; border-radius:2px; font-family:'DM Mono',monospace; font-size:10px; background: var(--bg3); border:1px solid var(--border); color: var(--ink3); }

/* ── kV badges ────────────────────────────────── */
.kv { display:inline-block; padding:3px 10px; border-radius:2px; font-family:'DM Mono',monospace; font-size:11px; font-weight:600; }
.kv-345 { color: var(--red-dark); background: var(--red-light); border:1px solid var(--red-mid); }
.kv-230 { color: #7a5a00; background: var(--gold-lt); border:1px solid #d4a820; }
.kv-138 { color: #1a4a1a; background: #e8f5e8; border:1px solid #90c890; }
.kv-115 { color: #1a3a7a; background: #e8f0fe; border:1px solid #a8c0f0; }
.kv-69  { color: var(--ink2); background: var(--bg3); border:1px solid var(--border2); }
.kv-34  { color: var(--ink4); background: var(--bg3); border:1px solid var(--border); }

/* ── Map placeholder ──────────────────────────── */
.map-placeholder {
    text-align: center; padding: 60px 20px;
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 2px;
}
.map-placeholder .mp-icon { font-size: 32px; margin-bottom: 14px; opacity: 0.5; }
.map-placeholder .mp-title {
    font-family: 'Playfair Display', serif;
    font-size: 16px; font-weight: 600; color: var(--ink2);
    margin-bottom: 8px;
}
.map-placeholder .mp-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px; line-height: 1.7; color: var(--ink4);
}

/* ── Confidence labels ────────────────────────── */
.conf-high { color: #1a6a1a; font-weight: 600; }
.conf-med  { color: var(--gold); font-weight: 600; }
.conf-low  { color: var(--red); font-weight: 600; }

/* ── Streamlit tabs ───────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg) !important;
    border-bottom: 2px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0 !important;
    color: var(--ink3) !important;
    background: transparent !important;
    padding: 10px 22px !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
}
.stTabs [aria-selected="true"] {
    color: var(--red) !important;
    border-bottom: 2px solid var(--red) !important;
    font-weight: 600 !important;
}

/* ── Inputs & selects ─────────────────────────── */
.stTextInput input,
div[data-baseweb="select"] > div,
.stNumberInput input {
    background-color: var(--bg) !important;
    border: 1px solid var(--border2) !important;
    color: var(--ink) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    border-radius: 2px !important;
    box-shadow: none !important;
}
.stTextInput input:focus,
div[data-baseweb="select"] > div:focus-within {
    border-color: var(--red) !important;
    box-shadow: 0 0 0 3px rgba(200,16,46,0.08) !important;
}

/* ── Buttons ──────────────────────────────────── */
.stDownloadButton button, .stButton button {
    background: var(--bg) !important;
    border: 1px solid var(--border2) !important;
    color: var(--ink2) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    border-radius: 2px !important;
    transition: all 0.15s !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    border-color: var(--red) !important;
    color: var(--red) !important;
    background: var(--red-light) !important;
    box-shadow: none !important;
}
button[kind="primary"] {
    background: var(--red) !important;
    border: 1px solid var(--red) !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(200,16,46,0.25) !important;
    text-shadow: none !important;
}
button[kind="primary"]:hover {
    background: var(--red-dark) !important;
    border-color: var(--red-dark) !important;
    box-shadow: 0 4px 16px rgba(200,16,46,0.35) !important;
}

/* ── Metrics ──────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-top: 3px solid var(--red) !important;
    border-radius: 2px !important;
    padding: 16px 18px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    animation: none !important;
}
[data-testid="stMetric"]::after { display: none !important; }
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    color: var(--ink4) !important;
    text-transform: uppercase !important;
    letter-spacing: .12em !important;
    font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    color: var(--ink) !important;
    font-size: 26px !important;
    font-weight: 700 !important;
    text-shadow: none !important;
    letter-spacing: -0.02em !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
}

/* ── Checkboxes ───────────────────────────────── */
[data-testid="stCheckbox"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    color: var(--ink2) !important;
    letter-spacing: 0 !important;
}

/* ── DataFrames ───────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}

/* ── Alerts ───────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 2px !important;
    border-left-width: 4px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Misc ─────────────────────────────────────── */
div[data-testid="stMarkdownContainer"] p {
    color: var(--ink2);
    font-size: 14px;
    line-height: 1.6;
    font-family: 'DM Sans', sans-serif;
}
hr { border-color: var(--border) !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--red); }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# Data loading
# ═══════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Loading ERCOT settlement points...")
def load_data():
    df = pd.read_csv("Settlement_Points_02202026_094122.csv", dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "ELECTRICAL_BUS":       "Bus",
        "NODE_NAME":            "Node",
        "PSSE_BUS_NAME":        "PSSE Name",
        "VOLTAGE_LEVEL":        "kV",
        "SUBSTATION":           "Substation",
        "SETTLEMENT_LOAD_ZONE": "Zone",
        "RESOURCE_NODE":        "Resource Node",
        "HUB_BUS_NAME":         "Hub Bus",
        "HUB":                  "Hub",
        "PSSE_BUS_NUMBER":      "PSSE #",
    })
    df["kV_num"] = pd.to_numeric(df["kV"], errors="coerce")
    return df

df = load_data()
TRANS_KV = ["345", "230", "138", "115", "69", "34.5"]

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def kv_cls(kv):
    try:
        v = float(kv)
        if v >= 345: return "kv-345"
        if v >= 230: return "kv-230"
        if v >= 138: return "kv-138"
        if v >= 115: return "kv-115"
        if v >= 69:  return "kv-69"
    except: pass
    return "kv-34"

def to_csv_bytes(d): return d.to_csv(index=False).encode()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def neon_plotly_layout(title="", height=320):
    return dict(
        title=dict(text=title, font=dict(family="Playfair Display", size=14, color="#1a1a18"), x=0.01),
        height=height,
        paper_bgcolor="#ffffff", plot_bgcolor="#f7f7f5",
        font=dict(family="DM Sans", color="#3d3d38", size=11),
        xaxis=dict(gridcolor="#e2e0db", linecolor="#d0cdc6", tickfont=dict(size=10, color="#6b6b64")),
        yaxis=dict(gridcolor="#e2e0db", linecolor="#d0cdc6", tickfont=dict(size=10, color="#6b6b64")),
        legend=dict(bgcolor="rgba(247,247,245,0.95)", bordercolor="#e2e0db", borderwidth=1),
        margin=dict(l=50, r=20, t=40, b=40),
    )


# ═══════════════════════════════════════════════════════════════════
# ZIP / CSV parser
# ═══════════════════════════════════════════════════════════════════
def parse_lmp_upload(uploaded_file):
    """Accept ZIP (multiple CSVs) or single CSV. Returns unified DataFrame."""
    name = uploaded_file.name.lower()
    frames = []

    if name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(uploaded_file.read())) as z:
            csv_files = [f for f in z.namelist() if f.endswith(".csv")]
            for fn in csv_files:
                try:
                    raw = pd.read_csv(z.open(fn), dtype=str).fillna("")
                    raw["_source_file"] = fn
                    frames.append(raw)
                except Exception:
                    pass
        if not frames:
            return None, "No CSV files found in ZIP"
        combined = pd.concat(frames, ignore_index=True)
    else:
        try:
            combined = pd.read_csv(uploaded_file, dtype=str).fillna("")
            combined["_source_file"] = name
        except Exception as e:
            return None, str(e)

    # Auto-detect columns — handles DAM, SCED, RTM, and all other ERCOT formats
    col_map = {}
    for c in combined.columns:
        u = c.upper().strip().replace(" ", "").replace("_", "")
        if any(k in u for k in [
            "SETTLEMENTPOINTNAME","SETTLEMENTPOINT","SPNAME",
            "BUSNAME","NODENAME","ELECTRICALBUS","ELECBUS","BUSID","SETTLEMENTBUS",
        ]):
            if "bus" not in col_map: col_map["bus"] = c
        elif any(k in u for k in [
            "SETTLEMENTPOINTPRICE","PRICE","LMP","SPP","RTLMP","DAMLMP","MCPRICE",
        ]):
            if "price" not in col_map: col_map["price"] = c
        elif any(k in u for k in [
            "SCEDTIMESTAMP","TIMESTAMP","INTERVALTIME","OPERATINGHOUR","INTERVALENDING",
        ]):
            if "timestamp" not in col_map: col_map["timestamp"] = c
        elif any(k in u for k in ["HOURENDING","HOUROFDAY","HOUR","DELIVERYHOUR"]):
            if "hour" not in col_map: col_map["hour"] = c
        elif any(k in u for k in ["DELIVERYDATE","TRADINGDATE"]):
            if "date" not in col_map: col_map["date"] = c
        elif u == "DATE":
            if "date" not in col_map: col_map["date"] = c

    if "bus" not in col_map or "price" not in col_map:
        return combined, f"Could not detect columns. Found: {list(combined.columns)}"

    rename = {v: k for k, v in col_map.items()}
    combined = combined.rename(columns=rename)
    combined["price"] = pd.to_numeric(combined["price"], errors="coerce")

    # Build datetime — priority: full timestamp > date+hour > hour > index
    if "timestamp" in col_map:
        combined["datetime"] = pd.to_datetime(combined["timestamp"], errors="coerce")
        if combined["datetime"].isna().all():
            combined["datetime"] = pd.to_datetime(
                combined["timestamp"].str.replace(r"[+-]\d{2}:\d{2}$", "", regex=True),
                errors="coerce"
            )
    elif "date" in col_map and "hour" in combined.columns:
        try:
            combined["hour_int"] = pd.to_numeric(combined["hour"], errors="coerce").fillna(0).astype(int)
            combined["datetime"] = pd.to_datetime(combined["date"], errors="coerce") + \
                                   pd.to_timedelta(combined["hour_int"] - 1, unit="h")
        except:
            combined["datetime"] = pd.NaT
    elif "hour" in combined.columns:
        combined["datetime"] = pd.to_numeric(combined["hour"], errors="coerce")
    else:
        combined["datetime"] = pd.RangeIndex(len(combined))

    return combined, None


# ═══════════════════════════════════════════════════════════════════
# Live ERCOT API
# ═══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ercot_dam_live(settlement_point, date_from, date_to):
    """Fetch DAM LMP from ERCOT public API."""
    url = "https://data.ercot.com/api/public-reports/np4-190-cd/dam_stlmnt_pnt_prices"
    params = {
        "deliveryDateFrom": date_from,
        "deliveryDateTo":   date_to,
        "settlementPoint":  settlement_point,
        "size":             1000,
        "page":             1,
    }
    try:
        r = requests.get(url, params=params, timeout=20,
                         headers={"Accept": "application/json", "User-Agent": "SunStripe-ERCOT/1.0"})
        r.raise_for_status()
        data = r.json()
        rows = data.get("data", []) or data.get("reports", []) or []
        if not rows:
            return None, "No data returned from ERCOT API"
        ddf = pd.DataFrame(rows)
        return ddf, None
    except Exception as e:
        return None, f"ERCOT API error: {e}"


# ═══════════════════════════════════════════════════════════════════
# LMP Analytics engine
# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════
# BESS rolling-average helper (from ERCOT BESS Dashboard)
# ═══════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════
# PDF Report Generator
# ═══════════════════════════════════════════════════════════════════
def generate_pdf_report(search_results, ercot_sub, sub_df, lmp_summary=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_fill_color(26, 26, 24)
    pdf.rect(0, 0, 210, 28, 'F')
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(200, 16, 46)
    pdf.set_xy(15, 8)
    pdf.cell(0, 10, "SUNSTRIPE  |  ERCOT NODAL ANALYSIS REPORT", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.set_xy(15, 19)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}  |  Confidential", ln=True)
    pdf.set_xy(15, 34)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(200, 16, 46)
    pdf.cell(0, 8, "SEARCH SUMMARY", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    if search_results:
        pdf.cell(0, 6, f"Centre: {search_results['lat']:.4f}, {search_results['lon']:.4f}  |  Radius: {search_results['radius_mi']} miles", ln=True)
        pdf.cell(0, 6, f"Substations found: {len(search_results['elements'])}  |  Hubs: {sum(1 for e in search_results['elements'] if e['is_hub'])}  |  Nodes: {sum(1 for e in search_results['elements'] if not e['is_hub'])}", ln=True)
    pdf.ln(4)
    if ercot_sub:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(200, 16, 46)
        pdf.cell(0, 8, f"ERCOT SUBSTATION: {ercot_sub}", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)
        buses = sub_df["Bus"].tolist()
        kvs   = ", ".join(sorted(sub_df["kV"].unique(), key=lambda x: -float(x) if x else 0))
        zones = ", ".join(sub_df["Zone"].unique())
        hubs  = ", ".join(sub_df[sub_df["Hub"]!=""]["Hub"].unique()) or "—"
        rn    = sub_df[sub_df["Resource Node"]!=""].shape[0]
        pdf.cell(0, 6, f"Buses: {len(buses)}  |  Voltages: {kvs} kV  |  Zone(s): {zones}", ln=True)
        pdf.cell(0, 6, f"Hub(s): {hubs}  |  Resource Nodes: {rn}", ln=True)
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(240, 240, 240)
        col_w = [45, 20, 25, 35, 35, 30]
        for h, w in zip(["Bus Name","kV","Zone","PSSE Name","PSSE #","Resource Node"], col_w):
            pdf.cell(w, 7, h, border=1, fill=True)
        pdf.ln()
        pdf.set_font("Helvetica", "", 8)
        for _, row in sub_df.head(40).iterrows():
            for val, w in zip([row["Bus"], row["kV"], row["Zone"],
                               row["PSSE Name"][:15], row["PSSE #"], row["Resource Node"][:12]], col_w):
                pdf.cell(w, 6, str(val), border=1)
            pdf.ln()
        if len(sub_df) > 40:
            pdf.set_font("Helvetica", "I", 8)
            pdf.cell(0, 6, f"  ... and {len(sub_df)-40} more buses", ln=True)
    if lmp_summary is not None and len(lmp_summary):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(200, 16, 46)
        pdf.cell(0, 8, "LMP PRICE ANALYSIS", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)
        for col in lmp_summary.columns[:6]:
            pdf.cell(30, 6, str(col)[:12], border=1, fill=True)
        pdf.ln()
        for _, row in lmp_summary.head(20).iterrows():
            for col in lmp_summary.columns[:6]:
                pdf.cell(30, 6, str(row[col])[:12], border=1)
            pdf.ln()
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, "SunStripe Confidential  |  ERCOT Nodal Analysis Platform", align="C")
    return pdf.output()


# ═══════════════════════════════════════════════════════════════════
# Overpass search — mirror fallback chain
# ═══════════════════════════════════════════════════════════════════
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
]

def _parse_overpass_elements(raw_elements, lat, lon):
    elements = []
    for el in raw_elements:
        elat = el.get("lat") or (el.get("center") or {}).get("lat")
        elon = el.get("lon") or (el.get("center") or {}).get("lon")
        if not elat or not elon: continue
        tags = el.get("tags", {})
        raw_volt = tags.get("voltage", "")
        try:
            rv = float(raw_volt.split(";")[0].strip())
            volt_kv = rv / 1000 if rv > 1000 else rv
        except:
            volt_kv = None
        dist_km = haversine(lat, lon, elat, elon)
        elements.append({
            "lat": elat, "lon": elon,
            "name": tags.get("name", ""),
            "voltage": raw_volt, "volt_kv": volt_kv,
            "operator": tags.get("operator", ""),
            "ref": tags.get("ref", ""),
            "osm_id": str(el.get("id", "")),
            "dist_mi": round(dist_km / 1.60934, 2),
            "dist_km": round(dist_km, 2),
        })
    elements.sort(key=lambda x: x["dist_mi"])
    return elements

@st.cache_data(ttl=3600, show_spinner=False)
def search_substations_radius(lat, lon, radius_mi):
    radius_m = int(radius_mi * 1609.34)
    server_timeout = min(30, max(15, radius_mi))
    query = f"""[out:json][timeout:{server_timeout}];
(
  node["power"="substation"](around:{radius_m},{lat},{lon});
  way["power"="substation"](around:{radius_m},{lat},{lon});
  relation["power"="substation"](around:{radius_m},{lat},{lon});
);
out center tags;"""
    last_err = "Unknown error"
    for mirror in OVERPASS_MIRRORS:
        try:
            resp = requests.post(mirror, data={"data": query},
                timeout=(10, server_timeout + 15),
                headers={"User-Agent": "SunStripe-ERCOT/1.0", "Accept-Encoding": "gzip"})
            if resp.status_code == 504:
                last_err = f"504 on {mirror.split('/')[2]}"; continue
            resp.raise_for_status()
            elements = _parse_overpass_elements(resp.json().get("elements", []), lat, lon)
            return elements, None
        except requests.exceptions.ConnectTimeout:
            last_err = f"Connect timeout on {mirror.split('/')[2]}"; continue
        except requests.exceptions.ReadTimeout:
            last_err = f"Read timeout on {mirror.split('/')[2]}"; continue
        except requests.exceptions.HTTPError as e:
            last_err = f"HTTP {e.response.status_code} on {mirror.split('/')[2]}"; continue
        except Exception as e:
            last_err = f"{mirror.split('/')[2]}: {str(e)[:60]}"; continue
    return [], (f"All Overpass mirrors failed ({last_err}). Try a smaller radius or retry in 1–2 min.")


# ═══════════════════════════════════════════════════════════════════
# ERCOT fuzzy match index
# ═══════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def build_ercot_search_index():
    records = []
    for sub, grp in df.groupby("Substation"):
        tokens = set()
        for pn in grp["PSSE Name"].unique():
            clean = re.sub(r'[^A-Z]', '', pn.upper().split('_')[0])[:12]
            if len(clean) >= 3: tokens.add(clean)
        sub_clean = re.sub(r'[^A-Z]', '', sub.upper())
        if len(sub_clean) >= 3: tokens.add(sub_clean)
        records.append({"substation": sub, "tokens": tokens,
                         "kvs": sorted(grp["kV"].unique(), key=lambda x: -float(x) if x else 0),
                         "bus_count": len(grp)})
    return records

ercot_index = build_ercot_search_index()

def match_to_ercot(osm_name, osm_voltage_str=""):
    if not osm_name: return []
    osm_clean = re.sub(r'[^A-Z0-9 ]', '', osm_name.upper())
    for pat in [r'\bSUBSTATION\b',r'\bSWITCHING\b',r'\bSTATION\b',r'\bELECTRIC\b',
                r'\bPOWER\b',r'\bTRANS\b',r'\bSUB\b',r'\bSS\b']:
        osm_clean = re.sub(pat, '', osm_clean)
    osm_tokens = [t for t in osm_clean.split() if len(t) >= 3]
    osm_kv = None
    try:
        v_raw = float(re.sub(r'[^0-9.]', '', osm_voltage_str.split(";")[0]))
        osm_kv = v_raw / 1000 if v_raw > 1000 else v_raw
    except: pass
    results = []
    for rec in ercot_index:
        score = 0
        for ot in osm_tokens:
            for et in rec["tokens"]:
                if ot == et: score += 20
                elif ot in et and len(ot) >= 5: score += 12
                elif et in ot and len(et) >= 5: score += 10
                elif ot[:5] == et[:5] and len(ot) >= 5: score += 8
        if osm_kv and score > 0:
            for kv_str in rec["kvs"]:
                try:
                    if abs(float(kv_str) - osm_kv) < 10: score += 15; break
                except: pass
        if score >= 8: results.append((rec["substation"], score, rec))
    results.sort(key=lambda x: -x[1])
    return results[:6]


# ═══════════════════════════════════════════════════════════════════
# ERCOT card renderer
# ═══════════════════════════════════════════════════════════════════
def render_ercot_card(sub_name, sub_df):
    buses     = sub_df["Bus"].tolist()
    zones     = sub_df["Zone"].unique().tolist()
    kvs       = sorted(sub_df["kV"].unique(), key=lambda x: -float(x) if x else 0)
    psse_nums = sub_df["PSSE #"].tolist()
    rn_list   = sub_df[sub_df["Resource Node"]!=""]["Resource Node"].tolist()
    hubs      = sub_df[sub_df["Hub"]!=""]["Hub"].unique().tolist()
    bus_tags  = "".join(f'<span class="tag-bus">{b}</span>' for b in buses[:30])
    more_b    = f'<span style="color:#9b9b92;font-size:10px">+{len(buses)-30} more</span>' if len(buses)>30 else ""
    zone_tags = "".join(f'<span class="tag-zone">{z}</span>' for z in zones)
    psse_tags = "".join(f'<span class="tag-psse">{p}</span>' for p in psse_nums[:20])
    hub_tags  = "".join(f'<span class="tag-hub">{h}</span>' for h in hubs) if hubs else '<span style="color:#9b9b92;font-size:11px">—</span>'
    kv_tags   = "".join(f'<span class="kv {kv_cls(k)}">{k} kV</span>' for k in kvs)
    rn_tags   = "".join(f'<span class="tag-rn">{r}</span>' for r in rn_list[:10])
    st.markdown(f"""
    <div class="ercot-card">
        <h3>{sub_name}</h3>
        <div class="dg">
            <div class="di"><div class="dl">Buses</div><div class="dv" style="color:#c8102e;font-weight:700">{len(buses)}</div></div>
            <div class="di"><div class="dl">Voltage(s)</div><div class="dv">{kv_tags}</div></div>
            <div class="di"><div class="dl">Zone(s)</div><div class="dv">{zone_tags}</div></div>
            <div class="di"><div class="dl">Hub(s)</div><div class="dv">{hub_tags}</div></div>
            <div class="di"><div class="dl">Res. Nodes</div><div class="dv" style="color:#c8102e;font-weight:700">{len(rn_list)}</div></div>
        </div>
        <div style="margin-bottom:10px"><div class="dl" style="font-family:'DM Mono',monospace;font-size:9px;color:#9b9b92;letter-spacing:.14em;text-transform:uppercase;margin-bottom:5px">Bus Names</div><div class="tag-row">{bus_tags}{more_b}</div></div>
        <div style="margin-bottom:10px"><div class="dl" style="font-family:'DM Mono',monospace;font-size:9px;color:#9b9b92;letter-spacing:.14em;text-transform:uppercase;margin-bottom:5px">PSSE Numbers</div><div class="tag-row">{psse_tags}</div></div>
        {'<div><div class="dl" style="font-family:\'DM Mono\',monospace;font-size:9px;color:#9b9b92;letter-spacing:.14em;text-transform:uppercase;margin-bottom:5px">Resource Nodes</div><div class="tag-row">'+rn_tags+'</div></div>' if rn_list else ''}
    </div>
    """, unsafe_allow_html=True)




def bess_calc(bdf: pd.DataFrame, half_w: int):
    """
    3-hour centred rolling-average BESS strategy.
    bdf must have columns: Hour (numeric 1-24), price ($/MWh)
    half_w: 1 = 2H storage (±1hr), 2 = 4H storage (±2hr)
    Returns: revenue, roll_series, low_hr, high_hr, charge_win, discharge_win
    """
    roll = (bdf["price"]
            .rolling(window=3, center=True, min_periods=1)
            .mean()
            .reset_index(drop=True))
    low_idx  = roll.idxmin()
    high_idx = roll.idxmax()
    low_hr   = bdf["Hour"].iloc[low_idx]
    high_hr  = bdf["Hour"].iloc[high_idx]
    hr_min, hr_max = bdf["Hour"].min(), bdf["Hour"].max()
    charge_win    = (max(hr_min, low_hr  - half_w), min(hr_max, low_hr  + half_w))
    discharge_win = (max(hr_min, high_hr - half_w), min(hr_max, high_hr + half_w))
    ch_mask  = (bdf["Hour"] >= charge_win[0])    & (bdf["Hour"] <= charge_win[1])
    dis_mask = (bdf["Hour"] >= discharge_win[0]) & (bdf["Hour"] <= discharge_win[1])
    ch_avg   = bdf.loc[ch_mask,  "price"].mean() if ch_mask.any()  else 0.0
    dis_avg  = bdf.loc[dis_mask, "price"].mean() if dis_mask.any() else 0.0
    revenue  = round(dis_avg - ch_avg, 2)
    return revenue, roll, low_hr, high_hr, charge_win, discharge_win


# ═══════════════════════════════════════════════════════════════════
# LMP Analytics engine — all use-cases
# ═══════════════════════════════════════════════════════════════════
def run_lmp_analytics(lmp_df, resolved_df, use_case, batt_mw=100, batt_mwh=400, efficiency=0.85):
    """
    All use-case analytics. Congestion/Curtailment use the CI/CSS/CPI/ECS formulas
    from the ERCOT analytics pipeline (see reference script).
    """
    import numpy as np
    buses = set(resolved_df["Bus"].str.upper())
    lmp_df["_bus_up"] = lmp_df["bus"].astype(str).str.upper().str.strip()
    matched = lmp_df[lmp_df["_bus_up"].isin(buses)].copy()
    if matched.empty:
        return None, "No matching buses in LMP data"
    matched = matched.sort_values("datetime")

    # ── CONGESTION INDEX (CI) + CSS ───────────────────────────────
    # CI(node, t) = LMP_hub(t) − LMP_node(t)
    # CSS(node)   = mean(|CI|)  — Congestion Severity Score
    if use_case == "congestion":
        bus_list = matched["_bus_up"].unique().tolist()
        if len(bus_list) < 2:
            # Single-bus: compute CI vs synthetic mean of all available buses
            pass

        # Build hourly pivot: rows=time, cols=bus, values=LMP
        pivot = matched.pivot_table(
            index="datetime", columns="_bus_up", values="price", aggfunc="mean")

        # Choose hub: prefer HB_ hub if present, else highest-avg-price bus
        hub_candidates = [b for b in pivot.columns if b.startswith("HB_")]
        if hub_candidates:
            hub = hub_candidates[0]
        else:
            hub = pivot.mean().idxmax()

        results = []
        for node in pivot.columns:
            if node == hub:
                continue
            ci_series = pivot[hub] - pivot[node]           # CI(node,t)
            css       = ci_series.abs().mean()             # CSS = mean(|CI|)
            congested_hours = int((ci_series.abs() > 10).sum())
            congestion_pct  = round((ci_series.abs() > 10).mean() * 100, 1)
            source_side     = int((ci_series >  10).sum())
            load_side       = int((ci_series < -10).sum())
            avg_ci          = round(ci_series.mean(), 2)
            max_ci          = round(ci_series.abs().max(), 2)

            # Risk label (from reference)
            if css > 10:   cong_risk = "🔴 HIGH"
            elif css > 3:  cong_risk = "🟡 MEDIUM"
            else:          cong_risk = "🟢 LOW"

            # Congestion Rent proxy: CR = CI × capacity_mw ($/hr)
            cr_proxy = round(ci_series.mean() * batt_mw, 0)

            results.append({
                "Node":               node,
                "Hub (reference)":    hub,
                "Avg CI ($/MWh)":     avg_ci,
                "CSS ($/MWh)":        round(css, 2),
                "Max |CI| ($/MWh)":   max_ci,
                "Congestion %":       congestion_pct,
                "Congested Hours":    congested_hours,
                "Source-Side Hours":  source_side,
                "Load-Side Hours":    load_side,
                "CR Proxy ($/hr)":    cr_proxy,
                "Congestion Risk":    cong_risk,
            })

        if not results:
            return None, "Not enough nodes for congestion analysis (need ≥2 buses)"

        df_out = pd.DataFrame(results).sort_values("CSS ($/MWh)", ascending=False)
        # Also return the full CI time-series for chart
        df_out.attrs["pivot"]  = pivot
        df_out.attrs["hub"]    = hub
        return df_out, None

    # ── CURTAILMENT PROBABILITY INDEX (CPI) + ECS ────────────────
    # CPI(node) = (count LMP ≤ 0) / T × 100
    # ECS       = 1 if LMP ≤ 0 (economic curtailment signal)
    elif use_case == "curtailment":
        import numpy as np
        results = []
        for bus in matched["_bus_up"].unique():
            bdf   = matched[matched["_bus_up"] == bus].copy()
            total = len(bdf)
            if total == 0: continue

            # ECS per interval
            bdf["ECS"] = (bdf["price"] <= 0).astype(int)

            neg_count   = int((bdf["price"] < 0).sum())
            zero_count  = int((bdf["price"] <= 0).sum())
            deep_neg    = int((bdf["price"] < -20).sum())
            cpi         = round(zero_count / total * 100, 2)    # CPI_%
            avg_p       = round(bdf["price"].mean(), 2)
            min_p       = round(bdf["price"].min(), 2)
            p5          = round(bdf["price"].quantile(0.05), 2)

            # Weighted curtailment: avg LMP during curtailed hours
            curt_lmp    = round(bdf.loc[bdf["price"] <= 0, "price"].mean(), 2) if zero_count else 0.0

            # ECS hours = consecutive curtailment windows
            ecs_runs    = int((bdf["ECS"].diff() != 0).sum() // 2) if zero_count else 0

            # Risk labels (from reference: >20% HIGH, >5% MEDIUM, else LOW)
            if cpi > 20:   curt_risk = "🔴 HIGH"
            elif cpi > 5:  curt_risk = "🟡 MEDIUM"
            else:          curt_risk = "🟢 LOW"

            results.append({
                "Bus":                   bus,
                "Total Intervals":       total,
                "CPI % (LMP ≤ 0)":      cpi,
                "Neg Price Hours":       neg_count,
                "≤ $0 Hours":           zero_count,
                "< −$20 Hours":         deep_neg,
                "ECS Events":            ecs_runs,
                "Avg LMP ($/MWh)":       avg_p,
                "Min LMP ($/MWh)":       min_p,
                "P5 LMP ($/MWh)":        p5,
                "Avg Curtailed LMP":     curt_lmp,
                "Curtailment Risk":      curt_risk,
            })

        return pd.DataFrame(results).sort_values("CPI % (LMP ≤ 0)", ascending=False), None

    # ── FTR SCANNER ───────────────────────────────────────────────
    elif use_case == "ftr":
        pivot = matched.pivot_table(index="datetime", columns="_bus_up", values="price", aggfunc="mean")
        results = []
        cols = pivot.columns.tolist()
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                spread = pivot[cols[i]] - pivot[cols[j]]
                pos_spread = spread[spread > 0]
                results.append({"Buy Node": cols[i], "Sell Node": cols[j],
                    "Avg FTR Value $/MWh": round(pos_spread.mean(), 2) if len(pos_spread) else 0,
                    "Max FTR Value $/MWh": round(spread.max(), 2),
                    "Profitable Hours": len(pos_spread),
                    "Win Rate %": round(len(pos_spread)/len(spread)*100, 1) if len(spread) else 0})
        return pd.DataFrame(results).sort_values("Avg FTR Value $/MWh", ascending=False), None

    # ── REVENUE MODEL ─────────────────────────────────────────────
    elif use_case == "revenue":
        results = []
        for bus in matched["_bus_up"].unique():
            bdf = matched[matched["_bus_up"] == bus]
            avg = bdf["price"].mean()
            results.append({"Bus": bus,
                "Avg LMP $/MWh": round(avg, 2),
                "Annual Solar Rev ($/MW)": round(avg * 8760 * 0.25, 0),
                "Annual Wind Rev ($/MW)":  round(avg * 8760 * 0.35, 0),
                "Annual BESS Rev ($/MW)":  round((bdf["price"].max()-bdf["price"].min())*365*0.5, 0),
                "P90 Price $/MWh": round(bdf["price"].quantile(0.1), 2),
                "P10 Price $/MWh": round(bdf["price"].quantile(0.9), 2)})
        return pd.DataFrame(results), None

    return None, "Unknown use case"


# ═══════════════════════════════════════════════════════════════════
# LMP render — upload → instant 24h chart + BESS strategy overlays
# ═══════════════════════════════════════════════════════════════════
def render_lmp_full(resolved_df, key_prefix="lmp", search_results=None, ercot_sub=None):
    st.markdown('<div class="section-label">LMP Analysis Engine</div>', unsafe_allow_html=True)

    lmp_key = f"{key_prefix}_lmpdf"
    bus_key = f"{key_prefix}_selbus"
    if lmp_key not in st.session_state: st.session_state[lmp_key] = None
    if bus_key  not in st.session_state: st.session_state[bus_key] = None

    # ── Upload + Live API ─────────────────────────────────────────
    up_col, api_col = st.columns([3, 2])
    with up_col:
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#6b6b64;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px;font-weight:500">Upload LMP File (CSV or ZIP)</div>', unsafe_allow_html=True)
        up = st.file_uploader("LMP file", type=["csv","zip"],
                              key=f"{key_prefix}_uploader", label_visibility="collapsed")
        if up:
            with st.spinner("Parsing..."):
                ldf, err = parse_lmp_upload(up)
            if err and ldf is None:
                st.error(err)
            else:
                if err: st.warning(err)
                if ldf is not None and "bus" not in ldf.columns:
                    cands = [c for c in ldf.columns if any(k in c.upper().replace("_","")
                             for k in ["ELECTRICALBUS","SETTLEMENTPOINT","BUSNAME","NODENAME","ELECBUS"])]
                    if cands: ldf = ldf.rename(columns={cands[0]: "bus"})
                if ldf is not None:
                    st.session_state[lmp_key] = ldf
                    st.session_state[bus_key] = None
                    files = ldf["_source_file"].nunique() if "_source_file" in ldf.columns else 1
                    st.success(f"✓ {len(ldf):,} rows · {files} file(s)")

    with api_col:
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#6b6b64;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px;font-weight:500">Live ERCOT API</div>', unsafe_allow_html=True)
        a1, a2 = st.columns([2, 1])
        with a1:
            live_bus = st.selectbox("Bus", resolved_df["Bus"].tolist(),
                                    key=f"{key_prefix}_live_bus", label_visibility="collapsed")
        with a2:
            days_back = st.selectbox("Days", [1,7,14,30,60],
                                     key=f"{key_prefix}_live_days", label_visibility="collapsed")
        if st.button("Fetch Live →", key=f"{key_prefix}_fetch_live",
                     type="primary", use_container_width=True):
            d_to   = datetime.now().strftime("%Y-%m-%d")
            d_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            with st.spinner(f"Fetching {live_bus}..."):
                ldf, err = fetch_ercot_dam_live(live_bus, d_from, d_to)
            if err:
                st.error("API unavailable — upload a file instead")
            elif ldf is not None:
                ldf.columns = [c.lower().replace(" ","_") for c in ldf.columns]
                price_col = next((c for c in ldf.columns if "price" in c), None)
                hour_col  = next((c for c in ldf.columns if "hour" in c), None)
                date_col  = next((c for c in ldf.columns if "date" in c or "delivery" in c), None)
                if price_col:
                    ldf = ldf.rename(columns={price_col: "price"})
                    ldf["bus"] = live_bus
                    ldf["price"] = pd.to_numeric(ldf["price"], errors="coerce")
                    if date_col and hour_col:
                        ldf["hour_int"] = pd.to_numeric(ldf[hour_col], errors="coerce").fillna(0).astype(int)
                        ldf["datetime"] = pd.to_datetime(ldf[date_col], errors="coerce") + \
                                          pd.to_timedelta(ldf["hour_int"]-1, unit="h")
                    st.session_state[lmp_key] = ldf
                    st.session_state[bus_key] = None
                    st.success(f"✓ {len(ldf):,} rows for {live_bus}")

    # ── Check data ────────────────────────────────────────────────
    ldf = st.session_state[lmp_key]
    if ldf is None:
        st.markdown("""<div class="map-placeholder" style="padding:32px;margin-top:12px">
            <div class="mp-icon">📊</div>
            <div class="mp-title">No data loaded</div>
            <div class="mp-sub">Upload a CSV or ZIP above — the chart will appear instantly</div>
        </div>""", unsafe_allow_html=True)
        return None

    # ── Match buses ───────────────────────────────────────────────
    buses_up = set(resolved_df["Bus"].str.upper())
    ldf["_bus_up"] = ldf["bus"].astype(str).str.upper().str.strip()
    matched = ldf[ldf["_bus_up"].isin(buses_up)].copy()
    if matched.empty:
        st.warning("No buses matched. Check settlement point names in your file.")
        return None

    # ── Data metrics row ─────────────────────────────────────────
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Total Rows",    f"{len(ldf):,}")
    m2.metric("Matched Rows",  f"{len(matched):,}")
    m3.metric("Buses Matched", f"{matched['_bus_up'].nunique()} / {len(buses_up)}")
    m4.metric("Avg LMP",       f"${matched['price'].mean():.2f}/MWh")
    st.markdown('<hr style="border-color:#e2e0db;margin:14px 0"/>', unsafe_allow_html=True)

    # ── Bus + Date controls ───────────────────────────────────────
    bus_list = sorted(matched["_bus_up"].unique().tolist())
    if st.session_state[bus_key] not in bus_list:
        st.session_state[bus_key] = bus_list[0]

    c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
    with c1:
        sel_bus = st.selectbox("Bus / Settlement Point", bus_list,
            index=bus_list.index(st.session_state[bus_key]),
            key=f"{key_prefix}_bus_sel", label_visibility="collapsed")
        st.session_state[bus_key] = sel_bus

    # ── Prepare data for selected bus ────────────────────────────
    bdf_full = matched[matched["_bus_up"] == sel_bus].copy()
    bdf_full["datetime"] = pd.to_datetime(bdf_full["datetime"], errors="coerce")
    bdf_full = bdf_full.dropna(subset=["datetime"]).sort_values("datetime")

    d_min = bdf_full["datetime"].dt.date.min()
    d_max = bdf_full["datetime"].dt.date.max()

    with c2:
        sel_date = st.date_input("Date", value=d_max,
            min_value=d_min, max_value=d_max,
            key=f"{key_prefix}_date_sel", label_visibility="collapsed")
    with c3:
        show_all = st.checkbox("All dates", value=(d_min==d_max), key=f"{key_prefix}_showall")
    with c4:
        multi_date = st.checkbox("Compare dates", value=False, key=f"{key_prefix}_multidate")

    # ── Filter ───────────────────────────────────────────────────
    if show_all or d_min == d_max:
        plot_bdf = bdf_full.copy()
        date_label = f"{d_min} → {d_max}"
    else:
        plot_bdf = bdf_full[bdf_full["datetime"].dt.date == sel_date].copy()
        date_label = str(sel_date)

    if plot_bdf.empty:
        st.warning(f"No data for {sel_date}. Try 'All dates'.")
        return None

    # ── Build hourly profile (the key fix) ───────────────────────
    # Extract hour-of-day from timestamps, handling SCED millisecond noise
    time_span = (plot_bdf["datetime"].max() - plot_bdf["datetime"].min()).total_seconds()
    n_rows = len(plot_bdf)

    if n_rows > 1 and time_span < 120:
        # Sub-second timestamps → assign synthetic hour-of-day by position
        # 19000 rows ÷ 24 hours = ~792 rows/hour
        rows_per_hour = max(1, n_rows // 24)
        plot_bdf = plot_bdf.reset_index(drop=True)
        plot_bdf["Hour"] = (plot_bdf.index // rows_per_hour) + 1
        plot_bdf["Hour"] = plot_bdf["Hour"].clip(1, 24)
        hourly = plot_bdf.groupby("Hour")["price"].mean().reset_index()
        hourly.columns = ["Hour", "price"]
        fixed_timestamps = True
    else:
        plot_bdf["Hour"] = plot_bdf["datetime"].dt.hour + 1  # 1-24
        hourly = plot_bdf.groupby("Hour")["price"].mean().reset_index()
        hourly.columns = ["Hour", "price"]
        fixed_timestamps = False

    if hourly.empty or len(hourly) < 2:
        st.warning("Not enough hourly data points. Try 'All dates' for a fuller dataset.")
        return None

    # ── Summary metrics ───────────────────────────────────────────
    avg_p    = hourly["price"].mean()
    last_p   = hourly["price"].iloc[-1]
    peak_p   = hourly["price"].max()
    peak_h   = hourly.loc[hourly["price"].idxmax(), "Hour"]
    min_p    = hourly["price"].min()
    min_h    = hourly.loc[hourly["price"].idxmin(), "Hour"]
    vol      = hourly["price"].std()
    spread   = peak_p - min_p
    pct_chg  = ((last_p - hourly["price"].iloc[0]) / abs(hourly["price"].iloc[0]) * 100) if hourly["price"].iloc[0] != 0 else 0
    vol_lbl  = "HIGH" if vol > 15 else "MOD" if vol > 5 else "LOW"

    sm1,sm2,sm3,sm4,sm5 = st.columns(5)
    sm1.metric("Last LMP",   f"${last_p:.2f}",  f"{pct_chg:+.1f}%")
    sm2.metric("Avg LMP",    f"${avg_p:.2f}")
    sm3.metric("Peak LMP",   f"${peak_p:.2f}",  f"Hr {peak_h:.0f}")
    sm4.metric("Min LMP",    f"${min_p:.2f}",   f"Hr {min_h:.0f}")
    sm5.metric("Spread",     f"${spread:.2f}",  vol_lbl)

    # ── Strategy recommendation ───────────────────────────────────
    if spread > 80:
        st.success("✅  Pure Merchant Arbitrage Opportunity — spread > $80/MWh")
    elif spread > 40:
        st.warning("⚠️  Solar + Storage Overbuild — spread $40–80/MWh")
    else:
        st.info("ℹ️  Low Spread — focus on Capacity / Ancillary markets")

    # ── Overlay controls ─────────────────────────────────────────
    st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#6b6b64;letter-spacing:.14em;text-transform:uppercase;margin:12px 0 8px;font-weight:500">Chart Overlays</div>', unsafe_allow_html=True)
    ov1, ov2, ov3, ov4, ov5, ov6 = st.columns([2, 2, 1, 1, 1, 1])

    # BESS strategy selector — defaults to None (not shown until selected)
    with ov1:
        bess_strategy = st.selectbox(
            "BESS Storage Strategy",
            ["None", "2H Storage (±1 hr)", "4H Storage (±2 hr)", "Both (2H + 4H)"],
            index=0,
            key=f"{key_prefix}_bess_strategy",
            label_visibility="visible"
        )
    ov_2h = bess_strategy in ("2H Storage (±1 hr)", "Both (2H + 4H)")
    ov_4h = bess_strategy in ("4H Storage (±2 hr)", "Both (2H + 4H)")

    with ov2:
        ov_ma3    = st.checkbox("MA3 Line",    value=True,  key=f"{key_prefix}_ov_ma3")
        ov_avg    = st.checkbox("Avg Line",    value=True,  key=f"{key_prefix}_ov_avg")
    with ov3:
        ov_neg    = st.checkbox("Neg. Prices", value=False, key=f"{key_prefix}_ov_neg")
    with ov4:
        ov_spread = st.checkbox("Spread Band", value=False, key=f"{key_prefix}_ov_spread")
    with ov5:
        ov_multi  = st.checkbox("All Buses",   value=False, key=f"{key_prefix}_ov_multi")

    # ── Only compute BESS strategy when selected ──────────────────
    if ov_2h or ov_4h:
        rev2, roll2, low2, high2, cw2, dw2 = bess_calc(hourly, half_w=1)
        rev4, roll4, low4, high4, cw4, dw4 = bess_calc(hourly, half_w=2)
    else:
        rev2 = rev4 = low2 = high2 = low4 = high4 = 0
        roll2 = roll4 = hourly["price"]
        cw2 = cw4 = dw2 = dw4 = (0, 0)

    # ── BUILD CHART ───────────────────────────────────────────────
    PALETTE = ["#c8102e","#1a3a7a","#b8860b","#1a6a1a","#7a1a5a","#5a3a1a","#1a5a7a"]
    fig = go.Figure()

    # Multi-date comparison
    if multi_date and not show_all and d_min != d_max:
        all_dates = sorted(bdf_full["datetime"].dt.date.unique().tolist())
        compare_dates = st.multiselect("Select dates to compare", all_dates,
            default=all_dates[:min(3,len(all_dates))], key=f"{key_prefix}_cmp_dates")
        for di, cdate in enumerate(compare_dates):
            cdf = bdf_full[bdf_full["datetime"].dt.date == cdate].copy()
            cdf["Hour"] = cdf["datetime"].dt.hour + 1
            ch = cdf.groupby("Hour")["price"].mean().reset_index()
            ch.columns = ["Hour","price"]
            if ch.empty: continue
            col = PALETTE[di % len(PALETTE)]
            fig.add_trace(go.Scatter(x=ch["Hour"], y=ch["price"], mode="lines",
                name=str(cdate), line=dict(color=col, width=2),
                hovertemplate=f"{cdate} Hr%{{x}}: $%{{y:.2f}}<extra></extra>"))
    else:
        # BESS shaded zones BELOW lines
        if ov_2h:
            fig.add_vrect(x0=cw2[0]-0.4, x1=cw2[1]+0.4,
                          fillcolor="rgba(26,106,26,0.10)", layer="below", line_width=0,
                          annotation_text=f"Charge 2H\nHr {cw2[0]:.0f}–{cw2[1]:.0f}",
                          annotation_font=dict(size=9, color="#1a6a1a", family="DM Mono"),
                          annotation_position="top left")
            fig.add_vrect(x0=dw2[0]-0.4, x1=dw2[1]+0.4,
                          fillcolor="rgba(200,16,46,0.08)", layer="below", line_width=0,
                          annotation_text=f"Discharge 2H\nHr {dw2[0]:.0f}–{dw2[1]:.0f}",
                          annotation_font=dict(size=9, color="#c8102e", family="DM Mono"),
                          annotation_position="top right")

        if ov_4h:
            fig.add_vrect(x0=cw4[0]-0.4, x1=cw4[1]+0.4,
                          fillcolor="rgba(26,58,122,0.06)", layer="below", line_width=0,
                          annotation_text=f"Charge 4H\nHr {cw4[0]:.0f}–{cw4[1]:.0f}",
                          annotation_font=dict(size=9, color="#1a3a7a", family="DM Mono"),
                          annotation_position="bottom left")
            fig.add_vrect(x0=dw4[0]-0.4, x1=dw4[1]+0.4,
                          fillcolor="rgba(184,134,11,0.06)", layer="below", line_width=0,
                          annotation_text=f"Discharge 4H\nHr {dw4[0]:.0f}–{dw4[1]:.0f}",
                          annotation_font=dict(size=9, color="#b8860b", family="DM Mono"),
                          annotation_position="bottom right")

        # Negative price zones
        if ov_neg:
            neg_hrs = hourly[hourly["price"] < 0]["Hour"].tolist()
            for h in neg_hrs:
                fig.add_vrect(x0=h-0.5, x1=h+0.5, fillcolor="rgba(120,0,160,0.12)",
                              layer="below", line_width=0)

        # Average horizontal line
        if ov_avg:
            fig.add_hline(y=avg_p, line_dash="dash",
                          line_color="rgba(100,100,100,0.5)", line_width=1,
                          annotation_text=f"Avg ${avg_p:.2f}",
                          annotation_font=dict(color="#6b6b64", size=10, family="DM Mono"),
                          annotation_position="right")

        # All buses comparison (dimmed)
        if ov_multi:
            for bi, other_bus in enumerate([b for b in bus_list if b != sel_bus][:5]):
                obdf = matched[matched["_bus_up"]==other_bus].copy()
                obdf["datetime"] = pd.to_datetime(obdf["datetime"], errors="coerce")
                if not (show_all or d_min==d_max):
                    obdf = obdf[obdf["datetime"].dt.date == sel_date]
                obdf["Hour"] = obdf["datetime"].dt.hour + 1
                oh = obdf.groupby("Hour")["price"].mean().reset_index()
                oh.columns = ["Hour","price"]
                if oh.empty: continue
                fig.add_trace(go.Scatter(x=oh["Hour"], y=oh["price"], mode="lines",
                    name=other_bus, line=dict(color=PALETTE[(bi+1)%len(PALETTE)], width=1.2),
                    opacity=0.45,
                    hovertemplate=f"{other_bus} Hr%{{x}}: $%{{y:.2f}}<extra></extra>"))

        # MA3 rolling average
        if ov_ma3:
            fig.add_trace(go.Scatter(x=hourly["Hour"], y=roll2,
                mode="lines", name="MA3 (3-hr roll avg)",
                line=dict(color="#c8102e", width=1.5, dash="dot"),
                opacity=0.55,
                hovertemplate="MA3 Hr%{x}: $%{y:.2f}<extra></extra>"))

        # Spread band (min/max envelope)
        if ov_spread:
            fig.add_hline(y=peak_p, line_dash="dot", line_color="rgba(200,16,46,0.3)", line_width=1)
            fig.add_hline(y=min_p,  line_dash="dot", line_color="rgba(26,106,26,0.3)", line_width=1)

        # Main LMP line
        fig.add_trace(go.Scatter(
            x=hourly["Hour"], y=hourly["price"],
            mode="lines+markers", name=sel_bus,
            line=dict(color="#c8102e", width=2.5),
            marker=dict(size=5, color="#c8102e"),
            hovertemplate=f"{sel_bus} Hr%{{x}}: $%{{y:.2f}}/MWh<extra></extra>"
        ))

        # 2H BESS strategy band
        if ov_2h:
            bess2_y = []
            for _, r in hourly.iterrows():
                h = r["Hour"]
                if cw2[0] <= h <= cw2[1]:   bess2_y.append(r["price"] - spread * 0.12)
                elif dw2[0] <= h <= dw2[1]: bess2_y.append(r["price"] + spread * 0.12)
                else:                        bess2_y.append(r["price"])
            fig.add_trace(go.Scatter(x=hourly["Hour"], y=bess2_y,
                mode="lines", name=f"2H BESS Band  (rev ${rev2:.2f}/MWh)",
                line=dict(color="#1a6a1a", width=2, dash="dashdot"),
                hovertemplate="2H Band Hr%{x}: $%{y:.2f}<extra></extra>"))

            # Charge / Discharge markers
            fig.add_trace(go.Scatter(
                x=[low2], y=[hourly.loc[hourly["Hour"].sub(low2).abs().idxmin(),"price"]],
                mode="markers+text",
                marker=dict(size=14, color="#1a6a1a", symbol="triangle-up"),
                text=[f"  Charge\nHr {low2:.0f}"], textposition="middle right",
                textfont=dict(color="#1a6a1a", size=9, family="DM Mono"),
                name=f"2H Charge Hr {low2:.0f}", showlegend=False))
            fig.add_trace(go.Scatter(
                x=[high2], y=[hourly.loc[hourly["Hour"].sub(high2).abs().idxmin(),"price"]],
                mode="markers+text",
                marker=dict(size=14, color="#c8102e", symbol="triangle-down"),
                text=[f"  Discharge\nHr {high2:.0f}"], textposition="middle right",
                textfont=dict(color="#c8102e", size=9, family="DM Mono"),
                name=f"2H Discharge Hr {high2:.0f}", showlegend=False))

        # 4H BESS strategy band
        if ov_4h:
            bess4_y = []
            for _, r in hourly.iterrows():
                h = r["Hour"]
                if cw4[0] <= h <= cw4[1]:   bess4_y.append(r["price"] - spread * 0.20)
                elif dw4[0] <= h <= dw4[1]: bess4_y.append(r["price"] + spread * 0.20)
                else:                        bess4_y.append(r["price"])
            fig.add_trace(go.Scatter(x=hourly["Hour"], y=bess4_y,
                mode="lines", name=f"4H BESS Band  (rev ${rev4:.2f}/MWh)",
                line=dict(color="#1a3a7a", width=2, dash="dash"),
                hovertemplate="4H Band Hr%{x}: $%{y:.2f}<extra></extra>"))

    # ── Chart layout ──────────────────────────────────────────────
    fig.update_layout(
        title=dict(
            text=f"24-Hour LMP Profile — {sel_bus} — {date_label}",
            font=dict(family="Playfair Display", size=15, color="#1a1a18"), x=0.01
        ),
        height=480,
        paper_bgcolor="#ffffff", plot_bgcolor="#f7f7f5",
        font=dict(family="DM Sans", color="#1a1a18", size=11),
        xaxis=dict(
            title=dict(text="Hour Ending", font=dict(color="#6b6b64", size=11)),
            tickmode="linear", dtick=1,
            range=[0.5, 24.5],
            gridcolor="#e2e0db", linecolor="#d0cdc6",
            tickfont=dict(size=10, color="#6b6b64"),
            showgrid=True,
        ),
        yaxis=dict(
            title=dict(text="LMP ($/MWh)", font=dict(color="#6b6b64", size=11)),
            gridcolor="#e2e0db", linecolor="#d0cdc6",
            tickfont=dict(size=10, color="#6b6b64"),
            tickprefix="$",
        ),
        legend=dict(
            bgcolor="rgba(247,247,245,0.96)", bordercolor="#e2e0db", borderwidth=1,
            font=dict(size=10, family="DM Sans"),
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
        ),
        margin=dict(l=60, r=20, t=60, b=50),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── BESS revenue summary cards ────────────────────────────────
    if ov_2h or ov_4h:
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#6b6b64;letter-spacing:.14em;text-transform:uppercase;margin:12px 0 8px;font-weight:500">Rolling-Average BESS Strategy Results</div>', unsafe_allow_html=True)

        with st.expander("ℹ️ How the rolling-average BESS strategy works", expanded=False):
            st.markdown("""
**Step 1 — Smooth the curve:** A 3-hour centred rolling average removes single-hour spikes.

**Step 2 — Find optimal hours:** Hour with lowest rolling avg → charge centre. Hour with highest → discharge centre.

**Step 3 — Set windows:**
| Storage | Charge window | Discharge window |
|---|---|---|
| 2H BESS | ±1 hr around avg-low | ±1 hr around avg-high |
| 4H BESS | ±2 hr around avg-low | ±2 hr around avg-high |

**Revenue** = avg LMP during discharge − avg LMP during charge
            """)

        r1,r2,r3,r4,r5,r6 = st.columns(6)
        r1.metric("2H Charge Hr",    f"Hr {low2:.0f}",  f"Avg ${hourly.loc[hourly['Hour'].sub(low2).abs().idxmin(),'price']:.2f}")
        r2.metric("2H Discharge Hr", f"Hr {high2:.0f}", f"Avg ${hourly.loc[hourly['Hour'].sub(high2).abs().idxmin(),'price']:.2f}")
        r3.metric("2H Revenue",      f"${rev2:.2f}/MWh")
        r4.metric("4H Charge Hr",    f"Hr {low4:.0f}",  f"Avg ${hourly.loc[hourly['Hour'].sub(low4).abs().idxmin(),'price']:.2f}")
        r5.metric("4H Discharge Hr", f"Hr {high4:.0f}", f"Avg ${hourly.loc[hourly['Hour'].sub(high4).abs().idxmin(),'price']:.2f}")
        r6.metric("4H Revenue",      f"${rev4:.2f}/MWh")

    # ── Deep-dive use-case analysis ───────────────────────────────
    st.markdown('<div class="section-label" style="margin-top:24px">Deep-Dive Analysis</div>', unsafe_allow_html=True)

    USE_CASES = {
        "congestion":  ("🔥 Congestion Analysis", "Node-pair price spreads · bottleneck detection"),
        "curtailment": ("⚠️ Curtailment Risk",    "Negative price frequency · renewable impact"),
        "ftr":         ("🎯 FTR Scanner",          "Node-pair FTR value · win rate"),
        "revenue":     ("🏗️ Revenue Model",        "Solar · Wind · BESS annual revenue per MW"),
    }

    uc_sel = st.selectbox("Analysis module", list(USE_CASES.keys()),
        format_func=lambda k: USE_CASES[k][0],
        key=f"{key_prefix}_uc_sel", label_visibility="collapsed")
    uc_title, uc_desc = USE_CASES[uc_sel]
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:13px;color:#6b6b64;margin-bottom:10px">{uc_desc}</div>', unsafe_allow_html=True)

    run_btn = st.button(f"Run {uc_title} →", key=f"{key_prefix}_run_{uc_sel}",
                        type="primary", use_container_width=False)
    result = None
    if run_btn:
        with st.spinner("Analysing..."):
            result, err = run_lmp_analytics(matched.copy(), resolved_df, uc_sel)
        if err:
            st.error(err); result = None
        else:
            for old_uc in list(USE_CASES.keys()):
                if old_uc != uc_sel:
                    st.session_state.pop(f"{key_prefix}_uc_result_{old_uc}", None)
            st.session_state[f"{key_prefix}_uc_result_{uc_sel}"] = result
    elif f"{key_prefix}_uc_result_{uc_sel}" in st.session_state:
        result = st.session_state[f"{key_prefix}_uc_result_{uc_sel}"]

    if result is None:
        pass

    # ══════════════════════════════════════════════════════════════
    # CONGESTION — CI / CSS dashboard
    # ══════════════════════════════════════════════════════════════
    elif uc_sel == "congestion" and isinstance(result, pd.DataFrame):
        hub = result["Hub (reference)"].iloc[0] if len(result) else "—"
        st.markdown(f"""
        <div style="background:#f0efec;border-left:4px solid #1a3a7a;border-radius:2px;
             padding:10px 16px;margin-bottom:14px;font-family:DM Sans,sans-serif;font-size:13px;color:#3d3d38">
            <b>Congestion Index (CI)</b> = LMP<sub>hub</sub> − LMP<sub>node</sub> &nbsp;·&nbsp;
            <b>Hub reference:</b> <code>{hub}</code> &nbsp;·&nbsp;
            <b>CSS</b> = mean(|CI|) per node &nbsp;·&nbsp;
            Threshold: |CI| &gt; $10/MWh = congested
        </div>""", unsafe_allow_html=True)

        # Summary metric row
        high_count = len(result[result["Congestion Risk"]=="🔴 HIGH"])
        med_count  = len(result[result["Congestion Risk"]=="🟡 MEDIUM"])
        low_count  = len(result[result["Congestion Risk"]=="🟢 LOW"])
        avg_css    = result["CSS ($/MWh)"].mean()
        max_css    = result["CSS ($/MWh)"].max()
        max_node   = result.loc[result["CSS ($/MWh)"].idxmax(), "Node"] if len(result) else "—"

        cm1,cm2,cm3,cm4,cm5 = st.columns(5)
        cm1.metric("Nodes Analysed",  len(result))
        cm2.metric("🔴 High Risk",    high_count)
        cm3.metric("🟡 Medium Risk",  med_count)
        cm4.metric("Avg CSS",         f"${avg_css:.2f}/MWh")
        cm5.metric("Most Congested",  max_node, f"${max_css:.2f} CSS")

        # CSS bar chart
        fig_css = go.Figure()
        color_map = {"🔴 HIGH": "#c8102e", "🟡 MEDIUM": "#b8860b", "🟢 LOW": "#1a6a1a"}
        for risk_label, grp in result.groupby("Congestion Risk"):
            fig_css.add_trace(go.Bar(
                x=grp["Node"], y=grp["CSS ($/MWh)"],
                name=risk_label,
                marker_color=color_map.get(risk_label, "#6b6b64"),
                hovertemplate="<b>%{x}</b><br>CSS: $%{y:.2f}/MWh<extra></extra>"))
        _lay = neon_plotly_layout("Congestion Severity Score (CSS) by Node", 300)
        _lay.update(barmode="stack", xaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",tickangle=-35,tickfont=dict(size=10,color="#6b6b64")), yaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",title="CSS ($/MWh)",tickprefix="$",tickfont=dict(size=10,color="#6b6b64")))
        fig_css.update_layout(**_lay)
        st.plotly_chart(fig_css, use_container_width=True)

        # Congestion % gauge-style bar
        fig_pct = go.Figure()
        result_s = result.sort_values("Congestion %", ascending=False)
        fig_pct.add_trace(go.Bar(
            x=result_s["Node"], y=result_s["Congestion %"],
            marker=dict(
                color=result_s["Congestion %"],
                colorscale=[[0,"#1a6a1a"],[0.3,"#b8860b"],[1,"#c8102e"]],
                showscale=True,
                colorbar=dict(title="%", ticksuffix="%", len=0.6),
            ),
            text=result_s["Congestion %"].apply(lambda v: f"{v:.1f}%"),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Congested: %{y:.1f}% of intervals<extra></extra>"))
        _lay = neon_plotly_layout("Congestion % of Intervals (|CI| > $10/MWh)", 300)
        _lay.update(xaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",tickangle=-35,tickfont=dict(size=10,color="#6b6b64")), yaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",title="Congestion %",ticksuffix="%",tickfont=dict(size=10,color="#6b6b64")))
        fig_pct.update_layout(**_lay)
        st.plotly_chart(fig_pct, use_container_width=True)

        # Source-side vs Load-side stacked bar
        if "Source-Side Hours" in result.columns:
            fig_side = go.Figure()
            fig_side.add_trace(go.Bar(
                x=result["Node"], y=result["Source-Side Hours"],
                name="Source-Side (CI > +10)", marker_color="#c8102e",
                hovertemplate="%{x}<br>Source-Side: %{y} hrs<extra></extra>"))
            fig_side.add_trace(go.Bar(
                x=result["Node"], y=result["Load-Side Hours"],
                name="Load-Side (CI < −10)",  marker_color="#1a3a7a",
                hovertemplate="%{x}<br>Load-Side: %{y} hrs<extra></extra>"))
            _lay = neon_plotly_layout("Congestion Direction — Source vs Load Side", 280)
            _lay.update(barmode="group", xaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",tickangle=-35,tickfont=dict(size=10,color="#6b6b64")), yaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",title="Hours",tickfont=dict(size=10,color="#6b6b64")))
            fig_side.update_layout(**_lay)
            st.plotly_chart(fig_side, use_container_width=True)

        # Congestion Rent proxy
        if "CR Proxy ($/hr)" in result.columns:
            st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:10px;color:#6b6b64;letter-spacing:.12em;text-transform:uppercase;margin:10px 0 6px">Congestion Rent Proxy at {batt_mw} MW capacity</div>', unsafe_allow_html=True)
            fig_cr = go.Figure(go.Bar(
                x=result["Node"], y=result["CR Proxy ($/hr)"],
                marker_color=["#c8102e" if v>=0 else "#1a3a7a" for v in result["CR Proxy ($/hr)"]],
                hovertemplate="%{x}<br>CR Proxy: $%{y:,.0f}/hr<extra></extra>"))
            _lay = neon_plotly_layout("Congestion Rent Proxy ($/hr) = Avg CI × Capacity MW", 240)
            _lay.update(xaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",tickangle=-35,tickfont=dict(size=10,color="#6b6b64")), yaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",title="$/hr",tickprefix="$",tickfont=dict(size=10,color="#6b6b64")))
            fig_cr.update_layout(**_lay)
            st.plotly_chart(fig_cr, use_container_width=True)

        # Full table
        with st.expander("Full Congestion Table"):
            st.dataframe(result, use_container_width=True,
                column_config={
                    "CSS ($/MWh)":       st.column_config.NumberColumn(format="$%.2f"),
                    "Avg CI ($/MWh)":    st.column_config.NumberColumn(format="$%.2f"),
                    "Max |CI| ($/MWh)":  st.column_config.NumberColumn(format="$%.2f"),
                    "Congestion %":      st.column_config.NumberColumn(format="%.1f%%"),
                    "CR Proxy ($/hr)":   st.column_config.NumberColumn(format="$%.0f"),
                })
        st.download_button("↓ Congestion CSV", data=to_csv_bytes(result),
                           file_name="congestion.csv", mime="text/csv", key=f"{key_prefix}_dl_cong")

    # ══════════════════════════════════════════════════════════════
    # CURTAILMENT — CPI / ECS dashboard
    # ══════════════════════════════════════════════════════════════
    elif uc_sel == "curtailment" and isinstance(result, pd.DataFrame):
        st.markdown("""
        <div style="background:#f0efec;border-left:4px solid #b8860b;border-radius:2px;
             padding:10px 16px;margin-bottom:14px;font-family:DM Sans,sans-serif;font-size:13px;color:#3d3d38">
            <b>CPI</b> = (intervals with LMP ≤ $0) ÷ Total Intervals × 100 &nbsp;·&nbsp;
            <b>ECS</b> = Economic Curtailment Signal (LMP ≤ 0) &nbsp;·&nbsp;
            Thresholds: CPI &gt; 20% = 🔴 HIGH, &gt; 5% = 🟡 MEDIUM, ≤ 5% = 🟢 LOW
        </div>""", unsafe_allow_html=True)

        # Summary row
        high_c = len(result[result["Curtailment Risk"]=="🔴 HIGH"])
        med_c  = len(result[result["Curtailment Risk"]=="🟡 MEDIUM"])
        avg_cpi = result["CPI % (LMP ≤ 0)"].mean()
        max_cpi = result["CPI % (LMP ≤ 0)"].max()
        max_bus = result.loc[result["CPI % (LMP ≤ 0)"].idxmax(), "Bus"] if len(result) else "—"
        total_neg = int(result["≤ $0 Hours"].sum())

        cm1,cm2,cm3,cm4,cm5 = st.columns(5)
        cm1.metric("Buses Analysed",     len(result))
        cm2.metric("🔴 High CPI",        high_c)
        cm3.metric("🟡 Medium CPI",      med_c)
        cm4.metric("Avg CPI %",          f"{avg_cpi:.1f}%")
        cm5.metric("Highest CPI",        max_bus, f"{max_cpi:.1f}%")

        # CPI % bar chart — color-coded
        result_s = result.sort_values("CPI % (LMP ≤ 0)", ascending=False)
        fig_cpi = go.Figure()
        risk_colors = {"🔴 HIGH":"#c8102e","🟡 MEDIUM":"#b8860b","🟢 LOW":"#1a6a1a"}
        for risk_label, grp in result_s.groupby("Curtailment Risk"):
            fig_cpi.add_trace(go.Bar(
                x=grp["Bus"], y=grp["CPI % (LMP ≤ 0)"],
                name=risk_label,
                marker_color=risk_colors.get(risk_label, "#6b6b64"),
                text=grp["CPI % (LMP ≤ 0)"].apply(lambda v: f"{v:.1f}%"),
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>CPI: %{y:.2f}%<extra></extra>"))
        # Add 20% and 5% threshold lines
        fig_cpi.add_hline(y=20, line_dash="dot", line_color="#c8102e", line_width=1,
                          annotation_text="HIGH threshold 20%",
                          annotation_font=dict(color="#c8102e", size=9, family="DM Mono"))
        fig_cpi.add_hline(y=5,  line_dash="dot", line_color="#b8860b", line_width=1,
                          annotation_text="MEDIUM threshold 5%",
                          annotation_font=dict(color="#b8860b", size=9, family="DM Mono"))
        _lay = neon_plotly_layout("Curtailment Probability Index (CPI %) by Bus", 320)
        _lay.update(barmode="stack", xaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",tickangle=-35,tickfont=dict(size=10,color="#6b6b64")), yaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",title="CPI %",ticksuffix="%",tickfont=dict(size=10,color="#6b6b64")))
        fig_cpi.update_layout(**_lay)
        st.plotly_chart(fig_cpi, use_container_width=True)

        # Curtailment hours breakdown: ≤$0 vs <-$20
        fig_hrs = go.Figure()
        fig_hrs.add_trace(go.Bar(
            x=result_s["Bus"], y=result_s["≤ $0 Hours"],
            name="≤ $0/MWh (ECS = 1)", marker_color="#b8860b",
            hovertemplate="%{x}<br>≤$0 hrs: %{y}<extra></extra>"))
        fig_hrs.add_trace(go.Bar(
            x=result_s["Bus"], y=result_s["< −$20 Hours"],
            name="< −$20/MWh (deep neg)", marker_color="#c8102e",
            hovertemplate="%{x}<br><−$20 hrs: %{y}<extra></extra>"))
        _lay = neon_plotly_layout("Curtailment Hours — ECS Events by Severity", 280)
        _lay.update(barmode="overlay", xaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",tickangle=-35,tickfont=dict(size=10,color="#6b6b64")), yaxis=dict(gridcolor="#e2e0db",linecolor="#d0cdc6",title="Hours",tickfont=dict(size=10,color="#6b6b64")))
        fig_hrs.update_layout(**_lay)
        st.plotly_chart(fig_hrs, use_container_width=True)

        # Risk cards per bus
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#6b6b64;letter-spacing:.12em;text-transform:uppercase;margin:10px 0 8px">Node Risk Summary</div>', unsafe_allow_html=True)
        for _, row in result_s.iterrows():
            rc = {"🔴 HIGH":"#c8102e","🟡 MEDIUM":"#b8860b","🟢 LOW":"#1a6a1a"}.get(row["Curtailment Risk"], "#9b9b92")
            st.markdown(f"""
            <div style="background:#f7f7f5;border:1px solid {rc};border-left:4px solid {rc};
                 border-radius:2px;padding:11px 16px;margin-bottom:5px;
                 display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr 1fr;align-items:center;gap:8px">
                <span style="font-family:'DM Mono',monospace;font-size:12px;color:#1a1a18;font-weight:600">{row["Bus"]}</span>
                <span style="text-align:center"><div style="font-family:'DM Mono',monospace;font-size:9px;color:#9b9b92">CPI %</div>
                    <div style="font-family:'Playfair Display',serif;font-size:16px;font-weight:700;color:{rc}">{row["CPI % (LMP ≤ 0)"]:.1f}%</div></span>
                <span style="text-align:center"><div style="font-family:'DM Mono',monospace;font-size:9px;color:#9b9b92">ECS Events</div>
                    <div style="font-family:'DM Sans',sans-serif;font-size:13px;color:#3d3d38">{row["ECS Events"]}</div></span>
                <span style="text-align:center"><div style="font-family:'DM Mono',monospace;font-size:9px;color:#9b9b92">≤$0 Hrs</div>
                    <div style="font-family:'DM Sans',sans-serif;font-size:13px;color:#3d3d38">{row["≤ $0 Hours"]}</div></span>
                <span style="text-align:center"><div style="font-family:'DM Mono',monospace;font-size:9px;color:#9b9b92">Avg LMP</div>
                    <div style="font-family:'DM Sans',sans-serif;font-size:13px;color:#3d3d38">${row["Avg LMP ($/MWh)"]:.2f}</div></span>
                <span style="text-align:right"><span style="font-family:'DM Sans',sans-serif;font-size:12px;font-weight:600;color:{rc}">{row["Curtailment Risk"]}</span></span>
            </div>""", unsafe_allow_html=True)

        with st.expander("Full Curtailment Table"):
            st.dataframe(result_s, use_container_width=True,
                column_config={
                    "CPI % (LMP ≤ 0)":  st.column_config.NumberColumn(format="%.2f%%"),
                    "Avg LMP ($/MWh)":   st.column_config.NumberColumn(format="$%.2f"),
                    "Min LMP ($/MWh)":   st.column_config.NumberColumn(format="$%.2f"),
                    "Avg Curtailed LMP": st.column_config.NumberColumn(format="$%.2f"),
                })
        st.download_button("↓ Curtailment CSV", data=to_csv_bytes(result),
                           file_name="curtailment.csv", mime="text/csv", key=f"{key_prefix}_dl_curt")

    elif uc_sel == "ftr" and isinstance(result, pd.DataFrame):
        st.dataframe(result, use_container_width=True,
            column_config={"Avg FTR Value $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                           "Max FTR Value $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                           "Win Rate %": st.column_config.NumberColumn(format="%.1f%%")})
        st.download_button("↓ FTR CSV", data=to_csv_bytes(result),
                           file_name="ftr.csv", mime="text/csv", key=f"{key_prefix}_dl_ftr")

    elif uc_sel == "revenue" and isinstance(result, pd.DataFrame):
        st.dataframe(result, use_container_width=True,
            column_config={"Annual Solar Rev ($/MW)": st.column_config.NumberColumn(format="$%.0f"),
                           "Annual Wind Rev ($/MW)":  st.column_config.NumberColumn(format="$%.0f"),
                           "Annual BESS Rev ($/MW)":  st.column_config.NumberColumn(format="$%.0f")})
        st.download_button("↓ Revenue CSV", data=to_csv_bytes(result),
                           file_name="revenue.csv", mime="text/csv", key=f"{key_prefix}_dl_rev")

    # ── PDF export ────────────────────────────────────────────────
    st.markdown('<div class="section-label" style="margin-top:20px">Export Report</div>', unsafe_allow_html=True)
    lmp_summary = None
    try:
        lmp_summary = matched.groupby("_bus_up")["price"].agg(
            Mean="mean", Max="max", Min="min", Count="count").reset_index().round(2)
    except: pass
    if ercot_sub and resolved_df is not None:
        pdf_bytes = generate_pdf_report(search_results, ercot_sub, resolved_df, lmp_summary)
        st.download_button("↓ Download PDF Report (SunStripe)",
            data=bytes(pdf_bytes),
            file_name=f"sunstripe_{ercot_sub}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf", key=f"{key_prefix}_pdf_dl", type="primary")
    return ldf



# ═══════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="padding:24px 20px 20px">
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.4);
             letter-spacing:.18em;text-transform:uppercase;margin-bottom:10px">Energy Intelligence</div>
        <div style="font-family:'Playfair Display',serif;font-size:22px;font-weight:700;
             color:#fff;line-height:1.2;letter-spacing:-0.02em">SunStripe</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:12px;font-weight:300;
             color:rgba(255,255,255,0.5);margin-top:2px;letter-spacing:.04em">ERCOT Nodal Intelligence</div>
        <div style="margin-top:14px;height:1px;background:rgba(200,16,46,0.6)"></div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "🗺️ Infrastructure Map",
        "⚡ Node & Hub Selector",
        "🔍 Bus Lookup",
        "🏭 Substation Lookup",
        "📋 Browse All",
    ], label_visibility="collapsed")

    st.markdown(f"""
    <div style="padding:20px 20px 0;margin-top:8px">
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.3);
             letter-spacing:.14em;text-transform:uppercase;margin-bottom:14px;
             padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.08)">Dataset · Feb 2026</div>
        <div style="display:flex;flex-direction:column;gap:14px">
            <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.45)">Settlement Points</span>
                <span style="font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:#fff">{len(df):,}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.45)">Substations</span>
                <span style="font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:#fff">{df["Substation"].nunique():,}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.45)">Hubs</span>
                <span style="font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:#c8102e">{df[df["Hub"]!=""]["Hub"].nunique()}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.45)">Resource Nodes</span>
                <span style="font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:#fff">{df[df["Resource Node"]!=""].shape[0]:,}</span>
            </div>
        </div>
        <div style="margin-top:20px;height:1px;background:rgba(255,255,255,0.08)"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:16px 20px 24px">
    <a href="https://ercot-bess-dashboard-nhh9eztsqeuqxxuz97kacu.streamlit.app/" target="_blank"
       style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;
              background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
              border-radius:2px;font-family:'DM Sans',sans-serif;font-size:12px;
              color:rgba(255,255,255,0.6);text-decoration:none;margin-bottom:6px">
        <span>ERCOT BESS Dashboard</span><span style="opacity:.4">↗</span></a>
    <a href="https://fatal-flaw-o7aks4agtoffgyydbvrguj.streamlit.app/" target="_blank"
       style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;
              background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
              border-radius:2px;font-family:'DM Sans',sans-serif;font-size:12px;
              color:rgba(255,255,255,0.6);text-decoration:none">
        <span>SiteIQ Fatal Flaw</span><span style="opacity:.4">↗</span></a>
    </div>
    """, unsafe_allow_html=True)


if page == "🗺️ Infrastructure Map":

    st.markdown(f"""<div class="page-header">
        <div><div class="tag">Infrastructure · OSM + ERCOT</div>
        <h1>Substation <span>Search</span></h1></div>
        <div class="ph-right">ERCOT Texas Grid<br>{len(df):,} settlement points</div>
    </div>""", unsafe_allow_html=True)

    for k, v in [("search_results",None),("selected_osm",None),("ercot_sel_sub",None),
                 ("search_lat",31.5),("search_lon",-97.5)]:
        if k not in st.session_state: st.session_state[k] = v

    # ── SEARCH PARAMETERS ─────────────────────────────────────────
    st.markdown('<div style="background:#f7f7f5;border:1px solid #e2e0db;border-radius:2px;padding:20px 22px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;letter-spacing:.14em;text-transform:uppercase;margin-bottom:16px;font-weight:500">Search Parameters</div>', unsafe_allow_html=True)

    # ── Geocode search bar ─────────────────────────────────────────
    geo_col, geo_btn = st.columns([5, 1])
    with geo_col:
        geo_input = st.text_input("Address / City", placeholder="Type address, city, county or project name (e.g. 'Wichita Falls TX' or '2800 Post Oak Blvd Houston')",
                                  label_visibility="collapsed", key="geo_input")
    with geo_btn:
        geo_go = st.button("Locate →", key="geo_go", use_container_width=True)

    if geo_go and geo_input.strip():
        coord_m = re.match(r"^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$", geo_input.strip())
        if coord_m:
            st.session_state.search_lat = float(coord_m.group(1))
            st.session_state.search_lon = float(coord_m.group(2))
        else:
            try:
                geo_r = requests.get("https://nominatim.openstreetmap.org/search",
                    params={"q": geo_input, "format": "json", "limit": 1, "countrycodes": "us"},
                    headers={"User-Agent": "SunStripe-ERCOT/1.0"}, timeout=8).json()
                if geo_r:
                    st.session_state.search_lat = float(geo_r[0]["lat"])
                    st.session_state.search_lon = float(geo_r[0]["lon"])
                    st.success(f"📍 {geo_r[0]['display_name'].split(',')[0]}")
                else:
                    st.warning("Location not found.")
            except Exception as e:
                st.warning(f"Geocoding error: {e}")

    col_lat, col_lon, col_radius, col_thresh = st.columns([2,2,2,2])
    with col_lat:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#3a6080;margin-bottom:4px">Latitude</div>', unsafe_allow_html=True)
        lat_input = st.number_input("lat", value=st.session_state.search_lat, format="%.6f",
                                    label_visibility="collapsed", key="lat_input", min_value=25.0, max_value=37.0, step=0.001)
    with col_lon:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#3a6080;margin-bottom:4px">Longitude</div>', unsafe_allow_html=True)
        lon_input = st.number_input("lon", value=st.session_state.search_lon, format="%.6f",
                                    label_visibility="collapsed", key="lon_input", min_value=-107.0, max_value=-93.0, step=0.001)
    with col_radius:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#3a6080;margin-bottom:4px">Search Radius (miles)</div>', unsafe_allow_html=True)
        radius_miles = st.selectbox("radius", [5,10,15,25,35,50,75,100], index=3,
                                    label_visibility="collapsed", key="radius_sel")
    with col_thresh:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#3a6080;margin-bottom:4px">Hub Threshold (kV ≥)</div>', unsafe_allow_html=True)
        hub_thresh = st.selectbox("thresh", [115,138,230,345], index=2,
                                  label_visibility="collapsed", key="hub_thresh")

    # kV filter pills
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#3a6080;margin:12px 0 6px">Filter Voltages</div>', unsafe_allow_html=True)
    kv_options = ["34.5","69","115","138","230","345","500","765"]
    kv_cols = st.columns(len(kv_options)+1)
    kv_selected = []
    for i, kv in enumerate(kv_options):
        if kv_cols[i].checkbox(f"{kv} kV", value=kv in ["69","115","138","230","345"], key=f"kv_pill_{kv}"):
            kv_selected.append(kv)
    inc_unknown = kv_cols[-1].checkbox("Unknown V", value=True, key="inc_unknown")

    oim_url = f"https://openinframap.org/#10/{lat_input:.4f}/{lon_input:.4f}"
    link_col, btn_col = st.columns([4,1])
    with link_col:
        st.markdown(f'<a href="{oim_url}" target="_blank" style="font-family:Share Tech Mono,monospace;font-size:11px;color:#00c8ff;text-decoration:none;text-shadow:0 0 6px #00c8ff">🔗 Open this area in OpenInfraMap ↗</a>', unsafe_allow_html=True)
    with btn_col:
        search_btn = st.button("🔍 Search", use_container_width=True, key="search_btn", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Run search ─────────────────────────────────────────────────
    if search_btn:
        st.session_state.selected_osm = None
        st.session_state.ercot_sel_sub = None
        with st.spinner(f"Searching {radius_miles} mi radius..."):
            raw_els, err = search_substations_radius(lat_input, lon_input, radius_miles)
        if err:
            st.error(err)
            st.session_state.search_results = None
        else:
            filtered = []
            for el in raw_els:
                v = el["volt_kv"]
                if v is None:
                    if inc_unknown: filtered.append(el)
                elif any(abs(v - float(kv)) < 5 for kv in kv_selected):
                    filtered.append(el)
            for el in filtered:
                v = el["volt_kv"]
                el["is_hub"] = (v is not None and v >= hub_thresh)
            st.session_state.search_results = {
                "elements": filtered, "total_raw": len(raw_els),
                "lat": lat_input, "lon": lon_input,
                "radius_mi": radius_miles, "hub_thresh": hub_thresh,
            }

    results = st.session_state.search_results

    if results is None:
        st.markdown("""<div class="map-placeholder">
            <div class="mp-icon">🗺️</div>
            <div class="mp-title">No search yet</div>
            <div class="mp-sub">Enter an address or coordinates above, set your radius, and click Search.</div>
        </div>""", unsafe_allow_html=True)
    else:
        elements  = results["elements"]
        hubs_list = [e for e in elements if e["is_hub"]]
        node_list = [e for e in elements if not e["is_hub"]]
        clat, clon = results["lat"], results["lon"]

        m1,m2,m3,m4,m5 = st.columns(5)
        m1.metric("Total Found",  len(elements))
        m2.metric(f"Hubs ≥{results['hub_thresh']}kV", len(hubs_list))
        m3.metric(f"Nodes <{results['hub_thresh']}kV", len(node_list))
        m4.metric("Radius",       f"{results['radius_mi']} mi")
        m5.metric("Centre",       f"{clat:.3f}, {clon:.3f}")

        # ── MAP ───────────────────────────────────────────────────
        fmap = folium.Map(location=[clat, clon], zoom_start=10, tiles=None, prefer_canvas=True)
        folium.TileLayer(tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            attr="© CartoDB", name="Dark", overlay=False, control=True).add_to(fmap)
        folium.TileLayer(tiles="https://tiles.openinframap.org/power_medium/{z}/{x}/{y}.png",
            attr="© OpenInfraMap", name="⚡ Power", overlay=True, control=True, opacity=0.85).add_to(fmap)
        folium.TileLayer(tiles="https://tiles.openinframap.org/power_high/{z}/{x}/{y}.png",
            attr="© OpenInfraMap", name="⚡ HV Lines", overlay=True, control=True, opacity=0.75).add_to(fmap)

        folium.Circle(location=[clat,clon], radius=results["radius_mi"]*1609.34,
            color="#00ff9d", weight=1, fill=False, dash_array="6 4",
            tooltip=f"{results['radius_mi']} mi radius").add_to(fmap)
        folium.Marker(location=[clat,clon],
            icon=folium.DivIcon(html='<div style="width:14px;height:14px;border-radius:50%;background:#00ff9d;border:2px solid #fff;box-shadow:0 0 10px #00ff9d;margin:-7px 0 0 -7px;"></div>'),
            tooltip="Search Centre").add_to(fmap)

        sel_id = st.session_state.selected_osm.get("osm_id") if st.session_state.selected_osm else None
        for el in elements:
            is_sel   = (el["osm_id"] == sel_id)
            is_hub   = el["is_hub"]
            fill_col = "#ff6b00" if is_hub else "#00c8ff"
            name     = el.get("name") or "Unnamed"
            v        = el["volt_kv"]
            v_label  = f"{v:.0f} kV" if v else "? kV"
            op       = el.get("operator","")
            popup_html = (
                f'<div style="font-family:Share Tech Mono,monospace;background:#030712;color:#c8e6ff;'
                f'padding:12px;border-radius:4px;min-width:200px;border:1px solid rgba(0,200,255,0.25);'
                f'box-shadow:0 0 20px rgba(0,200,255,0.1);">'
                f'<div style="font-size:12px;font-weight:600;color:{"#ff6b00" if is_hub else "#00c8ff"};margin-bottom:8px">'
                f'{"◆ HUB" if is_hub else "● NODE"} {name}</div>'
                f'<div style="font-size:10px;color:#3a6080">VOLTAGE</div>'
                f'<div style="font-size:12px;margin-bottom:5px">{v_label}</div>'
                f'{"<div style=font-size:10px;color:#3a6080>OPERATOR</div><div style=font-size:11px;margin-bottom:5px>"+op+"</div>" if op else ""}'
                f'<div style="font-size:10px;color:#3a6080">{el["dist_mi"]:.1f} mi · {el["dist_km"]:.1f} km</div>'
                f'</div>'
            )
            folium.CircleMarker(location=[el["lat"],el["lon"]],
                radius=12 if is_sel else 8,
                color="#00ff9d" if is_sel else fill_col,
                weight=3 if is_sel else 1,
                fill=True, fill_color=fill_col,
                fill_opacity=0.95 if is_sel else 0.75,
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=f'{"◆" if is_hub else "●"} {name} · {v_label} · {el["dist_mi"]:.1f} mi'
            ).add_to(fmap)

        folium.LayerControl(collapsed=False, position="topright").add_to(fmap)
        st_folium(fmap, key="search_map", use_container_width=True, height=480)

        # Legend
        st.markdown(f"""
        <div style="display:flex;gap:20px;font-family:DM Mono,monospace;font-size:11px;
             color:#6b6b64;padding:8px 14px;background:#f7f7f5;border:1px solid #e2e0db;
             border-radius:2px;margin-top:8px;flex-wrap:wrap;">
            <span>● <span style="color:#00ff9d;text-shadow:0 0 6px #00ff9d">Search Centre</span></span>
            <span>◆ <span style="color:#ff6b00;text-shadow:0 0 6px #ff6b00">Hub ≥{results["hub_thresh"]} kV</span> — {len(hubs_list)}</span>
            <span>● <span style="color:#00c8ff;text-shadow:0 0 6px #00c8ff">Node &lt;{results["hub_thresh"]} kV</span> — {len(node_list)}</span>
            <span style="color:#1a3050">- - Radius ring</span>
        </div>""", unsafe_allow_html=True)

        # ── SUBSTATION LIST ───────────────────────────────────────
        st.markdown('<div style="margin-top:20px">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">FOUND SUBSTATIONS</div>', unsafe_allow_html=True)

        tab_all, tab_hubs, tab_nodes = st.tabs([
            f"All ({len(elements)})", f"◆ Hubs ({len(hubs_list)})", f"● Nodes ({len(node_list)})"])

        def render_sub_list(sub_list, tab_prefix="t"):
            if not sub_list:
                st.caption("No substations in this category.")
                return
            for el in sub_list:
                name    = el.get("name") or "Unnamed Substation"
                v       = el["volt_kv"]
                v_label = f"{v:.0f} kV" if v else "? kV"
                is_hub  = el["is_hub"]
                op      = el.get("operator") or ""
                is_sel  = bool(st.session_state.selected_osm and
                               st.session_state.selected_osm.get("osm_id") == el["osm_id"])
                dot_col = "#8b0b1f" if is_hub else "#1a3a7a"
                hub_bdg = ('<span style="font-size:9px;background:rgba(255,107,0,0.12);'
                           'border:1px solid rgba(255,107,0,0.4);color:#ff6b00;border-radius:2px;'
                           'padding:1px 6px;margin-left:6px;font-family:Share Tech Mono,monospace">'
                           'HUB</span>') if is_hub else ""
                bdr = "2px solid #00ff9d" if is_sel else ("1px solid rgba(255,107,0,0.3)" if is_hub else "1px solid rgba(0,200,255,0.15)")
                bgc = "rgba(0,255,157,0.04)" if is_sel else "#060d1a"
                op_part = f'<span style="color:#3a6080">{op} · </span>' if op else ""
                html = (
                    f'<div style="background:{bgc};border:{bdr};border-radius:4px;padding:10px 14px;margin-bottom:4px;">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center">'
                    f'<div style="font-family:Share Tech Mono,monospace;font-size:12px;font-weight:600;color:{dot_col}">● {name}</div>'
                    f'{hub_bdg}'
                    f'<div style="text-align:right">'
                    f'<div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#c8e6ff">{v_label}</div>'
                    f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#3a6080">{el["dist_mi"]:.1f} mi</div>'
                    f'</div></div>'
                    f'<div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#3a6080;margin-top:3px">'
                    f'{op_part}{el["lat"]:.4f}, {el["lon"]:.4f}</div></div>'
                )
                col_a, col_b = st.columns([5,1])
                with col_a: st.markdown(html, unsafe_allow_html=True)
                with col_b:
                    if st.button("Inspect →", key=f"{tab_prefix}_{el['osm_id']}", use_container_width=True):
                        st.session_state.selected_osm  = el
                        st.session_state.ercot_sel_sub = None
                        st.rerun()

        with tab_all:   render_sub_list(elements,  "all")
        with tab_hubs:  render_sub_list(hubs_list, "hub")
        with tab_nodes: render_sub_list(node_list, "nod")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── SELECTED SUBSTATION DETAIL ────────────────────────────
        if st.session_state.selected_osm:
            sel      = st.session_state.selected_osm
            osm_name = sel.get("name","") or "Unnamed"
            osm_volt = sel.get("voltage","")
            v        = sel.get("volt_kv")
            v_label  = f"{v:.0f} kV" if v else "Unknown kV"
            is_hub   = sel.get("is_hub", False)

            st.markdown("---")
            st.markdown(f"""
            <div class="osm-card" style="border-left-color:{'#ff6b00' if is_hub else '#00c8ff'}">
                <div class="oc-title" style="color:{'#8b0b1f' if is_hub else '#1a3a7a'}">
                    {'◆ HUB' if is_hub else '● NODE'} &nbsp; {osm_name}
                </div>
                <div class="oc-grid">
                    <div class="oc-item"><div class="oc-lbl">Voltage</div><div class="oc-val">{v_label}</div></div>
                    <div class="oc-item"><div class="oc-lbl">Operator</div><div class="oc-val">{sel.get("operator","—") or "—"}</div></div>
                    <div class="oc-item"><div class="oc-lbl">Distance</div><div class="oc-val">{sel["dist_mi"]:.1f} mi</div></div>
                    <div class="oc-item"><div class="oc-lbl">Coordinates</div><div class="oc-val">{sel["lat"]:.4f}, {sel["lon"]:.4f}</div></div>
                </div>
                <a href="https://fatal-flaw-o7aks4agtoffgyydbvrguj.streamlit.app/?lat={sel['lat']}&lon={sel['lon']}&name={osm_name.replace(' ','%20')}"
                   target="_blank"
                   style="display:inline-block;margin-top:8px;padding:7px 16px;background:#f7f7f5;
                          border:1px solid #d0cdc6;border-radius:2px;font-family:'DM Sans',sans-serif;
                          font-size:12px;font-weight:500;color:#1a3a7a;text-decoration:none;">
                   🌿 Open in SiteIQ Fatal Flaw ↗
                </a>
            </div>
            """, unsafe_allow_html=True)

            # ERCOT match
            st.markdown('<div class="section-label">ERCOT Match</div>', unsafe_allow_html=True)
            matches = match_to_ercot(osm_name, osm_volt)
            if not matches:
                st.warning(f"No ERCOT match found for **{osm_name}**.")
            else:
                match_names = [m[0] for m in matches]
                scores = {m[0]: m[1] for m in matches}
                if st.session_state.ercot_sel_sub not in match_names:
                    st.session_state.ercot_sel_sub = match_names[0]
                def fmt_match(name):
                    s = scores[name]; conf = "HIGH" if s>=30 else "MED" if s>=15 else "LOW"
                    kvs = "/".join(sorted(df[df["Substation"]==name]["kV"].unique(), key=lambda x:-float(x) if x else 0)[:2])
                    cnt = len(df[df["Substation"]==name])
                    return f"{name}  [{kvs} kV · {cnt} buses · {conf}]"
                chosen = st.selectbox("ERCOT match", match_names, format_func=fmt_match,
                                      index=0, label_visibility="collapsed", key="ercot_match_radio")
                st.session_state.ercot_sel_sub = chosen

            if st.session_state.ercot_sel_sub:
                ercot_sub = st.session_state.ercot_sel_sub
                sub_df    = df[df["Substation"]==ercot_sub].copy()
                render_ercot_card(ercot_sub, sub_df)

                disp = ["Substation","Bus","kV","Zone","PSSE #","PSSE Name","Resource Node","Hub"]
                st.dataframe(sub_df[disp].sort_values("kV",ascending=False).reset_index(drop=True),
                    use_container_width=True, height=min(300,40+len(sub_df)*35))

                c1, c2 = st.columns([1,4])
                with c1:
                    st.download_button("↓ Bus List", data=to_csv_bytes(sub_df[disp]),
                        file_name=f"ercot_{ercot_sub}.csv", mime="text/csv")
                with c2:
                    st.info(f"⚡ {len(sub_df)} buses at **{ercot_sub}** — upload LMP below for price analysis")

                st.markdown("---")
                render_lmp_full(sub_df, key_prefix="map_lmp",
                                search_results=results, ercot_sub=ercot_sub)


# ═══════════════════════════════════════════════════════════════════
# PAGE 2: NODE & HUB SELECTOR
# ═══════════════════════════════════════════════════════════════════
elif page == "⚡ Node & Hub Selector":
    st.markdown(f"""<div class="page-header">
        <div><div class="tag">Settlement Points · LMP Analysis</div>
        <h1>Node & Hub <span>Selector</span></h1></div>
        <div class="ph-right">Select substations<br>to resolve buses & run LMP analysis</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label"><span class="step-badge">1</span> Voltage Level</div>', unsafe_allow_html=True)
    kv_labels = ["All Trans.","345 kV","230 kV","138 kV","115 kV","69 kV","34.5 kV"]
    kv_values = ["All","345","230","138","115","69","34.5"]
    if "sel_kv" not in st.session_state: st.session_state.sel_kv = "138"
    btn_cols = st.columns(len(kv_labels))
    for i,(label,val) in enumerate(zip(kv_labels,kv_values)):
        if btn_cols[i].button(label, key=f"kv_{val}", use_container_width=True):
            st.session_state.sel_kv = val
    sel_kv = st.session_state.sel_kv
    df_kv = df[df["kV"].isin(TRANS_KV)] if sel_kv=="All" else df[df["kV"]==sel_kv]

    st.markdown('<div class="section-label"><span class="step-badge">2</span> Select Substation(s)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3,1])
    with c2: zone_pre = st.selectbox("Zone",["All Zones","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"],key="zone_pre2")
    df_filt = df_kv[df_kv["Zone"]==zone_pre] if zone_pre!="All Zones" else df_kv
    sub_list = sorted(df_filt["Substation"].dropna().unique().tolist())
    with c1:
        selected_subs = st.multiselect("Substations", options=sub_list,
            placeholder=f"Choose from {len(sub_list):,} substations...", label_visibility="collapsed")

    if not selected_subs:
        st.markdown('<div class="map-placeholder" style="padding:40px;margin-top:8px"><div class="mp-icon">🏭</div><div class="mp-sub">Select substations to auto-resolve buses, zones & PSSE numbers</div></div>', unsafe_allow_html=True)
        st.stop()

    resolved = df_kv[df_kv["Substation"].isin(selected_subs)].copy()
    st.markdown('<div class="section-label"><span class="step-badge">3</span> Resolved Data</div>', unsafe_allow_html=True)
    for sub in selected_subs:
        render_ercot_card(sub, resolved[resolved["Substation"]==sub])

    disp_cols = ["Substation","Bus","kV","Zone","PSSE #","PSSE Name","Resource Node","Hub","Node"]
    st.dataframe(resolved[disp_cols].sort_values(["Substation","kV"],ascending=[True,False]).reset_index(drop=True),
        use_container_width=True, height=min(380,40+len(resolved)*35))
    st.download_button("↓ Export Bus List", data=to_csv_bytes(resolved[disp_cols]),
        file_name=f"ercot_{'_'.join(selected_subs[:3])}.csv", mime="text/csv")
    st.markdown("---")
    render_lmp_full(resolved, key_prefix="sel_lmp", ercot_sub=selected_subs[0] if len(selected_subs)==1 else None)


# ═══════════════════════════════════════════════════════════════════
# PAGE 3: BUS LOOKUP
# ═══════════════════════════════════════════════════════════════════
elif page == "🔍 Bus Lookup":
    st.markdown("""<div class="page-header"><div><div class="tag">Electrical Bus · PSSE Reference</div><h1>Bus <span>Lookup</span></h1></div></div>""", unsafe_allow_html=True)
    c1,c2 = st.columns([3,1])
    with c1: bus_q = st.text_input("Bus Name", placeholder="e.g. CAMPBELLSW, BUCKRA, 0001...", key="bus_q")
    with c2: bus_zone = st.selectbox("Zone",["All Zones","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"])
    if bus_q.strip():
        q = bus_q.strip().upper()
        mask = df["Bus"].str.upper().str.contains(q,na=False)|df["PSSE Name"].str.upper().str.contains(q,na=False)
        if bus_zone!="All Zones": mask &= df["Zone"]==bus_zone
        results = df[mask]
        exact = df[df["Bus"].str.upper()==q]
        if not exact.empty:
            r=exact.iloc[0]
            st.markdown(f'<div class="ercot-card"><h3>▶ {r["Bus"]}</h3><div class="dg"><div class="di"><div class="dl">Substation</div><div class="dv" style="color:#ff6b00">{r["Substation"]}</div></div><div class="di"><div class="dl">Voltage</div><div class="dv"><span class="kv {kv_cls(r["kV"])}">{r["kV"]} kV</span></div></div><div class="di"><div class="dl">Zone</div><div class="dv" style="color:#00c8ff">{r["Zone"]}</div></div><div class="di"><div class="dl">PSSE Name</div><div class="dv">{r["PSSE Name"] or "—"}</div></div><div class="di"><div class="dl">PSSE #</div><div class="dv">{r["PSSE #"] or "—"}</div></div><div class="di"><div class="dl">Resource Node</div><div class="dv">{r["Resource Node"] or "—"}</div></div><div class="di"><div class="dl">Hub</div><div class="dv">{r["Hub"] or "—"}</div></div></div></div>',unsafe_allow_html=True)
        st.markdown(f"**{len(results):,}** results for `{bus_q.strip()}`")
        disp=["Bus","PSSE Name","kV","Substation","Zone","Resource Node","PSSE #"]
        st.dataframe(results[disp].reset_index(drop=True),use_container_width=True,height=min(400,40+len(results)*35))
        if len(results): st.download_button("↓ Export CSV",data=to_csv_bytes(results[disp]),file_name=f"bus_{bus_q.strip()}.csv",mime="text/csv")
    else:
        st.markdown('<div class="map-placeholder"><div class="mp-icon">⚡</div><div class="mp-sub">Enter a bus name above</div></div>',unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 4: SUBSTATION LOOKUP
# ═══════════════════════════════════════════════════════════════════
elif page == "🏭 Substation Lookup":
    st.markdown("""<div class="page-header"><div><div class="tag">ERCOT Substation Registry</div><h1>Substation <span>Lookup</span></h1></div></div>""", unsafe_allow_html=True)
    c1,c2 = st.columns([3,1])
    with c1: sub_q = st.text_input("Substation Name", placeholder="e.g. CAMPBELL, LOOKOUT, VICTORIA...")
    with c2:
        kv_opts = ["All kV"]+sorted(df["kV"].dropna().unique(), key=lambda x:-float(x) if x else 0)
        sub_kv = st.selectbox("Voltage", kv_opts)
    if sub_q.strip():
        q = sub_q.strip().upper()
        mask = df["Substation"].str.upper().str.contains(q,na=False)
        if sub_kv!="All kV": mask &= df["kV"]==sub_kv
        results = df[mask]
        exact = df[df["Substation"].str.upper()==q]
        if not exact.empty: render_ercot_card(exact.iloc[0]["Substation"], exact)
        st.markdown(f"**{len(results):,}** results for `{sub_q.strip()}`")
        disp=["Substation","Bus","kV","Zone","PSSE #","PSSE Name","Resource Node"]
        st.dataframe(results[disp].reset_index(drop=True),use_container_width=True,height=min(400,40+len(results)*35))
        if len(results): st.download_button("↓ Export CSV",data=to_csv_bytes(results[disp]),file_name=f"sub_{sub_q.strip()}.csv",mime="text/csv")
    else:
        st.markdown('<div class="map-placeholder"><div class="mp-icon">🏭</div><div class="mp-sub">Enter a substation name above</div></div>',unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 5: BROWSE ALL
# ═══════════════════════════════════════════════════════════════════
elif page == "📋 Browse All":
    st.markdown("""<div class="page-header"><div><div class="tag">Full Dataset · 19,056 Points</div><h1>Browse <span>All</span></h1></div></div>""", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns([3,1,1,1])
    with c1: bq = st.text_input("Search","",placeholder="Bus, PSSE Name, Substation...")
    with c2: bz = st.selectbox("Zone",["All","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"])
    with c3:
        bkv_opts=["All kV"]+sorted(df["kV"].dropna().unique(),key=lambda x:-float(x) if x else 0)
        bkv=st.selectbox("kV",bkv_opts)
    with c4: brn=st.selectbox("Type",["All","Resource Nodes","Hubs"])
    f=df.copy()
    if bq.strip(): q=bq.strip().upper(); f=f[f["Bus"].str.upper().str.contains(q,na=False)|f["PSSE Name"].str.upper().str.contains(q,na=False)|f["Substation"].str.upper().str.contains(q,na=False)]
    if bz!="All": f=f[f["Zone"]==bz]
    if bkv!="All kV": f=f[f["kV"]==bkv]
    if brn=="Resource Nodes": f=f[f["Resource Node"]!=""]
    elif brn=="Hubs": f=f[f["Hub"]!=""]
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Records",f"{len(f):,}"); m2.metric("Substations",f"{f['Substation'].nunique():,}")
    m3.metric("kV Levels",f"{f['kV'].nunique()}"); m4.metric("Res. Nodes",f"{f[f['Resource Node']!=''].shape[0]:,}")
    disp=["Bus","PSSE Name","kV","Substation","Zone","Resource Node","Hub","PSSE #"]
    st.dataframe(f[disp].reset_index(drop=True),use_container_width=True,height=500)
    st.download_button("↓ Export CSV",data=to_csv_bytes(f[disp]),file_name="ercot_browse.csv",mime="text/csv")
