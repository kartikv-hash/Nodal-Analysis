import streamlit as st
import pandas as pd
import io

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ERCOT Bus · Substation Lookup",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS — dark industrial theme matching SunStripe BESS Dashboard
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* Root theme */
:root {
    --bg: #0a0e14;
    --surface: #111720;
    --surface2: #192030;
    --border: #1e2d42;
    --accent: #00d4ff;
    --accent2: #ff6b35;
    --accent3: #39d353;
    --text: #e8f0f8;
    --text-dim: #6b8aaa;
    --mono: 'IBM Plex Mono', monospace;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0e14 !important;
    font-family: 'IBM Plex Sans', sans-serif;
    color: #e8f0f8;
}

[data-testid="stSidebar"] {
    background-color: #111720 !important;
    border-right: 1px solid #1e2d42;
}

[data-testid="stSidebar"] * { color: #e8f0f8 !important; }

/* Header strip */
.header-strip {
    background: linear-gradient(90deg, #0a0e14 0%, #111720 100%);
    border-bottom: 1px solid #1e2d42;
    padding: 18px 0 14px;
    margin-bottom: 24px;
}
.header-strip h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px;
    font-weight: 600;
    color: #e8f0f8;
    margin: 0;
    letter-spacing: -0.02em;
}
.header-strip h1 span { color: #00d4ff; }
.header-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #00d4ff;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 4px;
}

/* Metric cards */
.metric-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.metric-card {
    background: #111720;
    border: 1px solid #1e2d42;
    border-radius: 6px;
    padding: 14px 20px;
    min-width: 150px;
    flex: 1;
}
.metric-card .val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 24px;
    font-weight: 600;
    color: #00d4ff;
    line-height: 1;
}
.metric-card .lbl {
    font-size: 10px;
    color: #3a5070;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
}

/* Detail card */
.detail-card {
    background: #111720;
    border: 1px solid rgba(0,212,255,0.25);
    border-left: 3px solid #00d4ff;
    border-radius: 6px;
    padding: 18px 22px;
    margin-bottom: 20px;
}
.detail-card h3 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 16px;
    font-weight: 600;
    color: #ff6b35;
    margin: 0 0 14px;
}
.detail-grid { display: flex; flex-wrap: wrap; gap: 16px; }
.detail-item { min-width: 140px; }
.detail-item .d-lbl {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    color: #3a5070;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.detail-item .d-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 500;
    color: #e8f0f8;
    margin-top: 2px;
}

/* kV badges */
.kv { display: inline-block; padding: 1px 8px; border-radius: 10px; font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 600; }
.kv-500 { color: #ff4d4d; background: rgba(255,77,77,0.1); border: 1px solid rgba(255,77,77,0.3); }
.kv-345 { color: #ff9933; background: rgba(255,153,51,0.1); border: 1px solid rgba(255,153,51,0.3); }
.kv-230 { color: #ffcc00; background: rgba(255,204,0,0.1); border: 1px solid rgba(255,204,0,0.3); }
.kv-138 { color: #00d4ff; background: rgba(0,212,255,0.1); border: 1px solid rgba(0,212,255,0.3); }
.kv-69  { color: #39d353; background: rgba(57,211,83,0.1); border: 1px solid rgba(57,211,83,0.3); }
.kv-other { color: #6b8aaa; background: rgba(107,138,170,0.1); border: 1px solid rgba(107,138,170,0.3); }

/* Zone badge */
.zone { display: inline-block; padding: 1px 8px; border-radius: 10px; font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 500;
        color: #39d353; background: rgba(57,211,83,0.08); border: 1px solid rgba(57,211,83,0.25); }

/* Streamlit input overrides */
.stTextInput input, .stSelectbox select, div[data-baseweb="select"] {
    background-color: #111720 !important;
    border-color: #1e2d42 !important;
    color: #e8f0f8 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.stTextInput input:focus { border-color: #00d4ff !important; box-shadow: 0 0 0 1px #00d4ff22 !important; }

/* Dataframe styling */
.stDataFrame { border: 1px solid #1e2d42; border-radius: 6px; }
[data-testid="stDataFrameResizable"] { background: #111720; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1e2d42;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #3a5070;
    background: transparent;
    border: none;
    padding: 10px 20px;
}
.stTabs [aria-selected="true"] { color: #00d4ff !important; border-bottom: 2px solid #00d4ff !important; }

/* Download button */
.stDownloadButton button {
    background: transparent !important;
    border: 1px solid #1e2d42 !important;
    color: #6b8aaa !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 4px !important;
}
.stDownloadButton button:hover { border-color: #00d4ff !important; color: #00d4ff !important; }

/* Sidebar nav links */
.nav-link {
    display: block;
    padding: 8px 12px;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: #6b8aaa;
    text-decoration: none;
    margin-bottom: 4px;
    transition: all 0.15s;
}
.nav-link:hover { background: #192030; color: #00d4ff; }

div[data-testid="stMarkdownContainer"] p { color: #6b8aaa; font-size: 13px; }

hr { border-color: #1e2d42; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading ERCOT settlement points...")
def load_data():
    df = pd.read_csv("Settlement_Points_02202026_094122.csv", dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    # Rename for convenience
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


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def kv_badge(kv):
    try:
        v = float(kv)
        if v >= 500: cls = "kv-500"
        elif v >= 345: cls = "kv-345"
        elif v >= 230: cls = "kv-230"
        elif v >= 138: cls = "kv-138"
        elif v >= 69: cls = "kv-69"
        else: cls = "kv-other"
    except: cls = "kv-other"
    return f'<span class="kv {cls}">{kv} kV</span>'

def zone_badge(z):
    return f'<span class="zone">{z}</span>' if z else "—"

def to_csv(dataframe):
    return dataframe.to_csv(index=False).encode("utf-8")


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 20px;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#00d4ff;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:6px;">⚡ SunStripe</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:15px;font-weight:600;color:#e8f0f8;line-height:1.3;">ERCOT Bus /<br>Substation Lookup</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:10px;">Navigation</div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Go to",
        ["🔍 Bus → Substation", "🏭 Substation → Buses", "📋 Browse All"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Dataset stats
    n_buses = len(df)
    n_subs = df["Substation"].nunique()
    n_zones = df["Zone"].nunique()
    n_rn = df[df["Resource Node"] != ""].shape[0]

    st.markdown(f"""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px;">Dataset</div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <div><div style="font-size:18px;font-weight:600;color:#00d4ff;">{n_buses:,}</div><div style="font-size:10px;color:#3a5070;">Settlement Points</div></div>
        <div><div style="font-size:18px;font-weight:600;color:#ff6b35;">{n_subs:,}</div><div style="font-size:10px;color:#3a5070;">Substations</div></div>
        <div><div style="font-size:18px;font-weight:600;color:#39d353;">{n_rn:,}</div><div style="font-size:10px;color:#3a5070;">Resource Nodes</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;text-align:center;">
        Data: ERCOT Feb 2026<br>
        <a href="https://github.com/sunstripe/ercot-bus-lookup" style="color:#1e2d42;">GitHub ↗</a>
    </div>
    """, unsafe_allow_html=True)

    # Link to ERCOT BESS Dashboard
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">Related Tools</div>
    <a href="https://ercot-bess-dashboard-nhh9eztsqeuqxxuz97kacu.streamlit.app/" target="_blank"
       style="display:block;padding:8px 10px;background:#192030;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:#6b8aaa;text-decoration:none;">
        ⚡ ERCOT BESS Dashboard ↗
    </a>
    <a href="https://fatal-flaw-o7aks4agtoffgyydbvrguj.streamlit.app/" target="_blank"
       style="display:block;padding:8px 10px;background:#192030;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:#6b8aaa;text-decoration:none;margin-top:6px;">
        🌿 SiteIQ Fatal Flaw ↗
    </a>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Page header
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-strip">
    <div class="header-tag">⚡ SunStripe · ERCOT</div>
    <h1>BUS <span>/</span> SUBSTATION LOOKUP</h1>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE 1 — Bus → Substation
# ═══════════════════════════════════════════════
if page == "🔍 Bus → Substation":

    st.markdown("Search any **Electrical Bus** name to find its substation, voltage, zone, and PSSE identifiers.")

    col1, col2 = st.columns([3, 1])
    with col1:
        bus_query = st.text_input("Electrical Bus Name", placeholder="e.g. 0001, BUCKRA, AEP...", key="bus_q")
    with col2:
        zone_filter = st.selectbox("Zone", ["All Zones", "LZ_NORTH", "LZ_SOUTH", "LZ_WEST", "LZ_HOUSTON"], key="bus_zone")

    if bus_query.strip():
        q = bus_query.strip().upper()
        mask = (
            df["Bus"].str.upper().str.contains(q, na=False) |
            df["PSSE Name"].str.upper().str.contains(q, na=False) |
            df["Node"].str.upper().str.contains(q, na=False)
        )
        if zone_filter != "All Zones":
            mask &= df["Zone"] == zone_filter

        results = df[mask].copy()

        # Exact match detail card
        exact = df[df["Bus"].str.upper() == q]
        if not exact.empty:
            r = exact.iloc[0]
            st.markdown(f"""
            <div class="detail-card">
                <h3>▶ {r['Bus']}</h3>
                <div class="detail-grid">
                    <div class="detail-item"><div class="d-lbl">Substation</div><div class="d-val" style="color:#ff6b35">{r['Substation']}</div></div>
                    <div class="detail-item"><div class="d-lbl">Voltage</div><div class="d-val">{kv_badge(r['kV'])}</div></div>
                    <div class="detail-item"><div class="d-lbl">Load Zone</div><div class="d-val">{zone_badge(r['Zone'])}</div></div>
                    <div class="detail-item"><div class="d-lbl">Node Name</div><div class="d-val">{r['Node'] or '—'}</div></div>
                    <div class="detail-item"><div class="d-lbl">PSSE Bus Name</div><div class="d-val">{r['PSSE Name'] or '—'}</div></div>
                    <div class="detail-item"><div class="d-lbl">PSSE Bus #</div><div class="d-val">{r['PSSE #'] or '—'}</div></div>
                    <div class="detail-item"><div class="d-lbl">Resource Node</div><div class="d-val">{r['Resource Node'] or '—'}</div></div>
                    <div class="detail-item"><div class="d-lbl">Hub</div><div class="d-val">{r['Hub'] or '—'}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"**{len(results):,}** result{'s' if len(results) != 1 else ''} for `{bus_query.strip()}`")

        if not results.empty:
            display_cols = ["Bus", "Node", "PSSE Name", "kV", "Substation", "Zone", "Resource Node", "PSSE #"]
            st.dataframe(
                results[display_cols].reset_index(drop=True),
                use_container_width=True,
                height=min(400, 40 + len(results) * 35),
                column_config={
                    "Bus": st.column_config.TextColumn("Bus Name", width="medium"),
                    "kV": st.column_config.TextColumn("kV", width="small"),
                    "Substation": st.column_config.TextColumn("Substation", width="medium"),
                    "Zone": st.column_config.TextColumn("Zone", width="small"),
                }
            )

            col_dl, col_hint = st.columns([1, 4])
            with col_dl:
                st.download_button(
                    "↓ Export CSV",
                    data=to_csv(results[display_cols]),
                    file_name=f"ercot_bus_{bus_query.strip()}.csv",
                    mime="text/csv",
                )
            # Quick-jump to substation view
            if not exact.empty:
                with col_hint:
                    sub_name = exact.iloc[0]["Substation"]
                    st.info(f"💡 Tip: Switch to **Substation → Buses** and search `{sub_name}` to see all buses at this substation.")
        else:
            st.warning("No matching buses found. Try a partial name or check spelling.")

    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#3a5070;font-family:'IBM Plex Mono',monospace;">
            <div style="font-size:36px;margin-bottom:12px;">⚡</div>
            Enter a bus name above to begin searching
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE 2 — Substation → Buses
# ═══════════════════════════════════════════════
elif page == "🏭 Substation → Buses":

    st.markdown("Search any **Substation** to find all its associated electrical buses.")

    col1, col2 = st.columns([3, 1])
    with col1:
        sub_query = st.text_input("Substation Name", placeholder="e.g. LOOKOUT, CAMPBELL, DOWGEN...", key="sub_q")
    with col2:
        kv_opts = ["All kV"] + sorted(df["kV"].dropna().unique().tolist(), key=lambda x: -float(x) if x else 0)
        kv_filter = st.selectbox("Voltage", kv_opts, key="sub_kv")

    if sub_query.strip():
        q = sub_query.strip().upper()
        mask = df["Substation"].str.upper().str.contains(q, na=False)
        if kv_filter != "All kV":
            mask &= df["kV"] == kv_filter

        results = df[mask].copy()

        # Exact match substation summary card
        exact_sub = df[df["Substation"].str.upper() == q]
        if not exact_sub.empty:
            sub_name = exact_sub.iloc[0]["Substation"]
            n_buses_sub = len(exact_sub)
            kvs = ", ".join(sorted(exact_sub["kV"].unique(), key=lambda x: -float(x) if x else 0))
            zones = ", ".join(exact_sub["Zone"].unique())
            n_rn_sub = exact_sub[exact_sub["Resource Node"] != ""].shape[0]

            st.markdown(f"""
            <div class="detail-card">
                <h3>▶ {sub_name}</h3>
                <div class="detail-grid">
                    <div class="detail-item"><div class="d-lbl">Total Buses</div><div class="d-val" style="color:#00d4ff">{n_buses_sub}</div></div>
                    <div class="detail-item"><div class="d-lbl">Voltage Levels</div><div class="d-val">{kvs} kV</div></div>
                    <div class="detail-item"><div class="d-lbl">Load Zone(s)</div><div class="d-val" style="color:#39d353">{zones}</div></div>
                    <div class="detail-item"><div class="d-lbl">Resource Nodes</div><div class="d-val">{n_rn_sub}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"**{len(results):,}** result{'s' if len(results) != 1 else ''} for `{sub_query.strip()}`")

        if not results.empty:
            display_cols = ["Substation", "Bus", "Node", "PSSE Name", "kV", "Zone", "Resource Node", "PSSE #"]
            st.dataframe(
                results[display_cols].reset_index(drop=True),
                use_container_width=True,
                height=min(400, 40 + len(results) * 35),
                column_config={
                    "Substation": st.column_config.TextColumn("Substation", width="medium"),
                    "Bus": st.column_config.TextColumn("Bus Name", width="medium"),
                    "kV": st.column_config.TextColumn("kV", width="small"),
                    "Zone": st.column_config.TextColumn("Zone", width="small"),
                }
            )
            st.download_button(
                "↓ Export CSV",
                data=to_csv(results[display_cols]),
                file_name=f"ercot_sub_{sub_query.strip()}.csv",
                mime="text/csv",
            )
        else:
            st.warning("No matching substations found. Try a partial name.")

    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#3a5070;font-family:'IBM Plex Mono',monospace;">
            <div style="font-size:36px;margin-bottom:12px;">🏭</div>
            Enter a substation name above to begin searching
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE 3 — Browse All
# ═══════════════════════════════════════════════
elif page == "📋 Browse All":

    st.markdown("Filter and explore the full ERCOT settlement points dataset.")

    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        browse_q = st.text_input("Search (Bus, PSSE Name, Substation)", placeholder="Type anything...", key="browse_q")
    with col2:
        b_zone = st.selectbox("Zone", ["All Zones", "LZ_NORTH", "LZ_SOUTH", "LZ_WEST", "LZ_HOUSTON"], key="b_zone")
    with col3:
        kv_opts_b = ["All kV"] + sorted(df["kV"].dropna().unique().tolist(), key=lambda x: -float(x) if x else 0)
        b_kv = st.selectbox("Voltage", kv_opts_b, key="b_kv")
    with col4:
        b_rn = st.selectbox("Type", ["All", "Resource Nodes Only", "Non-Resource Only"], key="b_rn")

    filtered = df.copy()

    if browse_q.strip():
        q = browse_q.strip().upper()
        filtered = filtered[
            filtered["Bus"].str.upper().str.contains(q, na=False) |
            filtered["PSSE Name"].str.upper().str.contains(q, na=False) |
            filtered["Substation"].str.upper().str.contains(q, na=False)
        ]
    if b_zone != "All Zones":
        filtered = filtered[filtered["Zone"] == b_zone]
    if b_kv != "All kV":
        filtered = filtered[filtered["kV"] == b_kv]
    if b_rn == "Resource Nodes Only":
        filtered = filtered[filtered["Resource Node"] != ""]
    elif b_rn == "Non-Resource Only":
        filtered = filtered[filtered["Resource Node"] == ""]

    # Summary metrics
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Matching Records", f"{len(filtered):,}")
    mc2.metric("Unique Substations", f"{filtered['Substation'].nunique():,}")
    mc3.metric("Unique kV Levels", f"{filtered['kV'].nunique():,}")
    mc4.metric("Resource Nodes", f"{filtered[filtered['Resource Node'] != ''].shape[0]:,}")

    st.markdown("---")

    display_cols = ["Bus", "PSSE Name", "kV", "Substation", "Zone", "Resource Node", "PSSE #"]
    st.dataframe(
        filtered[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=500,
        column_config={
            "Bus": st.column_config.TextColumn("Bus Name", width="medium"),
            "kV": st.column_config.TextColumn("kV", width="small"),
            "Substation": st.column_config.TextColumn("Substation", width="medium"),
            "Zone": st.column_config.TextColumn("Zone", width="small"),
            "Resource Node": st.column_config.TextColumn("Resource Node", width="medium"),
        }
    )

    col_dl1, col_dl2 = st.columns([1, 5])
    with col_dl1:
        st.download_button(
            "↓ Export CSV",
            data=to_csv(filtered[display_cols]),
            file_name="ercot_browse_export.csv",
            mime="text/csv",
        )
