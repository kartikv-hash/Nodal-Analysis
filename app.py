import streamlit as st
import pandas as pd

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
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0e14 !important;
    font-family: 'IBM Plex Sans', sans-serif;
    color: #e8f0f8;
}
[data-testid="stSidebar"] { background-color: #111720 !important; border-right: 1px solid #1e2d42; }
[data-testid="stSidebar"] * { color: #e8f0f8 !important; }

.page-header { border-bottom: 1px solid #1e2d42; padding-bottom: 16px; margin-bottom: 20px; }
.page-header .tag { font-family:'IBM Plex Mono',monospace; font-size:10px; color:#00d4ff; letter-spacing:.2em; text-transform:uppercase; margin-bottom:4px; }
.page-header h1 { font-family:'IBM Plex Mono',monospace; font-size:22px; font-weight:600; color:#e8f0f8; margin:0; }
.page-header h1 span { color:#00d4ff; }

.section-label {
    font-family:'IBM Plex Mono',monospace; font-size:10px; color:#3a5070;
    letter-spacing:.2em; text-transform:uppercase; margin:18px 0 10px;
    display:flex; align-items:center; gap:8px;
}
.section-label::after { content:''; flex:1; height:1px; background:#1e2d42; }

.step-badge {
    display:inline-flex; align-items:center; justify-content:center;
    width:20px; height:20px; border-radius:50%;
    background:#00d4ff; color:#000;
    font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:700;
}

.detail-card {
    background:#111720; border:1px solid rgba(0,212,255,0.2);
    border-left:3px solid #00d4ff; border-radius:6px; padding:16px 20px; margin-bottom:14px;
}
.detail-card h3 { font-family:'IBM Plex Mono',monospace; font-size:14px; font-weight:600; color:#ff6b35; margin:0 0 12px; }
.dg { display:flex; flex-wrap:wrap; gap:14px; margin-bottom:10px; }
.di .dl { font-family:'IBM Plex Mono',monospace; font-size:9px; color:#3a5070; letter-spacing:.15em; text-transform:uppercase; }
.di .dv { font-family:'IBM Plex Mono',monospace; font-size:12px; font-weight:500; color:#e8f0f8; margin-top:2px; }

.tag-row { display:flex; flex-wrap:wrap; gap:5px; margin-top:5px; }
.tag-bus { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:500; background:rgba(0,212,255,0.08); border:1px solid rgba(0,212,255,0.25); color:#00d4ff; }
.tag-zone { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; background:rgba(57,211,83,0.08); border:1px solid rgba(57,211,83,0.25); color:#39d353; }
.tag-psse { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; background:rgba(255,107,53,0.08); border:1px solid rgba(255,107,53,0.25); color:#ff6b35; }
.tag-hub  { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; background:rgba(255,204,0,0.08); border:1px solid rgba(255,204,0,0.25); color:#ffcc00; }

.kv { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:600; }
.kv-345 { color:#ff9933; background:rgba(255,153,51,0.1); border:1px solid rgba(255,153,51,0.3); }
.kv-230 { color:#ffcc00; background:rgba(255,204,0,0.1); border:1px solid rgba(255,204,0,0.3); }
.kv-138 { color:#00d4ff; background:rgba(0,212,255,0.1); border:1px solid rgba(0,212,255,0.3); }
.kv-115 { color:#a78bfa; background:rgba(167,139,250,0.1); border:1px solid rgba(167,139,250,0.3); }
.kv-69  { color:#39d353; background:rgba(57,211,83,0.1); border:1px solid rgba(57,211,83,0.3); }
.kv-34  { color:#6b8aaa; background:rgba(107,138,170,0.1); border:1px solid rgba(107,138,170,0.3); }

.stTabs [data-baseweb="tab-list"] { background:transparent; border-bottom:1px solid #1e2d42; }
.stTabs [data-baseweb="tab"] { font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:500; letter-spacing:.08em; text-transform:uppercase; color:#3a5070; background:transparent; padding:10px 18px; }
.stTabs [aria-selected="true"] { color:#00d4ff !important; border-bottom:2px solid #00d4ff !important; }

.stTextInput input, div[data-baseweb="select"] > div {
    background-color:#111720 !important; border-color:#1e2d42 !important;
    color:#e8f0f8 !important; font-family:'IBM Plex Mono',monospace !important;
}
.stDownloadButton button, .stButton button {
    background:transparent !important; border:1px solid #1e2d42 !important; color:#6b8aaa !important;
    font-family:'IBM Plex Mono',monospace !important; font-size:11px !important;
    font-weight:600 !important; letter-spacing:.08em !important; text-transform:uppercase !important; border-radius:4px !important;
}
.stDownloadButton button:hover, .stButton button:hover { border-color:#00d4ff !important; color:#00d4ff !important; }

[data-testid="stMetric"] { background:#111720; border:1px solid #1e2d42; border-radius:6px; padding:12px 16px; }
[data-testid="stMetricLabel"] { font-family:'IBM Plex Mono',monospace !important; font-size:10px !important; color:#3a5070 !important; text-transform:uppercase; letter-spacing:.1em; }
[data-testid="stMetricValue"] { font-family:'IBM Plex Mono',monospace !important; color:#00d4ff !important; font-size:22px !important; }

div[data-testid="stMarkdownContainer"] p { color:#6b8aaa; font-size:13px; }
hr { border-color:#1e2d42 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading ERCOT settlement points...")
def load_data():
    df = pd.read_csv("Settlement_Points_02202026_094122.csv", dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "ELECTRICAL_BUS": "Bus",
        "NODE_NAME": "Node",
        "PSSE_BUS_NAME": "PSSE Name",
        "VOLTAGE_LEVEL": "kV",
        "SUBSTATION": "Substation",
        "SETTLEMENT_LOAD_ZONE": "Zone",
        "RESOURCE_NODE": "Resource Node",
        "HUB_BUS_NAME": "Hub Bus",
        "HUB": "Hub",
        "PSSE_BUS_NUMBER": "PSSE #",
    })
    df["kV_num"] = pd.to_numeric(df["kV"], errors="coerce")
    return df

df = load_data()

TRANS_KV = ["345", "230", "138", "115", "69", "34.5"]

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

def to_csv_bytes(d):
    return d.to_csv(index=False).encode("utf-8")


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:14px 0 16px">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#00d4ff;letter-spacing:.2em;text-transform:uppercase;margin-bottom:5px">⚡ SunStripe · ERCOT</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:15px;font-weight:600;color:#e8f0f8;line-height:1.4">Nodal Analysis<br><span style="color:#00d4ff">Platform</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio("", [
        "⚡ Node & Hub Selector",
        "🔍 Bus Lookup",
        "🏭 Substation Lookup",
        "📋 Browse All",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:.15em;text-transform:uppercase;margin-bottom:10px">Dataset · Feb 2026</div>
    <div style="display:flex;flex-direction:column;gap:9px">
        <div><div style="font-size:17px;font-weight:600;color:#00d4ff">{len(df):,}</div><div style="font-size:10px;color:#3a5070">Settlement Points</div></div>
        <div><div style="font-size:17px;font-weight:600;color:#ff6b35">{df["Substation"].nunique():,}</div><div style="font-size:10px;color:#3a5070">Substations</div></div>
        <div><div style="font-size:17px;font-weight:600;color:#ffcc00">{df[df["Hub"]!=""]["Hub"].nunique()}</div><div style="font-size:10px;color:#3a5070">Hubs</div></div>
        <div><div style="font-size:17px;font-weight:600;color:#39d353">{df[df["Resource Node"]!=""].shape[0]:,}</div><div style="font-size:10px;color:#3a5070">Resource Nodes</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <a href="https://ercot-bess-dashboard-nhh9eztsqeuqxxuz97kacu.streamlit.app/" target="_blank"
       style="display:block;padding:7px 10px;background:#192030;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:#6b8aaa;text-decoration:none;margin-bottom:5px">
        ⚡ ERCOT BESS Dashboard ↗</a>
    <a href="https://fatal-flaw-o7aks4agtoffgyydbvrguj.streamlit.app/" target="_blank"
       style="display:block;padding:7px 10px;background:#192030;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:#6b8aaa;text-decoration:none">
        🌿 SiteIQ Fatal Flaw ↗</a>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# PAGE 1 — Node & Hub Selector
# ═══════════════════════════════════════════════════
if page == "⚡ Node & Hub Selector":

    st.markdown("""
    <div class="page-header">
        <div class="tag">⚡ SunStripe · ERCOT</div>
        <h1>NODE & HUB <span>SELECTOR</span></h1>
    </div>
    <p>Filter by voltage → pick substations → auto-resolve Bus Names, Zones & PSSE numbers → upload DAM LMP data for price analysis.</p>
    """, unsafe_allow_html=True)

    # ── STEP 1: kV ──────────────────────────────────
    st.markdown('<div class="section-label"><span class="step-badge">1</span> Select Voltage Level</div>', unsafe_allow_html=True)

    kv_labels = ["All Trans.", "345 kV", "230 kV", "138 kV", "115 kV", "69 kV", "34.5 kV"]
    kv_values = ["All",        "345",     "230",     "138",     "115",     "69",     "34.5"]

    if "sel_kv" not in st.session_state:
        st.session_state.sel_kv = "138"

    btn_cols = st.columns(len(kv_labels))
    for i, (label, val) in enumerate(zip(kv_labels, kv_values)):
        if btn_cols[i].button(label, key=f"kv_{val}", use_container_width=True):
            st.session_state.sel_kv = val

    sel_kv = st.session_state.sel_kv
    df_kv = df[df["kV"].isin(TRANS_KV)] if sel_kv == "All" else df[df["kV"] == sel_kv]

    kv_display_tag = f'<span class="kv {kv_cls(sel_kv) if sel_kv != "All" else "kv-138"}">{sel_kv} kV</span>' if sel_kv != "All" else '<span class="kv kv-138">All Trans.</span>'
    st.markdown(f"""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#3a5070;margin:8px 0 4px">
        {kv_display_tag} &nbsp;→&nbsp;
        <span style="color:#e8f0f8">{len(df_kv):,}</span> settlement points &nbsp;|&nbsp;
        <span style="color:#e8f0f8">{df_kv["Substation"].nunique():,}</span> substations
    </div>
    """, unsafe_allow_html=True)

    # ── STEP 2: Substation ──────────────────────────
    st.markdown('<div class="section-label"><span class="step-badge">2</span> Select Substation(s)</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c2:
        zone_pre = st.selectbox("Pre-filter Zone", ["All Zones","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"], key="zone_pre")

    df_filtered_kv = df_kv[df_kv["Zone"] == zone_pre] if zone_pre != "All Zones" else df_kv
    sub_list = sorted(df_filtered_kv["Substation"].dropna().unique().tolist())

    with c1:
        selected_subs = st.multiselect(
            "Substations",
            options=sub_list,
            placeholder=f"Choose from {len(sub_list):,} substations at {sel_kv} kV...",
            label_visibility="collapsed",
        )

    if not selected_subs:
        st.markdown("""
        <div style="text-align:center;padding:52px 20px;color:#3a5070;font-family:'IBM Plex Mono',monospace;background:#0f1a24;border:1px dashed #1e2d42;border-radius:6px;margin-top:8px">
            <div style="font-size:32px;margin-bottom:10px">🏭</div>
            Select one or more substations to auto-resolve buses, zones & PSSE numbers
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ── STEP 3: Resolved buses ───────────────────────
    resolved = df_kv[df_kv["Substation"].isin(selected_subs)].copy()

    st.markdown('<div class="section-label"><span class="step-badge">3</span> Auto-Resolved Buses · Zones · PSSE Numbers</div>', unsafe_allow_html=True)

    for sub in selected_subs:
        sub_df    = resolved[resolved["Substation"] == sub]
        buses     = sub_df["Bus"].tolist()
        zones     = sub_df["Zone"].unique().tolist()
        psse_nums = sub_df["PSSE #"].tolist()
        kvs       = sorted(sub_df["kV"].unique().tolist(), key=lambda x: -float(x) if x else 0)
        rn_count  = sub_df[sub_df["Resource Node"] != ""].shape[0]
        hubs      = sub_df[sub_df["Hub"] != ""]["Hub"].unique().tolist()

        bus_tags  = "".join(f'<span class="tag-bus">{b}</span>' for b in buses[:25])
        more_b    = f'<span style="color:#3a5070;font-family:IBM Plex Mono,monospace;font-size:11px">+{len(buses)-25} more</span>' if len(buses) > 25 else ""
        zone_tags = "".join(f'<span class="tag-zone">{z}</span>' for z in zones)
        psse_tags = "".join(f'<span class="tag-psse">{p}</span>' for p in psse_nums[:20])
        more_p    = f'<span style="color:#3a5070;font-family:IBM Plex Mono,monospace;font-size:11px">+{len(psse_nums)-20} more</span>' if len(psse_nums) > 20 else ""
        hub_tags  = "".join(f'<span class="tag-hub">{h}</span>' for h in hubs) if hubs else '<span style="color:#3a5070;font-size:11px;font-family:IBM Plex Mono,monospace">—</span>'
        kv_tags   = "".join(f'<span class="kv {kv_cls(k)}">{k} kV</span>' for k in kvs)

        st.markdown(f"""
        <div class="detail-card">
            <h3>▶ {sub}</h3>
            <div class="dg">
                <div class="di"><div class="dl">Buses</div><div class="dv" style="color:#00d4ff">{len(buses)}</div></div>
                <div class="di"><div class="dl">Voltage(s)</div><div class="dv">{kv_tags}</div></div>
                <div class="di"><div class="dl">Zone(s)</div><div class="dv">{zone_tags}</div></div>
                <div class="di"><div class="dl">Hub(s)</div><div class="dv">{hub_tags}</div></div>
                <div class="di"><div class="dl">Resource Nodes</div><div class="dv" style="color:#39d353">{rn_count}</div></div>
            </div>
            <div style="margin-bottom:8px">
                <div class="dl" style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:.15em;text-transform:uppercase;margin-bottom:4px">Bus Names</div>
                <div class="tag-row">{bus_tags}{more_b}</div>
            </div>
            <div>
                <div class="dl" style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:.15em;text-transform:uppercase;margin-bottom:4px">PSSE Bus Numbers</div>
                <div class="tag-row">{psse_tags}{more_p}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Full table
    disp_cols = ["Substation", "Bus", "kV", "Zone", "PSSE #", "PSSE Name", "Resource Node", "Hub", "Node"]
    st.markdown(f"**{len(resolved):,}** buses resolved across **{len(selected_subs)}** substation(s)")
    st.dataframe(
        resolved[disp_cols].sort_values(["Substation","kV"], ascending=[True,False]).reset_index(drop=True),
        use_container_width=True,
        height=min(380, 40 + len(resolved)*35),
        column_config={
            "kV":   st.column_config.TextColumn(width="small"),
            "Zone": st.column_config.TextColumn(width="small"),
            "PSSE #": st.column_config.TextColumn("PSSE #", width="small"),
        }
    )
    st.download_button("↓ Export Bus List", data=to_csv_bytes(resolved[disp_cols]),
        file_name=f"ercot_nodes_{'_'.join(selected_subs[:3])}.csv", mime="text/csv")

    # ── STEP 4: LMP Upload ──────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-label"><span class="step-badge">4</span> Upload DAM Hourly LMP Data (Optional)</div>', unsafe_allow_html=True)
    st.markdown("""
    <p>Upload ERCOT DAM Hourly LMP CSV to analyse prices at your selected nodes.<br>
    <span style="font-size:11px;color:#3a5070;font-family:'IBM Plex Mono',monospace">
    Source: ERCOT MIS → Prices → DAM Settlement Point Prices &nbsp;|&nbsp;
    Expected cols: Settlement Point Name, Hour Ending, Settlement Point Price
    </span></p>
    """, unsafe_allow_html=True)

    lmp_file = st.file_uploader("Upload LMP CSV", type=["csv"], label_visibility="collapsed")

    if lmp_file:
        try:
            lmp_raw = pd.read_csv(lmp_file, dtype=str)
            col_u = {c: c.upper().strip() for c in lmp_raw.columns}

            # Auto-detect key columns
            bus_col   = next((c for c,u in col_u.items() if any(k in u for k in ["SETTLEMENT POINT","SETTLEMENTPOINT","BUS","NODE","POINT NAME","POINTNAME"])), None)
            price_col = next((c for c,u in col_u.items() if any(k in u for k in ["PRICE","LMP","SPP","SETTLEMENTPOINTPRICE"])), None)
            hour_col  = next((c for c,u in col_u.items() if any(k in u for k in ["HOUR","TIME","DATE","INTERVAL","DELIVERY"])), None)

            if not bus_col or not price_col:
                st.warning("⚠ Could not auto-detect columns. Please map manually:")
                all_cols = lmp_raw.columns.tolist()
                cc1, cc2, cc3 = st.columns(3)
                bus_col   = cc1.selectbox("Bus/Node column",  all_cols, key="lc_bus")
                price_col = cc2.selectbox("Price column",     all_cols, key="lc_price")
                hour_col  = cc3.selectbox("Hour/Time column (optional)", [None]+all_cols, key="lc_hour")

            lmp_raw[price_col] = pd.to_numeric(lmp_raw[price_col], errors="coerce")

            # Match to resolved buses
            resolved_buses_upper = set(resolved["Bus"].str.upper())
            lmp_raw["_bus_upper"] = lmp_raw[bus_col].str.upper().str.strip()
            matched = lmp_raw[lmp_raw["_bus_upper"].isin(resolved_buses_upper)].copy()

            m1,m2,m3,m4 = st.columns(4)
            m1.metric("LMP Rows",        f"{len(lmp_raw):,}")
            m2.metric("Matched Rows",    f"{len(matched):,}")
            m3.metric("Buses Matched",   f"{matched[bus_col].nunique()} / {len(resolved_buses_upper)}")
            avg_p = matched[price_col].mean() if len(matched) else 0
            m4.metric("Avg LMP",         f"${avg_p:.2f}/MWh")

            if len(matched) == 0:
                st.warning("No buses matched. Confirm the bus name format in your LMP file matches ERCOT settlement point names.")
            else:
                # Summary table
                st.markdown('<div class="section-label">LMP Summary by Bus</div>', unsafe_allow_html=True)
                summary = matched.groupby(bus_col)[price_col].agg(
                    Mean="mean", Max="max", Min="min", Std="std", Count="count"
                ).reset_index().round(2)
                summary.columns = ["Bus","Avg ($/MWh)","Max ($/MWh)","Min ($/MWh)","Std Dev","Hours"]
                bus_meta = resolved[["Bus","Substation","kV","Zone","PSSE #"]].drop_duplicates("Bus")
                summary = summary.merge(bus_meta, on="Bus", how="left")

                st.dataframe(
                    summary[["Bus","Substation","kV","Zone","Avg ($/MWh)","Max ($/MWh)","Min ($/MWh)","Std Dev","Hours","PSSE #"]],
                    use_container_width=True,
                    height=min(400, 40 + len(summary)*35),
                    column_config={
                        "Avg ($/MWh)": st.column_config.NumberColumn(format="$%.2f"),
                        "Max ($/MWh)": st.column_config.NumberColumn(format="$%.2f"),
                        "Min ($/MWh)": st.column_config.NumberColumn(format="$%.2f"),
                        "Std Dev":     st.column_config.NumberColumn(format="%.2f"),
                    }
                )

                # Time series
                if hour_col:
                    st.markdown('<div class="section-label">LMP Time Series</div>', unsafe_allow_html=True)
                    try:
                        ts = matched[[hour_col, bus_col, price_col]].copy()
                        ts[hour_col] = pd.to_datetime(ts[hour_col], infer_datetime_format=True, errors="coerce")
                        ts = ts.dropna(subset=[hour_col])
                        pivot = ts.pivot_table(index=hour_col, columns=bus_col, values=price_col, aggfunc="mean")
                        st.line_chart(pivot, height=320)
                    except Exception as e:
                        st.caption(f"Could not render chart: {e}")

                # Spread analysis
                if len(summary) >= 2:
                    st.markdown('<div class="section-label">Bus-to-Bus Spread Analysis</div>', unsafe_allow_html=True)
                    avgs = summary.set_index("Bus")["Avg ($/MWh)"].to_dict()
                    buses_s = list(avgs.keys())
                    pairs = []
                    for i in range(len(buses_s)):
                        for j in range(i+1, len(buses_s)):
                            pairs.append({
                                "Bus A": buses_s[i], "Bus B": buses_s[j],
                                "Avg A": avgs[buses_s[i]], "Avg B": avgs[buses_s[j]],
                                "Spread ($/MWh)": round(abs(avgs[buses_s[i]] - avgs[buses_s[j]]), 2)
                            })
                    spread_df = pd.DataFrame(pairs).sort_values("Spread ($/MWh)", ascending=False)
                    st.dataframe(spread_df, use_container_width=True, height=min(280, 40+len(spread_df)*35),
                        column_config={
                            "Avg A": st.column_config.NumberColumn("Avg A ($/MWh)", format="$%.2f"),
                            "Avg B": st.column_config.NumberColumn("Avg B ($/MWh)", format="$%.2f"),
                            "Spread ($/MWh)": st.column_config.NumberColumn(format="$%.2f"),
                        })

                st.download_button("↓ Export LMP Analysis",
                    data=to_csv_bytes(summary),
                    file_name=f"lmp_analysis_{'_'.join(selected_subs[:3])}.csv", mime="text/csv")

        except Exception as e:
            st.error(f"Error reading LMP file: {e}")

    else:
        st.markdown("""
        <div style="background:#0f1a24;border:1px dashed #1e2d42;border-radius:6px;padding:28px;text-align:center">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:#3a5070">
                Upload ERCOT DAM Hourly LMP CSV to analyse prices at selected nodes<br>
                <span style="font-size:10px;margin-top:6px;display:block">Source: ERCOT MIS → Prices → DAM Settlement Point Prices</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# PAGE 2 — Bus Lookup
# ═══════════════════════════════════════════════════
elif page == "🔍 Bus Lookup":
    st.markdown("""<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>BUS <span>LOOKUP</span></h1></div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([3,1])
    with c1: bus_q = st.text_input("Bus Name", placeholder="e.g. 0001, BUCKRA, AEP...", key="bus_q")
    with c2: bus_zone = st.selectbox("Zone", ["All Zones","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"], key="bus_zone")

    if bus_q.strip():
        q = bus_q.strip().upper()
        mask = (df["Bus"].str.upper().str.contains(q, na=False) |
                df["PSSE Name"].str.upper().str.contains(q, na=False))
        if bus_zone != "All Zones": mask &= df["Zone"] == bus_zone
        results = df[mask]

        exact = df[df["Bus"].str.upper() == q]
        if not exact.empty:
            r = exact.iloc[0]
            st.markdown(f"""
            <div class="detail-card"><h3>▶ {r['Bus']}</h3>
            <div class="dg">
                <div class="di"><div class="dl">Substation</div><div class="dv" style="color:#ff6b35">{r['Substation']}</div></div>
                <div class="di"><div class="dl">Voltage</div><div class="dv"><span class="kv {kv_cls(r['kV'])}">{r['kV']} kV</span></div></div>
                <div class="di"><div class="dl">Zone</div><div class="dv" style="color:#39d353">{r['Zone']}</div></div>
                <div class="di"><div class="dl">PSSE Name</div><div class="dv">{r['PSSE Name'] or '—'}</div></div>
                <div class="di"><div class="dl">PSSE #</div><div class="dv">{r['PSSE #'] or '—'}</div></div>
                <div class="di"><div class="dl">Resource Node</div><div class="dv">{r['Resource Node'] or '—'}</div></div>
                <div class="di"><div class="dl">Hub</div><div class="dv">{r['Hub'] or '—'}</div></div>
            </div></div>""", unsafe_allow_html=True)

        st.markdown(f"**{len(results):,}** results for `{bus_q.strip()}`")
        disp = ["Bus","PSSE Name","kV","Substation","Zone","Resource Node","PSSE #"]
        st.dataframe(results[disp].reset_index(drop=True), use_container_width=True, height=min(400,40+len(results)*35))
        if len(results): st.download_button("↓ Export CSV", data=to_csv_bytes(results[disp]), file_name=f"bus_{bus_q.strip()}.csv", mime="text/csv")
    else:
        st.markdown('<div style="text-align:center;padding:60px;color:#3a5070;font-family:IBM Plex Mono,monospace"><div style="font-size:36px;margin-bottom:12px">⚡</div>Enter a bus name above</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# PAGE 3 — Substation Lookup
# ═══════════════════════════════════════════════════
elif page == "🏭 Substation Lookup":
    st.markdown("""<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>SUBSTATION <span>LOOKUP</span></h1></div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([3,1])
    with c1: sub_q = st.text_input("Substation Name", placeholder="e.g. LOOKOUT, CAMPBELL...", key="sub_q")
    with c2:
        kv_opts = ["All kV"] + sorted(df["kV"].dropna().unique().tolist(), key=lambda x: -float(x) if x else 0)
        sub_kv = st.selectbox("Voltage", kv_opts, key="sub_kv")

    if sub_q.strip():
        q = sub_q.strip().upper()
        mask = df["Substation"].str.upper().str.contains(q, na=False)
        if sub_kv != "All kV": mask &= df["kV"] == sub_kv
        results = df[mask]

        exact = df[df["Substation"].str.upper() == q]
        if not exact.empty:
            kvs   = ", ".join(sorted(exact["kV"].unique(), key=lambda x: -float(x) if x else 0))
            zones = ", ".join(exact["Zone"].unique())
            st.markdown(f"""
            <div class="detail-card"><h3>▶ {exact.iloc[0]['Substation']}</h3>
            <div class="dg">
                <div class="di"><div class="dl">Total Buses</div><div class="dv" style="color:#00d4ff">{len(exact)}</div></div>
                <div class="di"><div class="dl">Voltages</div><div class="dv">{kvs} kV</div></div>
                <div class="di"><div class="dl">Zone(s)</div><div class="dv" style="color:#39d353">{zones}</div></div>
                <div class="di"><div class="dl">Resource Nodes</div><div class="dv">{exact[exact['Resource Node']!=''].shape[0]}</div></div>
            </div></div>""", unsafe_allow_html=True)

        st.markdown(f"**{len(results):,}** results for `{sub_q.strip()}`")
        disp = ["Substation","Bus","kV","Zone","PSSE #","PSSE Name","Resource Node"]
        st.dataframe(results[disp].reset_index(drop=True), use_container_width=True, height=min(400,40+len(results)*35))
        if len(results): st.download_button("↓ Export CSV", data=to_csv_bytes(results[disp]), file_name=f"sub_{sub_q.strip()}.csv", mime="text/csv")
    else:
        st.markdown('<div style="text-align:center;padding:60px;color:#3a5070;font-family:IBM Plex Mono,monospace"><div style="font-size:36px;margin-bottom:12px">🏭</div>Enter a substation name above</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# PAGE 4 — Browse All
# ═══════════════════════════════════════════════════
elif page == "📋 Browse All":
    st.markdown("""<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>BROWSE <span>ALL</span></h1></div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns([3,1,1,1])
    with c1: bq  = st.text_input("Search", placeholder="Bus, PSSE Name, Substation...", key="bq")
    with c2: bz  = st.selectbox("Zone", ["All","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"], key="bz")
    with c3:
        bkv_opts = ["All kV"] + sorted(df["kV"].dropna().unique().tolist(), key=lambda x: -float(x) if x else 0)
        bkv = st.selectbox("kV", bkv_opts, key="bkv")
    with c4: brn = st.selectbox("Type", ["All","Resource Nodes","Hubs"], key="brn")

    f = df.copy()
    if bq.strip():
        q = bq.strip().upper()
        f = f[f["Bus"].str.upper().str.contains(q,na=False)|f["PSSE Name"].str.upper().str.contains(q,na=False)|f["Substation"].str.upper().str.contains(q,na=False)]
    if bz  != "All":      f = f[f["Zone"] == bz]
    if bkv != "All kV":   f = f[f["kV"] == bkv]
    if brn == "Resource Nodes": f = f[f["Resource Node"] != ""]
    elif brn == "Hubs":         f = f[f["Hub"] != ""]

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Records",      f"{len(f):,}")
    m2.metric("Substations",  f"{f['Substation'].nunique():,}")
    m3.metric("kV Levels",    f"{f['kV'].nunique()}")
    m4.metric("Res. Nodes",   f"{f[f['Resource Node']!=''].shape[0]:,}")

    disp = ["Bus","PSSE Name","kV","Substation","Zone","Resource Node","Hub","PSSE #"]
    st.dataframe(f[disp].reset_index(drop=True), use_container_width=True, height=500)
    st.download_button("↓ Export CSV", data=to_csv_bytes(f[disp]), file_name="ercot_browse.csv", mime="text/csv")
