import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import re

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

.page-header { border-bottom: 1px solid #1e2d42; padding-bottom: 14px; margin-bottom: 18px; }
.page-header .tag { font-family:'IBM Plex Mono',monospace; font-size:10px; color:#00d4ff; letter-spacing:.2em; text-transform:uppercase; margin-bottom:4px; }
.page-header h1 { font-family:'IBM Plex Mono',monospace; font-size:22px; font-weight:600; color:#e8f0f8; margin:0; }
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

.detail-card {
    background:#111720; border:1px solid rgba(0,212,255,0.2);
    border-left:3px solid #00d4ff; border-radius:6px; padding:14px 18px; margin-bottom:12px;
}
.detail-card h3 { font-family:'IBM Plex Mono',monospace; font-size:14px; font-weight:600; color:#ff6b35; margin:0 0 10px; }
.dg { display:flex; flex-wrap:wrap; gap:12px; margin-bottom:8px; }
.di .dl { font-family:'IBM Plex Mono',monospace; font-size:9px; color:#3a5070; letter-spacing:.15em; text-transform:uppercase; }
.di .dv { font-family:'IBM Plex Mono',monospace; font-size:12px; font-weight:500; color:#e8f0f8; margin-top:2px; }

.tag-row { display:flex; flex-wrap:wrap; gap:5px; margin-top:4px; }
.tag-bus  { display:inline-block; padding:2px 8px; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:500; background:rgba(0,212,255,0.08); border:1px solid rgba(0,212,255,0.25); color:#00d4ff; }
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

.map-info-card {
    background:#0f1a24; border:1px solid #1e2d42; border-radius:6px;
    padding:12px 16px; margin-bottom:10px; font-family:'IBM Plex Mono',monospace;
}
.map-info-card .mic-title { font-size:11px; color:#3a5070; letter-spacing:.1em; text-transform:uppercase; margin-bottom:6px; }
.map-info-card .mic-val { font-size:13px; color:#e8f0f8; font-weight:500; }

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
# Data loading
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading ERCOT settlement points...")
def load_data():
    df = pd.read_csv("Settlement_Points_02202026_094122.csv", dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "ELECTRICAL_BUS":    "Bus",
        "NODE_NAME":         "Node",
        "PSSE_BUS_NAME":     "PSSE Name",
        "VOLTAGE_LEVEL":     "kV",
        "SUBSTATION":        "Substation",
        "SETTLEMENT_LOAD_ZONE": "Zone",
        "RESOURCE_NODE":     "Resource Node",
        "HUB_BUS_NAME":      "Hub Bus",
        "HUB":               "Hub",
        "PSSE_BUS_NUMBER":   "PSSE #",
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
# Substation matching helpers
# ─────────────────────────────────────────────
def normalize_sub(name):
    """Normalize substation name for fuzzy matching."""
    name = name.upper().strip()
    # Remove common suffixes
    for pat in [r'\bSUBSTATION\b', r'\bSUBSTATION\b', r'\bSWITCHING\b',
                r'\bSWITCH\b', r'\bSWTC?\b', r'\bSTATION\b', r'\bSTA\b',
                r'\bELECTRIC\b', r'\bELEC\b', r'\bSUB\b', r'\bSS\b',
                r'\bTRANSMISSION\b', r'\bTRANS\b', r'\bKV\b', r'\d+']:
        name = re.sub(pat, '', name)
    name = re.sub(r'[^A-Z ]', '', name).strip()
    return name

@st.cache_data(show_spinner=False)
def build_match_index():
    """Build a lookup: normalized_token -> list of ERCOT substation names."""
    index = {}
    for sub in df["Substation"].unique():
        if not sub:
            continue
        # Index by substation abbreviation
        key = sub.upper().strip()
        index.setdefault(key, []).append(sub)
        # Also index by PSSE bus name tokens for this substation
    # Index by PSSE names (contains real location names like BOWIE, CAMPBELL etc)
    for _, row in df[["Substation","PSSE Name"]].drop_duplicates().iterrows():
        psse = row["PSSE Name"].upper().strip()
        sub  = row["Substation"]
        # Extract alpha prefix from PSSE name (e.g. "BOWIE8" -> "BOWIE")
        token = re.sub(r'[^A-Z]', '', psse.split('_')[0])[:12]
        if len(token) >= 3:
            index.setdefault(token, []).append(sub)
    return index

match_index = build_match_index()

def match_osm_to_ercot(osm_name, osm_voltage=None):
    """
    Given an OSM substation name and optional voltage string,
    return list of matching ERCOT substation names ranked by confidence.
    """
    if not osm_name:
        return []

    osm_norm = normalize_sub(osm_name)
    tokens   = [t for t in osm_norm.split() if len(t) >= 3]

    candidates = {}
    for token in tokens:
        # Exact token match
        for key, subs in match_index.items():
            score = 0
            if key == token:
                score = 10
            elif token in key and len(token) >= 4:
                score = 5
            elif key in token and len(key) >= 4:
                score = 4
            if score > 0:
                for s in subs:
                    candidates[s] = candidates.get(s, 0) + score

    # Also try matching against PSSE Names directly
    osm_upper = osm_name.upper()
    for _, row in df[["Substation","PSSE Name"]].drop_duplicates().iterrows():
        psse = row["PSSE Name"].upper()
        sub  = row["Substation"]
        clean_osm = re.sub(r'[^A-Z]', '', osm_upper)[:8]
        clean_psse = re.sub(r'[^A-Z]', '', psse)[:8]
        if clean_osm and clean_psse and (clean_osm[:5] in clean_psse or clean_psse[:5] in clean_osm):
            candidates[sub] = candidates.get(sub, 0) + 8

    # Voltage bonus
    if osm_voltage and candidates:
        for sub in list(candidates.keys()):
            sub_kvs = df[df["Substation"] == sub]["kV"].tolist()
            osm_v_str = str(osm_voltage).split(";")[0].strip()
            try:
                osm_v = float(osm_v_str) / 1000  # OSM stores in Volts
                if any(abs(float(kv) - osm_v) < 5 for kv in sub_kvs if kv):
                    candidates[sub] = candidates.get(sub, 0) + 6
            except:
                pass

    ranked = sorted(candidates.items(), key=lambda x: -x[1])
    return [s for s, score in ranked if score >= 4][:5]


# ─────────────────────────────────────────────
# Overpass query
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_substations_overpass(south, west, north, east):
    """Fetch power substations from Overpass API for a bounding box."""
    query = f"""
[out:json][timeout:30];
(
  node["power"="substation"]({south},{west},{north},{east});
  way["power"="substation"]({south},{west},{north},{east});
  relation["power"="substation"]({south},{west},{north},{east});
);
out center tags;
"""
    try:
        resp = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=35,
            headers={"User-Agent": "SunStripe-ERCOT/1.0"}
        )
        resp.raise_for_status()
        data = resp.json()
        elements = []
        for el in data.get("elements", []):
            lat = el.get("lat") or (el.get("center") or {}).get("lat")
            lon = el.get("lon") or (el.get("center") or {}).get("lon")
            if lat and lon:
                tags = el.get("tags", {})
                elements.append({
                    "lat": lat,
                    "lon": lon,
                    "name": tags.get("name", ""),
                    "voltage": tags.get("voltage", ""),
                    "operator": tags.get("operator", ""),
                    "osm_id": el.get("id", ""),
                    "osm_type": el.get("type", ""),
                })
        return elements, None
    except requests.exceptions.Timeout:
        return [], "Overpass API timed out. Try a smaller area."
    except Exception as e:
        return [], f"Overpass API error: {e}"


# ─────────────────────────────────────────────
# Map builder
# ─────────────────────────────────────────────
def build_map(center_lat=31.5, center_lon=-97.5, zoom=7, substations=None, selected_osm_id=None):
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles=None,
        prefer_canvas=True,
    )

    # Dark base layer
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
        name="Dark Base",
        overlay=False,
        control=True,
        max_zoom=20,
    ).add_to(m)

    # OpenInfraMap power layer
    folium.TileLayer(
        tiles="https://tiles.openinframap.org/power_medium/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://openinframap.org">OpenInfraMap</a>',
        name="Power Infrastructure (OpenInfraMap)",
        overlay=True,
        control=True,
        opacity=0.85,
        max_zoom=17,
    ).add_to(m)

    # High-voltage lines layer
    folium.TileLayer(
        tiles="https://tiles.openinframap.org/power_high/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://openinframap.org">OpenInfraMap</a>',
        name="HV Lines (OpenInfraMap)",
        overlay=True,
        control=True,
        opacity=0.7,
        max_zoom=17,
    ).add_to(m)

    # Plot Overpass substations
    if substations:
        for sub in substations:
            is_selected = (str(sub.get("osm_id")) == str(selected_osm_id))

            volt_str = sub.get("voltage", "")
            try:
                volt_kv = float(volt_str.split(";")[0]) / 1000
                if volt_kv >= 345:   color = "#ff9933"
                elif volt_kv >= 230: color = "#ffcc00"
                elif volt_kv >= 138: color = "#00d4ff"
                elif volt_kv >= 69:  color = "#39d353"
                else:                color = "#6b8aaa"
            except:
                color = "#6b8aaa"
                volt_kv = None

            radius = 10 if is_selected else 7
            fill_opacity = 0.95 if is_selected else 0.75
            border_color = "#ffffff" if is_selected else color

            name = sub.get("name") or "Unnamed"
            volt_label = f"{volt_kv:.0f} kV" if volt_kv else "? kV"
            operator   = sub.get("operator", "")

            popup_html = f"""
            <div style="font-family:'IBM Plex Mono',monospace;background:#111720;color:#e8f0f8;padding:10px;border-radius:4px;min-width:180px;border:1px solid #1e2d42;">
                <div style="font-size:13px;font-weight:600;color:#ff6b35;margin-bottom:6px">{name}</div>
                <div style="font-size:10px;color:#3a5070;margin-bottom:2px">VOLTAGE</div>
                <div style="font-size:12px;margin-bottom:6px">{volt_label}</div>
                {'<div style="font-size:10px;color:#3a5070;margin-bottom:2px">OPERATOR</div><div style="font-size:11px;margin-bottom:6px">' + operator + '</div>' if operator else ''}
                <div style="font-size:10px;color:#3a5070">OSM ID: {sub.get("osm_id","")}</div>
            </div>
            """

            tooltip_html = f"<b>{name}</b><br>{volt_label}"

            folium.CircleMarker(
                location=[sub["lat"], sub["lon"]],
                radius=radius,
                color=border_color,
                weight=2 if is_selected else 1,
                fill=True,
                fill_color=color,
                fill_opacity=fill_opacity,
                popup=folium.Popup(popup_html, max_width=240),
                tooltip=tooltip_html,
            ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    # ERCOT bounding box guide
    folium.Rectangle(
        bounds=[[25.8, -106.7], [36.5, -93.5]],
        color="#00d4ff",
        weight=1,
        fill=False,
        dash_array="6 4",
        tooltip="ERCOT Grid Approximate Boundary",
    ).add_to(m)

    return m


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
        "🗺️ Infrastructure Map",
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


# ═══════════════════════════════════════════════════════════════════
# PAGE 1 — Infrastructure Map
# ═══════════════════════════════════════════════════════════════════
if page == "🗺️ Infrastructure Map":

    st.markdown("""
    <div class="page-header">
        <div class="tag">⚡ SunStripe · ERCOT</div>
        <h1>INFRASTRUCTURE <span>MAP</span></h1>
    </div>
    <p>View live power infrastructure from OpenInfraMap. Search substations from OpenStreetMap → auto-match to ERCOT settlement points → analyse LMP prices.</p>
    """, unsafe_allow_html=True)

    # ── Map Controls ────────────────────────────────
    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([2, 1, 1, 1])

    with col_ctrl1:
        map_search = st.text_input(
            "Search location (city, county, coordinates)",
            placeholder="e.g. Wichita Falls, TX  or  33.7944,-98.5706",
            key="map_search",
            label_visibility="collapsed"
        )
    with col_ctrl2:
        kv_map_filter = st.selectbox(
            "Filter substations by kV",
            ["All kV", "345+ kV", "230 kV", "138 kV", "115 kV", "69 kV", "34.5 kV"],
            key="kv_map"
        )
    with col_ctrl3:
        zoom_level = st.selectbox("Zoom", [6, 7, 8, 9, 10, 11, 12], index=2, key="zoom_sel")
    with col_ctrl4:
        fetch_btn = st.button("🔍 Fetch Substations", use_container_width=True, key="fetch_btn")

    # Parse location input
    center_lat, center_lon = 31.5, -97.5
    if map_search.strip():
        # Try coordinate parse first
        coord_match = re.match(r"^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$", map_search.strip())
        if coord_match:
            center_lat = float(coord_match.group(1))
            center_lon = float(coord_match.group(2))
        else:
            # Use Nominatim geocoding
            try:
                geo_resp = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": map_search, "format": "json", "limit": 1, "countrycodes": "us"},
                    headers={"User-Agent": "SunStripe-ERCOT/1.0"},
                    timeout=8
                )
                geo_data = geo_resp.json()
                if geo_data:
                    center_lat = float(geo_data[0]["lat"])
                    center_lon = float(geo_data[0]["lon"])
                    st.success(f"📍 Found: {geo_data[0].get('display_name','').split(',')[0]}")
                else:
                    st.warning("Location not found. Try a different search.")
            except Exception as e:
                st.warning(f"Geocoding unavailable: {e}")

    # Session state for fetched substations
    if "osm_substations" not in st.session_state:
        st.session_state.osm_substations = []
    if "osm_error" not in st.session_state:
        st.session_state.osm_error = None
    if "selected_osm" not in st.session_state:
        st.session_state.selected_osm = None
    if "ercot_matches" not in st.session_state:
        st.session_state.ercot_matches = []

    # Fetch from Overpass
    if fetch_btn:
        delta = {6: 3.0, 7: 2.0, 8: 1.0, 9: 0.5, 10: 0.25, 11: 0.15, 12: 0.08}.get(zoom_level, 1.0)
        south = center_lat - delta
        north = center_lat + delta
        west  = center_lon - delta * 1.5
        east  = center_lon + delta * 1.5

        with st.spinner(f"Fetching substations from OpenStreetMap ({south:.2f},{west:.2f} → {north:.2f},{east:.2f})..."):
            subs, err = fetch_substations_overpass(south, west, north, east)

        if err:
            st.session_state.osm_error = err
            st.session_state.osm_substations = []
        else:
            # Apply kV filter
            if kv_map_filter != "All kV":
                def kv_passes(volt_str):
                    try:
                        v = float(volt_str.split(";")[0]) / 1000
                        if kv_map_filter == "345+ kV":   return v >= 345
                        if kv_map_filter == "230 kV":    return 200 <= v < 345
                        if kv_map_filter == "138 kV":    return 120 <= v < 200
                        if kv_map_filter == "115 kV":    return 100 <= v < 120
                        if kv_map_filter == "69 kV":     return 50  <= v < 100
                        if kv_map_filter == "34.5 kV":   return v < 50
                    except:
                        return True
                    return True
                subs = [s for s in subs if kv_passes(s.get("voltage",""))]

            st.session_state.osm_substations = subs
            st.session_state.osm_error = None
            st.session_state.selected_osm = None
            st.session_state.ercot_matches = []

    # ── Map + Sidebar layout ──────────────────────
    map_col, panel_col = st.columns([3, 2])

    with map_col:
        subs_to_plot = st.session_state.osm_substations
        sel_id = st.session_state.selected_osm.get("osm_id") if st.session_state.selected_osm else None

        m = build_map(
            center_lat=center_lat,
            center_lon=center_lon,
            zoom=zoom_level,
            substations=subs_to_plot,
            selected_osm_id=sel_id,
        )

        map_result = st_folium(m, width=None, height=520, returned_objects=["last_object_clicked_popup", "last_clicked"])

    with panel_col:
        if st.session_state.osm_error:
            st.error(st.session_state.osm_error)

        n_subs = len(st.session_state.osm_substations)
        if n_subs:
            st.markdown(f"""
            <div class="map-info-card">
                <div class="mic-title">Substations Loaded</div>
                <div class="mic-val" style="color:#00d4ff">{n_subs} from OpenStreetMap</div>
            </div>
            """, unsafe_allow_html=True)

            # Substation selector from list
            st.markdown('<div class="section-label">Select Substation</div>', unsafe_allow_html=True)
            sub_options = {
                f"{s.get('name') or 'Unnamed'} [{s.get('voltage','?V')}]": s
                for s in st.session_state.osm_substations
            }
            chosen_label = st.selectbox(
                "Pick from loaded substations",
                options=["— click map or select —"] + list(sub_options.keys()),
                key="sub_picker",
                label_visibility="collapsed"
            )

            if chosen_label != "— click map or select —":
                st.session_state.selected_osm = sub_options[chosen_label]

        # Handle map click (popup click)
        if map_result and map_result.get("last_object_clicked_popup"):
            popup_text = map_result["last_object_clicked_popup"]
            # Find matching substation from popup content
            for s in st.session_state.osm_substations:
                name = s.get("name","")
                if name and name in str(popup_text):
                    st.session_state.selected_osm = s
                    break

        # ── ERCOT Matching ──────────────────────────
        selected = st.session_state.selected_osm
        if selected:
            osm_name = selected.get("name","") or "Unnamed"
            osm_volt = selected.get("voltage","")
            try:
                volt_kv = float(osm_volt.split(";")[0]) / 1000
                volt_label = f"{volt_kv:.0f} kV"
            except:
                volt_label = osm_volt or "?"

            st.markdown(f"""
            <div class="detail-card">
                <h3>▶ {osm_name}</h3>
                <div class="dg">
                    <div class="di"><div class="dl">OSM Voltage</div><div class="dv">{volt_label}</div></div>
                    <div class="di"><div class="dl">Operator</div><div class="dv">{selected.get("operator","—") or "—"}</div></div>
                    <div class="di"><div class="dl">Coords</div><div class="dv">{selected["lat"]:.4f}, {selected["lon"]:.4f}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Find ERCOT matches
            with st.spinner("Matching to ERCOT settlement points..."):
                ercot_matches = match_osm_to_ercot(osm_name, osm_volt)

            if ercot_matches:
                st.markdown('<div class="section-label">ERCOT Matches</div>', unsafe_allow_html=True)

                # Let user pick best match if multiple
                if len(ercot_matches) > 1:
                    ercot_sel = st.selectbox(
                        "Select best ERCOT substation match",
                        ercot_matches,
                        key="ercot_match_sel",
                        label_visibility="collapsed"
                    )
                else:
                    ercot_sel = ercot_matches[0]
                    st.markdown(f"""
                    <div class="map-info-card">
                        <div class="mic-title">Best ERCOT Match</div>
                        <div class="mic-val" style="color:#ff6b35">{ercot_sel}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Show resolved buses
                sub_df = df[df["Substation"] == ercot_sel].copy()
                buses  = sub_df["Bus"].tolist()
                zones  = sub_df["Zone"].unique().tolist()
                kvs    = sorted(sub_df["kV"].unique().tolist(), key=lambda x: -float(x) if x else 0)
                psse_nums = sub_df["PSSE #"].tolist()
                hubs   = sub_df[sub_df["Hub"]!=""]["Hub"].unique().tolist()

                bus_tags  = "".join(f'<span class="tag-bus">{b}</span>' for b in buses[:20])
                more_b    = f'<span style="color:#3a5070;font-family:IBM Plex Mono,monospace;font-size:11px">+{len(buses)-20} more</span>' if len(buses)>20 else ""
                zone_tags = "".join(f'<span class="tag-zone">{z}</span>' for z in zones)
                psse_tags = "".join(f'<span class="tag-psse">{p}</span>' for p in psse_nums[:12])
                more_p    = f'<span style="color:#3a5070;font-family:IBM Plex Mono,monospace;font-size:11px">+{len(psse_nums)-12} more</span>' if len(psse_nums)>12 else ""
                kv_tags   = "".join(f'<span class="kv {kv_cls(k)}">{k} kV</span>' for k in kvs)
                hub_tags  = "".join(f'<span class="tag-hub">{h}</span>' for h in hubs) if hubs else '<span style="color:#3a5070;font-size:11px;font-family:IBM Plex Mono,monospace">—</span>'

                st.markdown(f"""
                <div class="detail-card">
                    <h3>⚡ ERCOT: {ercot_sel}</h3>
                    <div class="dg">
                        <div class="di"><div class="dl">Buses</div><div class="dv" style="color:#00d4ff">{len(buses)}</div></div>
                        <div class="di"><div class="dl">Voltage(s)</div><div class="dv">{kv_tags}</div></div>
                        <div class="di"><div class="dl">Zone(s)</div><div class="dv">{zone_tags}</div></div>
                        <div class="di"><div class="dl">Hub(s)</div><div class="dv">{hub_tags}</div></div>
                    </div>
                    <div style="margin-bottom:8px">
                        <div class="dl" style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:.15em;text-transform:uppercase;margin-bottom:4px">Bus Names</div>
                        <div class="tag-row">{bus_tags}{more_b}</div>
                    </div>
                    <div>
                        <div class="dl" style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:.15em;text-transform:uppercase;margin-bottom:4px">PSSE Numbers</div>
                        <div class="tag-row">{psse_tags}{more_p}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.session_state.ercot_matches = sub_df

            else:
                st.warning(f"No ERCOT settlement point match found for **{osm_name}**. Try selecting a nearby substation or search by name in the Bus/Substation Lookup pages.")
                st.session_state.ercot_matches = []

        elif not n_subs and not st.session_state.osm_error:
            st.markdown("""
            <div style="text-align:center;padding:40px 16px;color:#3a5070;font-family:'IBM Plex Mono',monospace">
                <div style="font-size:28px;margin-bottom:10px">🗺️</div>
                <div style="font-size:12px">Enter a location and click<br><strong style="color:#00d4ff">Fetch Substations</strong><br>to load power infrastructure</div>
            </div>
            """, unsafe_allow_html=True)

    # ── LMP Analysis for map-selected substation ──
    if isinstance(st.session_state.ercot_matches, pd.DataFrame) and len(st.session_state.ercot_matches) > 0:
        resolved = st.session_state.ercot_matches
        st.markdown("---")
        st.markdown('<div class="section-label"><span class="step-badge">+</span> Upload DAM LMP Data for This Substation</div>', unsafe_allow_html=True)
        st.markdown("""<p>Upload ERCOT DAM Hourly LMP CSV to plot prices for the matched buses above.<br>
        <span style="font-size:11px;color:#3a5070;font-family:'IBM Plex Mono',monospace">Source: ERCOT MIS → Prices → DAM Settlement Point Prices</span></p>""", unsafe_allow_html=True)

        lmp_file = st.file_uploader("Upload LMP CSV", type=["csv"], key="map_lmp", label_visibility="collapsed")
        if lmp_file:
            try:
                lmp_raw = pd.read_csv(lmp_file, dtype=str)
                col_u = {c: c.upper().strip() for c in lmp_raw.columns}
                bus_col   = next((c for c,u in col_u.items() if any(k in u for k in ["SETTLEMENT POINT","SETTLEMENTPOINT","BUS","NODE","POINT NAME"])), None)
                price_col = next((c for c,u in col_u.items() if any(k in u for k in ["PRICE","LMP","SPP","SETTLEMENTPOINTPRICE"])), None)
                hour_col  = next((c for c,u in col_u.items() if any(k in u for k in ["HOUR","TIME","DATE","INTERVAL","DELIVERY"])), None)

                if not bus_col or not price_col:
                    all_cols = lmp_raw.columns.tolist()
                    cc1,cc2,cc3 = st.columns(3)
                    bus_col   = cc1.selectbox("Bus column",   all_cols, key="mc_bus")
                    price_col = cc2.selectbox("Price column", all_cols, key="mc_price")
                    hour_col  = cc3.selectbox("Hour column",  [None]+all_cols, key="mc_hour")

                lmp_raw[price_col] = pd.to_numeric(lmp_raw[price_col], errors="coerce")
                resolved_upper = set(resolved["Bus"].str.upper())
                lmp_raw["_bu"] = lmp_raw[bus_col].str.upper().str.strip()
                matched = lmp_raw[lmp_raw["_bu"].isin(resolved_upper)].copy()

                m1,m2,m3,m4 = st.columns(4)
                m1.metric("LMP Rows",    f"{len(lmp_raw):,}")
                m2.metric("Matched",     f"{len(matched):,}")
                m3.metric("Buses Hit",   f"{matched[bus_col].nunique()} / {len(resolved_upper)}")
                avg_p = matched[price_col].mean() if len(matched) else 0
                m4.metric("Avg LMP",     f"${avg_p:.2f}/MWh")

                if len(matched):
                    summary = matched.groupby(bus_col)[price_col].agg(
                        Mean="mean", Max="max", Min="min", Std="std", Count="count"
                    ).reset_index().round(2)
                    summary.columns = ["Bus","Avg ($/MWh)","Max ($/MWh)","Min ($/MWh)","Std Dev","Hours"]
                    summary = summary.merge(resolved[["Bus","kV","Zone","PSSE #"]].drop_duplicates("Bus"), on="Bus", how="left")

                    st.markdown('<div class="section-label">LMP Summary</div>', unsafe_allow_html=True)
                    st.dataframe(summary[["Bus","kV","Zone","Avg ($/MWh)","Max ($/MWh)","Min ($/MWh)","Std Dev","Hours","PSSE #"]],
                        use_container_width=True, height=min(300, 40+len(summary)*35),
                        column_config={
                            "Avg ($/MWh)": st.column_config.NumberColumn(format="$%.2f"),
                            "Max ($/MWh)": st.column_config.NumberColumn(format="$%.2f"),
                            "Min ($/MWh)": st.column_config.NumberColumn(format="$%.2f"),
                        })

                    if hour_col:
                        st.markdown('<div class="section-label">LMP Time Series</div>', unsafe_allow_html=True)
                        try:
                            ts = matched[[hour_col, bus_col, price_col]].copy()
                            ts[hour_col] = pd.to_datetime(ts[hour_col], infer_datetime_format=True, errors="coerce")
                            ts = ts.dropna(subset=[hour_col])
                            pivot = ts.pivot_table(index=hour_col, columns=bus_col, values=price_col, aggfunc="mean")
                            st.line_chart(pivot, height=320)
                        except Exception as e:
                            st.caption(f"Chart error: {e}")

                    st.download_button("↓ Export LMP Analysis",
                        data=to_csv_bytes(summary),
                        file_name=f"lmp_map_{st.session_state.selected_osm.get('name','sub')}.csv",
                        mime="text/csv")
            except Exception as e:
                st.error(f"Error: {e}")

    # Legend
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#3a5070;margin-top:8px;display:flex;gap:16px;flex-wrap:wrap">
        <span>● <span style="color:#ff9933">345 kV</span></span>
        <span>● <span style="color:#ffcc00">230 kV</span></span>
        <span>● <span style="color:#00d4ff">138 kV</span></span>
        <span>● <span style="color:#39d353">69 kV</span></span>
        <span>● <span style="color:#6b8aaa">&lt;69 kV</span></span>
        <span style="margin-left:12px;color:#1e2d42">──── ERCOT boundary (approx)</span>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 2 — Node & Hub Selector
# ═══════════════════════════════════════════════════════════════════
elif page == "⚡ Node & Hub Selector":

    st.markdown("""
    <div class="page-header">
        <div class="tag">⚡ SunStripe · ERCOT</div>
        <h1>NODE & HUB <span>SELECTOR</span></h1>
    </div>
    <p>Filter by voltage → pick substations → auto-resolve Bus Names, Zones & PSSE numbers → upload DAM LMP data for price analysis.</p>
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
    kv_tag = f'<span class="kv {kv_cls(sel_kv) if sel_kv!="All" else "kv-138"}">{sel_kv} kV</span>'
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#3a5070;margin:6px 0 4px">{kv_tag} → <span style="color:#e8f0f8">{len(df_kv):,}</span> points | <span style="color:#e8f0f8">{df_kv["Substation"].nunique():,}</span> substations</div>', unsafe_allow_html=True)

    # Step 2: Substation
    st.markdown('<div class="section-label"><span class="step-badge">2</span> Select Substation(s)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3,1])
    with c2:
        zone_pre = st.selectbox("Zone Filter", ["All Zones","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"], key="zone_pre2")
    df_filt = df_kv[df_kv["Zone"]==zone_pre] if zone_pre != "All Zones" else df_kv
    sub_list = sorted(df_filt["Substation"].dropna().unique().tolist())
    with c1:
        selected_subs = st.multiselect("Substations", options=sub_list,
            placeholder=f"Choose from {len(sub_list):,} substations...", label_visibility="collapsed")

    if not selected_subs:
        st.markdown('<div style="text-align:center;padding:52px 20px;color:#3a5070;font-family:IBM Plex Mono,monospace;background:#0f1a24;border:1px dashed #1e2d42;border-radius:6px;margin-top:8px"><div style="font-size:32px;margin-bottom:10px">🏭</div>Select substations to auto-resolve buses, zones & PSSE numbers</div>', unsafe_allow_html=True)
        st.stop()

    resolved = df_kv[df_kv["Substation"].isin(selected_subs)].copy()

    # Step 3: Resolved
    st.markdown('<div class="section-label"><span class="step-badge">3</span> Auto-Resolved Buses · Zones · PSSE Numbers</div>', unsafe_allow_html=True)
    for sub in selected_subs:
        sub_df = resolved[resolved["Substation"]==sub]
        buses = sub_df["Bus"].tolist()
        zones = sub_df["Zone"].unique().tolist()
        kvs   = sorted(sub_df["kV"].unique().tolist(), key=lambda x: -float(x) if x else 0)
        rn_c  = sub_df[sub_df["Resource Node"]!=""].shape[0]
        hubs  = sub_df[sub_df["Hub"]!=""]["Hub"].unique().tolist()
        psse_nums = sub_df["PSSE #"].tolist()

        bus_tags  = "".join(f'<span class="tag-bus">{b}</span>' for b in buses[:25])
        more_b    = f'<span style="color:#3a5070;font-size:11px;font-family:IBM Plex Mono,monospace">+{len(buses)-25} more</span>' if len(buses)>25 else ""
        zone_tags = "".join(f'<span class="tag-zone">{z}</span>' for z in zones)
        psse_tags = "".join(f'<span class="tag-psse">{p}</span>' for p in psse_nums[:20])
        more_p    = f'<span style="color:#3a5070;font-size:11px;font-family:IBM Plex Mono,monospace">+{len(psse_nums)-20} more</span>' if len(psse_nums)>20 else ""
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
                <div class="di"><div class="dl">Resource Nodes</div><div class="dv" style="color:#39d353">{rn_c}</div></div>
            </div>
            <div style="margin-bottom:8px"><div class="dl" style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:.15em;text-transform:uppercase;margin-bottom:4px">Bus Names</div><div class="tag-row">{bus_tags}{more_b}</div></div>
            <div><div class="dl" style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#3a5070;letter-spacing:.15em;text-transform:uppercase;margin-bottom:4px">PSSE Numbers</div><div class="tag-row">{psse_tags}{more_p}</div></div>
        </div>
        """, unsafe_allow_html=True)

    disp_cols = ["Substation","Bus","kV","Zone","PSSE #","PSSE Name","Resource Node","Hub","Node"]
    st.markdown(f"**{len(resolved):,}** buses across **{len(selected_subs)}** substation(s)")
    st.dataframe(resolved[disp_cols].sort_values(["Substation","kV"],ascending=[True,False]).reset_index(drop=True),
        use_container_width=True, height=min(380,40+len(resolved)*35),
        column_config={"kV":st.column_config.TextColumn(width="small"),"Zone":st.column_config.TextColumn(width="small")})
    st.download_button("↓ Export Bus List", data=to_csv_bytes(resolved[disp_cols]),
        file_name=f"ercot_nodes_{'_'.join(selected_subs[:3])}.csv", mime="text/csv")

    # Step 4: LMP
    st.markdown("---")
    st.markdown('<div class="section-label"><span class="step-badge">4</span> Upload DAM Hourly LMP Data</div>', unsafe_allow_html=True)
    st.markdown('<p>Upload ERCOT DAM Hourly LMP CSV. App auto-matches selected buses and shows price analysis.<br><span style="font-size:11px;color:#3a5070;font-family:IBM Plex Mono,monospace">Source: ERCOT MIS → Prices → DAM Settlement Point Prices</span></p>', unsafe_allow_html=True)

    lmp_file = st.file_uploader("Upload LMP CSV", type=["csv"], key="sel_lmp", label_visibility="collapsed")
    if lmp_file:
        try:
            lmp_raw = pd.read_csv(lmp_file, dtype=str)
            col_u = {c: c.upper().strip() for c in lmp_raw.columns}
            bus_col   = next((c for c,u in col_u.items() if any(k in u for k in ["SETTLEMENT POINT","SETTLEMENTPOINT","BUS","NODE","POINT NAME"])), None)
            price_col = next((c for c,u in col_u.items() if any(k in u for k in ["PRICE","LMP","SPP","SETTLEMENTPOINTPRICE"])), None)
            hour_col  = next((c for c,u in col_u.items() if any(k in u for k in ["HOUR","TIME","DATE","INTERVAL","DELIVERY"])), None)
            if not bus_col or not price_col:
                all_cols = lmp_raw.columns.tolist()
                cc1,cc2,cc3 = st.columns(3)
                bus_col   = cc1.selectbox("Bus column",   all_cols, key="sc_bus")
                price_col = cc2.selectbox("Price column", all_cols, key="sc_price")
                hour_col  = cc3.selectbox("Hour column",  [None]+all_cols, key="sc_hour")
            lmp_raw[price_col] = pd.to_numeric(lmp_raw[price_col], errors="coerce")
            resolved_upper = set(resolved["Bus"].str.upper())
            lmp_raw["_bu"] = lmp_raw[bus_col].str.upper().str.strip()
            matched = lmp_raw[lmp_raw["_bu"].isin(resolved_upper)].copy()

            m1,m2,m3,m4 = st.columns(4)
            m1.metric("LMP Rows", f"{len(lmp_raw):,}")
            m2.metric("Matched",  f"{len(matched):,}")
            m3.metric("Buses",    f"{matched[bus_col].nunique()} / {len(resolved_upper)}")
            m4.metric("Avg LMP",  f"${matched[price_col].mean():.2f}/MWh" if len(matched) else "$—")

            if len(matched):
                summary = matched.groupby(bus_col)[price_col].agg(Mean="mean",Max="max",Min="min",Std="std",Count="count").reset_index().round(2)
                summary.columns = ["Bus","Avg ($/MWh)","Max ($/MWh)","Min ($/MWh)","Std Dev","Hours"]
                summary = summary.merge(resolved[["Bus","Substation","kV","Zone","PSSE #"]].drop_duplicates("Bus"), on="Bus", how="left")
                st.markdown('<div class="section-label">LMP Summary by Bus</div>', unsafe_allow_html=True)
                st.dataframe(summary[["Bus","Substation","kV","Zone","Avg ($/MWh)","Max ($/MWh)","Min ($/MWh)","Std Dev","Hours","PSSE #"]],
                    use_container_width=True, height=min(400,40+len(summary)*35),
                    column_config={"Avg ($/MWh)":st.column_config.NumberColumn(format="$%.2f"),"Max ($/MWh)":st.column_config.NumberColumn(format="$%.2f"),"Min ($/MWh)":st.column_config.NumberColumn(format="$%.2f")})
                if hour_col:
                    st.markdown('<div class="section-label">LMP Time Series</div>', unsafe_allow_html=True)
                    try:
                        ts = matched[[hour_col,bus_col,price_col]].copy()
                        ts[hour_col] = pd.to_datetime(ts[hour_col], infer_datetime_format=True, errors="coerce")
                        ts = ts.dropna(subset=[hour_col])
                        pivot = ts.pivot_table(index=hour_col, columns=bus_col, values=price_col, aggfunc="mean")
                        st.line_chart(pivot, height=320)
                    except Exception as e:
                        st.caption(f"Chart error: {e}")
                if len(summary) >= 2:
                    st.markdown('<div class="section-label">Bus-to-Bus Spread</div>', unsafe_allow_html=True)
                    avgs = summary.set_index("Bus")["Avg ($/MWh)"].to_dict()
                    buses_s = list(avgs.keys())
                    pairs = [{"Bus A":buses_s[i],"Bus B":buses_s[j],"Avg A":avgs[buses_s[i]],"Avg B":avgs[buses_s[j]],"Spread ($/MWh)":round(abs(avgs[buses_s[i]]-avgs[buses_s[j]]),2)} for i in range(len(buses_s)) for j in range(i+1,len(buses_s))]
                    spread_df = pd.DataFrame(pairs).sort_values("Spread ($/MWh)",ascending=False)
                    st.dataframe(spread_df, use_container_width=True, height=min(280,40+len(spread_df)*35),
                        column_config={"Avg A":st.column_config.NumberColumn("Avg A ($/MWh)",format="$%.2f"),"Avg B":st.column_config.NumberColumn("Avg B ($/MWh)",format="$%.2f"),"Spread ($/MWh)":st.column_config.NumberColumn(format="$%.2f")})
                st.download_button("↓ Export LMP Analysis", data=to_csv_bytes(summary),
                    file_name=f"lmp_{'_'.join(selected_subs[:3])}.csv", mime="text/csv")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.markdown('<div style="background:#0f1a24;border:1px dashed #1e2d42;border-radius:6px;padding:28px;text-align:center"><div style="font-family:IBM Plex Mono,monospace;font-size:12px;color:#3a5070">Upload ERCOT DAM Hourly LMP CSV to analyse prices at selected nodes<br><span style="font-size:10px;margin-top:6px;display:block">Source: ERCOT MIS → Prices → DAM Settlement Point Prices</span></div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 3 — Bus Lookup
# ═══════════════════════════════════════════════════════════════════
elif page == "🔍 Bus Lookup":
    st.markdown('<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>BUS <span>LOOKUP</span></h1></div>', unsafe_allow_html=True)
    c1,c2 = st.columns([3,1])
    with c1: bus_q = st.text_input("Bus Name", placeholder="e.g. 0001, BUCKRA, AEP...", key="bus_q")
    with c2: bus_zone = st.selectbox("Zone", ["All Zones","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"])
    if bus_q.strip():
        q = bus_q.strip().upper()
        mask = df["Bus"].str.upper().str.contains(q,na=False)|df["PSSE Name"].str.upper().str.contains(q,na=False)
        if bus_zone != "All Zones": mask &= df["Zone"]==bus_zone
        results = df[mask]
        exact = df[df["Bus"].str.upper()==q]
        if not exact.empty:
            r = exact.iloc[0]
            st.markdown(f'<div class="detail-card"><h3>▶ {r["Bus"]}</h3><div class="dg"><div class="di"><div class="dl">Substation</div><div class="dv" style="color:#ff6b35">{r["Substation"]}</div></div><div class="di"><div class="dl">Voltage</div><div class="dv"><span class="kv {kv_cls(r["kV"])}">{r["kV"]} kV</span></div></div><div class="di"><div class="dl">Zone</div><div class="dv" style="color:#39d353">{r["Zone"]}</div></div><div class="di"><div class="dl">PSSE Name</div><div class="dv">{r["PSSE Name"] or "—"}</div></div><div class="di"><div class="dl">PSSE #</div><div class="dv">{r["PSSE #"] or "—"}</div></div><div class="di"><div class="dl">Resource Node</div><div class="dv">{r["Resource Node"] or "—"}</div></div><div class="di"><div class="dl">Hub</div><div class="dv">{r["Hub"] or "—"}</div></div></div></div>', unsafe_allow_html=True)
        st.markdown(f"**{len(results):,}** results for `{bus_q.strip()}`")
        disp = ["Bus","PSSE Name","kV","Substation","Zone","Resource Node","PSSE #"]
        st.dataframe(results[disp].reset_index(drop=True), use_container_width=True, height=min(400,40+len(results)*35))
        if len(results): st.download_button("↓ Export CSV", data=to_csv_bytes(results[disp]), file_name=f"bus_{bus_q.strip()}.csv", mime="text/csv")
    else:
        st.markdown('<div style="text-align:center;padding:60px;color:#3a5070;font-family:IBM Plex Mono,monospace"><div style="font-size:36px;margin-bottom:12px">⚡</div>Enter a bus name above</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 4 — Substation Lookup
# ═══════════════════════════════════════════════════════════════════
elif page == "🏭 Substation Lookup":
    st.markdown('<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>SUBSTATION <span>LOOKUP</span></h1></div>', unsafe_allow_html=True)
    c1,c2 = st.columns([3,1])
    with c1: sub_q = st.text_input("Substation Name", placeholder="e.g. LOOKOUT, CAMPBELL...")
    with c2:
        kv_opts = ["All kV"] + sorted(df["kV"].dropna().unique().tolist(), key=lambda x: -float(x) if x else 0)
        sub_kv = st.selectbox("Voltage", kv_opts)
    if sub_q.strip():
        q = sub_q.strip().upper()
        mask = df["Substation"].str.upper().str.contains(q,na=False)
        if sub_kv != "All kV": mask &= df["kV"]==sub_kv
        results = df[mask]
        exact = df[df["Substation"].str.upper()==q]
        if not exact.empty:
            kvs   = ", ".join(sorted(exact["kV"].unique(), key=lambda x: -float(x) if x else 0))
            zones = ", ".join(exact["Zone"].unique())
            st.markdown(f'<div class="detail-card"><h3>▶ {exact.iloc[0]["Substation"]}</h3><div class="dg"><div class="di"><div class="dl">Total Buses</div><div class="dv" style="color:#00d4ff">{len(exact)}</div></div><div class="di"><div class="dl">Voltages</div><div class="dv">{kvs} kV</div></div><div class="di"><div class="dl">Zone(s)</div><div class="dv" style="color:#39d353">{zones}</div></div><div class="di"><div class="dl">Resource Nodes</div><div class="dv">{exact[exact["Resource Node"]!=""].shape[0]}</div></div></div></div>', unsafe_allow_html=True)
        st.markdown(f"**{len(results):,}** results for `{sub_q.strip()}`")
        disp = ["Substation","Bus","kV","Zone","PSSE #","PSSE Name","Resource Node"]
        st.dataframe(results[disp].reset_index(drop=True), use_container_width=True, height=min(400,40+len(results)*35))
        if len(results): st.download_button("↓ Export CSV", data=to_csv_bytes(results[disp]), file_name=f"sub_{sub_q.strip()}.csv", mime="text/csv")
    else:
        st.markdown('<div style="text-align:center;padding:60px;color:#3a5070;font-family:IBM Plex Mono,monospace"><div style="font-size:36px;margin-bottom:12px">🏭</div>Enter a substation name above</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 5 — Browse All
# ═══════════════════════════════════════════════════════════════════
elif page == "📋 Browse All":
    st.markdown('<div class="page-header"><div class="tag">⚡ SunStripe · ERCOT</div><h1>BROWSE <span>ALL</span></h1></div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns([3,1,1,1])
    with c1: bq  = st.text_input("Search", placeholder="Bus, PSSE Name, Substation...")
    with c2: bz  = st.selectbox("Zone", ["All","LZ_NORTH","LZ_SOUTH","LZ_WEST","LZ_HOUSTON"])
    with c3:
        bkv_opts = ["All kV"] + sorted(df["kV"].dropna().unique().tolist(), key=lambda x: -float(x) if x else 0)
        bkv = st.selectbox("kV", bkv_opts)
    with c4: brn = st.selectbox("Type", ["All","Resource Nodes","Hubs"])
    f = df.copy()
    if bq.strip():
        q = bq.strip().upper()
        f = f[f["Bus"].str.upper().str.contains(q,na=False)|f["PSSE Name"].str.upper().str.contains(q,na=False)|f["Substation"].str.upper().str.contains(q,na=False)]
    if bz  != "All":    f = f[f["Zone"]==bz]
    if bkv != "All kV": f = f[f["kV"]==bkv]
    if brn == "Resource Nodes": f = f[f["Resource Node"]!=""]
    elif brn == "Hubs":         f = f[f["Hub"]!=""]
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Records",     f"{len(f):,}")
    m2.metric("Substations", f"{f['Substation'].nunique():,}")
    m3.metric("kV Levels",   f"{f['kV'].nunique()}")
    m4.metric("Res. Nodes",  f"{f[f['Resource Node']!=''].shape[0]:,}")
    disp = ["Bus","PSSE Name","kV","Substation","Zone","Resource Node","Hub","PSSE #"]
    st.dataframe(f[disp].reset_index(drop=True), use_container_width=True, height=500)
    st.download_button("↓ Export CSV", data=to_csv_bytes(f[disp]), file_name="ercot_browse.csv", mime="text/csv")
