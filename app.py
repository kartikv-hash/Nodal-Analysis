import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import re
import math

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
[data-testid="stSidebar"] {
    background-color: #111720 !important;
    border-right: 1px solid #1e2d42;
}
[data-testid="stSidebar"] * { color: #e8f0f8 !important; }

.page-header {
    border-bottom: 1px solid #1e2d42;
    padding-bottom: 14px; margin-bottom: 18px;
}
.page-header .tag {
    font-family:'IBM Plex Mono',monospace; font-size:10px; color:#00d4ff;
    letter-spacing:.2em; text-transform:uppercase; margin-bottom:4px;
}
.page-header h1 {
    font-family:'IBM Plex Mono',monospace; font-size:22px;
    font-weight:600; color:#e8f0f8; margin:0;
}
.page-header h1 span { color:#00d4ff; }

.section-label {
    font-family:'IBM Plex Mono',monospace; font-size:10px; color:#3a5070;
    letter-spacing:.2em; text-transform:uppercase; margin:16px 0 8px;
    display:flex; align-items:center; gap:8px;
}
.section-label::after { content:''; flex:1; height:1px; background:#1e2d42; }

.step-badge {
    display:inline-flex; align-items:center; justify-content:center;
    width:20px; height:20px; border-radius:50%;
    background:#00d4ff; color:#000;
    font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:700;
}

/* OSM substation info card */
.osm-card {
    background:#0f1a24; border:1px solid rgba(0,212,255,0.3);
    border-left:3px solid #00d4ff; border-radius:6px;
    padding:14px 18px; margin-bottom:12px;
}
.osm-card .oc-title {
    font-family:'IBM Plex Mono',monospace; font-size:15px; font-weight:600;
    color:#00d4ff; margin-bottom:10px;
}
.osm-card .oc-grid { display:flex; flex-wrap:wrap; gap:14px; margin-bottom:10px; }
.osm-card .oc-item .oc-lbl {
    font-family:'IBM Plex Mono',monospace; font-size:9px; color:#3a5070;
    letter-spacing:.15em; text-transform:uppercase;
}
.osm-card .oc-item .oc-val {
    font-family:'IBM Plex Mono',monospace; font-size:12px; font-weight:500;
    color:#e8f0f8; margin-top:2px;
}

/* ERCOT resolved card */
.ercot-card {
    background:#111720; border:1px solid rgba(255,107,53,0.3);
    border-left:3px solid #ff6b35; border-radius:6px;
    padding:14px 18px; margin-bottom:12px;
}
.ercot-card h3 {
    font-family:'IBM Plex Mono',monospace; font-size:14px; font-weight:600;
    color:#ff6b35; margin:0 0 10px;
}
.dg { display:flex; flex-wrap:wrap; gap:12px; margin-bottom:8px; }
.di .dl {
    font-family:'IBM Plex Mono',monospace; font-size:9px; color:#3a5070;
    letter-spacing:.15em; text-transform:uppercase;
}
.di .dv {
    font-family:'IBM Plex Mono',monospace; font-size:12px;
    font-weight:500; color:#e8f0f8; margin-top:2px;
}

/* Tag pills */
.tag-row { display:flex; flex-wrap:wrap; gap:5px; margin-top:4px; }
.tag-bus  { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:500; background:rgba(0,212,255,0.08); border:1px solid rgba(0,212,255,0.25); color:#00d4ff; }
.tag-zone { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; background:rgba(57,211,83,0.08); border:1px solid rgba(57,211,83,0.25); color:#39d353; }
.tag-psse { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; background:rgba(255,107,53,0.08); border:1px solid rgba(255,107,53,0.25); color:#ff6b35; }
.tag-hub  { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; background:rgba(255,204,0,0.08); border:1px solid rgba(255,204,0,0.25); color:#ffcc00; }
.tag-rn   { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; background:rgba(57,211,83,0.06); border:1px solid rgba(57,211,83,0.2); color:#39d353; }

/* kV badges */
.kv { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:600; }
.kv-345 { color:#ff9933; background:rgba(255,153,51,0.1); border:1px solid rgba(255,153,51,0.3); }
.kv-230 { color:#ffcc00; background:rgba(255,204,0,0.1); border:1px solid rgba(255,204,0,0.3); }
.kv-138 { color:#00d4ff; background:rgba(0,212,255,0.1); border:1px solid rgba(0,212,255,0.3); }
.kv-115 { color:#a78bfa; background:rgba(167,139,250,0.1); border:1px solid rgba(167,139,250,0.3); }
.kv-69  { color:#39d353; background:rgba(57,211,83,0.1); border:1px solid rgba(57,211,83,0.3); }
.kv-34  { color:#6b8aaa; background:rgba(107,138,170,0.1); border:1px solid rgba(107,138,170,0.3); }

/* No-selection placeholder */
.map-placeholder {
    text-align:center; padding:40px 20px; color:#3a5070;
    font-family:'IBM Plex Mono',monospace;
    background:#0a0e14; border:1px dashed #1e2d42; border-radius:6px;
}
.map-placeholder .mp-icon { font-size:32px; margin-bottom:10px; }
.map-placeholder .mp-title { font-size:13px; font-weight:600; color:#1e2d42; margin-bottom:6px; }
.map-placeholder .mp-sub { font-size:11px; line-height:1.6; }

/* Hint bar */
.hint-bar {
    background:#0f1a24; border:1px solid #1e2d42; border-radius:4px;
    padding:8px 14px; font-family:'IBM Plex Mono',monospace;
    font-size:11px; color:#3a5070; margin-bottom:10px;
    display:flex; align-items:center; gap:8px;
}

/* Confidence badge */
.conf-high  { color:#39d353; font-weight:600; }
.conf-med   { color:#ffcc00; font-weight:600; }
.conf-low   { color:#ff6b35; font-weight:600; }

/* Match row */
.match-row {
    display:flex; align-items:center; justify-content:space-between;
    background:#192030; border:1px solid #1e2d42; border-radius:4px;
    padding:8px 12px; margin-bottom:6px; cursor:pointer;
    font-family:'IBM Plex Mono',monospace; font-size:12px;
}
.match-row:hover { border-color:#00d4ff; }
.match-row .mr-name { color:#e8f0f8; font-weight:500; }
.match-row .mr-meta { color:#3a5070; font-size:10px; }

/* Streamlit overrides */
.stTabs [data-baseweb="tab-list"] { background:transparent; border-bottom:1px solid #1e2d42; }
.stTabs [data-baseweb="tab"] { font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:500; letter-spacing:.08em; text-transform:uppercase; color:#3a5070; background:transparent; padding:10px 18px; }
.stTabs [aria-selected="true"] { color:#00d4ff !important; border-bottom:2px solid #00d4ff !important; }

.stTextInput input, div[data-baseweb="select"] > div {
    background-color:#111720 !important; border-color:#1e2d42 !important;
    color:#e8f0f8 !important; font-family:'IBM Plex Mono',monospace !important;
}
.stDownloadButton button, .stButton button {
    background:transparent !important; border:1px solid #1e2d42 !important;
    color:#6b8aaa !important; font-family:'IBM Plex Mono',monospace !important;
    font-size:11px !important; font-weight:600 !important;
    letter-spacing:.08em !important; text-transform:uppercase !important; border-radius:4px !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    border-color:#00d4ff !important; color:#00d4ff !important;
}
[data-testid="stMetric"] {
    background:#111720; border:1px solid #1e2d42;
    border-radius:6px; padding:12px 16px;
}
[data-testid="stMetricLabel"] {
    font-family:'IBM Plex Mono',monospace !important; font-size:10px !important;
    color:#3a5070 !important; text-transform:uppercase; letter-spacing:.1em;
}
[data-testid="stMetricValue"] {
    font-family:'IBM Plex Mono',monospace !important;
    color:#00d4ff !important; font-size:22px !important;
}
div[data-testid="stMarkdownContainer"] p { color:#6b8aaa; font-size:13px; }
hr { border-color:#1e2d42 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# Data & helpers
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

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


# ─────────────────────────────────────────────────────────────────
# Overpass: fetch substations near a click point
# ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_near_click(lat, lon, radius_deg=0.15):
    """Query Overpass for power substations within radius_deg of click."""
    s, w = lat - radius_deg, lon - radius_deg * 1.4
    n, e = lat + radius_deg, lon + radius_deg * 1.4
    query = f"""[out:json][timeout:20];
(
  node["power"="substation"]({s},{w},{n},{e});
  way["power"="substation"]({s},{w},{n},{e});
  relation["power"="substation"]({s},{w},{n},{e});
);
out center tags;"""
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query}, timeout=25,
            headers={"User-Agent": "SunStripe-ERCOT/1.0"}
        )
        r.raise_for_status()
        elements = []
        for el in r.json().get("elements", []):
            elat = el.get("lat") or (el.get("center") or {}).get("lat")
            elon = el.get("lon") or (el.get("center") or {}).get("lon")
            if elat and elon:
                tags = el.get("tags", {})
                elements.append({
                    "lat": elat, "lon": elon,
                    "name":     tags.get("name", ""),
                    "voltage":  tags.get("voltage", ""),
                    "operator": tags.get("operator", ""),
                    "ref":      tags.get("ref", ""),
                    "osm_id":   el.get("id", ""),
                })
        # Sort by distance from click
        elements.sort(key=lambda x: haversine(lat, lon, x["lat"], x["lon"]))
        return elements, None
    except requests.exceptions.Timeout:
        return [], "Overpass API timed out. Try again."
    except Exception as e:
        return [], f"Overpass error: {e}"


# ─────────────────────────────────────────────────────────────────
# ERCOT matching engine
# ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def build_ercot_search_index():
    """
    Build searchable index of ERCOT substations with their PSSE name tokens.
    Returns: list of dicts {substation, tokens, psse_names}
    """
    records = []
    grouped = df.groupby("Substation")
    for sub, grp in grouped:
        psse_names = grp["PSSE Name"].unique().tolist()
        # Extract clean alphabetic tokens from PSSE names
        tokens = set()
        for pn in psse_names:
            # "JACKSBOR_9" -> "JACKSBOR", "BOWIE8" -> "BOWIE", "CAMPBELLSW" -> "CAMPBELLSW"
            clean = re.sub(r'[^A-Z]', '', pn.upper().split('_')[0])
            if len(clean) >= 3:
                tokens.add(clean)
            # Also add sub prefix
            sub_clean = re.sub(r'[^A-Z]', '', sub.upper())
            if len(sub_clean) >= 3:
                tokens.add(sub_clean)
        records.append({
            "substation": sub,
            "tokens": tokens,
            "psse_names": psse_names,
            "kvs": sorted(grp["kV"].unique().tolist(), key=lambda x: -float(x) if x else 0),
            "zones": grp["Zone"].unique().tolist(),
            "bus_count": len(grp),
        })
    return records

ercot_index = build_ercot_search_index()

def match_to_ercot(osm_name, osm_voltage_str=""):
    """
    Score every ERCOT substation against an OSM name.
    Returns ranked list of (substation_name, score, confidence).
    """
    if not osm_name:
        return []

    osm_clean = re.sub(r'[^A-Z0-9 ]', '', osm_name.upper())
    # Remove noise words
    for pat in [r'\bSUBSTATION\b', r'\bSWITCHING\b', r'\bSWITCH\b', r'\bSTATION\b',
                r'\bELECTRIC\b', r'\bELECTRICAL\b', r'\bPOWER\b', r'\bENERGY\b',
                r'\bTRANSMISSION\b', r'\bTRANS\b', r'\bSUB\b', r'\bSS\b',
                r'\b\d+\s*KV\b', r'\bKV\b']:
        osm_clean = re.sub(pat, '', osm_clean)
    osm_tokens = [t for t in osm_clean.split() if len(t) >= 3]

    # Parse OSM voltage (stored in Volts)
    osm_kv = None
    try:
        v_str = osm_voltage_str.split(";")[0].strip()
        v_raw = float(re.sub(r'[^0-9.]', '', v_str))
        osm_kv = v_raw / 1000 if v_raw > 1000 else v_raw
    except:
        pass

    results = []
    for rec in ercot_index:
        score = 0

        for osm_tok in osm_tokens:
            for ercot_tok in rec["tokens"]:
                if osm_tok == ercot_tok:
                    score += 20
                elif osm_tok in ercot_tok and len(osm_tok) >= 5:
                    score += 12
                elif ercot_tok in osm_tok and len(ercot_tok) >= 5:
                    score += 10
                elif osm_tok[:5] == ercot_tok[:5] and len(osm_tok) >= 5:
                    score += 8

        # Voltage match bonus
        if osm_kv and score > 0:
            for kv_str in rec["kvs"]:
                try:
                    if abs(float(kv_str) - osm_kv) < 10:
                        score += 15
                        break
                except:
                    pass

        if score >= 8:
            results.append((rec["substation"], score, rec))

    results.sort(key=lambda x: -x[1])
    return results[:6]


# ─────────────────────────────────────────────────────────────────
# Map builder
# ─────────────────────────────────────────────────────────────────
def build_infrastructure_map(center_lat=31.5, center_lon=-97.5, zoom=7,
                              click_marker=None, nearby_subs=None, selected_sub=None):
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles=None,
        prefer_canvas=True,
    )

    # ── Tile layers ──────────────────────────────
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr='© OpenStreetMap © CARTO',
        name="Dark Base",
        overlay=False, control=True, max_zoom=20,
    ).add_to(m)

    # OpenInfraMap — shows all power infrastructure visually
    folium.TileLayer(
        tiles="https://tiles.openinframap.org/power_medium/{z}/{x}/{y}.png",
        attr='© <a href="https://openinframap.org">OpenInfraMap</a>',
        name="⚡ Power Infrastructure",
        overlay=True, control=True, opacity=0.9, max_zoom=17,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://tiles.openinframap.org/power_high/{z}/{x}/{y}.png",
        attr='© <a href="https://openinframap.org">OpenInfraMap</a>',
        name="⚡ HV Lines",
        overlay=True, control=True, opacity=0.8, max_zoom=17,
    ).add_to(m)

    # ── Click marker ────────────────────────────
    if click_marker:
        folium.Marker(
            location=click_marker,
            icon=folium.DivIcon(html="""
                <div style="
                    width:16px; height:16px; border-radius:50%;
                    background:#ffffff; border:3px solid #00d4ff;
                    box-shadow:0 0 8px #00d4ff; margin:-8px 0 0 -8px;">
                </div>"""),
            tooltip="You clicked here",
        ).add_to(m)

    # ── Nearby substations from Overpass ────────
    if nearby_subs:
        for i, sub in enumerate(nearby_subs):
            is_selected = (selected_sub and sub.get("osm_id") == selected_sub.get("osm_id"))

            # Colour by voltage
            try:
                v = float(sub.get("voltage","0").split(";")[0]) / 1000
                if v >= 345:   col = "#ff9933"
                elif v >= 230: col = "#ffcc00"
                elif v >= 138: col = "#00d4ff"
                elif v >= 69:  col = "#39d353"
                else:          col = "#8899aa"
            except:
                col = "#8899aa"
                v   = None

            name    = sub.get("name") or f"Substation #{i+1}"
            v_label = f"{v:.0f} kV" if v else "? kV"
            op      = sub.get("operator", "")
            dist_km = haversine(click_marker[0], click_marker[1], sub["lat"], sub["lon"]) if click_marker else 0

            # Popup HTML
            popup_html = f"""
<div style="font-family:'IBM Plex Mono',monospace;background:#0f1a24;color:#e8f0f8;
     padding:12px 14px;border-radius:6px;min-width:200px;border:1px solid #1e2d42;">
  <div style="font-size:13px;font-weight:600;color:{'#00d4ff' if is_selected else '#ff6b35'};margin-bottom:8px">
    {'✓ ' if is_selected else ''}{name}
  </div>
  <div style="font-size:10px;color:#3a5070;margin-bottom:2px">VOLTAGE</div>
  <div style="font-size:12px;margin-bottom:6px">{v_label}</div>
  {'<div style="font-size:10px;color:#3a5070;margin-bottom:2px">OPERATOR</div><div style="font-size:11px;margin-bottom:6px">'+op+'</div>' if op else ''}
  <div style="font-size:10px;color:#3a5070">Distance: {dist_km:.1f} km from click</div>
</div>"""

            folium.CircleMarker(
                location=[sub["lat"], sub["lon"]],
                radius=12 if is_selected else 8,
                color="#ffffff" if is_selected else col,
                weight=3 if is_selected else 1,
                fill=True,
                fill_color=col,
                fill_opacity=0.95 if is_selected else 0.75,
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=f"<b>{name}</b> · {v_label}",
            ).add_to(m)

    folium.LayerControl(collapsed=False, position="topright").add_to(m)

    return m


# ─────────────────────────────────────────────────────────────────
# LMP analysis helper (shared across pages)
# ─────────────────────────────────────────────────────────────────
def render_lmp_section(resolved_df, key_prefix="lmp"):
    st.markdown(f"""
    <div class="section-label"><span class="step-badge">+</span> Upload DAM Hourly LMP Data</div>
    <p>Upload ERCOT DAM Hourly LMP CSV — app auto-matches your buses and plots prices.<br>
    <span style="font-size:11px;color:#3a5070;font-family:'IBM Plex Mono',monospace">
    Source: ERCOT MIS → Reports → DAM Settlement Point Prices (CSV)
    </span></p>
    """, unsafe_allow_html=True)

    lmp_file = st.file_uploader("Upload LMP CSV", type=["csv"], key=f"{key_prefix}_file",
                                 label_visibility="collapsed")
    if not lmp_file:
        st.markdown("""
        <div style="background:#0f1a24;border:1px dashed #1e2d42;border-radius:6px;
             padding:24px;text-align:center;font-family:'IBM Plex Mono',monospace;
             font-size:11px;color:#3a5070">
            Drag and drop your ERCOT DAM LMP CSV here<br>
            <span style="font-size:10px;margin-top:4px;display:block">
            Expected: Settlement Point Name · Hour Ending · Settlement Point Price
            </span>
        </div>""", unsafe_allow_html=True)
        return

    try:
        lmp_raw = pd.read_csv(lmp_file, dtype=str)
        col_u = {c: c.upper().strip().replace(" ","") for c in lmp_raw.columns}

        bus_col   = next((c for c,u in col_u.items() if any(k in u for k in
                          ["SETTLEMENTPOINT","POINTNAME","BUS","NODE"])), None)
        price_col = next((c for c,u in col_u.items() if any(k in u for k in
                          ["PRICE","LMP","SPP","SETTLEMENTPOINTPRICE"])), None)
        hour_col  = next((c for c,u in col_u.items() if any(k in u for k in
                          ["HOUR","TIME","DATE","INTERVAL","DELIVERY"])), None)

        if not bus_col or not price_col:
            st.warning("⚠ Could not auto-detect columns. Map them manually:")
            cc1, cc2, cc3 = st.columns(3)
            all_c = lmp_raw.columns.tolist()
            bus_col   = cc1.selectbox("Bus/Node column",  all_c, key=f"{key_prefix}_bc")
            price_col = cc2.selectbox("Price column",     all_c, key=f"{key_prefix}_pc")
            hour_col  = cc3.selectbox("Hour column (opt)", [None]+all_c, key=f"{key_prefix}_hc")
        else:
            st.success(f"✓ Auto-detected — Bus: `{bus_col}` · Price: `{price_col}` · Hour: `{hour_col or 'not found'}`")

        lmp_raw[price_col] = pd.to_numeric(lmp_raw[price_col], errors="coerce")
        resolved_upper     = set(resolved_df["Bus"].str.upper())
        lmp_raw["_bu"]     = lmp_raw[bus_col].str.upper().str.strip()
        matched            = lmp_raw[lmp_raw["_bu"].isin(resolved_upper)].copy()

        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total LMP Rows",   f"{len(lmp_raw):,}")
        m2.metric("Matched Rows",     f"{len(matched):,}")
        m3.metric("Buses Matched",    f"{matched[bus_col].nunique()} / {len(resolved_upper)}")
        avg_p = matched[price_col].mean() if len(matched) else None
        m4.metric("Avg LMP",          f"${avg_p:.2f}/MWh" if avg_p is not None else "—")

        if len(matched) == 0:
            st.warning("No buses matched. Check that bus names in your LMP file match ERCOT settlement point names (e.g. `CAMPBELLSW`).")
            return

        # Summary table
        st.markdown('<div class="section-label">Price Summary by Bus</div>', unsafe_allow_html=True)
        summ = matched.groupby(bus_col)[price_col].agg(
            Mean="mean", Max="max", Min="min", Std="std", Count="count"
        ).reset_index().round(2)
        summ.columns = ["Bus", "Avg $/MWh", "Max $/MWh", "Min $/MWh", "Std Dev", "Hours"]
        meta = resolved_df[["Bus","Substation","kV","Zone","PSSE #","Resource Node"]].drop_duplicates("Bus")
        summ = summ.merge(meta, on="Bus", how="left")

        st.dataframe(
            summ[["Bus","Substation","kV","Zone","Avg $/MWh","Max $/MWh","Min $/MWh","Std Dev","Hours","PSSE #","Resource Node"]],
            use_container_width=True,
            height=min(400, 40 + len(summ)*35),
            column_config={
                "Avg $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                "Max $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                "Min $/MWh": st.column_config.NumberColumn(format="$%.2f"),
            }
        )

        # Time series
        if hour_col:
            st.markdown('<div class="section-label">LMP Time Series</div>', unsafe_allow_html=True)
            try:
                ts = matched[[hour_col, bus_col, price_col]].copy()
                ts[hour_col] = pd.to_datetime(ts[hour_col], infer_datetime_format=True, errors="coerce")
                ts = ts.dropna(subset=[hour_col])
                pivot = ts.pivot_table(index=hour_col, columns=bus_col,
                                       values=price_col, aggfunc="mean")
                st.line_chart(pivot, height=300)
            except Exception as e:
                st.caption(f"Time series error: {e}")

        # Spread
        if len(summ) >= 2:
            st.markdown('<div class="section-label">Bus-to-Bus Spread</div>', unsafe_allow_html=True)
            avgs = summ.set_index("Bus")["Avg $/MWh"].to_dict()
            buses_s = list(avgs.keys())
            pairs = [{
                "Bus A": buses_s[i], "Bus B": buses_s[j],
                "Avg A $/MWh": avgs[buses_s[i]], "Avg B $/MWh": avgs[buses_s[j]],
                "Spread $/MWh": round(abs(avgs[buses_s[i]] - avgs[buses_s[j]]), 2)
            } for i in range(len(buses_s)) for j in range(i+1, len(buses_s))]
            spread_df = pd.DataFrame(pairs).sort_values("Spread $/MWh", ascending=False)
            st.dataframe(spread_df, use_container_width=True,
                height=min(260, 40+len(spread_df)*35),
                column_config={
                    "Avg A $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                    "Avg B $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                    "Spread $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                })

        st.download_button(
            "↓ Export LMP Analysis",
            data=to_csv_bytes(summ),
            file_name="lmp_analysis.csv", mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error reading LMP file: {e}")


# ─────────────────────────────────────────────────────────────────
# Resolved buses card renderer (shared)
# ─────────────────────────────────────────────────────────────────
def render_ercot_card(sub_name, sub_df):
    buses     = sub_df["Bus"].tolist()
    zones     = sub_df["Zone"].unique().tolist()
    kvs       = sorted(sub_df["kV"].unique().tolist(), key=lambda x: -float(x) if x else 0)
    psse_nums = sub_df["PSSE #"].tolist()
    rn_list   = sub_df[sub_df["Resource Node"]!=""]["Resource Node"].tolist()
    hubs      = sub_df[sub_df["Hub"]!=""]["Hub"].unique().tolist()

    bus_tags  = "".join(f'<span class="tag-bus">{b}</span>' for b in buses[:30])
    more_b    = f'<span style="color:#3a5070;font-size:11px;font-family:IBM Plex Mono,monospace">+{len(buses)-30} more</span>' if len(buses)>30 else ""
    zone_tags = "".join(f'<span class="tag-zone">{z}</span>' for z in zones)
    psse_tags = "".join(f'<span class="tag-psse">{p}</span>' for p in psse_nums[:20])
    more_p    = f'<span style="color:#3a5070;font-size:11px;font-family:IBM Plex Mono,monospace">+{len(psse_nums)-20} more</span>' if len(psse_nums)>20 else ""
    hub_tags  = "".join(f'<span class="tag-hub">{h}</span>' for h in hubs) if hubs else '<span style="color:#3a5070;font-size:11px;font-family:IBM Plex Mono,monospace">—</span>'
    kv_tags   = "".join(f'<span class="kv {kv_cls(k)}">{k} kV</span>' for k in kvs)
    rn_tags   = "".join(f'<span class="tag-rn">{r}</span>' for r in rn_list[:10])
    more_rn   = f'<span style="color:#3a5070;font-size:11px;font-family:IBM Plex Mono,monospace">+{len(rn_list)-10} more</span>' if len(rn_list)>10 else ""

    st.markdown(f"""
    <div class="ercot-card">
        <h3>⚡ ERCOT Substation: {sub_name}</h3>
        <div class="dg">
            <div class="di"><div class="dl">Total Buses</div><div class="dv" style="color:#00d4ff">{len(buses)}</div></div>
            <div class="di"><div class="dl">Voltage(s)</div><div class="dv">{kv_tags}</div></div>
            <div class="di"><div class="dl">Zone(s)</div><div class="dv">{zone_tags}</div></div>
            <div class="di"><div class="dl">Hub(s)</div><div class="dv">{hub_tags}</div></div>
            <div class="di"><div class="dl">Resource Nodes</div><div class="dv" style="color:#39d353">{len(rn_list)}</div></div>
        </div>
        <div style="margin-bottom:10px">
            <div class="dl" style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:.15em;text-transform:uppercase;margin-bottom:5px">Bus Names (Settlement Points)</div>
            <div class="tag-row">{bus_tags}{more_b}</div>
        </div>
        <div style="margin-bottom:10px">
            <div class="dl" style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:.15em;text-transform:uppercase;margin-bottom:5px">PSSE Bus Numbers</div>
            <div class="tag-row">{psse_tags}{more_p}</div>
        </div>
        {'<div><div class="dl" style="font-family:IBM Plex Mono,monospace;font-size:9px;color:#3a5070;letter-spacing:.15em;text-transform:uppercase;margin-bottom:5px">Resource Nodes</div><div class="tag-row">' + rn_tags + more_rn + '</div></div>' if rn_list else ''}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:14px 0 16px">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#00d4ff;
             letter-spacing:.2em;text-transform:uppercase;margin-bottom:5px">⚡ SunStripe · ERCOT</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:15px;font-weight:600;
             color:#e8f0f8;line-height:1.4">Nodal Analysis<br><span style="color:#00d4ff">Platform</span></div>
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
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;
         letter-spacing:.15em;text-transform:uppercase;margin-bottom:10px">Dataset · Feb 2026</div>
    <div style="display:flex;flex-direction:column;gap:9px">
        <div><div style="font-size:17px;font-weight:600;color:#00d4ff">{len(df):,}</div>
             <div style="font-size:10px;color:#3a5070">Settlement Points</div></div>
        <div><div style="font-size:17px;font-weight:600;color:#ff6b35">{df["Substation"].nunique():,}</div>
             <div style="font-size:10px;color:#3a5070">Substations</div></div>
        <div><div style="font-size:17px;font-weight:600;color:#ffcc00">{df[df["Hub"]!=""]["Hub"].nunique()}</div>
             <div style="font-size:10px;color:#3a5070">Hubs</div></div>
        <div><div style="font-size:17px;font-weight:600;color:#39d353">{df[df["Resource Node"]!=""].shape[0]:,}</div>
             <div style="font-size:10px;color:#3a5070">Resource Nodes</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <a href="https://ercot-bess-dashboard-nhh9eztsqeuqxxuz97kacu.streamlit.app/" target="_blank"
       style="display:block;padding:7px 10px;background:#192030;border-radius:4px;
              font-family:'IBM Plex Mono',monospace;font-size:11px;color:#6b8aaa;
              text-decoration:none;margin-bottom:5px">⚡ ERCOT BESS Dashboard ↗</a>
    <a href="https://fatal-flaw-o7aks4agtoffgyydbvrguj.streamlit.app/" target="_blank"
       style="display:block;padding:7px 10px;background:#192030;border-radius:4px;
              font-family:'IBM Plex Mono',monospace;font-size:11px;color:#6b8aaa;
              text-decoration:none">🌿 SiteIQ Fatal Flaw ↗</a>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ██████████████████████  PAGE 1: INFRASTRUCTURE MAP  ██████████████████████
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🗺️ Infrastructure Map":

    st.markdown("""
    <div class="page-header">
        <div class="tag">⚡ SunStripe · ERCOT</div>
        <h1>INFRASTRUCTURE <span>MAP</span></h1>
    </div>
    """, unsafe_allow_html=True)

    # ── Init session state ──────────────────────────────────────────
    for key, default in [
        ("map_center",   [31.5, -97.5]),
        ("map_zoom",     7),
        ("click_point",  None),
        ("osm_nearby",   []),
        ("osm_selected", None),
        ("ercot_sel_sub", None),
        ("ercot_matches", []),
        ("overpass_err", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Top bar: geocode search ─────────────────────────────────────
    col_search, col_go = st.columns([5, 1])
    with col_search:
        loc_input = st.text_input(
            "Navigate to location",
            placeholder="Type a city, town, or coordinates (e.g. 'Wichita Falls TX' or '33.79,-98.57')",
            label_visibility="collapsed",
            key="loc_input"
        )
    with col_go:
        go_btn = st.button("Go →", use_container_width=True, key="go_btn")

    if go_btn and loc_input.strip():
        coord_m = re.match(r"^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$", loc_input.strip())
        if coord_m:
            st.session_state.map_center = [float(coord_m.group(1)), float(coord_m.group(2))]
            st.session_state.map_zoom   = 12
        else:
            try:
                geo = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": loc_input, "format": "json", "limit": 1, "countrycodes": "us"},
                    headers={"User-Agent": "SunStripe-ERCOT/1.0"}, timeout=8
                ).json()
                if geo:
                    st.session_state.map_center = [float(geo[0]["lat"]), float(geo[0]["lon"])]
                    st.session_state.map_zoom   = 12
                    st.success(f"📍 {geo[0]['display_name'].split(',')[0]}")
                else:
                    st.warning("Location not found.")
            except Exception as e:
                st.warning(f"Geocoding error: {e}")

    # ── Hint bar ────────────────────────────────────────────────────
    st.markdown("""
    <div class="hint-bar">
        <span style="color:#00d4ff">ℹ</span>
        <span>Navigate the map to your area of interest · Zoom in to see substations on the power layer ·
        <strong style="color:#e8f0f8">Click anywhere</strong> on or near a substation to identify it</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Map | Info panel layout ─────────────────────────────────────
    map_col, info_col = st.columns([3, 2], gap="medium")

    with map_col:
        m = build_infrastructure_map(
            center_lat   = st.session_state.map_center[0],
            center_lon   = st.session_state.map_center[1],
            zoom         = st.session_state.map_zoom,
            click_marker = st.session_state.click_point,
            nearby_subs  = st.session_state.osm_nearby,
            selected_sub = st.session_state.osm_selected,
        )

        map_data = st_folium(
            m,
            key="infra_map",
            use_container_width=True,
            height=560,
            returned_objects=["last_clicked", "center", "zoom"],
        )

        # Legend
        st.markdown("""
        <div style="display:flex;gap:14px;flex-wrap:wrap;font-family:'IBM Plex Mono',monospace;
             font-size:10px;color:#3a5070;margin-top:6px;padding:6px 10px;
             background:#0a0e14;border:1px solid #1e2d42;border-radius:4px;">
            <span>● <span style="color:#ff9933">345 kV</span></span>
            <span>● <span style="color:#ffcc00">230 kV</span></span>
            <span>● <span style="color:#00d4ff">138 kV</span></span>
            <span>● <span style="color:#39d353">69 kV</span></span>
            <span>● <span style="color:#8899aa">&lt;69 kV</span></span>
            <span style="margin-left:8px;color:#1e4060">Enable "⚡ Power Infrastructure" layer to see lines</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Process map click ───────────────────────────────────────────
    if map_data and map_data.get("last_clicked"):
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lon = map_data["last_clicked"]["lng"]

        # Only re-query if click point changed meaningfully (>50m)
        prev = st.session_state.click_point
        moved = (prev is None or
                 haversine(prev[0], prev[1], clicked_lat, clicked_lon) > 0.05)

        if moved:
            st.session_state.click_point  = [clicked_lat, clicked_lon]
            st.session_state.osm_selected = None
            st.session_state.ercot_sel_sub = None
            st.session_state.ercot_matches = []

            with info_col:
                with st.spinner("Finding substations near click..."):
                    subs, err = fetch_near_click(clicked_lat, clicked_lon, radius_deg=0.12)
                st.session_state.osm_nearby  = subs
                st.session_state.overpass_err = err

            st.rerun()

    # ── Info panel ──────────────────────────────────────────────────
    with info_col:

        if st.session_state.overpass_err:
            st.error(st.session_state.overpass_err)

        if not st.session_state.click_point:
            st.markdown("""
            <div class="map-placeholder">
                <div class="mp-icon">🗺️</div>
                <div class="mp-title">No location selected</div>
                <div class="mp-sub">
                    Navigate the map using the <strong>⚡ Power Infrastructure</strong>
                    tile layer to see substations and lines, then
                    <strong>click</strong> on a substation to identify it.
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif st.session_state.osm_nearby is not None:
            cp = st.session_state.click_point
            n_found = len(st.session_state.osm_nearby)

            st.markdown(f"""
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                 color:#3a5070;margin-bottom:10px;">
                📍 Click: <span style="color:#e8f0f8">{cp[0]:.4f}, {cp[1]:.4f}</span>
                &nbsp;·&nbsp; Found <span style="color:#00d4ff">{n_found}</span> substation(s) nearby
            </div>
            """, unsafe_allow_html=True)

            if n_found == 0:
                st.markdown("""
                <div class="map-placeholder" style="padding:24px">
                    <div class="mp-icon">🔍</div>
                    <div class="mp-sub">No OSM substations found within ~13 km.<br>
                    Try clicking closer to a substation symbol on the map,<br>
                    or zoom in and try again.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # ── Substation selector ─────────────────────────
                st.markdown('<div class="section-label">Nearby Substations</div>', unsafe_allow_html=True)

                osm_opts = {}
                for s in st.session_state.osm_nearby[:8]:
                    name = s.get("name") or "Unnamed Substation"
                    try:
                        v = float(s.get("voltage","0").split(";")[0]) / 1000
                        v_str = f"{v:.0f} kV"
                    except:
                        v_str = "? kV"
                    dist = haversine(cp[0], cp[1], s["lat"], s["lon"])
                    label = f"{name}  ·  {v_str}  ·  {dist:.1f} km"
                    osm_opts[label] = s

                sel_label = st.radio(
                    "Select substation",
                    list(osm_opts.keys()),
                    label_visibility="collapsed",
                    key="osm_radio",
                )
                chosen_osm = osm_opts[sel_label]

                if chosen_osm != st.session_state.osm_selected:
                    st.session_state.osm_selected  = chosen_osm
                    st.session_state.ercot_sel_sub = None
                    st.session_state.ercot_matches = []

                # ── OSM details ─────────────────────────────────
                osm_name = chosen_osm.get("name","") or "Unnamed"
                osm_volt = chosen_osm.get("voltage","")
                try:
                    v_kv = float(osm_volt.split(";")[0]) / 1000
                    v_label = f"{v_kv:.0f} kV"
                except:
                    v_label = osm_volt or "Unknown"

                st.markdown(f"""
                <div class="osm-card">
                    <div class="oc-title">📡 {osm_name}</div>
                    <div class="oc-grid">
                        <div class="oc-item">
                            <div class="oc-lbl">OSM Voltage</div>
                            <div class="oc-val">{v_label}</div>
                        </div>
                        <div class="oc-item">
                            <div class="oc-lbl">Operator</div>
                            <div class="oc-val">{chosen_osm.get("operator","—") or "—"}</div>
                        </div>
                        <div class="oc-item">
                            <div class="oc-lbl">Coordinates</div>
                            <div class="oc-val">{chosen_osm["lat"]:.4f}, {chosen_osm["lon"]:.4f}</div>
                        </div>
                        <div class="oc-item">
                            <div class="oc-lbl">Ref</div>
                            <div class="oc-val">{chosen_osm.get("ref","—") or "—"}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Match to ERCOT ──────────────────────────────
                st.markdown('<div class="section-label">Match to ERCOT CSV</div>', unsafe_allow_html=True)

                matches = match_to_ercot(osm_name, osm_volt)

                if not matches:
                    st.warning(f"No ERCOT match found for **{osm_name}**. Try searching by substation name in the Substation Lookup page.")
                else:
                    match_names = [m[0] for m in matches]
                    scores      = {m[0]: m[1] for m in matches}

                    # Auto-select top match; allow override
                    if st.session_state.ercot_sel_sub not in match_names:
                        st.session_state.ercot_sel_sub = match_names[0]

                    if len(matches) > 1:
                        def fmt_opt(name):
                            s = scores[name]
                            conf = "HIGH" if s >= 30 else "MED" if s >= 15 else "LOW"
                            sub_row = df[df["Substation"]==name].iloc[0] if len(df[df["Substation"]==name]) else None
                            kvs = "/".join(sorted(df[df["Substation"]==name]["kV"].unique(), key=lambda x:-float(x) if x else 0)[:2]) if sub_row is not None else ""
                            return f"{name}  [{kvs} kV]  conf:{conf}"

                        chosen_ercot = st.selectbox(
                            "ERCOT match",
                            match_names,
                            format_func=fmt_opt,
                            index=0,
                            label_visibility="collapsed",
                            key="ercot_match_sel"
                        )
                        st.session_state.ercot_sel_sub = chosen_ercot
                    else:
                        st.session_state.ercot_sel_sub = match_names[0]
                        score = scores[match_names[0]]
                        conf  = "HIGH" if score >= 30 else "MED" if score >= 15 else "LOW"
                        conf_cls = "conf-high" if conf=="HIGH" else "conf-med" if conf=="MED" else "conf-low"
                        st.markdown(f"""
                        <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                             color:#3a5070;margin-bottom:6px;">
                            Best match: <span style="color:#ff6b35">{match_names[0]}</span>
                            &nbsp;·&nbsp; confidence: <span class="{conf_cls}">{conf}</span>
                        </div>
                        """, unsafe_allow_html=True)

    # ── Below the map: full ERCOT data + LMP ───────────────────────
    sel_sub = st.session_state.get("ercot_sel_sub")
    if sel_sub:
        sub_df = df[df["Substation"] == sel_sub].copy()

        st.markdown("---")
        render_ercot_card(sel_sub, sub_df)

        # Full table
        disp = ["Substation","Bus","kV","Zone","PSSE #","PSSE Name","Resource Node","Hub"]
        st.dataframe(
            sub_df[disp].sort_values(["kV"],ascending=[False]).reset_index(drop=True),
            use_container_width=True,
            height=min(320, 40 + len(sub_df)*35),
            column_config={
                "kV":   st.column_config.TextColumn(width="small"),
                "Zone": st.column_config.TextColumn(width="small"),
            }
        )

        c1, c2 = st.columns([1, 5])
        with c1:
            st.download_button(
                "↓ Export Bus List",
                data=to_csv_bytes(sub_df[disp]),
                file_name=f"ercot_{sel_sub}.csv", mime="text/csv"
            )
        with c2:
            st.info(f"💡 {len(sub_df)} buses found at **{sel_sub}**. Upload LMP data below to analyse prices.")

        st.markdown("---")
        render_lmp_section(sub_df, key_prefix="map_lmp")


# ═══════════════════════════════════════════════════════════════════════════════
# ██████████████████████  PAGE 2: NODE & HUB SELECTOR  █████████████████████
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚡ Node & Hub Selector":

    st.markdown("""
    <div class="page-header">
        <div class="tag">⚡ SunStripe · ERCOT</div>
        <h1>NODE & HUB <span>SELECTOR</span></h1>
    </div>
    <p>Filter by voltage → pick substations → auto-resolve Bus Names, Zones & PSSE numbers → upload DAM LMP data.</p>
    """, unsafe_allow_html=True)

    # Step 1: kV
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
    kv_tag = f'<span class="kv {kv_cls(sel_kv) if sel_kv != "All" else "kv-138"}">{sel_kv} kV</span>'
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#3a5070;margin:6px 0 4px">{kv_tag} → <span style="color:#e8f0f8">{len(df_kv):,}</span> settlement points | <span style="color:#e8f0f8">{df_kv["Substation"].nunique():,}</span> substations</div>', unsafe_allow_html=True)

    # Step 2: Substation
    st.markdown('<div class="section-label"><span class="step-badge">2</span> Select Substation(s)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c2:
        zone_pre = st.selectbox("Zone", ["All Zones","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"], key="zone_pre2")
    df_filt = df_kv[df_kv["Zone"] == zone_pre] if zone_pre != "All Zones" else df_kv
    sub_list = sorted(df_filt["Substation"].dropna().unique().tolist())
    with c1:
        selected_subs = st.multiselect("Substations", options=sub_list,
            placeholder=f"Choose from {len(sub_list):,} substations...", label_visibility="collapsed")

    if not selected_subs:
        st.markdown('<div style="text-align:center;padding:52px 20px;color:#3a5070;font-family:IBM Plex Mono,monospace;background:#0f1a24;border:1px dashed #1e2d42;border-radius:6px;margin-top:8px"><div style="font-size:32px;margin-bottom:10px">🏭</div>Select substations above to auto-resolve buses, zones & PSSE numbers</div>', unsafe_allow_html=True)
        st.stop()

    resolved = df_kv[df_kv["Substation"].isin(selected_subs)].copy()

    # Step 3: Cards
    st.markdown('<div class="section-label"><span class="step-badge">3</span> Resolved Buses · Zones · PSSE Numbers</div>', unsafe_allow_html=True)
    for sub in selected_subs:
        render_ercot_card(sub, resolved[resolved["Substation"] == sub])

    disp_cols = ["Substation","Bus","kV","Zone","PSSE #","PSSE Name","Resource Node","Hub","Node"]
    st.markdown(f"**{len(resolved):,}** buses across **{len(selected_subs)}** substation(s)")
    st.dataframe(
        resolved[disp_cols].sort_values(["Substation","kV"], ascending=[True,False]).reset_index(drop=True),
        use_container_width=True, height=min(380, 40+len(resolved)*35),
        column_config={"kV": st.column_config.TextColumn(width="small"), "Zone": st.column_config.TextColumn(width="small")}
    )
    st.download_button("↓ Export Bus List", data=to_csv_bytes(resolved[disp_cols]),
        file_name=f"ercot_nodes_{'_'.join(selected_subs[:3])}.csv", mime="text/csv")

    st.markdown("---")
    render_lmp_section(resolved, key_prefix="sel_lmp")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: BUS LOOKUP
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Bus Lookup":
    st.markdown('<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>BUS <span>LOOKUP</span></h1></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1: bus_q = st.text_input("Bus Name", placeholder="e.g. 0001, BUCKRA, CAMPBELLSW...", key="bus_q")
    with c2: bus_zone = st.selectbox("Zone", ["All Zones","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"])
    if bus_q.strip():
        q = bus_q.strip().upper()
        mask = df["Bus"].str.upper().str.contains(q, na=False) | df["PSSE Name"].str.upper().str.contains(q, na=False)
        if bus_zone != "All Zones": mask &= df["Zone"] == bus_zone
        results = df[mask]
        exact = df[df["Bus"].str.upper() == q]
        if not exact.empty:
            r = exact.iloc[0]
            st.markdown(f'<div class="ercot-card"><h3>▶ {r["Bus"]}</h3><div class="dg"><div class="di"><div class="dl">Substation</div><div class="dv" style="color:#ff6b35">{r["Substation"]}</div></div><div class="di"><div class="dl">Voltage</div><div class="dv"><span class="kv {kv_cls(r["kV"])}">{r["kV"]} kV</span></div></div><div class="di"><div class="dl">Zone</div><div class="dv" style="color:#39d353">{r["Zone"]}</div></div><div class="di"><div class="dl">PSSE Name</div><div class="dv">{r["PSSE Name"] or "—"}</div></div><div class="di"><div class="dl">PSSE #</div><div class="dv">{r["PSSE #"] or "—"}</div></div><div class="di"><div class="dl">Resource Node</div><div class="dv">{r["Resource Node"] or "—"}</div></div><div class="di"><div class="dl">Hub</div><div class="dv">{r["Hub"] or "—"}</div></div></div></div>', unsafe_allow_html=True)
        st.markdown(f"**{len(results):,}** results for `{bus_q.strip()}`")
        disp = ["Bus","PSSE Name","kV","Substation","Zone","Resource Node","PSSE #"]
        st.dataframe(results[disp].reset_index(drop=True), use_container_width=True, height=min(400,40+len(results)*35))
        if len(results): st.download_button("↓ Export CSV", data=to_csv_bytes(results[disp]), file_name=f"bus_{bus_q.strip()}.csv", mime="text/csv")
    else:
        st.markdown('<div style="text-align:center;padding:60px;color:#3a5070;font-family:IBM Plex Mono,monospace"><div style="font-size:36px;margin-bottom:12px">⚡</div>Enter a bus name above</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: SUBSTATION LOOKUP
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🏭 Substation Lookup":
    st.markdown('<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>SUBSTATION <span>LOOKUP</span></h1></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1: sub_q = st.text_input("Substation Name", placeholder="e.g. LOOKOUT, CAMPBELL, VICTORIA...")
    with c2:
        kv_opts = ["All kV"] + sorted(df["kV"].dropna().unique().tolist(), key=lambda x: -float(x) if x else 0)
        sub_kv = st.selectbox("Voltage", kv_opts)
    if sub_q.strip():
        q = sub_q.strip().upper()
        mask = df["Substation"].str.upper().str.contains(q, na=False)
        if sub_kv != "All kV": mask &= df["kV"] == sub_kv
        results = df[mask]
        exact = df[df["Substation"].str.upper() == q]
        if not exact.empty:
            render_ercot_card(exact.iloc[0]["Substation"], exact)
        st.markdown(f"**{len(results):,}** results for `{sub_q.strip()}`")
        disp = ["Substation","Bus","kV","Zone","PSSE #","PSSE Name","Resource Node"]
        st.dataframe(results[disp].reset_index(drop=True), use_container_width=True, height=min(400,40+len(results)*35))
        if len(results): st.download_button("↓ Export CSV", data=to_csv_bytes(results[disp]), file_name=f"sub_{sub_q.strip()}.csv", mime="text/csv")
    else:
        st.markdown('<div style="text-align:center;padding:60px;color:#3a5070;font-family:IBM Plex Mono,monospace"><div style="font-size:36px;margin-bottom:12px">🏭</div>Enter a substation name above</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5: BROWSE ALL
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Browse All":
    st.markdown('<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>BROWSE <span>ALL</span></h1></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
    with c1: bq  = st.text_input("Search", placeholder="Bus, PSSE Name, Substation...")
    with c2: bz  = st.selectbox("Zone",    ["All","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"])
    with c3:
        bkv_opts = ["All kV"] + sorted(df["kV"].dropna().unique().tolist(), key=lambda x: -float(x) if x else 0)
        bkv = st.selectbox("kV", bkv_opts)
    with c4: brn = st.selectbox("Type",    ["All","Resource Nodes","Hubs"])
    f = df.copy()
    if bq.strip():
        q = bq.strip().upper()
        f = f[f["Bus"].str.upper().str.contains(q,na=False)|f["PSSE Name"].str.upper().str.contains(q,na=False)|f["Substation"].str.upper().str.contains(q,na=False)]
    if bz  != "All":    f = f[f["Zone"] == bz]
    if bkv != "All kV": f = f[f["kV"]   == bkv]
    if brn == "Resource Nodes": f = f[f["Resource Node"] != ""]
    elif brn == "Hubs":         f = f[f["Hub"] != ""]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Records",     f"{len(f):,}")
    m2.metric("Substations", f"{f['Substation'].nunique():,}")
    m3.metric("kV Levels",   f"{f['kV'].nunique()}")
    m4.metric("Res. Nodes",  f"{f[f['Resource Node']!=''].shape[0]:,}")
    disp = ["Bus","PSSE Name","kV","Substation","Zone","Resource Node","Hub","PSSE #"]
    st.dataframe(f[disp].reset_index(drop=True), use_container_width=True, height=500)
    st.download_button("↓ Export CSV", data=to_csv_bytes(f[disp]), file_name="ercot_browse.csv", mime="text/csv")
