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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── SUNSTRIPE BRAND PALETTE
   bg:        #FFFFFF  white
   surface:   #F8F9FA  off-white card
   surface2:  #F0F2F5  raised surface
   border:    #E2E5EA  light border
   accent:    #CC1E27  SunStripe Red
   text:      #1A1A1A  near-black
   muted:     #6B7280  gray
── */

html, body, [data-testid="stAppViewContainer"] {
    background-color: #F4F5F7 !important;
    font-family: 'Inter', sans-serif;
    color: #1A1A1A;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A1A1A 0%, #111111 100%) !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #F8F9FA !important; }
[data-testid="stSidebar"] hr { border-color: #2e2e2e !important; }

/* Page header */
.page-header {
    border-bottom: 2px solid #E2E5EA;
    padding-bottom: 14px; margin-bottom: 20px;
}
.page-header .tag {
    font-family:'JetBrains Mono',monospace; font-size:10px; color:#CC1E27;
    letter-spacing:.2em; text-transform:uppercase; margin-bottom:4px;
}
.page-header h1 {
    font-family:'Inter',sans-serif; font-size:24px;
    font-weight:700; color:#1A1A1A; margin:0;
}
.page-header h1 span { color:#CC1E27; }

/* Section label */
.section-label {
    font-family:'JetBrains Mono',monospace; font-size:10px; color:#9CA3AF;
    letter-spacing:.2em; text-transform:uppercase; margin:18px 0 10px;
    display:flex; align-items:center; gap:8px;
}
.section-label::after { content:''; flex:1; height:1px; background:#E2E5EA; }

/* Step badge */
.step-badge {
    display:inline-flex; align-items:center; justify-content:center;
    width:22px; height:22px; border-radius:50%;
    background:#CC1E27; color:#fff;
    font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700;
}

/* OSM card */
.osm-card {
    background:#FFFFFF; border:1px solid #E2E5EA;
    border-left:4px solid #CC1E27; border-radius:8px;
    padding:16px 20px; margin-bottom:14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.osm-card .oc-title {
    font-family:'Inter',sans-serif; font-size:15px; font-weight:700;
    color:#1A1A1A; margin-bottom:12px;
}
.osm-card .oc-grid { display:flex; flex-wrap:wrap; gap:16px; margin-bottom:10px; }
.osm-card .oc-item .oc-lbl {
    font-family:'JetBrains Mono',monospace; font-size:9px; color:#9CA3AF;
    letter-spacing:.15em; text-transform:uppercase;
}
.osm-card .oc-item .oc-val {
    font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:500;
    color:#1A1A1A; margin-top:2px;
}

/* ERCOT card */
.ercot-card {
    background:#FFFFFF; border:1px solid #E2E5EA;
    border-left:4px solid #CC1E27; border-radius:8px;
    padding:16px 20px; margin-bottom:14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.ercot-card h3 {
    font-family:'Inter',sans-serif; font-size:14px; font-weight:700;
    color:#CC1E27; margin:0 0 12px;
}
.dg { display:flex; flex-wrap:wrap; gap:16px; margin-bottom:10px; }
.di .dl {
    font-family:'JetBrains Mono',monospace; font-size:9px; color:#9CA3AF;
    letter-spacing:.15em; text-transform:uppercase;
}
.di .dv {
    font-family:'JetBrains Mono',monospace; font-size:12px;
    font-weight:500; color:#1A1A1A; margin-top:2px;
}

/* Tag pills */
.tag-row { display:flex; flex-wrap:wrap; gap:5px; margin-top:4px; }
.tag-bus  { display:inline-block; padding:2px 9px; border-radius:12px; font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:500; background:rgba(204,30,39,0.07); border:1px solid rgba(204,30,39,0.25); color:#CC1E27; }
.tag-zone { display:inline-block; padding:2px 9px; border-radius:12px; font-family:'JetBrains Mono',monospace; font-size:11px; background:rgba(5,150,105,0.07); border:1px solid rgba(5,150,105,0.25); color:#CC1E27; }
.tag-psse { display:inline-block; padding:2px 9px; border-radius:12px; font-family:'JetBrains Mono',monospace; font-size:11px; background:rgba(107,114,128,0.08); border:1px solid rgba(107,114,128,0.25); color:#374151; }
.tag-hub  { display:inline-block; padding:2px 9px; border-radius:12px; font-family:'JetBrains Mono',monospace; font-size:11px; background:rgba(217,119,6,0.08); border:1px solid rgba(217,119,6,0.3); color:#D97706; }
.tag-rn   { display:inline-block; padding:2px 9px; border-radius:12px; font-family:'JetBrains Mono',monospace; font-size:11px; background:rgba(5,150,105,0.06); border:1px solid rgba(5,150,105,0.2); color:#CC1E27; }

/* kV badges */
.kv { display:inline-block; padding:2px 9px; border-radius:12px; font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700; }
.kv-345 { color:#B45309; background:#FEF3C7; border:1px solid #FCD34D; }
.kv-230 { color:#D97706; background:#FFFBEB; border:1px solid #FDE68A; }
.kv-138 { color:#CC1E27; background:#FEF2F2; border:1px solid #FECACA; }
.kv-115 { color:#7C3AED; background:#F5F3FF; border:1px solid #DDD6FE; }
.kv-69  { color:#CC1E27; background:#ECFDF5; border:1px solid #A7F3D0; }
.kv-34  { color:#6B7280; background:#F9FAFB; border:1px solid #E5E7EB; }

/* Placeholder */
.map-placeholder {
    text-align:center; padding:48px 20px; color:#9CA3AF;
    font-family:'Inter',sans-serif;
    background:#FFFFFF; border:2px dashed #E2E5EA; border-radius:8px;
}
.map-placeholder .mp-icon { font-size:36px; margin-bottom:12px; }
.map-placeholder .mp-title { font-size:14px; font-weight:600; color:#6B7280; margin-bottom:6px; }
.map-placeholder .mp-sub { font-size:12px; line-height:1.7; color:#9CA3AF; }

/* Hint bar */
.hint-bar {
    background:#FEF2F2; border:1px solid #FECACA; border-radius:6px;
    padding:8px 16px; font-family:'Inter',sans-serif;
    font-size:12px; color:#991B1B; margin-bottom:12px;
    display:flex; align-items:center; gap:10px;
}

/* Confidence */
.conf-high { color:#CC1E27; font-weight:600; }
.conf-med  { color:#D97706; font-weight:600; }
.conf-low  { color:#CC1E27; font-weight:600; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background:#FFFFFF;
    border-bottom:2px solid #E2E5EA;
    border-radius:8px 8px 0 0;
}
.stTabs [data-baseweb="tab"] {
    font-family:'Inter',sans-serif; font-size:12px; font-weight:500;
    letter-spacing:.03em; text-transform:uppercase;
    color:#9CA3AF; background:transparent; padding:10px 20px;
}
.stTabs [aria-selected="true"] {
    color:#CC1E27 !important;
    border-bottom:2px solid #CC1E27 !important;
    font-weight:700 !important;
}

/* Inputs */
.stTextInput input, div[data-baseweb="select"] > div {
    background-color:#FFFFFF !important; border-color:#E2E5EA !important;
    color:#1A1A1A !important; font-family:'JetBrains Mono',monospace !important;
    border-radius:6px !important;
}
.stNumberInput input {
    background-color:#FFFFFF !important; border-color:#E2E5EA !important;
    color:#1A1A1A !important; font-family:'JetBrains Mono',monospace !important;
}

/* Buttons */
.stDownloadButton button, .stButton button {
    background:#FFFFFF !important; border:1px solid #E2E5EA !important;
    color:#6B7280 !important; font-family:'Inter',sans-serif !important;
    font-size:11px !important; font-weight:600 !important;
    letter-spacing:.05em !important; text-transform:uppercase !important;
    border-radius:6px !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    border-color:#CC1E27 !important; color:#CC1E27 !important;
    background:#FEF2F2 !important;
}

/* Primary button */
button[kind="primary"], [data-testid="stButton"] button[kind="primary"] {
    background:#CC1E27 !important; border:none !important;
    color:#FFFFFF !important; font-weight:700 !important;
    box-shadow: 0 2px 8px rgba(204,30,39,0.3) !important;
}
button[kind="primary"]:hover, [data-testid="stButton"] button[kind="primary"]:hover {
    background:#A31621 !important; color:#FFFFFF !important;
    box-shadow: 0 4px 12px rgba(204,30,39,0.4) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background:#FFFFFF; border:1px solid #E2E5EA;
    border-radius:8px; padding:16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
[data-testid="stMetricLabel"] {
    font-family:'JetBrains Mono',monospace !important; font-size:10px !important;
    color:#9CA3AF !important; text-transform:uppercase; letter-spacing:.12em;
}
[data-testid="stMetricValue"] {
    font-family:'Inter',sans-serif !important;
    color:#CC1E27 !important; font-size:26px !important; font-weight:700 !important;
}

/* Checkboxes */
[data-testid="stCheckbox"] label {
    font-family:'JetBrains Mono',monospace !important; font-size:11px !important;
    color:#374151 !important;
}

div[data-testid="stMarkdownContainer"] p { color:#6B7280; font-size:13px; }
hr { border-color:#E2E5EA !important; }

/* Scrollbar */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#F4F5F7; }
::-webkit-scrollbar-thumb { background:#E2E5EA; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:#CC1E27; }
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
                    background:#ffffff; border:3px solid #CC1E27;
                    box-shadow:0 0 8px #CC1E27; margin:-8px 0 0 -8px;">
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
                if v >= 345:   col = "#B45309"
                elif v >= 230: col = "#D97706"
                elif v >= 138: col = "#CC1E27"
                elif v >= 69:  col = "#CC1E27"
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
<div style="font-family:'JetBrains Mono',monospace;background:#FFFFFF;color:#1A1A1A;
     padding:12px 14px;border-radius:6px;min-width:200px;border:1px solid #E2E5EA;">
  <div style="font-size:13px;font-weight:600;color:{'#CC1E27' if is_selected else '#CC1E27'};margin-bottom:8px">
    {'✓ ' if is_selected else ''}{name}
  </div>
  <div style="font-size:10px;color:#9CA3AF;margin-bottom:2px">VOLTAGE</div>
  <div style="font-size:12px;margin-bottom:6px">{v_label}</div>
  {'<div style="font-size:10px;color:#9CA3AF;margin-bottom:2px">OPERATOR</div><div style="font-size:11px;margin-bottom:6px">'+op+'</div>' if op else ''}
  <div style="font-size:10px;color:#9CA3AF">Distance: {dist_km:.1f} km from click</div>
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
    <span style="font-size:11px;color:#9CA3AF;font-family:'JetBrains Mono',monospace">
    Source: ERCOT MIS → Reports → DAM Settlement Point Prices (CSV)
    </span></p>
    """, unsafe_allow_html=True)

    lmp_file = st.file_uploader("Upload LMP CSV", type=["csv"], key=f"{key_prefix}_file",
                                 label_visibility="collapsed")
    if not lmp_file:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px dashed #E2E5EA;border-radius:6px;
             padding:24px;text-align:center;font-family:'JetBrains Mono',monospace;
             font-size:11px;color:#9CA3AF">
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
    more_b    = f'<span style="color:#9CA3AF;font-size:11px;font-family:JetBrains Mono,monospace">+{len(buses)-30} more</span>' if len(buses)>30 else ""
    zone_tags = "".join(f'<span class="tag-zone">{z}</span>' for z in zones)
    psse_tags = "".join(f'<span class="tag-psse">{p}</span>' for p in psse_nums[:20])
    more_p    = f'<span style="color:#9CA3AF;font-size:11px;font-family:JetBrains Mono,monospace">+{len(psse_nums)-20} more</span>' if len(psse_nums)>20 else ""
    hub_tags  = "".join(f'<span class="tag-hub">{h}</span>' for h in hubs) if hubs else '<span style="color:#9CA3AF;font-size:11px;font-family:JetBrains Mono,monospace">—</span>'
    kv_tags   = "".join(f'<span class="kv {kv_cls(k)}">{k} kV</span>' for k in kvs)
    rn_tags   = "".join(f'<span class="tag-rn">{r}</span>' for r in rn_list[:10])
    more_rn   = f'<span style="color:#9CA3AF;font-size:11px;font-family:JetBrains Mono,monospace">+{len(rn_list)-10} more</span>' if len(rn_list)>10 else ""

    st.markdown(f"""
    <div class="ercot-card">
        <h3>⚡ ERCOT Substation: {sub_name}</h3>
        <div class="dg">
            <div class="di"><div class="dl">Total Buses</div><div class="dv" style="color:#CC1E27">{len(buses)}</div></div>
            <div class="di"><div class="dl">Voltage(s)</div><div class="dv">{kv_tags}</div></div>
            <div class="di"><div class="dl">Zone(s)</div><div class="dv">{zone_tags}</div></div>
            <div class="di"><div class="dl">Hub(s)</div><div class="dv">{hub_tags}</div></div>
            <div class="di"><div class="dl">Resource Nodes</div><div class="dv" style="color:#CC1E27">{len(rn_list)}</div></div>
        </div>
        <div style="margin-bottom:10px">
            <div class="dl" style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#9CA3AF;letter-spacing:.15em;text-transform:uppercase;margin-bottom:5px">Bus Names (Settlement Points)</div>
            <div class="tag-row">{bus_tags}{more_b}</div>
        </div>
        <div style="margin-bottom:10px">
            <div class="dl" style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#9CA3AF;letter-spacing:.15em;text-transform:uppercase;margin-bottom:5px">PSSE Bus Numbers</div>
            <div class="tag-row">{psse_tags}{more_p}</div>
        </div>
        {'<div><div class="dl" style="font-family:JetBrains Mono,monospace;font-size:9px;color:#9CA3AF;letter-spacing:.15em;text-transform:uppercase;margin-bottom:5px">Resource Nodes</div><div class="tag-row">' + rn_tags + more_rn + '</div></div>' if rn_list else ''}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:14px 0 16px">
        <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#E8192C;
             letter-spacing:.2em;text-transform:uppercase;margin-bottom:5px">⚡ SunStripe · ERCOT</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:600;
             color:#1A1A1A;line-height:1.4">Nodal Analysis<br><span style="color:#CC1E27">Platform</span></div>
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
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#9CA3AF;
         letter-spacing:.15em;text-transform:uppercase;margin-bottom:10px">Dataset · Feb 2026</div>
    <div style="display:flex;flex-direction:column;gap:9px">
        <div><div style="font-size:17px;font-weight:600;color:#E8192C">{len(df):,}</div>
             <div style="font-size:10px;color:#9CA3AF">Settlement Points</div></div>
        <div><div style="font-size:17px;font-weight:600;color:#fca5a5">{df["Substation"].nunique():,}</div>
             <div style="font-size:10px;color:#9CA3AF">Substations</div></div>
        <div><div style="font-size:17px;font-weight:600;color:#fcd34d">{df[df["Hub"]!=""]["Hub"].nunique()}</div>
             <div style="font-size:10px;color:#9CA3AF">Hubs</div></div>
        <div><div style="font-size:17px;font-weight:600;color:#6ee7b7">{df[df["Resource Node"]!=""].shape[0]:,}</div>
             <div style="font-size:10px;color:#9CA3AF">Resource Nodes</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <a href="https://ercot-bess-dashboard-nhh9eztsqeuqxxuz97kacu.streamlit.app/" target="_blank"
       style="display:block;padding:7px 10px;background:#F0F2F5;border-radius:4px;
              font-family:'JetBrains Mono',monospace;font-size:11px;color:#9CA3AF;
              text-decoration:none;margin-bottom:5px">⚡ ERCOT BESS Dashboard ↗</a>
    <a href="https://fatal-flaw-o7aks4agtoffgyydbvrguj.streamlit.app/" target="_blank"
       style="display:block;padding:7px 10px;background:#F0F2F5;border-radius:4px;
              font-family:'JetBrains Mono',monospace;font-size:11px;color:#9CA3AF;
              text-decoration:none">🌿 SiteIQ Fatal Flaw ↗</a>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ██████████████████  PAGE 1: INFRASTRUCTURE MAP  ███████████████████████████
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🗺️ Infrastructure Map":

    st.markdown("""
    <div class="page-header">
        <div class="tag">⚡ SunStripe · ERCOT</div>
        <h1>SUBSTATION <span>SEARCH</span></h1>
    </div>
    """, unsafe_allow_html=True)

    # ── Session state ─────────────────────────────────────────────────────────
    for k, v in [
        ("search_results", None), ("selected_osm", None),
        ("ercot_sel_sub", None),  ("search_lat", 31.5),
        ("search_lon", -97.5),    ("last_search_key", ""),
    ]:
        if k not in st.session_state:
            st.session_state[k] = v

    # ── SEARCH PARAMETERS ────────────────────────────────────────────────────
    st.markdown('<div style="background:#FFFFFF;border:1px solid #E2E5EA;border-radius:8px;padding:18px 20px;margin-bottom:18px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:#9CA3AF;letter-spacing:.2em;text-transform:uppercase;margin-bottom:14px">SEARCH PARAMETERS</div>', unsafe_allow_html=True)

    col_lat, col_lon, col_radius, col_thresh = st.columns([2, 2, 2, 2])

    with col_lat:
        st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#6B7280;margin-bottom:4px">Latitude</div>', unsafe_allow_html=True)
        lat_input = st.number_input("lat", value=st.session_state.search_lat,
            format="%.6f", label_visibility="collapsed", key="lat_input",
            min_value=25.0, max_value=37.0, step=0.001)

    with col_lon:
        st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#6B7280;margin-bottom:4px">Longitude</div>', unsafe_allow_html=True)
        lon_input = st.number_input("lon", value=st.session_state.search_lon,
            format="%.6f", label_visibility="collapsed", key="lon_input",
            min_value=-107.0, max_value=-93.0, step=0.001)

    with col_radius:
        st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#6B7280;margin-bottom:4px">Search Radius (miles)</div>', unsafe_allow_html=True)
        radius_miles = st.selectbox("radius", [5, 10, 15, 25, 35, 50, 75, 100],
            index=3, label_visibility="collapsed", key="radius_sel")

    with col_thresh:
        st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#6B7280;margin-bottom:4px">Hub Threshold (kV ≥)</div>', unsafe_allow_html=True)
        hub_thresh = st.selectbox("thresh", [115, 138, 230, 345],
            index=2, label_visibility="collapsed", key="hub_thresh")

    # Voltage filter pills
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#6B7280;margin:12px 0 6px">Filter Voltages</div>', unsafe_allow_html=True)
    kv_options = ["34.5", "69", "115", "138", "230", "345", "500", "765"]
    kv_cols = st.columns(len(kv_options) + 1)
    kv_selected = []
    for i, kv in enumerate(kv_options):
        default = kv in ["69", "115", "138", "230", "345"]
        if kv_cols[i].checkbox(f"{kv} kV", value=default, key=f"kv_pill_{kv}"):
            kv_selected.append(kv)
    inc_unknown = kv_cols[-1].checkbox("Unknown V", value=True, key="inc_unknown")

    # Bottom row: link + search button
    link_col, btn_col = st.columns([4, 1])
    with link_col:
        oim_url = f"https://openinframap.org/#10/{lat_input:.4f}/{lon_input:.4f}"
        st.markdown(f'<a href="{oim_url}" target="_blank" style="font-family:JetBrains Mono,monospace;font-size:11px;color:#CC1E27;text-decoration:none;">🔗 Open this area in OpenInfraMap ↗</a>', unsafe_allow_html=True)
    with btn_col:
        search_btn = st.button("🔍 Search Substations", use_container_width=True, key="search_btn",
                               type="primary")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── OVERPASS QUERY ───────────────────────────────────────────────────────
    if search_btn:
        st.session_state.search_lat     = lat_input
        st.session_state.search_lon     = lon_input
        st.session_state.selected_osm   = None
        st.session_state.ercot_sel_sub  = None

        radius_m = int(radius_miles * 1609.34)

        # Build kV filter for Overpass
        # We'll fetch everything and filter client-side (more reliable)
        query = f"""[out:json][timeout:40];
(
  node["power"="substation"](around:{radius_m},{lat_input},{lon_input});
  way["power"="substation"](around:{radius_m},{lat_input},{lon_input});
  relation["power"="substation"](around:{radius_m},{lat_input},{lon_input});
);
out center tags;"""

        with st.spinner(f"Searching {radius_miles} mi radius around {lat_input:.4f}, {lon_input:.4f}..."):
            try:
                resp = requests.post(
                    "https://overpass-api.de/api/interpreter",
                    data={"data": query}, timeout=45,
                    headers={"User-Agent": "SunStripe-ERCOT/1.0"}
                )
                resp.raise_for_status()
                raw_elements = []
                for el in resp.json().get("elements", []):
                    elat = el.get("lat") or (el.get("center") or {}).get("lat")
                    elon = el.get("lon") or (el.get("center") or {}).get("lon")
                    if not elat or not elon:
                        continue
                    tags = el.get("tags", {})
                    raw_volt_str = tags.get("voltage", "")
                    # Parse voltage to kV
                    try:
                        raw_v = float(raw_volt_str.split(";")[0].strip())
                        volt_kv = raw_v / 1000 if raw_v > 1000 else raw_v
                    except:
                        volt_kv = None

                    dist_km = haversine(lat_input, lon_input, elat, elon)
                    dist_mi = dist_km / 1.60934

                    raw_elements.append({
                        "lat": elat, "lon": elon,
                        "name":      tags.get("name", ""),
                        "voltage":   raw_volt_str,
                        "volt_kv":   volt_kv,
                        "operator":  tags.get("operator", ""),
                        "ref":       tags.get("ref", ""),
                        "osm_id":    str(el.get("id", "")),
                        "dist_mi":   round(dist_mi, 2),
                        "dist_km":   round(dist_km, 2),
                    })

                # Apply voltage filter
                filtered = []
                for el in raw_elements:
                    v = el["volt_kv"]
                    if v is None:
                        if inc_unknown:
                            filtered.append(el)
                    else:
                        v_str = str(int(v)) if v == int(v) else str(v)
                        if any(abs(v - float(kv)) < 5 for kv in kv_selected):
                            filtered.append(el)

                # Sort by distance
                filtered.sort(key=lambda x: x["dist_mi"])

                # Classify Hub vs Node using hub_thresh
                for el in filtered:
                    v = el["volt_kv"]
                    el["is_hub"] = (v is not None and v >= hub_thresh)

                st.session_state.search_results = {
                    "elements": filtered,
                    "total_raw": len(raw_elements),
                    "lat": lat_input, "lon": lon_input,
                    "radius_mi": radius_miles,
                    "hub_thresh": hub_thresh,
                }

            except requests.exceptions.Timeout:
                st.error("Overpass API timed out. Try a smaller radius or try again.")
                st.session_state.search_results = None
            except Exception as e:
                st.error(f"Search error: {e}")
                st.session_state.search_results = None

    # ── RESULTS ──────────────────────────────────────────────────────────────
    results = st.session_state.search_results

    if results is None:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#9CA3AF;font-family:JetBrains Mono,monospace;
             background:#F4F5F7;border:1px dashed #E2E5EA;border-radius:8px;">
            <div style="font-size:40px;margin-bottom:12px">⚡</div>
            <div style="font-size:14px;font-weight:600;color:#E2E5EA;margin-bottom:6px">No search yet</div>
            <div style="font-size:11px;line-height:1.7">Enter coordinates · set radius · click <strong style="color:#CC1E27">Search Substations</strong></div>
        </div>""", unsafe_allow_html=True)

    else:
        elements  = results["elements"]
        hubs_list = [e for e in elements if e["is_hub"]]
        node_list = [e for e in elements if not e["is_hub"]]
        clat, clon = results["lat"], results["lon"]

        # ── METRICS ROW ──────────────────────────────────────────────
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Found",    len(elements))
        m2.metric(f"Hubs (≥{results['hub_thresh']} kV)", len(hubs_list))
        m3.metric(f"Nodes (<{results['hub_thresh']} kV)", len(node_list))
        m4.metric("Radius",         f"{results['radius_mi']} mi")
        m5.metric("Centre",         f"{clat:.3f}, {clon:.3f}")

        # ── MAP ──────────────────────────────────────────────────────
        m = folium.Map(location=[clat, clon], zoom_start=10, tiles=None, prefer_canvas=True)

        # Dark base
        folium.TileLayer(
            tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            attr="© CartoDB", name="Dark", overlay=False, control=True
        ).add_to(m)

        # OpenInfraMap power overlay
        folium.TileLayer(
            tiles="https://tiles.openinframap.org/power_medium/{z}/{x}/{y}.png",
            attr="© OpenInfraMap", name="⚡ Power Infrastructure",
            overlay=True, control=True, opacity=0.85
        ).add_to(m)
        folium.TileLayer(
            tiles="https://tiles.openinframap.org/power_high/{z}/{x}/{y}.png",
            attr="© OpenInfraMap", name="⚡ HV Lines",
            overlay=True, control=True, opacity=0.75
        ).add_to(m)

        # Search radius circle
        folium.Circle(
            location=[clat, clon],
            radius=results["radius_mi"] * 1609.34,
            color="#D97706", weight=1, fill=False,
            dash_array="6 4", tooltip=f"{results['radius_mi']} mi radius"
        ).add_to(m)

        # Centre marker
        folium.Marker(
            location=[clat, clon],
            icon=folium.DivIcon(html="""
                <div style="width:14px;height:14px;border-radius:50%;background:#D97706;
                     border:2px solid #fff;box-shadow:0 0 6px #D97706;margin:-7px 0 0 -7px;"></div>"""),
            tooltip="Search Centre",
        ).add_to(m)

        sel_id = st.session_state.selected_osm.get("osm_id") if st.session_state.selected_osm else None

        for el in elements:
            is_sel   = (el["osm_id"] == sel_id)
            is_hub   = el["is_hub"]
            name     = el.get("name") or "Unnamed"
            v        = el["volt_kv"]
            v_label  = f"{v:.0f} kV" if v else "? kV"
            op       = el.get("operator","")

            # Colour: yellow=hub, cyan=node, white border if selected
            fill_col = "#D97706" if is_hub else "#0891B2"
            ring_col = "#CC1E27" if is_sel else fill_col
            radius   = 11 if is_sel else (9 if is_hub else 7)

            popup_html = f"""
<div style="font-family:JetBrains Mono,monospace;background:#FFFFFF;color:#1A1A1A;
     padding:12px;border-radius:6px;min-width:210px;border:1px solid #E2E5EA;">
  <div style="font-size:12px;font-weight:600;color:{'#D97706' if is_hub else '#0891B2'};margin-bottom:8px">
    {'🔮 HUB' if is_hub else '🔵 NODE'} &nbsp; {name}
  </div>
  <div style="font-size:10px;color:#9CA3AF">VOLTAGE</div>
  <div style="font-size:12px;margin-bottom:5px">{v_label}</div>
  {'<div style="font-size:10px;color:#9CA3AF">OPERATOR</div><div style="font-size:11px;margin-bottom:5px">'+op+'</div>' if op else ''}
  <div style="font-size:10px;color:#9CA3AF">Distance</div>
  <div style="font-size:11px">{el["dist_mi"]:.1f} mi · {el["dist_km"]:.1f} km</div>
</div>"""

            folium.CircleMarker(
                location=[el["lat"], el["lon"]],
                radius=radius,
                color=ring_col, weight=3 if is_sel else 1,
                fill=True, fill_color=fill_col,
                fill_opacity=0.9 if is_sel else 0.75,
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=f"{'🔮' if is_hub else '🔵'} {name} · {v_label} · {el['dist_mi']:.1f} mi",
            ).add_to(m)

        folium.LayerControl(collapsed=False, position="topright").add_to(m)

        map_data = st_folium(m, key="search_map", use_container_width=True, height=500,
                             returned_objects=["last_object_clicked_tooltip"])

        # Legend
        st.markdown(f"""
        <div style="display:flex;gap:20px;font-family:JetBrains Mono,monospace;font-size:11px;
             color:#6B7280;padding:6px 12px;background:#F4F5F7;border:1px solid #E2E5EA;
             border-radius:4px;margin-top:6px;flex-wrap:wrap;">
            <span>● <span style="color:#D97706">Search Centre</span></span>
            <span>● <span style="color:#D97706">Hub (≥{results["hub_thresh"]} kV)</span> — {len(hubs_list)} found</span>
            <span>● <span style="color:#0891B2">Node (&lt;{results["hub_thresh"]} kV)</span> — {len(node_list)} found</span>
            <span style="color:#1e4060">— — Radius boundary</span>
        </div>
        """, unsafe_allow_html=True)

        # ── SUBSTATION LIST + SELECTION ──────────────────────────────
        st.markdown('<div style="margin-top:20px">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Found Substations — Click to Inspect</div>', unsafe_allow_html=True)

        # Two tabs: Hubs | Nodes | All
        tab_all, tab_hubs, tab_nodes = st.tabs([
            f"All ({len(elements)})",
            f"🔮 Hubs ({len(hubs_list)})",
            f"🔵 Nodes ({len(node_list)})",
        ])

        def render_sub_list(sub_list, tab_prefix="t"):
            if not sub_list:
                st.caption("No substations in this category.")
                return
            for el in sub_list:
                name     = el.get("name") or "Unnamed Substation"
                v        = el["volt_kv"]
                v_label  = f"{v:.0f} kV" if v else "? kV"
                is_hub   = el["is_hub"]
                operator = el.get("operator") or ""
                is_sel   = bool(st.session_state.selected_osm and
                                st.session_state.selected_osm.get("osm_id") == el["osm_id"])

                dot_col  = "#D97706" if is_hub else "#0891B2"
                hub_bdg  = ('<span style="font-size:9px;background:rgba(217,119,6,0.12);'
                            'border:1px solid rgba(217,119,6,0.35);color:#D97706;border-radius:3px;'
                            'padding:1px 6px;margin-left:6px;font-family:JetBrains Mono,monospace">'
                            'HUB</span>') if is_hub else ""
                if is_sel:
                    bdr = "2px solid #1A1A1A"
                    bgc = "rgba(8,145,178,0.04)"
                elif is_hub:
                    bdr = "1px solid rgba(217,119,6,0.3)"
                    bgc = "#FFFFFF"
                else:
                    bdr = "1px solid rgba(8,145,178,0.12)"
                    bgc = "#FFFFFF"
                op_part = (f'<span style="color:#9CA3AF">{operator} · </span>') if operator else ""
                html = (
                    f'<div style="background:{bgc};border:{bdr};border-radius:7px;padding:10px 14px;margin-bottom:4px;">' +
                    f'<div style="display:flex;justify-content:space-between;align-items:center">' +
                    f'<div style="font-family:JetBrains Mono,monospace;font-size:12px;font-weight:600;color:{dot_col}">● {name}</div>' +
                    hub_bdg +
                    f'<div style="text-align:right">' +
                    f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#1A1A1A">{v_label}</div>' +
                    f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#9CA3AF">{el["dist_mi"]:.1f} mi</div>' +
                    f'</div></div>' +
                    f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#9CA3AF;margin-top:3px">' +
                    op_part +
                    f'{el["lat"]:.4f}, {el["lon"]:.4f}</div></div>'
                )
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(html, unsafe_allow_html=True)
                with col_b:
                    if st.button("Inspect →", key=f"{tab_prefix}_{el['osm_id']}", use_container_width=True):
                        st.session_state.selected_osm  = el
                        st.session_state.ercot_sel_sub = None
                        st.rerun()

        with tab_all:   render_sub_list(elements,   "all")
        with tab_hubs:  render_sub_list(hubs_list,  "hub")
        with tab_nodes: render_sub_list(node_list,  "nod")

        st.markdown('</div>', unsafe_allow_html=True)

        # ── SELECTED SUBSTATION DETAIL ───────────────────────────────
        if st.session_state.selected_osm:
            sel = st.session_state.selected_osm
            osm_name = sel.get("name","") or "Unnamed"
            osm_volt = sel.get("voltage","")
            v        = sel.get("volt_kv")
            v_label  = f"{v:.0f} kV" if v else "Unknown kV"
            is_hub   = sel.get("is_hub", False)

            st.markdown("---")
            st.markdown(f"""
            <div class="osm-card" style="border-left-color:{'#D97706' if is_hub else '#0891B2'}">
                <div class="oc-title" style="color:{'#D97706' if is_hub else '#0891B2'}">
                    {'🔮 HUB' if is_hub else '🔵 NODE'} &nbsp; {osm_name}
                </div>
                <div class="oc-grid">
                    <div class="oc-item"><div class="oc-lbl">Voltage</div><div class="oc-val">{v_label}</div></div>
                    <div class="oc-item"><div class="oc-lbl">Operator</div><div class="oc-val">{sel.get("operator","—") or "—"}</div></div>
                    <div class="oc-item"><div class="oc-lbl">Distance</div><div class="oc-val">{sel["dist_mi"]:.1f} mi</div></div>
                    <div class="oc-item"><div class="oc-lbl">Coordinates</div><div class="oc-val">{sel["lat"]:.4f}, {sel["lon"]:.4f}</div></div>
                    <div class="oc-item"><div class="oc-lbl">Ref</div><div class="oc-val">{sel.get("ref","—") or "—"}</div></div>
                    <div class="oc-item"><div class="oc-lbl">OSM ID</div><div class="oc-val">{sel.get("osm_id","")}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ERCOT matching
            st.markdown('<div class="section-label">ERCOT CSV Match</div>', unsafe_allow_html=True)

            ercot_matches = match_to_ercot(osm_name, osm_volt)

            if not ercot_matches:
                st.warning(f"No ERCOT settlement point match found for **{osm_name}**. "
                           "Try searching by name in the Substation Lookup page.")
            else:
                match_names = [m[0] for m in ercot_matches]
                scores      = {m[0]: m[1] for m in ercot_matches}

                if st.session_state.ercot_sel_sub not in match_names:
                    st.session_state.ercot_sel_sub = match_names[0]

                def fmt_match(name):
                    s    = scores[name]
                    conf = "HIGH" if s >= 30 else "MED" if s >= 15 else "LOW"
                    kvs  = "/".join(sorted(df[df["Substation"]==name]["kV"].unique(),
                                          key=lambda x: -float(x) if x else 0)[:2])
                    cnt  = len(df[df["Substation"]==name])
                    return f"{name}  [{kvs} kV · {cnt} buses · conf:{conf}]"

                chosen = st.selectbox(
                    "ERCOT match", match_names,
                    format_func=fmt_match, index=0,
                    label_visibility="collapsed", key="ercot_match_radio"
                )
                st.session_state.ercot_sel_sub = chosen

            # ── FULL ERCOT DATA ──────────────────────────────────────
            if st.session_state.ercot_sel_sub:
                ercot_sub = st.session_state.ercot_sel_sub
                sub_df    = df[df["Substation"] == ercot_sub].copy()

                render_ercot_card(ercot_sub, sub_df)

                disp = ["Substation","Bus","kV","Zone","PSSE #","PSSE Name","Resource Node","Hub"]
                st.dataframe(
                    sub_df[disp].sort_values("kV", ascending=False).reset_index(drop=True),
                    use_container_width=True,
                    height=min(320, 40 + len(sub_df)*35),
                    column_config={
                        "kV":   st.column_config.TextColumn(width="small"),
                        "Zone": st.column_config.TextColumn(width="small"),
                    }
                )

                dl_col, info_col2 = st.columns([1, 4])
                with dl_col:
                    st.download_button("↓ Export Bus List",
                        data=to_csv_bytes(sub_df[disp]),
                        file_name=f"ercot_{ercot_sub}.csv", mime="text/csv")
                with info_col2:
                    st.info(f"💡 **{len(sub_df)}** buses at **{ercot_sub}** — upload DAM LMP below to analyse prices")

                st.markdown("---")
                render_lmp_section(sub_df, key_prefix="map_lmp")

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
    st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#9CA3AF;margin:6px 0 4px">{kv_tag} → <span style="color:#1A1A1A">{len(df_kv):,}</span> settlement points | <span style="color:#1A1A1A">{df_kv["Substation"].nunique():,}</span> substations</div>', unsafe_allow_html=True)

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
        st.markdown('<div style="text-align:center;padding:52px 20px;color:#9CA3AF;font-family:JetBrains Mono,monospace;background:#FFFFFF;border:1px dashed #E2E5EA;border-radius:6px;margin-top:8px"><div style="font-size:32px;margin-bottom:10px">🏭</div>Select substations above to auto-resolve buses, zones & PSSE numbers</div>', unsafe_allow_html=True)
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
            st.markdown(f'<div class="ercot-card"><h3>▶ {r["Bus"]}</h3><div class="dg"><div class="di"><div class="dl">Substation</div><div class="dv" style="color:#CC1E27">{r["Substation"]}</div></div><div class="di"><div class="dl">Voltage</div><div class="dv"><span class="kv {kv_cls(r["kV"])}">{r["kV"]} kV</span></div></div><div class="di"><div class="dl">Zone</div><div class="dv" style="color:#CC1E27">{r["Zone"]}</div></div><div class="di"><div class="dl">PSSE Name</div><div class="dv">{r["PSSE Name"] or "—"}</div></div><div class="di"><div class="dl">PSSE #</div><div class="dv">{r["PSSE #"] or "—"}</div></div><div class="di"><div class="dl">Resource Node</div><div class="dv">{r["Resource Node"] or "—"}</div></div><div class="di"><div class="dl">Hub</div><div class="dv">{r["Hub"] or "—"}</div></div></div></div>', unsafe_allow_html=True)
        st.markdown(f"**{len(results):,}** results for `{bus_q.strip()}`")
        disp = ["Bus","PSSE Name","kV","Substation","Zone","Resource Node","PSSE #"]
        st.dataframe(results[disp].reset_index(drop=True), use_container_width=True, height=min(400,40+len(results)*35))
        if len(results): st.download_button("↓ Export CSV", data=to_csv_bytes(results[disp]), file_name=f"bus_{bus_q.strip()}.csv", mime="text/csv")
    else:
        st.markdown('<div style="text-align:center;padding:60px;color:#9CA3AF;font-family:JetBrains Mono,monospace"><div style="font-size:36px;margin-bottom:12px">⚡</div>Enter a bus name above</div>', unsafe_allow_html=True)


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
        st.markdown('<div style="text-align:center;padding:60px;color:#9CA3AF;font-family:JetBrains Mono,monospace"><div style="font-size:36px;margin-bottom:12px">🏭</div>Enter a substation name above</div>', unsafe_allow_html=True)


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
