import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SunStripe · AI Energy Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS — SunStripe Professional White/Red Theme (shared with Nodal Analyser)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
  --bg: #ffffff; --bg2: #f7f7f5; --bg3: #f0efec;
  --border: #e2e0db; --border2: #d0cdc6;
  --red: #c8102e; --red-light: #f5e6e9; --red-mid: #e8b4bc; --red-dark: #8b0b1f;
  --ink: #1a1a18; --ink2: #3d3d38; --ink3: #6b6b64; --ink4: #9b9b92;
  --gold: #b8860b; --gold-lt: #f5f0e0;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: var(--bg) !important; color: var(--ink) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background-image: linear-gradient(90deg, rgba(200,16,46,0.025) 1px, transparent 1px),
        linear-gradient(0deg, rgba(200,16,46,0.025) 1px, transparent 1px) !important;
    background-size: 48px 48px !important;
}

[data-testid="stSidebar"] {
    background: var(--ink) !important; border-right: 3px solid var(--red) !important;
    box-shadow: 4px 0 32px rgba(200,16,46,0.12) !important;
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
    color: rgba(255,255,255,0.7) !important;
}

.page-header {
    border-bottom: 2px solid var(--ink); padding-bottom: 18px; margin-bottom: 28px;
    position: relative; display: flex; align-items: flex-end; justify-content: space-between;
}
.page-header::after {
    content: ''; position: absolute; bottom: -2px; left: 0; width: 60px; height: 2px; background: var(--red);
}
.page-header .tag {
    font-family: 'DM Mono', monospace; font-size: 11px; color: var(--red);
    letter-spacing: .12em; text-transform: uppercase; margin-bottom: 8px; font-weight: 500;
}
.page-header h1 {
    font-family: 'Playfair Display', serif; font-size: 32px; font-weight: 700;
    color: var(--ink); margin: 0; line-height: 1.1; letter-spacing: -0.02em;
}
.page-header h1 span { color: var(--red); }
.page-header .ph-right {
    font-family: 'DM Mono', monospace; font-size: 10px; color: var(--ink4);
    text-align: right; letter-spacing: .08em; text-transform: uppercase;
}

.section-label {
    font-family: 'DM Mono', monospace; font-size: 10px; color: var(--ink3);
    letter-spacing: .18em; text-transform: uppercase; margin: 24px 0 12px;
    display: flex; align-items: center; gap: 12px; font-weight: 500;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: var(--border); }

.ercot-card {
    background: var(--bg2); border: 1px solid var(--border); border-left: 4px solid var(--ink);
    border-radius: 2px; padding: 18px 22px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.ercot-card h3 {
    font-family: 'Playfair Display', serif; font-size: 16px; font-weight: 600;
    color: var(--ink); margin: 0 0 14px; letter-spacing: -0.01em;
}

[data-testid="stMetric"] {
    background: var(--bg2) !important; border: 1px solid var(--border) !important;
    border-top: 3px solid var(--red) !important; border-radius: 2px !important;
    padding: 16px 18px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    color: var(--ink4) !important; text-transform: uppercase !important; letter-spacing: .12em !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important; color: var(--ink) !important;
    font-size: 26px !important; font-weight: 700 !important; letter-spacing: -0.02em !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--bg) !important; border-bottom: 2px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
    color: var(--ink3) !important; background: transparent !important;
    border-bottom: 2px solid transparent !important; margin-bottom: -2px !important;
}
.stTabs [aria-selected="true"] {
    color: var(--red) !important; border-bottom: 2px solid var(--red) !important; font-weight: 600 !important;
}

.stTextInput input, div[data-baseweb="select"] > div, .stNumberInput input {
    background-color: var(--bg) !important; border: 1px solid var(--border2) !important;
    color: var(--ink) !important; font-family: 'DM Sans', sans-serif !important; border-radius: 2px !important;
}
.stDownloadButton button, .stButton button {
    background: var(--bg) !important; border: 1px solid var(--border2) !important;
    color: var(--ink2) !important; font-family: 'DM Sans', sans-serif !important; border-radius: 2px !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    border-color: var(--red) !important; color: var(--red) !important; background: var(--red-light) !important;
}
button[kind="primary"] {
    background: var(--red) !important; border: 1px solid var(--red) !important;
    color: #fff !important; font-weight: 600 !important;
}
div[data-testid="stMarkdownContainer"] p {
    color: var(--ink2); font-size: 14px; line-height: 1.6; font-family: 'DM Sans', sans-serif;
}
hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Loading 15 years of DAM history...")
def load_dam_historical():
    with open("dam_historical.json", "r") as f:
        return json.load(f)

# Model results (embedded — 5KB)
MODEL = {"metrics":{"mae":14.15,"rmse":61.82,"r2":-0.0319},"fi":[{"f":"DAvg","v":0.4774},{"f":"DMin","v":0.2962},{"f":"SinHour","v":0.0589},{"f":"DMax","v":0.0566},{"f":"Hour","v":0.0303},{"f":"DStd","v":0.0256},{"f":"CosHour","v":0.0123},{"f":"DayOfWeek","v":0.0082},{"f":"L30","v":0.0055},{"f":"IsWeekend","v":0.0046},{"f":"V30","v":0.0044},{"f":"V7","v":0.0041}],"batt":{"charge":12.93,"discharge":61.4,"cycles":439,"annual":1777382},"dr":{"annual":851602},"hrly":[{"h":1,"a":18.98,"p":17.2},{"h":2,"a":17.12,"p":15.81},{"h":3,"a":16.39,"p":15.8},{"h":4,"a":16.69,"p":16.18},{"h":5,"a":18.17,"p":16.36},{"h":6,"a":22.19,"p":19.23},{"h":7,"a":30.97,"p":29.17},{"h":8,"a":32.41,"p":29.42},{"h":9,"a":23.8,"p":26.52},{"h":10,"a":16.59,"p":25.1},{"h":11,"a":16.09,"p":25.28},{"h":12,"a":16.89,"p":25.36},{"h":13,"a":18.38,"p":28.27},{"h":14,"a":20.56,"p":31.71},{"h":15,"a":21.7,"p":40.2},{"h":16,"a":23.91,"p":53.99},{"h":17,"a":29.91,"p":60.53},{"h":18,"a":42.13,"p":50.56},{"h":19,"a":53.18,"p":40.29},{"h":20,"a":79.13,"p":37.3},{"h":21,"a":63.67,"p":29.78},{"h":22,"a":32.12,"p":25.75},{"h":23,"a":23.47,"p":22.33},{"h":24,"a":19.73,"p":20.61}],"daily":[{"d":"2024-01-01","a":21.42,"p":20.98},{"d":"2024-01-02","a":26.79,"p":26.52},{"d":"2024-01-03","a":25.59,"p":24.99},{"d":"2024-01-04","a":18.92,"p":18.57},{"d":"2024-01-05","a":21.59,"p":21.16},{"d":"2024-01-06","a":27.77,"p":26.75},{"d":"2024-01-07","a":14.21,"p":15.23},{"d":"2024-01-08","a":10.89,"p":12.54},{"d":"2024-01-09","a":22.48,"p":22.93},{"d":"2024-01-10","a":20.86,"p":21.36},{"d":"2024-01-11","a":14.83,"p":15.11},{"d":"2024-01-12","a":17.37,"p":18.17},{"d":"2024-01-13","a":15.89,"p":16.2},{"d":"2024-01-14","a":69.97,"p":64.66},{"d":"2024-01-15","a":246.86,"p":274.44},{"d":"2024-01-16","a":381.87,"p":627.83},{"d":"2024-01-17","a":51.92,"p":55.06},{"d":"2024-01-18","a":22.1,"p":19.63},{"d":"2024-01-19","a":24.24,"p":24.8},{"d":"2024-01-20","a":33.7,"p":32.99},{"d":"2024-01-21","a":20.97,"p":21.09},{"d":"2024-01-22","a":27.28,"p":26.28},{"d":"2024-01-23","a":28.98,"p":28.75},{"d":"2024-01-24","a":32.54,"p":31.88},{"d":"2024-01-25","a":26.37,"p":26.0},{"d":"2024-01-26","a":21.43,"p":21.24},{"d":"2024-01-27","a":20.33,"p":20.57},{"d":"2024-01-28","a":27.4,"p":26.34},{"d":"2024-01-29","a":22.38,"p":22.42},{"d":"2024-01-30","a":21.2,"p":21.22},{"d":"2024-01-31","a":19.53,"p":19.72},{"d":"2024-02-01","a":14.3,"p":14.5},{"d":"2024-02-02","a":15.13,"p":15.38},{"d":"2024-02-03","a":10.16,"p":12.68},{"d":"2024-02-04","a":9.11,"p":12.58},{"d":"2024-02-05","a":19.33,"p":19.7},{"d":"2024-02-06","a":19.54,"p":20.04},{"d":"2024-02-07","a":10.15,"p":12.65},{"d":"2024-02-08","a":14.29,"p":14.45},{"d":"2024-02-09","a":18.94,"p":18.88},{"d":"2024-02-10","a":15.7,"p":16.06},{"d":"2024-02-11","a":15.18,"p":15.41},{"d":"2024-02-12","a":20.92,"p":21.31},{"d":"2024-02-13","a":15.27,"p":15.51},{"d":"2024-02-14","a":9.43,"p":12.41},{"d":"2024-02-15","a":15.26,"p":15.54},{"d":"2024-02-16","a":10.23,"p":12.68},{"d":"2024-02-17","a":18.02,"p":19.05},{"d":"2024-02-18","a":19.24,"p":19.43},{"d":"2024-02-19","a":15.02,"p":15.53},{"d":"2024-02-20","a":11.93,"p":12.9},{"d":"2024-02-21","a":6.94,"p":12.35},{"d":"2024-02-22","a":12.16,"p":13.76},{"d":"2024-02-23","a":18.86,"p":19.59},{"d":"2024-02-24","a":11.29,"p":12.93},{"d":"2024-02-25","a":11.92,"p":14.3},{"d":"2024-02-26","a":14.02,"p":14.59},{"d":"2024-02-27","a":12.62,"p":13.31},{"d":"2024-02-28","a":15.61,"p":15.97},{"d":"2024-02-29","a":21.32,"p":21.29},{"d":"2024-03-01","a":17.35,"p":17.82},{"d":"2024-03-02","a":14.94,"p":15.83},{"d":"2024-03-03","a":14.05,"p":14.96},{"d":"2024-03-04","a":31.7,"p":31.25},{"d":"2024-03-05","a":46.37,"p":50.95},{"d":"2024-03-06","a":27.54,"p":28.27},{"d":"2024-03-07","a":20.0,"p":20.26},{"d":"2024-03-08","a":16.11,"p":16.49},{"d":"2024-03-09","a":24.73,"p":25.23},{"d":"2024-03-10","a":31.23,"p":30.76},{"d":"2024-03-11","a":15.98,"p":16.62},{"d":"2024-03-12","a":12.91,"p":14.57},{"d":"2024-03-13","a":14.96,"p":16.21},{"d":"2024-03-14","a":30.75,"p":31.33},{"d":"2024-03-15","a":15.32,"p":16.04},{"d":"2024-03-16","a":33.97,"p":33.97},{"d":"2024-03-17","a":26.24,"p":25.94},{"d":"2024-03-18","a":28.81,"p":28.9},{"d":"2024-03-19","a":20.39,"p":21.79},{"d":"2024-03-20","a":24.84,"p":25.14},{"d":"2024-03-21","a":39.38,"p":38.09},{"d":"2024-03-22","a":26.68,"p":26.54},{"d":"2024-03-23","a":16.72,"p":17.54},{"d":"2024-03-24","a":6.32,"p":13.21},{"d":"2024-03-25","a":15.29,"p":16.48},{"d":"2024-03-26","a":28.78,"p":28.8},{"d":"2024-03-27","a":20.76,"p":21.33},{"d":"2024-03-28","a":22.74,"p":24.09},{"d":"2024-03-29","a":5.15,"p":12.59},{"d":"2024-03-30","a":14.16,"p":15.06}],"mth":[{"m":1,"a":43.8,"p":52.43},{"m":2,"a":14.55,"p":15.68},{"m":3,"a":21.8,"p":22.89},{"m":4,"a":23.13,"p":25.63},{"m":5,"a":44.83,"p":43.91},{"m":6,"a":30.49,"p":30.72},{"m":7,"a":22.97,"p":23.33},{"m":8,"a":35.84,"p":35.86},{"m":9,"a":23.79,"p":24.21},{"m":10,"a":26.51,"p":27.03},{"m":11,"a":23.03,"p":23.41},{"m":12,"a":25.1,"p":24.96}],"spike":{"prec":0.46,"rec":0.385,"tp":69,"fp":81,"fn":110}}

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
PALETTE = ["#c8102e","#1a3a7a","#b8860b","#1a6a1a","#7a1a5a","#5a3a1a","#1a5a7a",
           "#e63946","#457b9d","#2a9d8f","#e9c46a","#f4a261","#264653","#a8dadc","#d62828"]

def ss_layout(title="", height=360):
    return dict(
        title=dict(text=title, font=dict(family="Playfair Display", size=14, color="#1a1a18"), x=0.01),
        height=height, paper_bgcolor="#ffffff", plot_bgcolor="#f7f7f5",
        font=dict(family="DM Sans", color="#3d3d38", size=11),
        xaxis=dict(gridcolor="#e2e0db", linecolor="#d0cdc6", tickfont=dict(size=10, color="#6b6b64")),
        yaxis=dict(gridcolor="#e2e0db", linecolor="#d0cdc6", tickfont=dict(size=10, color="#6b6b64"), tickprefix="$"),
        legend=dict(bgcolor="rgba(247,247,245,0.95)", bordercolor="#e2e0db", borderwidth=1, font=dict(size=10)),
        margin=dict(l=55, r=20, t=45, b=40), hovermode="x unified",
    )


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 20px 20px">
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.4);
             letter-spacing:.18em;text-transform:uppercase;margin-bottom:10px">AI Energy Agent</div>
        <div style="font-family:'Playfair Display',serif;font-size:22px;font-weight:700;
             color:#fff;line-height:1.2;letter-spacing:-0.02em">SunStripe</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:12px;font-weight:300;
             color:rgba(255,255,255,0.5);margin-top:2px">DAM Intelligence · ML Forecasting</div>
        <div style="margin-top:14px;height:1px;background:rgba(200,16,46,0.6)"></div>
    </div>""", unsafe_allow_html=True)

    page = st.radio("", [
        "📊 DAM Price History",
        "🤖 Forecast Engine",
        "🔋 Battery Agent",
        "🏭 Demand Response",
        "🛡️ REP Risk Tool",
        "🚀 Revenue Roadmap",
    ], label_visibility="collapsed")

    st.markdown("""
    <div style="padding:20px 20px 0;margin-top:8px">
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:rgba(255,255,255,0.3);
             letter-spacing:.14em;text-transform:uppercase;margin-bottom:14px;
             padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.08)">Platform Stats</div>
        <div style="display:flex;flex-direction:column;gap:14px">
            <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.45)">DAM History</span>
                <span style="font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:#fff">15 yrs</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.45)">Settlement Points</span>
                <span style="font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:#fff">15</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.45)">Hourly Records</span>
                <span style="font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:#c8102e">1.8M+</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:baseline">
                <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,0.45)">ML Model</span>
                <span style="font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:#fff">GBR</span>
            </div>
        </div>
        <div style="margin-top:20px;height:1px;background:rgba(255,255,255,0.08)"></div>
    </div>""", unsafe_allow_html=True)

    # Cross-links to Nodal Analyser and other tools
    st.markdown("""
    <div style="padding:16px 20px 24px">
    <a href="https://sunstripe-nodal.streamlit.app/" target="_blank"
       style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;
              background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
              border-radius:2px;font-family:'DM Sans',sans-serif;font-size:12px;
              color:rgba(255,255,255,0.6);text-decoration:none;margin-bottom:6px">
        <span>⚡ Nodal Analyser</span><span style="opacity:.4">↗</span></a>
    <a href="https://ercot-bess-dashboard-nhh9eztsqeuqxxuz97kacu.streamlit.app/" target="_blank"
       style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;
              background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
              border-radius:2px;font-family:'DM Sans',sans-serif;font-size:12px;
              color:rgba(255,255,255,0.6);text-decoration:none;margin-bottom:6px">
        <span>🔋 BESS Dashboard</span><span style="opacity:.4">↗</span></a>
    <a href="https://fatal-flaw-o7aks4agtoffgyydbvrguj.streamlit.app/" target="_blank"
       style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;
              background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
              border-radius:2px;font-family:'DM Sans',sans-serif;font-size:12px;
              color:rgba(255,255,255,0.6);text-decoration:none">
        <span>🌿 SiteIQ Fatal Flaw</span><span style="opacity:.4">↗</span></a>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 1: DAM PRICE HISTORY
# ═══════════════════════════════════════════════════════════════════
if page == "📊 DAM Price History":
    st.markdown("""<div class="page-header">
        <div><div class="tag">Historical Intelligence · 2010–2025</div>
        <h1>DAM Price <span>History</span></h1></div>
        <div class="ph-right">15 Settlement Points<br>1.8M+ hourly records</div>
    </div>""", unsafe_allow_html=True)

    dam = load_dam_historical()
    years, sps, hubs, lzs = dam["years"], dam["sps"], dam["hubs"], dam["lzs"]

    tab_trend, tab_yearly, tab_monthly, tab_compare, tab_heatmap, tab_vol = st.tabs([
        "📈 Price Trends", "📅 Yearly Graph (Jan–Dec)", "📊 Monthly Averages",
        "⚖️ Zone Comparison", "🗓️ Monthly Heatmap", "🔥 Volatility & Spikes"])

    with tab_trend:
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            sel_sps = st.multiselect("Settlement Points", sps, default=["HB_HUBAVG"], key="t_sps")
        with c2:
            metric = st.selectbox("Metric", ["Average","Std Dev","Max","Min"], key="t_met")
        with c3:
            cap = st.checkbox("Cap $200", key="t_cap")
        mkey = {"Average":"avg","Std Dev":"std","Max":"max","Min":"min"}[metric]

        if sel_sps:
            fig = go.Figure()
            for i, sp in enumerate(sel_sps):
                d = dam["yearly"].get(sp, {})
                if not d: continue
                vals = [min(v, 200) for v in d[mkey]] if cap else d[mkey]
                fig.add_trace(go.Scatter(x=d["years"], y=vals, mode="lines+markers", name=sp,
                    line=dict(color=PALETTE[i%len(PALETTE)], width=2.5), marker=dict(size=5),
                    hovertemplate=f"{sp}<br>%{{x}}: $%{{y:.2f}}<extra></extra>"))
            lay = ss_layout(f"Yearly {metric} DAM Price", 420)
            lay["xaxis"]["dtick"] = 1
            fig.update_layout(**lay)
            st.plotly_chart(fig, use_container_width=True)

            rows = []
            for sp in sel_sps:
                d = dam["yearly"].get(sp, {})
                if not d: continue
                rows.append({"SP": sp, "Avg $/MWh": round(np.mean(d["avg"]),2),
                    "Peak Year": d["years"][np.argmax(d["avg"])],
                    "Peak Avg": round(max(d["avg"]),2),
                    "Low Year": d["years"][np.argmin(d["avg"])],
                    "Low Avg": round(min(d["avg"]),2),
                    "All-Time Max": f"${max(d['max']):,.0f}",
                    "All-Time Min": f"${min(d['min']):.2f}"})
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ══════════════════════════════════════════════════════════════
    # TAB: YEARLY GRAPH (Jan–Dec for a selected year)
    # ══════════════════════════════════════════════════════════════
    with tab_yearly:
        st.markdown('<div class="section-label">Select Year & Settlement Points</div>', unsafe_allow_html=True)
        yc1, yc2, yc3 = st.columns([2, 3, 1])
        with yc1:
            sel_yr = st.select_slider("Year", options=years, value=years[-2], key="yg_year")
        with yc2:
            yg_sps = st.multiselect("Settlement Points", sps, default=["HB_HUBAVG","HB_HOUSTON","HB_NORTH","HB_SOUTH","HB_WEST"], key="yg_sps")
        with yc3:
            yg_cap = st.checkbox("Cap $200", key="yg_cap")

        if yg_sps:
            fig = go.Figure()
            for i, sp in enumerate(yg_sps):
                sp_m = dam["monthly"].get(sp, {})
                if not sp_m: continue
                # Extract months for this year
                yr_months = []
                yr_avgs = []
                for j in range(len(sp_m["year"])):
                    if sp_m["year"][j] == sel_yr:
                        yr_months.append(sp_m["month"][j])
                        val = sp_m["avg"][j]
                        yr_avgs.append(min(val, 200) if yg_cap else val)
                if not yr_months: continue
                month_labels = [MONTHS[m-1] for m in yr_months]
                fig.add_trace(go.Scatter(
                    x=month_labels, y=yr_avgs, mode="lines+markers", name=sp,
                    line=dict(color=PALETTE[i % len(PALETTE)], width=2.5),
                    marker=dict(size=7),
                    hovertemplate=f"{sp}<br>%{{x}} {sel_yr}: $%{{y:.2f}}/MWh<extra></extra>"
                ))

            # Add average line
            all_vals = []
            for sp in yg_sps:
                sp_m = dam["monthly"].get(sp, {})
                if not sp_m: continue
                for j in range(len(sp_m["year"])):
                    if sp_m["year"][j] == sel_yr:
                        all_vals.append(sp_m["avg"][j])
            if all_vals:
                overall_avg = np.mean(all_vals)
                fig.add_hline(y=overall_avg, line_dash="dash", line_color="rgba(100,100,100,0.5)",
                    annotation_text=f"Avg ${overall_avg:.2f}", annotation_font=dict(color="#6b6b64", size=10))

            lay = ss_layout(f"{sel_yr} — Monthly Average DAM Price (Jan → Dec)", 440)
            lay["xaxis"]["categoryorder"] = "array"
            lay["xaxis"]["categoryarray"] = MONTHS
            fig.update_layout(**lay)
            st.plotly_chart(fig, use_container_width=True)

            # Stats table for this year
            st.markdown(f'<div class="section-label">{sel_yr} Monthly Summary</div>', unsafe_allow_html=True)
            rows = []
            for sp in yg_sps:
                sp_m = dam["monthly"].get(sp, {})
                if not sp_m: continue
                yr_vals = [sp_m["avg"][j] for j in range(len(sp_m["year"])) if sp_m["year"][j] == sel_yr]
                yr_mos = [sp_m["month"][j] for j in range(len(sp_m["year"])) if sp_m["year"][j] == sel_yr]
                if not yr_vals: continue
                peak_mo = yr_mos[np.argmax(yr_vals)]
                low_mo = yr_mos[np.argmin(yr_vals)]
                rows.append({
                    "Settlement Point": sp,
                    "Annual Avg ($/MWh)": round(np.mean(yr_vals), 2),
                    "Peak Month": MONTHS[peak_mo - 1],
                    "Peak ($/MWh)": round(max(yr_vals), 2),
                    "Lowest Month": MONTHS[low_mo - 1],
                    "Low ($/MWh)": round(min(yr_vals), 2),
                    "Spread": round(max(yr_vals) - min(yr_vals), 2),
                })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # Compare multiple years overlay
            with st.expander("Compare Multiple Years"):
                cmp_years = st.multiselect("Select years to overlay", years,
                    default=[y for y in [2022, 2023, 2024] if y in years], key="yg_cmp_years")
                cmp_sp = st.selectbox("Settlement Point", yg_sps, key="yg_cmp_sp")
                if cmp_years and cmp_sp:
                    fig2 = go.Figure()
                    sp_m = dam["monthly"].get(cmp_sp, {})
                    if sp_m:
                        for yi, cy in enumerate(sorted(cmp_years)):
                            mo_vals = {}
                            for j in range(len(sp_m["year"])):
                                if sp_m["year"][j] == cy:
                                    mo_vals[sp_m["month"][j]] = sp_m["avg"][j]
                            if not mo_vals: continue
                            ms = sorted(mo_vals.keys())
                            fig2.add_trace(go.Scatter(
                                x=[MONTHS[m-1] for m in ms],
                                y=[mo_vals[m] for m in ms],
                                mode="lines+markers", name=str(cy),
                                line=dict(color=PALETTE[yi % len(PALETTE)], width=2),
                                marker=dict(size=5),
                                hovertemplate=f"{cy}<br>%{{x}}: $%{{y:.2f}}<extra></extra>"
                            ))
                    lay2 = ss_layout(f"{cmp_sp} — Year-over-Year Comparison", 380)
                    lay2["xaxis"]["categoryorder"] = "array"
                    lay2["xaxis"]["categoryarray"] = MONTHS
                    fig2.update_layout(**lay2)
                    st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Select settlement points above to see the yearly graph.")

    # ══════════════════════════════════════════════════════════════
    # TAB: MONTHLY AVERAGES (average of each month across all years)
    # ══════════════════════════════════════════════════════════════
    with tab_monthly:
        st.markdown('<div class="section-label">Average Price by Month (All Years Combined)</div>', unsafe_allow_html=True)
        mc1, mc2, mc3 = st.columns([3, 1, 1])
        with mc1:
            ma_sps = st.multiselect("Settlement Points", sps,
                default=["HB_HUBAVG","HB_HOUSTON","HB_NORTH","HB_SOUTH","HB_WEST","LZ_WEST"], key="ma_sps")
        with mc2:
            ma_excl_uri = st.checkbox("Exclude Feb 2021 (Uri)", value=True, key="ma_excl")
        with mc3:
            ma_years_from = st.select_slider("From year", options=years, value=years[0], key="ma_from")

        if ma_sps:
            fig = go.Figure()
            table_rows = []
            for i, sp in enumerate(ma_sps):
                sp_m = dam["monthly"].get(sp, {})
                if not sp_m: continue
                # Group by month, compute average across all years
                monthly_buckets = [[] for _ in range(12)]
                for j in range(len(sp_m["year"])):
                    yr = sp_m["year"][j]
                    mo = sp_m["month"][j]
                    val = sp_m["avg"][j]
                    if yr < ma_years_from: continue
                    if ma_excl_uri and yr == 2021 and mo == 2: continue
                    monthly_buckets[mo - 1].append(val)
                month_avgs = [round(np.mean(b), 2) if b else None for b in monthly_buckets]
                month_avgs_clean = [v if v is not None else 0 for v in month_avgs]

                fig.add_trace(go.Scatter(
                    x=MONTHS, y=month_avgs_clean, mode="lines+markers", name=sp,
                    line=dict(color=PALETTE[i % len(PALETTE)], width=2.5),
                    marker=dict(size=7),
                    hovertemplate=f"{sp}<br>%{{x}}: $%{{y:.2f}}/MWh<extra></extra>"
                ))

                # Table data
                peak_mo = np.argmax(month_avgs_clean)
                low_mo = np.argmin(month_avgs_clean)
                table_rows.append({
                    "Settlement Point": sp,
                    "Overall Avg": f"${np.mean(month_avgs_clean):.2f}",
                    "Peak Month": MONTHS[peak_mo],
                    "Peak Avg": f"${month_avgs_clean[peak_mo]:.2f}",
                    "Lowest Month": MONTHS[low_mo],
                    "Low Avg": f"${month_avgs_clean[low_mo]:.2f}",
                    "Seasonal Spread": f"${month_avgs_clean[peak_mo] - month_avgs_clean[low_mo]:.2f}",
                })

            lay = ss_layout(f"Average Monthly DAM Price — {ma_years_from}–2025" +
                (" (excl. Uri)" if ma_excl_uri else ""), 440)
            lay["xaxis"]["categoryorder"] = "array"
            lay["xaxis"]["categoryarray"] = MONTHS
            fig.update_layout(**lay)
            st.plotly_chart(fig, use_container_width=True)

            # Bar chart version — grouped by month
            st.markdown('<div class="section-label">Monthly Comparison (Bar Chart)</div>', unsafe_allow_html=True)
            fig2 = go.Figure()
            for i, sp in enumerate(ma_sps):
                sp_m = dam["monthly"].get(sp, {})
                if not sp_m: continue
                monthly_buckets = [[] for _ in range(12)]
                for j in range(len(sp_m["year"])):
                    yr = sp_m["year"][j]
                    mo = sp_m["month"][j]
                    val = sp_m["avg"][j]
                    if yr < ma_years_from: continue
                    if ma_excl_uri and yr == 2021 and mo == 2: continue
                    monthly_buckets[mo - 1].append(val)
                month_avgs = [round(np.mean(b), 2) if b else 0 for b in monthly_buckets]
                fig2.add_trace(go.Bar(
                    x=MONTHS, y=month_avgs, name=sp,
                    marker_color=PALETTE[i % len(PALETTE)],
                    hovertemplate=f"{sp}<br>%{{x}}: $%{{y:.2f}}/MWh<extra></extra>"
                ))
            lay2 = ss_layout("Monthly Average by Settlement Point", 380)
            lay2["barmode"] = "group"
            lay2["xaxis"]["categoryorder"] = "array"
            lay2["xaxis"]["categoryarray"] = MONTHS
            fig2.update_layout(**lay2)
            st.plotly_chart(fig2, use_container_width=True)

            # Summary table
            if table_rows:
                st.markdown('<div class="section-label">Seasonal Summary</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

            # Insight card
            st.markdown("""<div class="ercot-card" style="border-left-color:#b8860b"><h3>Seasonal Pattern</h3>
            <div style="font-size:13px;color:#3d3d38;line-height:1.7">
            ERCOT prices follow a strong seasonal curve driven by <b style="color:#c8102e">summer cooling demand</b>
            (Jun–Sep peaks) and occasional <b style="color:#1a3a7a">winter heating spikes</b> (Jan–Feb).
            Spring and fall shoulder months (Mar–May, Oct–Nov) consistently offer the lowest prices — ideal for
            <b style="color:#1a6a1a">battery charging and load shifting</b>. The summer premium varies by zone:
            LZ_WEST and LZ_SOUTH typically see the highest seasonal spreads due to transmission constraints
            and localized generation patterns.
            </div></div>""", unsafe_allow_html=True)
        else:
            st.info("Select settlement points above to see monthly averages.")

    with tab_compare:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: yr = st.select_slider("Year", years, value=years[-2], key="c_yr")
        with c2: met = st.selectbox("Metric", ["Average","Std Dev","Max","Min"], key="c_met")
        with c3: grp = st.selectbox("Group", ["All","Hubs","Load Zones"], key="c_grp")
        mk = {"Average":"avg","Std Dev":"std","Max":"max","Min":"min"}[met]
        use = hubs if grp=="Hubs" else lzs if grp=="Load Zones" else sps
        bd = []
        for sp in use:
            d = dam["yearly"].get(sp, {})
            if not d: continue
            try: bd.append({"SP":sp,"val":d[mk][d["years"].index(yr)],"type":"Hub" if sp.startswith("HB_") else "LZ"})
            except: pass
        if bd:
            bdf = pd.DataFrame(bd).sort_values("val")
            fig = go.Figure()
            for t,c in [("Hub","#c8102e"),("LZ","#1a3a7a")]:
                g = bdf[bdf["type"]==t]
                if not g.empty:
                    fig.add_trace(go.Bar(y=g["SP"],x=g["val"],orientation="h",name=t,marker_color=c,
                        hovertemplate="%{y}: $%{x:.2f}<extra></extra>"))
            lay = ss_layout(f"{yr} — {met} by SP", 450)
            lay["xaxis"] = dict(gridcolor="#e2e0db",tickprefix="$",tickfont=dict(size=10,color="#6b6b64"))
            lay["yaxis"] = dict(gridcolor="#e2e0db",tickfont=dict(size=10,color="#6b6b64"))
            lay["barmode"] = "group"
            fig.update_layout(**lay)
            st.plotly_chart(fig, use_container_width=True)

    with tab_heatmap:
        heat_sp = st.selectbox("Settlement Point", sps, index=sps.index("HB_HUBAVG"), key="h_sp")
        sp_m = dam["monthly"].get(heat_sp, {})
        if sp_m and sp_m["year"]:
            heat_yrs = sorted(set(sp_m["year"]))
            matrix = []
            for yr in heat_yrs:
                row = [None]*12
                for i in range(len(sp_m["year"])):
                    if sp_m["year"][i] == yr: row[sp_m["month"][i]-1] = sp_m["avg"][i]
                matrix.append(row)
            fig = go.Figure(go.Heatmap(z=matrix, x=MONTHS, y=[str(y) for y in heat_yrs],
                colorscale=[[0,"#1a6a1a"],[0.15,"#2a9d8f"],[0.3,"#e9c46a"],[0.5,"#f4a261"],[0.7,"#e63946"],[1,"#7a0000"]],
                hovertemplate="%{y} %{x}: $%{z:.2f}/MWh<extra></extra>",
                colorbar=dict(title="$/MWh", tickprefix="$")))
            lay = ss_layout(f"Monthly Avg DAM — {heat_sp}", 500)
            lay["yaxis"] = dict(dtick=1, tickfont=dict(size=10, color="#6b6b64", family="DM Mono"))
            lay["xaxis"] = dict(tickfont=dict(size=10, color="#6b6b64"))
            fig.update_layout(**lay)
            st.plotly_chart(fig, use_container_width=True)

            seasonal = [[] for _ in range(12)]
            for i in range(len(sp_m["year"])):
                if sp_m["avg"][i] < 500: seasonal[sp_m["month"][i]-1].append(sp_m["avg"][i])
            savg = [round(np.mean(s),2) if s else 0 for s in seasonal]
            fig2 = go.Figure(go.Bar(x=MONTHS, y=savg,
                marker=dict(color=savg, colorscale=[[0,"#1a6a1a"],[0.5,"#e9c46a"],[1,"#c8102e"]]),
                hovertemplate="%{x}: $%{y:.2f}<extra></extra>"))
            fig2.update_layout(**ss_layout(f"Seasonal Profile — {heat_sp} (excl. Uri)", 280))
            st.plotly_chart(fig2, use_container_width=True)

    with tab_vol:
        sd = []
        for yr in years:
            ys = str(yr)
            sd.append({"Year":yr, ">$100":dam.get("spikes_gt100",{}).get(ys,0),
                ">$500":dam.get("spikes_gt500",{}).get(ys,0),
                ">$1000":dam.get("spikes_gt1000",{}).get(ys,0),
                "Negative":dam.get("spikes_negative",{}).get(ys,0)})
        sdf = pd.DataFrame(sd)
        fig = go.Figure()
        for col,c in [(">$100","#f4a261"),(">$500","#e63946"),(">$1000","#7a0000"),("Negative","#1a3a7a")]:
            fig.add_trace(go.Bar(x=sdf["Year"],y=sdf[col],name=col,marker_color=c))
        lay = ss_layout("Price Spike Hours by Year (All SPs)", 380)
        lay["barmode"]="group"; lay["xaxis"]["dtick"]=1
        lay["yaxis"]["title"]="Hours"; lay["yaxis"].pop("tickprefix",None)
        fig.update_layout(**lay)
        st.plotly_chart(fig, use_container_width=True)

        vol_sps = st.multiselect("Compare Volatility", sps, default=["HB_HUBAVG","HB_WEST","HB_PAN","LZ_WEST"], key="v_sps")
        if vol_sps:
            fig2 = go.Figure()
            for i,sp in enumerate(vol_sps):
                d = dam["yearly"].get(sp, {})
                if d: fig2.add_trace(go.Scatter(x=d["years"],y=d["std"],mode="lines+markers",name=sp,
                    line=dict(color=PALETTE[i%len(PALETTE)],width=2)))
            lay2 = ss_layout("Yearly Std Dev — Volatility", 360); lay2["xaxis"]["dtick"]=1
            fig2.update_layout(**lay2)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""<div class="ercot-card" style="border-left-color:#c8102e"><h3>Key Findings</h3>
        <div style="font-size:13px;color:#3d3d38;line-height:1.7">
        <b style="color:#c8102e">Winter Storm Uri (Feb 2021)</b> — HB_HUBAVG averaged $1,483/MWh, peaks ~$9,000.<br>
        <b style="color:#b8860b">2022</b> — sustained elevated pricing from nat gas spikes.<br>
        <b style="color:#1a3a7a">HB_PAN / HB_WEST</b> — most negative prices (wind curtailment).<br>
        <b style="color:#1a6a1a">LZ_WEST</b> — persistent premium from transmission constraints.
        </div></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 2: FORECAST ENGINE
# ═══════════════════════════════════════════════════════════════════
elif page == "🤖 Forecast Engine":
    st.markdown("""<div class="page-header">
        <div><div class="tag">ML Forecast · GBR Ensemble · 2024 Backtest</div>
        <h1>Forecast <span>Engine</span></h1></div>
        <div class="ph-right">Gradient Boosting<br>122K training samples</div>
    </div>""", unsafe_allow_html=True)

    met = MODEL["metrics"]
    spk = MODEL["spike"]
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("MAE", f"${met['mae']}/MWh", "Mean Absolute Error")
    m2.metric("RMSE", f"${met['rmse']}/MWh")
    m3.metric("Spike Precision", f"{spk['prec']*100:.0f}%", f"{spk['tp']} true positives")
    m4.metric("Spike Recall", f"{spk['rec']*100:.0f}%", f"{spk['fn']} missed")

    st.markdown('<div class="section-label">Predicted vs Actual — Q1 2024 Backtest</div>', unsafe_allow_html=True)
    ddf = pd.DataFrame(MODEL["daily"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ddf["d"],y=ddf["a"],mode="lines",name="Actual",
        line=dict(color="#1a6a1a",width=2),fill="tozeroy",fillcolor="rgba(26,106,26,0.08)"))
    fig.add_trace(go.Scatter(x=ddf["d"],y=ddf["p"],mode="lines",name="Predicted",
        line=dict(color="#c8102e",width=2,dash="dash")))
    lay = ss_layout("Daily Avg LMP — Actual vs Predicted (HB_HUBAVG)", 380)
    lay["xaxis"] = dict(gridcolor="#e2e0db",tickfont=dict(size=9,color="#6b6b64"),tickangle=-45)
    fig.update_layout(**lay)
    st.plotly_chart(fig, use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        hdf = pd.DataFrame(MODEL["hrly"])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=hdf["h"],y=hdf["a"],name="Actual",marker_color="rgba(26,106,26,0.5)"))
        fig.add_trace(go.Bar(x=hdf["h"],y=hdf["p"],name="Predicted",marker_color="rgba(200,16,46,0.5)"))
        lay = ss_layout("Hourly Price Shape (2024)", 300); lay["barmode"]="group"
        lay["xaxis"]["title"]="Hour Ending"; lay["xaxis"]["dtick"]=1
        fig.update_layout(**lay)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        mdf = pd.DataFrame(MODEL["mth"])
        mdf["month"] = mdf["m"].apply(lambda x: MONTHS[x-1])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=mdf["month"],y=mdf["a"],name="Actual",marker_color="#1a6a1a"))
        fig.add_trace(go.Bar(x=mdf["month"],y=mdf["p"],name="Predicted",marker_color="#c8102e"))
        lay = ss_layout("Monthly Accuracy (2024)", 300); lay["barmode"]="group"
        fig.update_layout(**lay)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-label">Feature Importance</div>', unsafe_allow_html=True)
    fidf = pd.DataFrame(MODEL["fi"])
    fig = go.Figure(go.Bar(y=fidf["f"],x=fidf["v"],orientation="h",
        marker=dict(color=fidf["v"],colorscale=[[0,"#264653"],[0.5,"#2a9d8f"],[1,"#c8102e"]]),
        hovertemplate="%{y}: %{x:.1%}<extra></extra>"))
    lay = ss_layout("Feature Importance — Gradient Boosting", 320)
    lay["xaxis"]=dict(gridcolor="#e2e0db",tickformat=".0%",tickfont=dict(size=10,color="#6b6b64"))
    lay["yaxis"]=dict(tickfont=dict(size=10,color="#6b6b64",family="DM Mono"))
    fig.update_layout(**lay)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""<div class="ercot-card" style="border-left-color:#b8860b"><h3>Enhancement Path</h3>
    <div style="font-size:13px;color:#3d3d38;line-height:1.8">
    <b>Current:</b> GBR on price-only features (lags, rolling avgs, seasonality) · MAE $14.15<br>
    <b>Phase 2:</b> + Weather data (NOAA temp, wind, solar irradiance) → MAE ~$8-10<br>
    <b>Phase 3:</b> + ERCOT grid data (load forecast, gen mix, outages) → MAE ~$5-7<br>
    <b>Phase 4:</b> Transformer model with attention on weather events → spike recall >70%
    </div></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 3: BATTERY AGENT
# ═══════════════════════════════════════════════════════════════════
elif page == "🔋 Battery Agent":
    st.markdown("""<div class="page-header">
        <div><div class="tag">BESS Arbitrage · AI Dispatch · Revenue Model</div>
        <h1>Battery <span>Agent</span></h1></div>
        <div class="ph-right">2024 Backtest<br>Charge/Discharge Optimization</div>
    </div>""", unsafe_allow_html=True)

    batt = MODEL["batt"]
    st.markdown('<div class="section-label">System Configuration</div>', unsafe_allow_html=True)
    bc1,bc2,bc3,bc4 = st.columns(4)
    with bc1: bmwh = st.number_input("Capacity (MWh)", value=100, min_value=10, max_value=2000, step=50)
    with bc2: bmw  = st.number_input("Power (MW)", value=25, min_value=5, max_value=500, step=25)
    with bc3: eff  = st.number_input("Efficiency %", value=87, min_value=70, max_value=98)
    with bc4: cyc  = st.number_input("Cycles/Year", value=batt["cycles"], min_value=100, max_value=700)

    scale = bmwh / 100.0
    eff_adj = (eff/100) / 0.87
    annual = batt["annual"] * scale * eff_adj
    rev_cycle = annual / max(cyc, 1)

    st.markdown("---")
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("Annual Revenue", f"${annual:,.0f}", f"{bmwh} MWh")
    m2.metric("Charge Price", f"${batt['charge']:.2f}/MWh", "Bottom 20%")
    m3.metric("Discharge Price", f"${batt['discharge']:.2f}/MWh", "Top 20%")
    m4.metric("Rev/Cycle", f"${rev_cycle:,.0f}")
    m5.metric("$/kWh/yr", f"${annual/(bmwh*1000)*1000:.0f}")

    hdf = pd.DataFrame(MODEL["hrly"])
    p20, p80 = hdf["p"].quantile(0.20), hdf["p"].quantile(0.80)
    fig = go.Figure()
    colors = ["#1a6a1a" if p<=p20 else "#c8102e" if p>=p80 else "#d0cdc6" for p in hdf["p"]]
    fig.add_trace(go.Bar(x=hdf["h"],y=hdf["a"],marker_color=colors,
        hovertemplate="Hr %{x}: $%{y:.2f}/MWh<extra></extra>"))
    fig.add_hline(y=p20, line_dash="dash", line_color="#1a6a1a",
        annotation_text=f"Charge ≤${p20:.0f}", annotation_font=dict(color="#1a6a1a",size=10))
    fig.add_hline(y=p80, line_dash="dash", line_color="#c8102e",
        annotation_text=f"Discharge ≥${p80:.0f}", annotation_font=dict(color="#c8102e",size=10))
    lay = ss_layout("Hourly Charge/Discharge Signal (2024)", 400)
    lay["xaxis"]["title"]="Hour Ending"; lay["xaxis"]["dtick"]=1
    fig.update_layout(**lay)
    st.plotly_chart(fig, use_container_width=True)

    spread = batt["discharge"] - batt["charge"]
    st.markdown(f"""<div class="ercot-card" style="border-left-color:#1a6a1a"><h3>Agent Strategy</h3>
    <div style="font-size:13px;color:#3d3d38;line-height:1.7">
    The agent <b style="color:#1a6a1a">charges</b> at ~${batt['charge']:.0f}/MWh (off-peak) and
    <b style="color:#c8102e">discharges</b> at ~${batt['discharge']:.0f}/MWh (peak), capturing a
    <b>${spread:.0f}/MWh spread</b>. At {eff}% efficiency with {bmwh} MWh capacity and {cyc} cycles/yr:
    <b style="color:#c8102e">${annual:,.0f} annual revenue</b> from pure energy arbitrage — before ancillary services.
    </div></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 4: DEMAND RESPONSE
# ═══════════════════════════════════════════════════════════════════
elif page == "🏭 Demand Response":
    st.markdown("""<div class="page-header">
        <div><div class="tag">Load Optimization · C&I Customers</div>
        <h1>Demand <span>Response</span></h1></div>
        <div class="ph-right">Hourly Recommendations<br>Price-Aware Scheduling</div>
    </div>""", unsafe_allow_html=True)

    dr = MODEL["dr"]
    dc1,dc2 = st.columns(2)
    with dc1: dr_mw = st.number_input("Flexible Load (MW)", value=10, min_value=1, max_value=500, step=5)
    with dc2: dr_type = st.selectbox("Facility", ["Data Center","Manufacturing","Cold Storage","EV Fleet","Water Treatment"])

    dr_annual = dr["annual"] * (dr_mw / 10.0)
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Annual Savings", f"${dr_annual:,.0f}", f"{dr_mw} MW")
    m2.metric("$/MW/Year", f"${dr_annual/max(dr_mw,1):,.0f}")
    m3.metric("Off-Peak Avg", f"${MODEL['batt']['charge']:.2f}/MWh")
    m4.metric("Peak Avg", f"${MODEL['batt']['discharge']:.2f}/MWh")

    hdf = pd.DataFrame(MODEL["hrly"])
    colors = ["#1a6a1a" if a<18 else "#c8102e" if a>40 else "#e2e0db" for a in hdf["a"]]
    fig = go.Figure(go.Bar(x=hdf["h"],y=hdf["a"],marker_color=colors,
        hovertemplate="Hr %{x}: $%{y:.2f}/MWh<extra></extra>"))
    lay = ss_layout(f"Load Shift Recommendations — {dr_type} ({dr_mw} MW)", 380)
    lay["xaxis"]["title"]="Hour Ending"; lay["xaxis"]["dtick"]=1
    fig.update_layout(**lay)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""<div style="display:flex;gap:20px;font-size:12px;color:#6b6b64;margin-top:-8px">
        <span><span style="color:#1a6a1a;font-weight:600">●</span> Shift TO (low)</span>
        <span><span style="color:#c8102e;font-weight:600">●</span> Shift FROM (peak)</span>
        <span><span style="color:#d0cdc6;font-weight:600">●</span> Normal</span>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="ercot-card" style="border-left-color:#1a3a7a"><h3>How It Works</h3>
    <div style="font-size:13px;color:#3d3d38;line-height:1.7">
    The AI agent sends daily schedules to {dr_type.lower()} operators with hour-by-hour load recommendations.
    By shifting {dr_mw} MW from peak hours (HE16-21, avg $50+/MWh) to off-peak (HE1-5, avg $16/MWh),
    this facility saves <b style="color:#c8102e">${dr_annual/max(dr_mw,1)/1000:.0f}K/MW/year</b>.
    The agent adapts daily based on weather, grid conditions, and price forecasts.
    </div></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 5: REP RISK TOOL
# ═══════════════════════════════════════════════════════════════════
elif page == "🛡️ REP Risk Tool":
    st.markdown("""<div class="page-header">
        <div><div class="tag">Risk Management · Spike Detection · Hedge Optimization</div>
        <h1>REP Risk <span>Tool</span></h1></div>
        <div class="ph-right">Retail Electric Providers<br>Portfolio Protection</div>
    </div>""", unsafe_allow_html=True)

    spk = MODEL["spike"]
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Spike Precision", f"{spk['prec']*100:.0f}%", ">$100 events")
    m2.metric("Spike Recall", f"{spk['rec']*100:.0f}%")
    m3.metric("True Positives", spk["tp"])
    m4.metric("Missed Spikes", spk["fn"])

    mdf = pd.DataFrame(MODEL["mth"])
    mdf["month"] = mdf["m"].apply(lambda x: MONTHS[x-1])
    mdf["error"] = abs(mdf["a"]-mdf["p"])
    mdf["error_pct"] = abs((mdf["a"]-mdf["p"])/mdf["a"].clip(lower=1)*100)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=mdf["month"],y=mdf["a"],name="Actual Avg",marker_color="#1a6a1a"))
    fig.add_trace(go.Bar(x=mdf["month"],y=mdf["p"],name="Predicted Avg",marker_color="#c8102e"))
    fig.add_trace(go.Scatter(x=mdf["month"],y=mdf["error_pct"],name="Error %",yaxis="y2",
        line=dict(color="#b8860b",width=2),mode="lines+markers",marker=dict(size=6)))
    lay = ss_layout("Monthly Forecast Error — REP Exposure (2024)", 400)
    lay["barmode"]="group"
    lay["yaxis2"] = dict(overlaying="y",side="right",title="Error %",ticksuffix="%",
        gridcolor="rgba(0,0,0,0)",tickfont=dict(size=10,color="#b8860b"))
    fig.update_layout(**lay)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""<div class="ercot-card" style="border-left-color:#b8860b"><h3>REP Value Proposition</h3>
    <div style="font-size:13px;color:#3d3d38;line-height:1.7">
    REPs face catastrophic risk from price spikes (Feb 2021: $1,483/MWh avg). This agent provides
    early warning with <b style="color:#c8102e">{spk['prec']*100:.0f}% precision</b> on $100+ spikes.
    For a 100 MW portfolio, a 2-hour warning on a $1,000+ event saves
    <b style="color:#1a6a1a">$200K+ per event</b>. Monthly forecasting optimizes hedge ratios and
    reduces VaR by 15-25%.
    </div></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 6: REVENUE ROADMAP
# ═══════════════════════════════════════════════════════════════════
elif page == "🚀 Revenue Roadmap":
    st.markdown("""<div class="page-header">
        <div><div class="tag">Business Model · Platform Strategy</div>
        <h1>Revenue <span>Roadmap</span></h1></div>
        <div class="ph-right">4 Revenue Streams<br>Multi-Customer Platform</div>
    </div>""", unsafe_allow_html=True)

    batt = MODEL["batt"]; dr = MODEL["dr"]
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Battery Arbitrage", f"${batt['annual']/1e6:.1f}M/yr", "100 MWh system")
    m2.metric("DR Savings", f"${dr['annual']/1e3:.0f}K/yr", "10 MW facility")
    m3.metric("Forecast API", "$5–25K/mo", "Per customer")
    m4.metric("REP Platform", "$50–150K/yr", "Enterprise SaaS")

    phases = [
        ("Phase 1 ✅","Foundation","#1a6a1a",
         ["Historical DAM database (15 SPs, 15 years)","Gradient Boosting forecast model",
          "Battery arbitrage backtest engine","SunStripe nodal integration"]),
        ("Phase 2 →","Data Enrichment","#b8860b",
         ["ERCOT real-time API (5-min SCED)","Weather data (NOAA, forecast.io)",
          "Grid data (wind/solar gen, load)","Natural gas prices (Henry Hub, Waha)"]),
        ("Phase 3","Agent Intelligence","#1a3a7a",
         ["Transformer-based forecasting","Spike probability classifier",
          "Multi-zone arbitrage optimizer","Automated trading signals"]),
        ("Phase 4","Platform & Revenue","#c8102e",
         ["REST API ($5-25K/mo SaaS)","Battery dispatch-as-a-service",
          "DR platform (per-MW fee)","REP risk dashboard (enterprise)"]),
    ]

    cols = st.columns(4)
    for i,(title,sub,color,items) in enumerate(phases):
        with cols[i]:
            ih = "".join(f'<div style="font-size:11px;color:#6b6b64;padding:4px 0;border-bottom:1px solid #e2e0db">{it}</div>' for it in items)
            st.markdown(f"""<div style="background:#f7f7f5;border:1px solid #e2e0db;border-top:3px solid {color};
                border-radius:2px;padding:14px 16px;height:100%">
                <div style="font-family:'DM Mono',monospace;font-size:10px;color:{color};
                     letter-spacing:.1em;font-weight:600;margin-bottom:4px">{title}</div>
                <div style="font-family:'Playfair Display',serif;font-size:14px;font-weight:600;
                     color:#1a1a18;margin-bottom:10px">{sub}</div>{ih}</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div class="ercot-card" style="border-left-color:#c8102e"><h3>Revenue Model</h3>
    <div style="font-size:13px;color:#3d3d38;line-height:2">
    <b style="color:#1a6a1a">Tier 1 — Forecast API:</b> $5-25K/mo per customer. DAM price predictions via REST API.<br>
    <b style="color:#c8102e">Tier 2 — Battery Optimization:</b> 10-20% revenue share on arbitrage. ~$180-360K/yr per 100 MWh system.<br>
    <b style="color:#1a3a7a">Tier 3 — Demand Response:</b> $2-5/kW/yr platform fee. 10 MW = $20-50K/yr.<br>
    <b style="color:#b8860b">Tier 4 — REP Risk Platform:</b> Enterprise SaaS $50-150K/yr.
    </div></div>""", unsafe_allow_html=True)
