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
    page_title="ERCOT Nodal Analysis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS — Cyberpunk Neon
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Share+Tech+Mono&family=Exo+2:wght@300;400;500;600&display=swap');

:root {
  --void:  #030712;
  --surf:  #060d1a;
  --panel: #091424;
  --grid:  #0a1f35;
  --ng:    #00ff9d;
  --nb:    #00c8ff;
  --np:    #bf00ff;
  --no:    #ff6b00;
  --nr:    #ff2d55;
  --text:  #c8e6ff;
  --dim:   #3a6080;
  --faint: #1a3050;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--void) !important;
    font-family: 'Exo 2', sans-serif;
    color: var(--text);
    background-image: repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,200,255,0.015) 2px,rgba(0,200,255,0.015) 4px) !important;
}
[data-testid="stAppViewContainer"]::before {
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background-image: radial-gradient(circle, rgba(0,200,255,0.07) 1px, transparent 1px);
    background-size: 28px 28px;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #04090f 0%, #030712 100%) !important;
    border-right: 1px solid var(--ng) !important;
    box-shadow: 4px 0 30px rgba(0,255,157,0.08) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] hr { border-color: var(--faint) !important; }

.page-header { border-bottom: 1px solid var(--ng); padding-bottom:14px; margin-bottom:20px; position:relative; }
.page-header::after { content:''; position:absolute; bottom:-1px; left:0; width:80px; height:2px; background:linear-gradient(90deg,var(--ng),transparent); box-shadow:0 0 8px var(--ng); }
.page-header .tag { font-family:'Share Tech Mono',monospace; font-size:10px; color:var(--ng); letter-spacing:.3em; text-transform:uppercase; margin-bottom:6px; text-shadow:0 0 8px var(--ng); }
.page-header h1 { font-family:'Orbitron',monospace; font-size:22px; font-weight:700; color:var(--text); margin:0; text-transform:uppercase; letter-spacing:.08em; }
.page-header h1 span { color:var(--ng); text-shadow:0 0 12px var(--ng),0 0 24px rgba(0,255,157,0.4); animation:flicker 8s infinite; }

.section-label { font-family:'Share Tech Mono',monospace; font-size:10px; color:var(--ng); letter-spacing:.25em; text-transform:uppercase; margin:20px 0 10px; display:flex; align-items:center; gap:10px; text-shadow:0 0 6px var(--ng); }
.section-label::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,rgba(0,255,157,0.4),transparent); }

.step-badge { display:inline-flex; align-items:center; justify-content:center; width:22px; height:22px; border-radius:50%; background:transparent; border:1px solid var(--ng); color:var(--ng); font-family:'Orbitron',monospace; font-size:10px; font-weight:700; box-shadow:0 0 8px rgba(0,255,157,0.5),inset 0 0 8px rgba(0,255,157,0.1); text-shadow:0 0 6px var(--ng); }

.osm-card { background:linear-gradient(135deg,rgba(0,200,255,0.04),rgba(0,255,157,0.02)); border:1px solid rgba(0,200,255,0.3); border-left:3px solid var(--nb); border-radius:4px; padding:16px 20px; margin-bottom:14px; box-shadow:0 0 20px rgba(0,200,255,0.06),inset 0 0 30px rgba(0,200,255,0.02); position:relative; overflow:hidden; }
.osm-card::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,var(--nb),transparent); opacity:.6; }
.osm-card .oc-title { font-family:'Orbitron',monospace; font-size:13px; font-weight:600; color:var(--nb); margin-bottom:12px; text-transform:uppercase; letter-spacing:.05em; text-shadow:0 0 10px var(--nb); }
.osm-card .oc-grid { display:flex; flex-wrap:wrap; gap:16px; margin-bottom:10px; }
.osm-card .oc-item .oc-lbl { font-family:'Share Tech Mono',monospace; font-size:9px; color:var(--dim); letter-spacing:.2em; text-transform:uppercase; }
.osm-card .oc-item .oc-val { font-family:'Share Tech Mono',monospace; font-size:12px; font-weight:500; color:var(--text); margin-top:2px; }

.ercot-card { background:linear-gradient(135deg,rgba(191,0,255,0.04),rgba(0,255,157,0.02)); border:1px solid rgba(0,255,157,0.25); border-left:3px solid var(--ng); border-radius:4px; padding:16px 20px; margin-bottom:14px; box-shadow:0 0 20px rgba(0,255,157,0.06),inset 0 0 30px rgba(0,255,157,0.02); position:relative; overflow:hidden; }
.ercot-card::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,var(--ng),transparent); opacity:.5; }
.ercot-card h3 { font-family:'Orbitron',monospace; font-size:13px; font-weight:600; color:var(--ng); margin:0 0 12px; text-transform:uppercase; letter-spacing:.05em; text-shadow:0 0 10px var(--ng); }
.dg { display:flex; flex-wrap:wrap; gap:14px; margin-bottom:10px; }
.di .dl { font-family:'Share Tech Mono',monospace; font-size:9px; color:var(--dim); letter-spacing:.2em; text-transform:uppercase; }
.di .dv { font-family:'Share Tech Mono',monospace; font-size:12px; font-weight:500; color:var(--text); margin-top:2px; }

.use-case-card { background:var(--surf); border:1px solid var(--faint); border-radius:4px; padding:14px 18px; margin-bottom:8px; cursor:pointer; transition:all .2s; }
.use-case-card:hover,.use-case-card.active { border-color:var(--ng); background:rgba(0,255,157,0.04); box-shadow:0 0 16px rgba(0,255,157,0.1); }
.use-case-card .uc-title { font-family:'Orbitron',monospace; font-size:12px; font-weight:600; color:var(--ng); margin-bottom:4px; text-transform:uppercase; letter-spacing:.05em; }
.use-case-card .uc-desc { font-family:'Share Tech Mono',monospace; font-size:10px; color:var(--dim); line-height:1.5; }
.use-case-card .uc-who { font-size:10px; color:var(--nb); font-family:'Share Tech Mono',monospace; margin-top:4px; }

.tag-row { display:flex; flex-wrap:wrap; gap:5px; margin-top:4px; }
.tag-bus  { display:inline-block; padding:2px 10px; border-radius:2px; font-family:'Share Tech Mono',monospace; font-size:10px; font-weight:500; background:rgba(0,255,157,0.07); border:1px solid rgba(0,255,157,0.35); color:var(--ng); text-shadow:0 0 6px rgba(0,255,157,0.5); }
.tag-zone { display:inline-block; padding:2px 10px; border-radius:2px; font-family:'Share Tech Mono',monospace; font-size:10px; background:rgba(0,200,255,0.07); border:1px solid rgba(0,200,255,0.35); color:var(--nb); text-shadow:0 0 6px rgba(0,200,255,0.5); }
.tag-psse { display:inline-block; padding:2px 10px; border-radius:2px; font-family:'Share Tech Mono',monospace; font-size:10px; background:rgba(191,0,255,0.07); border:1px solid rgba(191,0,255,0.35); color:#d966ff; text-shadow:0 0 6px rgba(191,0,255,0.5); }
.tag-hub  { display:inline-block; padding:2px 10px; border-radius:2px; font-family:'Share Tech Mono',monospace; font-size:10px; background:rgba(255,107,0,0.07); border:1px solid rgba(255,107,0,0.35); color:var(--no); text-shadow:0 0 6px rgba(255,107,0,0.5); }
.tag-rn   { display:inline-block; padding:2px 10px; border-radius:2px; font-family:'Share Tech Mono',monospace; font-size:10px; background:rgba(0,255,157,0.05); border:1px solid rgba(0,255,157,0.2); color:var(--ng); }

.kv { display:inline-block; padding:2px 10px; border-radius:2px; font-family:'Share Tech Mono',monospace; font-size:11px; font-weight:600; }
.kv-345 { color:var(--no); background:rgba(255,107,0,0.1); border:1px solid rgba(255,107,0,0.4); text-shadow:0 0 6px var(--no); }
.kv-230 { color:#ffd700; background:rgba(255,215,0,0.08); border:1px solid rgba(255,215,0,0.35); text-shadow:0 0 6px #ffd700; }
.kv-138 { color:var(--ng); background:rgba(0,255,157,0.08); border:1px solid rgba(0,255,157,0.35); text-shadow:0 0 6px var(--ng); }
.kv-115 { color:#d966ff; background:rgba(191,0,255,0.08); border:1px solid rgba(191,0,255,0.35); text-shadow:0 0 6px #d966ff; }
.kv-69  { color:var(--nb); background:rgba(0,200,255,0.08); border:1px solid rgba(0,200,255,0.35); text-shadow:0 0 6px var(--nb); }
.kv-34  { color:var(--dim); background:rgba(58,96,128,0.1); border:1px solid rgba(58,96,128,0.3); }

.map-placeholder { text-align:center; padding:48px 20px; color:var(--dim); font-family:'Share Tech Mono',monospace; background:var(--surf); border:1px solid var(--faint); border-radius:4px; }
.map-placeholder .mp-icon { font-size:36px; margin-bottom:12px; filter:drop-shadow(0 0 8px var(--ng)); }
.map-placeholder .mp-title { font-size:13px; font-weight:600; color:var(--faint); margin-bottom:6px; font-family:'Orbitron',monospace; text-transform:uppercase; letter-spacing:.1em; }
.map-placeholder .mp-sub { font-size:11px; line-height:1.8; color:var(--dim); }

.hint-bar { background:rgba(0,200,255,0.04); border:1px solid rgba(0,200,255,0.2); border-radius:4px; padding:8px 16px; font-family:'Share Tech Mono',monospace; font-size:11px; color:var(--dim); margin-bottom:12px; display:flex; align-items:center; gap:10px; }
.conf-high { color:var(--ng); font-weight:600; text-shadow:0 0 6px var(--ng); }
.conf-med  { color:#ffd700; font-weight:600; text-shadow:0 0 6px #ffd700; }
.conf-low  { color:var(--nr); font-weight:600; text-shadow:0 0 6px var(--nr); }

.stTabs [data-baseweb="tab-list"] { background:var(--surf) !important; border-bottom:1px solid rgba(0,255,157,0.2) !important; }
.stTabs [data-baseweb="tab"] { font-family:'Share Tech Mono',monospace !important; font-size:11px !important; font-weight:500 !important; letter-spacing:.15em !important; text-transform:uppercase !important; color:var(--dim) !important; background:transparent !important; padding:10px 20px !important; }
.stTabs [aria-selected="true"] { color:var(--ng) !important; border-bottom:2px solid var(--ng) !important; text-shadow:0 0 8px var(--ng) !important; background:rgba(0,255,157,0.04) !important; }

.stTextInput input, div[data-baseweb="select"] > div, .stNumberInput input {
    background-color:var(--panel) !important; border:1px solid rgba(0,200,255,0.25) !important;
    color:var(--text) !important; font-family:'Share Tech Mono',monospace !important; border-radius:3px !important;
}
.stDownloadButton button, .stButton button {
    background:var(--panel) !important; border:1px solid rgba(0,200,255,0.3) !important;
    color:var(--nb) !important; font-family:'Share Tech Mono',monospace !important;
    font-size:11px !important; font-weight:500 !important; letter-spacing:.12em !important;
    text-transform:uppercase !important; border-radius:3px !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    border-color:var(--ng) !important; color:var(--ng) !important;
    background:rgba(0,255,157,0.06) !important; box-shadow:0 0 12px rgba(0,255,157,0.2) !important;
}
button[kind="primary"] {
    background:linear-gradient(135deg,rgba(0,255,157,0.15),rgba(0,200,255,0.1)) !important;
    border:1px solid var(--ng) !important; color:var(--ng) !important; font-weight:600 !important;
    box-shadow:0 0 16px rgba(0,255,157,0.25),inset 0 0 16px rgba(0,255,157,0.05) !important;
    text-shadow:0 0 8px var(--ng) !important;
}
button[kind="primary"]:hover {
    background:linear-gradient(135deg,rgba(0,255,157,0.25),rgba(0,200,255,0.15)) !important;
    box-shadow:0 0 24px rgba(0,255,157,0.4),inset 0 0 20px rgba(0,255,157,0.08) !important;
}

[data-testid="stMetric"] { background:linear-gradient(135deg,var(--surf),var(--panel)); border:1px solid rgba(0,255,157,0.15); border-radius:4px; padding:14px 18px; position:relative; overflow:hidden; animation:pulse-glow 4s ease-in-out infinite; }
[data-testid="stMetric"]::after { content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,rgba(0,255,157,0.4),transparent); }
[data-testid="stMetricLabel"] { font-family:'Share Tech Mono',monospace !important; font-size:9px !important; color:var(--dim) !important; text-transform:uppercase !important; letter-spacing:.2em !important; }
[data-testid="stMetricValue"] { font-family:'Orbitron',monospace !important; color:var(--ng) !important; font-size:22px !important; font-weight:700 !important; text-shadow:0 0 12px var(--ng) !important; }

[data-testid="stCheckbox"] label { font-family:'Share Tech Mono',monospace !important; font-size:11px !important; letter-spacing:.05em !important; }
[data-testid="stDataFrame"] { border:1px solid rgba(0,200,255,0.15) !important; border-radius:4px !important; }

div[data-testid="stMarkdownContainer"] p { color:var(--dim); font-size:13px; }
hr { border-color:var(--faint) !important; }

::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:var(--void); }
::-webkit-scrollbar-thumb { background:rgba(0,255,157,0.2); border-radius:2px; }
::-webkit-scrollbar-thumb:hover { background:var(--ng); box-shadow:0 0 6px var(--ng); }

@keyframes flicker { 0%,95%,100%{opacity:1} 96%{opacity:.85} 97%{opacity:1} 98%{opacity:.9} }
@keyframes pulse-glow { 0%,100%{box-shadow:0 0 16px rgba(0,255,157,0.04)} 50%{box-shadow:0 0 24px rgba(0,255,157,0.10)} }
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
        title=dict(text=title, font=dict(family="Orbitron", size=13, color="#00ff9d"), x=0.01),
        height=height,
        paper_bgcolor="#030712", plot_bgcolor="#060d1a",
        font=dict(family="Share Tech Mono", color="#c8e6ff", size=11),
        xaxis=dict(gridcolor="#0a1f35", linecolor="#1a3050", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#0a1f35", linecolor="#1a3050", tickfont=dict(size=10)),
        legend=dict(bgcolor="rgba(6,13,26,0.8)", bordercolor="#1a3050", borderwidth=1),
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

    # Auto-detect column names (ERCOT format varies slightly)
    col_map = {}
    for c in combined.columns:
        u = c.upper().strip().replace(" ", "").replace("_", "")
        if any(k in u for k in ["SETTLEMENTPOINTNAME","SETTLEMENTPOINT","SPNAME","BUSNAME","NODENAME"]):
            col_map["bus"] = c
        elif any(k in u for k in ["SETTLEMENTPOINTPRICE","PRICE","LMP","SPP"]):
            col_map["price"] = c
        elif any(k in u for k in ["HOURENDING","HOUROFDAY","HOUR","DELIVERYHOUR"]):
            col_map["hour"] = c
        elif any(k in u for k in ["DELIVERYDATE","DATE","TRADINGDATE"]):
            col_map["date"] = c

    if "bus" not in col_map or "price" not in col_map:
        return combined, f"Could not detect columns. Found: {list(combined.columns)}"

    # Rename to standard
    rename = {v: k for k, v in col_map.items()}
    combined = combined.rename(columns=rename)
    combined["price"] = pd.to_numeric(combined["price"], errors="coerce")

    # Build datetime
    if "date" in col_map and "hour" in combined.columns:
        try:
            combined["hour_int"] = pd.to_numeric(combined["hour"], errors="coerce").fillna(0).astype(int)
            combined["datetime"] = pd.to_datetime(combined["date"], errors="coerce") + \
                                   pd.to_timedelta(combined["hour_int"] - 1, unit="h")
        except:
            combined["datetime"] = pd.NaT
    elif "hour" in combined.columns:
        combined["datetime"] = pd.to_numeric(combined["hour"], errors="coerce")
    else:
        combined["datetime"] = range(len(combined))

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
def run_lmp_analytics(lmp_df, resolved_df, use_case, batt_mw=100, batt_mwh=400, efficiency=0.85):
    buses = set(resolved_df["Bus"].str.upper())
    lmp_df["_bus_up"] = lmp_df["bus"].str.upper().str.strip()
    matched = lmp_df[lmp_df["_bus_up"].isin(buses)].copy()
    if matched.empty:
        return None, "No matching buses in LMP data"

    matched = matched.sort_values("datetime")

    if use_case == "24h_profile":
        # ── 24-Hour LMP Profile per selected bus ──────────────────
        return matched, None

    elif use_case == "arbitrage":
        # ── Energy Arbitrage: best charge/discharge windows ───────
        daily = matched.groupby(["_bus_up", "datetime"])["price"].mean().reset_index()
        results = []
        for bus in daily["_bus_up"].unique():
            bdf = daily[daily["_bus_up"] == bus].sort_values("datetime")
            if len(bdf) < 2: continue
            prices = bdf["price"].values
            # Find cheapest 4h window (charge) and most expensive 4h (discharge)
            charge_idx   = prices.argsort()[:4]
            discharge_idx= prices.argsort()[-4:]
            avg_charge   = prices[charge_idx].mean()
            avg_discharge= prices[discharge_idx].mean()
            spread       = avg_discharge - avg_charge
            daily_rev    = spread * batt_mw * efficiency
            ann_rev      = daily_rev * 365
            results.append({"Bus": bus, "Avg Charge $/MWh": round(avg_charge,2),
                             "Avg Discharge $/MWh": round(avg_discharge,2),
                             "Spread $/MWh": round(spread,2),
                             "Daily Revenue $": round(daily_rev,0),
                             "Annual Revenue $": round(ann_rev,0)})
        return pd.DataFrame(results), None

    elif use_case == "congestion":
        # ── Congestion: price spreads between buses ───────────────
        pivot = matched.pivot_table(index="datetime", columns="_bus_up", values="price", aggfunc="mean")
        if pivot.shape[1] < 2:
            return None, "Need ≥2 buses for congestion analysis"
        spreads = []
        cols = pivot.columns.tolist()
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                diff = (pivot[cols[i]] - pivot[cols[j]]).abs()
                spreads.append({
                    "Bus A": cols[i], "Bus B": cols[j],
                    "Avg Spread $/MWh": round(diff.mean(), 2),
                    "Max Spread $/MWh": round(diff.max(), 2),
                    "Congestion Hours": int((diff > 20).sum()),
                    "Congestion %": round((diff > 20).mean() * 100, 1)
                })
        return pd.DataFrame(spreads).sort_values("Avg Spread $/MWh", ascending=False), None

    elif use_case == "curtailment":
        # ── Curtailment Risk: negative/zero price frequency ───────
        results = []
        for bus in matched["_bus_up"].unique():
            bdf = matched[matched["_bus_up"] == bus]
            total = len(bdf)
            neg   = (bdf["price"] < 0).sum()
            zero  = (bdf["price"] <= 0).sum()
            very_neg = (bdf["price"] < -20).sum()
            results.append({
                "Bus": bus,
                "Total Hours": total,
                "Negative Price Hours": int(neg),
                "Negative Price %": round(neg/total*100, 1) if total else 0,
                "≤$0 Hours": int(zero),
                "< -$20 Hours": int(very_neg),
                "Avg Price $/MWh": round(bdf["price"].mean(), 2),
                "Min Price $/MWh": round(bdf["price"].min(), 2),
                "Curtailment Risk": "HIGH" if neg/total > 0.15 else "MED" if neg/total > 0.05 else "LOW",
            })
        return pd.DataFrame(results), None

    elif use_case == "bess_dispatch":
        # ── BESS Dispatch Optimization ────────────────────────────
        bus = matched["_bus_up"].mode()[0]
        bdf = matched[matched["_bus_up"] == bus].sort_values("datetime").copy()
        bdf["roll_avg"] = bdf["price"].rolling(3, center=True, min_periods=1).mean()
        bdf["signal"]   = "HOLD"
        bdf.loc[bdf["price"] < bdf["roll_avg"] * 0.8, "signal"] = "CHARGE"
        bdf.loc[bdf["price"] > bdf["roll_avg"] * 1.2, "signal"] = "DISCHARGE"

        charge_rev    = bdf[bdf["signal"]=="DISCHARGE"]["price"].sum() * batt_mw / 1000
        charge_cost   = bdf[bdf["signal"]=="CHARGE"]["price"].sum() * batt_mw / 1000
        net           = charge_rev - abs(charge_cost)

        return {"data": bdf, "bus": bus, "net_revenue": round(net,0),
                "charge_hours": int((bdf["signal"]=="CHARGE").sum()),
                "discharge_hours": int((bdf["signal"]=="DISCHARGE").sum())}, None

    elif use_case == "ftr":
        # ── FTR Opportunity Scanner ───────────────────────────────
        pivot = matched.pivot_table(index="datetime", columns="_bus_up", values="price", aggfunc="mean")
        results = []
        cols = pivot.columns.tolist()
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                spread = pivot[cols[i]] - pivot[cols[j]]
                pos_spread = spread[spread > 0]
                results.append({
                    "Buy Node (sink)": cols[i], "Sell Node (source)": cols[j],
                    "Avg FTR Value $/MWh": round(pos_spread.mean(), 2) if len(pos_spread) else 0,
                    "Max FTR Value $/MWh": round(spread.max(), 2),
                    "Profitable Hours": len(pos_spread),
                    "Win Rate %": round(len(pos_spread)/len(spread)*100, 1) if len(spread) else 0,
                })
        return pd.DataFrame(results).sort_values("Avg FTR Value $/MWh", ascending=False), None

    elif use_case == "revenue":
        # ── Revenue Estimation ────────────────────────────────────
        results = []
        for bus in matched["_bus_up"].unique():
            bdf = matched[matched["_bus_up"] == bus]
            avg = bdf["price"].mean()
            results.append({
                "Bus": bus,
                "Avg LMP $/MWh": round(avg, 2),
                "Annual Solar Rev ($/MW)": round(avg * 8760 * 0.25, 0),
                "Annual Wind Rev ($/MW)": round(avg * 8760 * 0.35, 0),
                "Annual BESS Rev ($/MW)": round((bdf["price"].max()-bdf["price"].min())*365*0.5, 0),
                "P90 Price $/MWh": round(bdf["price"].quantile(0.1), 2),
                "P10 Price $/MWh": round(bdf["price"].quantile(0.9), 2),
            })
        return pd.DataFrame(results), None

    return None, "Unknown use case"


# ═══════════════════════════════════════════════════════════════════
# PDF Report Generator
# ═══════════════════════════════════════════════════════════════════
def generate_pdf_report(search_results, ercot_sub, sub_df, lmp_summary=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    # Header bar
    pdf.set_fill_color(3, 7, 18)
    pdf.rect(0, 0, 210, 28, 'F')
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(0, 255, 157)
    pdf.set_xy(15, 8)
    pdf.cell(0, 10, "SUNSTRIPE  |  ERCOT NODAL ANALYSIS REPORT", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(58, 96, 128)
    pdf.set_xy(15, 19)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}  |  Confidential", ln=True)

    pdf.set_xy(15, 34)
    pdf.set_text_color(0, 0, 0)

    # Search summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 100, 80)
    pdf.cell(0, 8, "SEARCH SUMMARY", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    if search_results:
        pdf.cell(0, 6, f"Centre: {search_results['lat']:.4f}, {search_results['lon']:.4f}  |  Radius: {search_results['radius_mi']} miles", ln=True)
        pdf.cell(0, 6, f"Total substations found: {len(search_results['elements'])}  |  Hubs: {sum(1 for e in search_results['elements'] if e['is_hub'])}  |  Nodes: {sum(1 for e in search_results['elements'] if not e['is_hub'])}", ln=True)
    pdf.ln(4)

    # ERCOT substation data
    if ercot_sub:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 100, 80)
        pdf.cell(0, 8, f"ERCOT SUBSTATION: {ercot_sub}", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)

        buses  = sub_df["Bus"].tolist()
        kvs    = ", ".join(sorted(sub_df["kV"].unique(), key=lambda x: -float(x) if x else 0))
        zones  = ", ".join(sub_df["Zone"].unique())
        hubs   = ", ".join(sub_df[sub_df["Hub"]!=""]["Hub"].unique()) or "—"
        rn     = sub_df[sub_df["Resource Node"]!=""].shape[0]

        pdf.cell(0, 6, f"Total Buses: {len(buses)}  |  Voltages: {kvs} kV  |  Zone(s): {zones}", ln=True)
        pdf.cell(0, 6, f"Hub(s): {hubs}  |  Resource Nodes: {rn}", ln=True)
        pdf.ln(3)

        # Bus table
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(230, 255, 245)
        col_w = [45, 20, 25, 35, 35, 30]
        headers = ["Bus Name", "kV", "Zone", "PSSE Name", "PSSE #", "Resource Node"]
        for i, (h, w) in enumerate(zip(headers, col_w)):
            pdf.cell(w, 7, h, border=1, fill=True)
        pdf.ln()
        pdf.set_font("Helvetica", "", 8)
        pdf.set_fill_color(255, 255, 255)
        for _, row in sub_df.head(40).iterrows():
            for val, w in zip([row["Bus"], row["kV"], row["Zone"], row["PSSE Name"][:15], row["PSSE #"], row["Resource Node"][:12]], col_w):
                pdf.cell(w, 6, str(val), border=1)
            pdf.ln()
        if len(sub_df) > 40:
            pdf.set_font("Helvetica", "I", 8)
            pdf.cell(0, 6, f"  ... and {len(sub_df)-40} more buses", ln=True)

    # LMP summary
    if lmp_summary is not None and len(lmp_summary):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 100, 80)
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

    # Footer
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, "SunStripe Confidential  |  www.sunstripe.com  |  ERCOT Nodal Analysis Platform", align="C")

    return pdf.output()


# ═══════════════════════════════════════════════════════════════════
# Overpass search
# ═══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def search_substations_radius(lat, lon, radius_mi):
    radius_m = int(radius_mi * 1609.34)
    query = f"""[out:json][timeout:40];
(
  node["power"="substation"](around:{radius_m},{lat},{lon});
  way["power"="substation"](around:{radius_m},{lat},{lon});
  relation["power"="substation"](around:{radius_m},{lat},{lon});
);
out center tags;"""
    try:
        resp = requests.post("https://overpass-api.de/api/interpreter",
            data={"data": query}, timeout=45,
            headers={"User-Agent": "SunStripe-ERCOT/1.0"})
        resp.raise_for_status()
        elements = []
        for el in resp.json().get("elements", []):
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
        return elements, None
    except requests.exceptions.Timeout:
        return [], "Overpass API timed out. Try a smaller radius."
    except Exception as e:
        return [], f"Search error: {e}"


# ═══════════════════════════════════════════════════════════════════
# ERCOT match index
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
        records.append({
            "substation": sub, "tokens": tokens,
            "kvs": sorted(grp["kV"].unique(), key=lambda x: -float(x) if x else 0),
            "bus_count": len(grp),
        })
    return records

ercot_index = build_ercot_search_index()

def match_to_ercot(osm_name, osm_voltage_str=""):
    if not osm_name: return []
    osm_clean = re.sub(r'[^A-Z0-9 ]', '', osm_name.upper())
    for pat in [r'\bSUBSTATION\b',r'\bSWITCHING\b',r'\bSTATION\b',r'\bELECTRIC\b',r'\bPOWER\b',r'\bTRANS\b',r'\bSUB\b',r'\bSS\b']:
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
# Shared UI renderers
# ═══════════════════════════════════════════════════════════════════
def render_ercot_card(sub_name, sub_df):
    buses     = sub_df["Bus"].tolist()
    zones     = sub_df["Zone"].unique().tolist()
    kvs       = sorted(sub_df["kV"].unique(), key=lambda x: -float(x) if x else 0)
    psse_nums = sub_df["PSSE #"].tolist()
    rn_list   = sub_df[sub_df["Resource Node"]!=""]["Resource Node"].tolist()
    hubs      = sub_df[sub_df["Hub"]!=""]["Hub"].unique().tolist()
    bus_tags  = "".join(f'<span class="tag-bus">{b}</span>' for b in buses[:30])
    more_b    = f'<span style="color:#3a6080;font-size:10px">+{len(buses)-30} more</span>' if len(buses)>30 else ""
    zone_tags = "".join(f'<span class="tag-zone">{z}</span>' for z in zones)
    psse_tags = "".join(f'<span class="tag-psse">{p}</span>' for p in psse_nums[:20])
    more_p    = f'<span style="color:#3a6080;font-size:10px">+{len(psse_nums)-20} more</span>' if len(psse_nums)>20 else ""
    hub_tags  = "".join(f'<span class="tag-hub">{h}</span>' for h in hubs) if hubs else '<span style="color:#3a6080;font-size:11px">—</span>'
    kv_tags   = "".join(f'<span class="kv {kv_cls(k)}">{k} kV</span>' for k in kvs)
    rn_tags   = "".join(f'<span class="tag-rn">{r}</span>' for r in rn_list[:10])
    st.markdown(f"""
    <div class="ercot-card">
        <h3>⚡ {sub_name}</h3>
        <div class="dg">
            <div class="di"><div class="dl">Buses</div><div class="dv" style="color:#00ff9d;text-shadow:0 0 8px #00ff9d">{len(buses)}</div></div>
            <div class="di"><div class="dl">Voltage(s)</div><div class="dv">{kv_tags}</div></div>
            <div class="di"><div class="dl">Zone(s)</div><div class="dv">{zone_tags}</div></div>
            <div class="di"><div class="dl">Hub(s)</div><div class="dv">{hub_tags}</div></div>
            <div class="di"><div class="dl">Res. Nodes</div><div class="dv" style="color:#00ff9d">{len(rn_list)}</div></div>
        </div>
        <div style="margin-bottom:10px"><div class="dl" style="font-family:Share Tech Mono,monospace;font-size:9px;color:#3a6080;letter-spacing:.2em;text-transform:uppercase;margin-bottom:5px">BUS NAMES</div><div class="tag-row">{bus_tags}{more_b}</div></div>
        <div style="margin-bottom:10px"><div class="dl" style="font-family:Share Tech Mono,monospace;font-size:9px;color:#3a6080;letter-spacing:.2em;text-transform:uppercase;margin-bottom:5px">PSSE NUMBERS</div><div class="tag-row">{psse_tags}{more_p}</div></div>
        {'<div><div class="dl" style="font-family:Share Tech Mono,monospace;font-size:9px;color:#3a6080;letter-spacing:.2em;text-transform:uppercase;margin-bottom:5px">RESOURCE NODES</div><div class="tag-row">'+rn_tags+'</div></div>' if rn_list else ''}
    </div>
    """, unsafe_allow_html=True)


def render_lmp_full(resolved_df, key_prefix="lmp", search_results=None, ercot_sub=None):
    """Full LMP section: ZIP/CSV upload + live API + use-case analysis + 24h chart."""
    st.markdown('<div class="section-label">⚡ LMP ANALYSIS ENGINE</div>', unsafe_allow_html=True)

    tab_upload, tab_live, tab_usecases = st.tabs([
        "📁 Upload ZIP / CSV",
        "🌐 Live ERCOT API",
        "📊 Use-Case Modules",
    ])

    # ── shared state ──
    lmp_key = f"{key_prefix}_lmpdf"
    if lmp_key not in st.session_state:
        st.session_state[lmp_key] = None

    # ── TAB 1: Upload ─────────────────────────────────────────────
    with tab_upload:
        st.markdown('<p style="color:#3a6080;font-family:Share Tech Mono,monospace;font-size:11px">Upload a ZIP file containing ERCOT LMP CSVs, or a single CSV. All files are auto-merged and matched to selected buses.</p>', unsafe_allow_html=True)
        up = st.file_uploader("Upload LMP file", type=["csv","zip"],
                              key=f"{key_prefix}_uploader", label_visibility="collapsed")
        if up:
            with st.spinner("Parsing file(s)..."):
                ldf, err = parse_lmp_upload(up)
            if err and ldf is None:
                st.error(err)
            else:
                if err: st.warning(err)
                st.session_state[lmp_key] = ldf
                files = ldf["_source_file"].nunique() if "_source_file" in ldf.columns else 1
                st.success(f"✓ Loaded {len(ldf):,} rows from {files} file(s)")

    # ── TAB 2: Live API ───────────────────────────────────────────
    with tab_live:
        st.markdown('<p style="color:#3a6080;font-family:Share Tech Mono,monospace;font-size:11px">Pull DAM Settlement Point Prices directly from the ERCOT public API — no file upload needed.</p>', unsafe_allow_html=True)

        buses_available = resolved_df["Bus"].tolist()
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            live_bus = st.selectbox("Select Bus", buses_available,
                                    key=f"{key_prefix}_live_bus", label_visibility="collapsed")
        with c2:
            days_back = st.selectbox("Days back", [1, 7, 14, 30, 60],
                                     key=f"{key_prefix}_live_days", label_visibility="collapsed")
        with c3:
            fetch_btn = st.button("Fetch Live →", key=f"{key_prefix}_fetch_live",
                                  type="primary", use_container_width=True)

        if fetch_btn and live_bus:
            d_to   = datetime.now().strftime("%Y-%m-%d")
            d_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            with st.spinner(f"Fetching {live_bus} from ERCOT API ({d_from} → {d_to})..."):
                ldf, err = fetch_ercot_dam_live(live_bus, d_from, d_to)
            if err:
                st.error(f"{err} — The ERCOT API may require authentication. Use the Upload tab instead.")
            elif ldf is not None:
                # Normalise to standard format
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
                    st.success(f"✓ Fetched {len(ldf):,} rows for {live_bus}")

    # ── Use uploaded/fetched data ─────────────────────────────────
    ldf = st.session_state[lmp_key]
    if ldf is None:
        st.markdown("""
        <div class="map-placeholder" style="padding:28px;margin-top:10px">
            <div class="mp-icon">📡</div>
            <div class="mp-sub">Upload a ZIP/CSV or fetch live data above to begin analysis</div>
        </div>""", unsafe_allow_html=True)
        return None

    buses_up  = set(resolved_df["Bus"].str.upper())
    ldf["_bus_up"] = ldf["bus"].str.upper().str.strip()
    matched   = ldf[ldf["_bus_up"].isin(buses_up)].copy()

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Total Rows",    f"{len(ldf):,}")
    m2.metric("Matched Rows",  f"{len(matched):,}")
    m3.metric("Buses Matched", f"{matched['_bus_up'].nunique()} / {len(buses_up)}")
    avg_p = matched["price"].mean() if len(matched) else None
    m4.metric("Avg LMP",       f"${avg_p:.2f}/MWh" if avg_p is not None else "—")

    if matched.empty:
        st.warning("No buses matched. Check settlement point names in your file.")
        return None

    # ── TAB 3: Use-Case Modules ───────────────────────────────────
    with tab_usecases:
        USE_CASES = {
            "24h_profile":   ("📈 24-Hour Profile",      "LMP curve for any selected bus across 24 hours", "Developers · Traders · BESS Operators"),
            "arbitrage":     ("💰 Energy Arbitrage",      "Best charge/discharge windows. Revenue estimate for BESS", "BESS Operators · Traders"),
            "congestion":    ("🔥 Congestion Analysis",   "Price spreads between nodes. Identify transmission bottlenecks", "Developers · Grid Planners"),
            "curtailment":   ("⚠️ Curtailment Risk",      "Negative/zero price frequency. Renewable revenue impact", "Solar · Wind Developers"),
            "bess_dispatch": ("⚡ BESS Dispatch",         "Optimal charge/discharge schedule using rolling-average logic", "BESS Operators"),
            "ftr":           ("🎯 FTR Opportunity",       "Node-pair spread analysis for Financial Transmission Rights", "Power Traders"),
            "revenue":       ("🏗️ Revenue Estimation",   "Annual revenue estimates for Solar, Wind, BESS by node", "Project Developers"),
        }

        uc_sel = st.selectbox(
            "Select Analysis",
            list(USE_CASES.keys()),
            format_func=lambda k: USE_CASES[k][0],
            key=f"{key_prefix}_uc_sel",
            label_visibility="collapsed"
        )

        uc_title, uc_desc, uc_who = USE_CASES[uc_sel]
        st.markdown(f"""
        <div style="background:rgba(0,255,157,0.04);border:1px solid rgba(0,255,157,0.15);
             border-radius:4px;padding:10px 16px;margin-bottom:14px;">
            <div style="font-family:Orbitron,monospace;font-size:12px;color:#00ff9d;margin-bottom:4px">{uc_title}</div>
            <div style="font-family:Share Tech Mono,monospace;font-size:11px;color:#3a6080">{uc_desc}</div>
            <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#00c8ff;margin-top:4px">👤 {uc_who}</div>
        </div>
        """, unsafe_allow_html=True)

        # BESS params if needed
        batt_mw, batt_mwh, eff = 100, 400, 0.85
        if uc_sel in ["arbitrage", "bess_dispatch"]:
            bc1, bc2, bc3 = st.columns(3)
            batt_mw  = bc1.number_input("Battery MW",  value=100, min_value=1,  key=f"{key_prefix}_bmw")
            batt_mwh = bc2.number_input("Battery MWh", value=400, min_value=10, key=f"{key_prefix}_bmwh")
            eff      = bc3.number_input("Efficiency",  value=0.85, min_value=0.5, max_value=1.0, step=0.01, key=f"{key_prefix}_eff")

        run_btn = st.button(f"Run {uc_title} →", key=f"{key_prefix}_run_{uc_sel}", type="primary", use_container_width=True)

        if run_btn or f"{key_prefix}_uc_result_{uc_sel}" in st.session_state:
            if run_btn:
                with st.spinner("Analysing..."):
                    result, err = run_lmp_analytics(matched.copy(), resolved_df, uc_sel, batt_mw, batt_mwh, eff)
                if err:
                    st.error(err)
                else:
                    st.session_state[f"{key_prefix}_uc_result_{uc_sel}"] = result
            else:
                result = st.session_state.get(f"{key_prefix}_uc_result_{uc_sel}")

            if result is None:
                pass
            # ── 24h Profile ──────────────────────────────────────
            elif uc_sel == "24h_profile":
                bus_list = sorted(matched["_bus_up"].unique().tolist())
                sel_bus = st.selectbox("Select Bus", bus_list, key=f"{key_prefix}_24h_bus")
                bdf = matched[matched["_bus_up"]==sel_bus].sort_values("datetime")

                # 24h average profile
                if hasattr(bdf["datetime"].iloc[0], "hour"):
                    bdf["hour_of_day"] = bdf["datetime"].dt.hour
                else:
                    bdf["hour_of_day"] = pd.to_numeric(bdf["datetime"], errors="coerce") % 24

                hourly = bdf.groupby("hour_of_day")["price"].agg(["mean","min","max"]).reset_index()
                hourly.columns = ["Hour", "Avg LMP", "Min LMP", "Max LMP"]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hourly["Hour"], y=hourly["Max LMP"], fill=None,
                    mode="lines", line=dict(width=0), showlegend=False))
                fig.add_trace(go.Scatter(x=hourly["Hour"], y=hourly["Min LMP"],
                    fill="tonexty", fillcolor="rgba(0,200,255,0.1)",
                    mode="lines", line=dict(width=0), name="Min-Max Range"))
                fig.add_trace(go.Scatter(x=hourly["Hour"], y=hourly["Avg LMP"],
                    mode="lines+markers", line=dict(color="#00ff9d", width=2.5),
                    marker=dict(size=6, color="#00ff9d", symbol="circle"),
                    name="Avg LMP"))

                # Rolling avg overlay
                roll = hourly["Avg LMP"].rolling(3, center=True, min_periods=1)
                fig.add_trace(go.Scatter(x=hourly["Hour"], y=roll.mean(),
                    mode="lines", line=dict(color="#ff6b00", width=1.5, dash="dot"),
                    name="Rolling Avg"))

                # BESS signal overlay
                roll_mean = roll.mean()
                charge_h    = hourly.loc[hourly["Avg LMP"] < roll_mean * 0.85, "Hour"].tolist()
                discharge_h = hourly.loc[hourly["Avg LMP"] > roll_mean * 1.15, "Hour"].tolist()
                for h in charge_h:
                    fig.add_vrect(x0=h-0.4, x1=h+0.4, fillcolor="rgba(0,255,157,0.12)",
                                  layer="below", line_width=0)
                for h in discharge_h:
                    fig.add_vrect(x0=h-0.4, x1=h+0.4, fillcolor="rgba(255,107,0,0.12)",
                                  layer="below", line_width=0)

                fig.update_layout(**neon_plotly_layout(f"24-HOUR LMP PROFILE — {sel_bus}", 360))
                fig.update_xaxes(title="Hour of Day (0–23)", dtick=2)
                fig.update_yaxes(title="LMP ($/MWh)")
                st.plotly_chart(fig, use_container_width=True)

                # Annotation
                st.markdown(f"""
                <div style="font-family:Share Tech Mono,monospace;font-size:10px;color:#3a6080;
                     display:flex;gap:20px;margin-top:-8px;padding:6px 10px;background:rgba(0,0,0,0.3);border-radius:3px">
                    <span>🟩 Green bands = CHARGE windows</span>
                    <span>🟧 Orange bands = DISCHARGE windows</span>
                    <span>── Rolling 3h avg</span>
                </div>
                """, unsafe_allow_html=True)

                # Also show full time series if dates available
                if hasattr(bdf["datetime"].iloc[0], "date"):
                    st.markdown('<div class="section-label" style="margin-top:16px">FULL TIME SERIES</div>', unsafe_allow_html=True)
                    fig2 = go.Figure()
                    for bus in matched["_bus_up"].unique()[:6]:
                        bdf2 = matched[matched["_bus_up"]==bus].sort_values("datetime")
                        col  = "#00ff9d" if bus==sel_bus else None
                        fig2.add_trace(go.Scatter(x=bdf2["datetime"], y=bdf2["price"],
                            mode="lines", name=bus,
                            line=dict(color=col, width=2 if bus==sel_bus else 1)))
                    fig2.update_layout(**neon_plotly_layout("LMP TIME SERIES", 280))
                    fig2.update_yaxes(title="LMP ($/MWh)")
                    st.plotly_chart(fig2, use_container_width=True)

            # ── Arbitrage ─────────────────────────────────────────
            elif uc_sel == "arbitrage" and isinstance(result, pd.DataFrame):
                st.dataframe(result, use_container_width=True,
                    column_config={
                        "Daily Revenue $":  st.column_config.NumberColumn(format="$%.0f"),
                        "Annual Revenue $": st.column_config.NumberColumn(format="$%.0f"),
                    })
                fig = go.Figure(go.Bar(
                    x=result["Bus"], y=result["Annual Revenue $"],
                    marker_color="#00ff9d",
                    marker_line_color="rgba(0,255,157,0.5)", marker_line_width=1
                ))
                fig.update_layout(**neon_plotly_layout("ANNUAL ARBITRAGE REVENUE BY BUS", 280))
                st.plotly_chart(fig, use_container_width=True)
                st.download_button("↓ Export Arbitrage Analysis", data=to_csv_bytes(result),
                    file_name="arbitrage_analysis.csv", mime="text/csv", key=f"{key_prefix}_dl_arb")

            # ── Congestion ────────────────────────────────────────
            elif uc_sel == "congestion" and isinstance(result, pd.DataFrame):
                st.dataframe(result, use_container_width=True)
                if len(result):
                    fig = go.Figure(go.Bar(
                        x=result["Bus A"] + " ↔ " + result["Bus B"],
                        y=result["Avg Spread $/MWh"],
                        marker_color="#ff6b00",
                        marker_line_color="rgba(255,107,0,0.5)", marker_line_width=1
                    ))
                    fig.update_layout(**neon_plotly_layout("CONGESTION SPREAD BY NODE PAIR", 280))
                    st.plotly_chart(fig, use_container_width=True)
                st.download_button("↓ Export Congestion Analysis", data=to_csv_bytes(result),
                    file_name="congestion_analysis.csv", mime="text/csv", key=f"{key_prefix}_dl_cong")

            # ── Curtailment ───────────────────────────────────────
            elif uc_sel == "curtailment" and isinstance(result, pd.DataFrame):
                for _, row in result.iterrows():
                    risk_col = {"HIGH":"#ff2d55","MED":"#ff6b00","LOW":"#00ff9d"}.get(row.get("Curtailment Risk",""), "#3a6080")
                    st.markdown(f"""
                    <div style="background:rgba({{'HIGH':'255,45,85','MED':'255,107,0','LOW':'0,255,157'}}.get('{row.get("Curtailment Risk","")}','58,96,128'),0.06);
                         border:1px solid {risk_col};border-radius:4px;padding:10px 16px;margin-bottom:8px;
                         display:flex;justify-content:space-between;align-items:center">
                        <span style="font-family:Orbitron,monospace;font-size:12px;color:#00c8ff">{row["Bus"]}</span>
                        <span style="font-family:Share Tech Mono,monospace;font-size:11px;color:#c8e6ff">Neg: <b style="color:{risk_col}">{row["Negative Price %"]}%</b></span>
                        <span style="font-family:Share Tech Mono,monospace;font-size:11px;color:#c8e6ff">Avg: ${row["Avg Price $/MWh"]}/MWh</span>
                        <span style="font-family:Orbitron,monospace;font-size:11px;color:{risk_col};text-shadow:0 0 6px {risk_col}">{row["Curtailment Risk"]}</span>
                    </div>""", unsafe_allow_html=True)
                st.download_button("↓ Export Curtailment Analysis", data=to_csv_bytes(result),
                    file_name="curtailment_analysis.csv", mime="text/csv", key=f"{key_prefix}_dl_curt")

            # ── BESS Dispatch ─────────────────────────────────────
            elif uc_sel == "bess_dispatch" and isinstance(result, dict):
                bdf  = result["data"]
                bus  = result["bus"]
                m1,m2,m3 = st.columns(3)
                m1.metric("Net Revenue",       f"${result['net_revenue']:,.0f}")
                m2.metric("Charge Hours",      result["charge_hours"])
                m3.metric("Discharge Hours",   result["discharge_hours"])

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=bdf["datetime"], y=bdf["price"],
                    mode="lines", name="LMP", line=dict(color="#00c8ff", width=1.5)))
                fig.add_trace(go.Scatter(x=bdf["datetime"], y=bdf["roll_avg"],
                    mode="lines", name="Rolling Avg", line=dict(color="#ff6b00", width=1.5, dash="dot")))

                charge_df    = bdf[bdf["signal"]=="CHARGE"]
                discharge_df = bdf[bdf["signal"]=="DISCHARGE"]
                fig.add_trace(go.Scatter(x=charge_df["datetime"], y=charge_df["price"],
                    mode="markers", name="CHARGE", marker=dict(color="#00ff9d", size=8, symbol="triangle-down")))
                fig.add_trace(go.Scatter(x=discharge_df["datetime"], y=discharge_df["price"],
                    mode="markers", name="DISCHARGE", marker=dict(color="#ff2d55", size=8, symbol="triangle-up")))

                fig.update_layout(**neon_plotly_layout(f"BESS DISPATCH SCHEDULE — {bus}", 360))
                st.plotly_chart(fig, use_container_width=True)
                st.download_button("↓ Export Dispatch Schedule", data=to_csv_bytes(bdf),
                    file_name="bess_dispatch.csv", mime="text/csv", key=f"{key_prefix}_dl_bess")

            # ── FTR ───────────────────────────────────────────────
            elif uc_sel == "ftr" and isinstance(result, pd.DataFrame):
                st.dataframe(result, use_container_width=True,
                    column_config={
                        "Avg FTR Value $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                        "Max FTR Value $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                        "Win Rate %": st.column_config.NumberColumn(format="%.1f%%"),
                    })
                st.download_button("↓ Export FTR Analysis", data=to_csv_bytes(result),
                    file_name="ftr_analysis.csv", mime="text/csv", key=f"{key_prefix}_dl_ftr")

            # ── Revenue ───────────────────────────────────────────
            elif uc_sel == "revenue" and isinstance(result, pd.DataFrame):
                st.dataframe(result, use_container_width=True,
                    column_config={
                        "Annual Solar Rev ($/MW)": st.column_config.NumberColumn(format="$%.0f"),
                        "Annual Wind Rev ($/MW)":  st.column_config.NumberColumn(format="$%.0f"),
                        "Annual BESS Rev ($/MW)":  st.column_config.NumberColumn(format="$%.0f"),
                    })
                st.download_button("↓ Export Revenue Analysis", data=to_csv_bytes(result),
                    file_name="revenue_analysis.csv", mime="text/csv", key=f"{key_prefix}_dl_rev")

    # ── PDF Export ────────────────────────────────────────────────
    st.markdown('<div class="section-label">📄 EXPORT REPORT</div>', unsafe_allow_html=True)
    lmp_summary = None
    if ldf is not None and "bus" in ldf.columns:
        try:
            lmp_summary = matched.groupby("_bus_up")["price"].agg(
                Mean="mean", Max="max", Min="min", Count="count"
            ).reset_index().round(2)
        except: pass

    if ercot_sub and resolved_df is not None:
        pdf_bytes = generate_pdf_report(search_results, ercot_sub, resolved_df, lmp_summary)
        st.download_button(
            "↓ Download PDF Report (SunStripe)",
            data=bytes(pdf_bytes),
            file_name=f"sunstripe_{ercot_sub}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            key=f"{key_prefix}_pdf_dl",
            type="primary",
        )

    return ldf


# ═══════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:14px 0 16px">
        <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#00ff9d;
             letter-spacing:.3em;text-transform:uppercase;margin-bottom:5px;text-shadow:0 0 8px #00ff9d">⚡ SunStripe · ERCOT</div>
        <div style="font-family:'Orbitron',monospace;font-size:13px;font-weight:700;
             color:#c8e6ff;line-height:1.5;letter-spacing:.05em">NODAL ANALYSIS<br>
             <span style="color:#00ff9d;text-shadow:0 0 10px #00ff9d">PLATFORM</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio("", [
        "🗺️ Infrastructure Map",
        "⚡ Node & Hub Selector",
        "🔍 Bus Lookup",
        "🏭 Substation Lookup",
        "📋 Browse All",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#3a6080;
         letter-spacing:.2em;text-transform:uppercase;margin-bottom:10px;
         border-bottom:1px solid #0a1f35;padding-bottom:6px">// DATASET · FEB 2026</div>
    <div style="display:flex;flex-direction:column;gap:9px">
        <div><div style="font-family:'Orbitron',monospace;font-size:18px;font-weight:700;color:#00ff9d;text-shadow:0 0 10px #00ff9d">{len(df):,}</div><div style="font-size:10px;color:#3a6080">Settlement Points</div></div>
        <div><div style="font-family:'Orbitron',monospace;font-size:18px;font-weight:700;color:#00c8ff;text-shadow:0 0 10px #00c8ff">{df["Substation"].nunique():,}</div><div style="font-size:10px;color:#3a6080">Substations</div></div>
        <div><div style="font-family:'Orbitron',monospace;font-size:18px;font-weight:700;color:#ff6b00;text-shadow:0 0 10px #ff6b00">{df[df["Hub"]!=""]["Hub"].nunique()}</div><div style="font-size:10px;color:#3a6080">Hubs</div></div>
        <div><div style="font-family:'Orbitron',monospace;font-size:18px;font-weight:700;color:#00ff9d;text-shadow:0 0 10px #00ff9d">{df[df["Resource Node"]!=""].shape[0]:,}</div><div style="font-size:10px;color:#3a6080">Resource Nodes</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <a href="https://ercot-bess-dashboard-nhh9eztsqeuqxxuz97kacu.streamlit.app/" target="_blank"
       style="display:block;padding:7px 10px;background:#091424;border-radius:4px;border:1px solid #0a1f35;
              font-family:'Share Tech Mono',monospace;font-size:11px;color:#3a6080;text-decoration:none;margin-bottom:5px">
              ⚡ ERCOT BESS Dashboard ↗</a>
    <a href="https://fatal-flaw-o7aks4agtoffgyydbvrguj.streamlit.app/" target="_blank"
       style="display:block;padding:7px 10px;background:#091424;border-radius:4px;border:1px solid #0a1f35;
              font-family:'Share Tech Mono',monospace;font-size:11px;color:#3a6080;text-decoration:none">
              🌿 SiteIQ Fatal Flaw ↗</a>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: INFRASTRUCTURE MAP
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🗺️ Infrastructure Map":

    st.markdown("""<div class="page-header">
        <div class="tag">⚡ SunStripe · ERCOT</div>
        <h1>SUBSTATION <span>SEARCH</span></h1>
    </div>""", unsafe_allow_html=True)

    for k, v in [("search_results",None),("selected_osm",None),("ercot_sel_sub",None),
                 ("search_lat",31.5),("search_lon",-97.5)]:
        if k not in st.session_state: st.session_state[k] = v

    # ── SEARCH PARAMETERS ─────────────────────────────────────────
    st.markdown('<div style="background:#060d1a;border:1px solid rgba(0,200,255,0.2);border-radius:4px;padding:18px 20px;margin-bottom:18px;box-shadow:0 0 24px rgba(0,200,255,0.04);">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:9px;color:#3a6080;letter-spacing:.2em;text-transform:uppercase;margin-bottom:14px">// SEARCH PARAMETERS</div>', unsafe_allow_html=True)

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
            <div class="mp-icon">⚡</div>
            <div class="mp-title">No search yet</div>
            <div class="mp-sub">Enter an address or coordinates above · set radius · click Search</div>
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
        <div style="display:flex;gap:20px;font-family:Share Tech Mono,monospace;font-size:11px;
             color:#3a6080;padding:6px 12px;background:rgba(3,7,18,0.9);border:1px solid rgba(0,200,255,0.2);
             border-radius:4px;margin-top:6px;flex-wrap:wrap;">
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
                dot_col = "#ff6b00" if is_hub else "#00c8ff"
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
                <div class="oc-title" style="color:{'#ff6b00' if is_hub else '#00c8ff'}">
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
                   style="display:inline-block;margin-top:8px;padding:5px 14px;background:rgba(0,200,255,0.08);
                          border:1px solid rgba(0,200,255,0.3);border-radius:3px;font-family:Share Tech Mono,monospace;
                          font-size:11px;color:#00c8ff;text-decoration:none;text-shadow:0 0 6px #00c8ff">
                   🌿 Open in SiteIQ Fatal Flaw ↗
                </a>
            </div>
            """, unsafe_allow_html=True)

            # ERCOT match
            st.markdown('<div class="section-label">ERCOT CSV MATCH</div>', unsafe_allow_html=True)
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
    st.markdown("""<div class="page-header">
        <div class="tag">⚡ SunStripe · ERCOT</div>
        <h1>NODE & HUB <span>SELECTOR</span></h1>
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
    st.markdown("""<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>BUS <span>LOOKUP</span></h1></div>""", unsafe_allow_html=True)
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
    st.markdown("""<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>SUBSTATION <span>LOOKUP</span></h1></div>""", unsafe_allow_html=True)
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
    st.markdown("""<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>BROWSE <span>ALL</span></h1></div>""", unsafe_allow_html=True)
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
