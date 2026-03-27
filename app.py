import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ═══════════════════════════════════════════════════════════════════
# ERCOT AUTH
# ═══════════════════════════════════════════════════════════════════
TOKEN_URL = (
    "https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com"
    "/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token"
)
CLIENT_ID = "fec253ea-0d06-4272-a5e6-b478baeecd70"
SCOPE     = f"openid {CLIENT_ID} offline_access"
API_BASE  = "https://api.ercot.com/api/public-reports"


def _get_credentials():
    try:
        return (
            st.secrets["ercot"]["username"],
            st.secrets["ercot"]["password"],
            st.secrets["ercot"]["subscription_key"],
        )
    except Exception:
        return (
            st.session_state.get("_ercot_user", ""),
            st.session_state.get("_ercot_pass", ""),
            st.session_state.get("_ercot_subkey", ""),
        )


def get_ercot_token(username: str, password: str):
    body = {
        "username":      username,
        "password":      password,
        "grant_type":    "password",
        "scope":         SCOPE,
        "client_id":     CLIENT_ID,
        "response_type": "id_token",
    }
    try:
        r = requests.post(
            TOKEN_URL, data=body, timeout=20,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if r.status_code == 200:
            data  = r.json()
            token = data.get("id_token") or data.get("access_token")
            if token:
                return token, None
            return None, f"Token not in response: {list(data.keys())}"
        return None, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return None, str(e)


def _ensure_token():
    now = time.time()
    if (
        "ercot_token" in st.session_state
        and st.session_state.get("ercot_token_exp", 0) > now + 60
    ):
        return st.session_state["ercot_token"], None
    username, password, _ = _get_credentials()
    if not username or not password:
        return None, "credentials_missing"
    token, err = get_ercot_token(username, password)
    if token:
        st.session_state["ercot_token"]     = token
        st.session_state["ercot_token_exp"] = now + 3500
        return token, None
    return None, err


# ═══════════════════════════════════════════════════════════════════
# ERCOT API DATA FETCH
# ═══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_dam_lmp(bus_name, date_from, date_to, _token, subscription_key, max_pages=20):
    endpoint = f"{API_BASE}/np4-183-cd/dam_hourly_lmp"
    headers  = {
        "Authorization":             f"Bearer {_token}",
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Accept":                    "application/json",
    }
    all_rows = []
    page     = 1
    body     = {}

    while page <= max_pages:
        params = {"deliveryDateFrom": date_from, "deliveryDateTo": date_to,
                  "busName": bus_name, "size": 1000, "page": page}
        try:
            r = requests.get(endpoint, headers=headers, params=params, timeout=30)
            if r.status_code == 403:
                return None, "403 Forbidden — token expired or subscription key invalid"
            if r.status_code == 400:
                return None, f"400 Bad Request — check bus name / date format: {r.text[:200]}"
            r.raise_for_status()
            body = r.json()
        except requests.exceptions.Timeout:
            return None, "Request timed out — try a smaller date range"
        except Exception as e:
            return None, str(e)

        raw = body.get("data", [])
        if isinstance(raw, dict):
            raw = raw.get("data", [])
        if not isinstance(raw, list):
            raw = []
        all_rows.extend(raw)

        meta      = body.get("_meta", {})
        total_pgs = meta.get("totalPages", 1)
        if page >= total_pgs:
            break
        page += 1

    if not all_rows:
        return None, "No data returned — verify bus name and date range"

    fields = body.get("fields", [])
    if fields:
        col_names = [f["name"] for f in fields]
    else:
        col_names = ["deliveryDate", "hourEnding", "busName", "LMP", "DSTFlag"]

    df         = pd.DataFrame(all_rows, columns=col_names[:len(all_rows[0])] if all_rows else col_names)
    df.columns = [c.lower().strip() for c in df.columns]
    lmp_col    = next((c for c in df.columns if c in ("lmp","settlementpointprice","price")), None)
    if lmp_col and lmp_col != "lmp":
        df = df.rename(columns={lmp_col: "lmp"})
    df["lmp"] = pd.to_numeric(df["lmp"], errors="coerce")

    if "deliverydate" in df.columns and "hourending" in df.columns:
        def parse_hour(h):
            h = str(h).strip()
            if ":" in h:
                return int(h.split(":")[0])
            try: return int(float(h))
            except: return 1
        df["_hour_int"] = df["hourending"].apply(parse_hour)
        df["datetime"]  = (
            pd.to_datetime(df["deliverydate"], errors="coerce")
            + pd.to_timedelta(df["_hour_int"] - 1, unit="h")
        )
    else:
        df["datetime"] = pd.NaT

    df = df.sort_values("datetime").reset_index(drop=True)
    return df, None


# ═══════════════════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════════════════
def compute_stats(df):
    lmps = df["lmp"].dropna()
    neg  = lmps[lmps < 0]
    return {
        "count":     len(lmps),
        "avg":       round(lmps.mean(), 2),
        "max":       round(lmps.max(), 2),
        "min":       round(lmps.min(), 2),
        "p50":       round(lmps.quantile(0.50), 2),
        "p90":       round(lmps.quantile(0.90), 2),
        "p10":       round(lmps.quantile(0.10), 2),
        "vol":       round(lmps.std(), 2),
        "spread":    round(lmps.max() - lmps.min(), 2),
        "neg_count": len(neg),
        "neg_pct":   round(len(neg) / len(lmps) * 100, 1) if len(lmps) else 0,
        "neg_avg":   round(neg.mean(), 2) if len(neg) else 0,
    }


# ═══════════════════════════════════════════════════════════════════
# BESS STRATEGY ENGINE
# charge_hrs / discharge_hrs are durations in hours
# 2H storage  → charge_hrs=2.5, discharge_hrs=2.0
# 4H storage  → charge_hrs=4.5, discharge_hrs=4.0
# ═══════════════════════════════════════════════════════════════════
def bess_strategy(hourly_df, charge_hrs, discharge_hrs, rte, capacity_mwh=100):
    """
    hourly_df : DataFrame with columns Hour(1-24) and lmp
    charge_hrs     : charging duration in hours (e.g. 2.5)
    discharge_hrs  : discharging duration in hours (e.g. 2.0)
    rte            : round-trip efficiency 0-1 (e.g. 0.85)
    capacity_mwh   : battery capacity in MWh

    Logic:
    1. Smooth with 3-hr centred rolling average to remove spikes
    2. Find lowest rolling-avg window of width charge_hrs → charge block
    3. Find highest rolling-avg window of width discharge_hrs → discharge block
    4. Build hourly SOC profile based on charge/discharge schedule and RTE
    5. Return revenue, windows, SOC series
    """
    hours = hourly_df["Hour"].values.astype(int)
    lmps  = hourly_df["lmp"].values

    # Rolling average
    roll = pd.Series(lmps).rolling(3, center=True, min_periods=1).mean().values

    n_charge    = max(1, round(charge_hrs))
    n_discharge = max(1, round(discharge_hrs))

    # Find best contiguous charge window (lowest avg LMP)
    best_ch_score  = np.inf
    best_ch_start  = 0
    for i in range(len(hours) - n_charge + 1):
        score = roll[i:i+n_charge].mean()
        if score < best_ch_score:
            best_ch_score = score
            best_ch_start = i
    ch_hours = set(hours[best_ch_start:best_ch_start + n_charge])

    # Find best contiguous discharge window (highest avg LMP)
    # Must not overlap charge window
    best_dis_score  = -np.inf
    best_dis_start  = 0
    for i in range(len(hours) - n_discharge + 1):
        if set(hours[i:i+n_discharge]) & ch_hours:
            continue
        score = roll[i:i+n_discharge].mean()
        if score > best_dis_score:
            best_dis_score = score
            best_dis_start = i
    dis_hours = set(hours[best_dis_start:best_dis_start + n_discharge])

    # Avg prices
    ch_prices  = [lmps[j] for j, h in enumerate(hours) if h in ch_hours]
    dis_prices = [lmps[j] for j, h in enumerate(hours) if h in dis_hours]
    avg_ch     = float(np.mean(ch_prices))  if ch_prices  else 0.0
    avg_dis    = float(np.mean(dis_prices)) if dis_prices else 0.0

    # Revenue accounting for RTE
    # Charge cost:    avg_ch  × capacity_mwh   (energy bought)
    # Discharge rev:  avg_dis × capacity_mwh × rte  (energy sold after losses)
    charge_cost  = avg_ch  * capacity_mwh
    discharge_rev= avg_dis * capacity_mwh * rte
    net_revenue  = round(discharge_rev - charge_cost, 2)
    revenue_mwh  = round(avg_dis * rte - avg_ch, 2)   # $/MWh of capacity

    # SOC profile (% of capacity)
    soc     = np.zeros(len(hours))
    current = 0.0
    for idx, h in enumerate(hours):
        if h in ch_hours:
            # charging: add energy (limited to capacity)
            current = min(100.0, current + (100.0 / n_charge))
        elif h in dis_hours:
            # discharging: remove energy × RTE
            current = max(0.0, current - (100.0 * rte / n_discharge))
        soc[idx] = round(current, 1)

    return {
        "ch_hours":      sorted(ch_hours),
        "dis_hours":     sorted(dis_hours),
        "avg_ch":        round(avg_ch, 2),
        "avg_dis":       round(avg_dis, 2),
        "charge_cost":   round(charge_cost, 2),
        "discharge_rev": round(discharge_rev, 2),
        "net_revenue":   net_revenue,
        "revenue_mwh":   revenue_mwh,
        "soc":           soc,
        "hours":         hours,
        "lmps":          lmps,
        "rte":           rte,
        "capacity_mwh":  capacity_mwh,
        "charge_hrs":    charge_hrs,
        "discharge_hrs": discharge_hrs,
    }


# ═══════════════════════════════════════════════════════════════════
# BESS CHART BUILDERS
# ═══════════════════════════════════════════════════════════════════
def _layout(title="", height=380):
    return dict(
        title=dict(text=title, font=dict(family="Playfair Display", size=14, color="#1a1a18"), x=0.01),
        height=height,
        paper_bgcolor="#ffffff", plot_bgcolor="#f7f7f5",
        font=dict(family="DM Sans", color="#1a1a18", size=11),
        xaxis=dict(gridcolor="#e2e0db", linecolor="#d0cdc6",
                   tickfont=dict(size=10, color="#6b6b64")),
        yaxis=dict(gridcolor="#e2e0db", linecolor="#d0cdc6",
                   tickfont=dict(size=10, color="#6b6b64")),
        legend=dict(bgcolor="rgba(247,247,245,0.96)", bordercolor="#e2e0db",
                    borderwidth=1, font=dict(size=10),
                    orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=20, t=55, b=50),
        hovermode="x unified",
    )


def chart_bess_lmp(res, label):
    """LMP bar chart with charge/discharge windows highlighted."""
    hours = res["hours"]
    lmps  = res["lmps"]
    ch    = set(res["ch_hours"])
    dis   = set(res["dis_hours"])

    colors = []
    for h, v in zip(hours, lmps):
        if h in ch:
            colors.append("#1D9E75")   # green = charging
        elif h in dis:
            colors.append("#c8102e")   # red   = discharging
        elif v < 0:
            colors.append("#E24B4A")   # light red = negative price
        else:
            colors.append("#B5D4F4")   # light blue = idle

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=hours, y=lmps,
        marker_color=colors, marker_line_width=0,
        name="LMP $/MWh",
        hovertemplate="Hr %{x}: $%{y:.2f}/MWh<extra></extra>",
    ))

    # Avg charge line
    fig.add_hline(y=res["avg_ch"], line_dash="dot", line_color="#1D9E75", line_width=1.5,
                  annotation_text=f"Avg charge ${res['avg_ch']:.2f}",
                  annotation_font=dict(color="#1D9E75", size=9), annotation_position="left")
    # Avg discharge line
    fig.add_hline(y=res["avg_dis"], line_dash="dot", line_color="#c8102e", line_width=1.5,
                  annotation_text=f"Avg discharge ${res['avg_dis']:.2f}",
                  annotation_font=dict(color="#c8102e", size=9), annotation_position="right")

    lay = _layout(f"{label} — LMP with Charge/Discharge Windows", 320)
    lay["xaxis"].update(title="Hour ending", tickmode="linear", dtick=1, range=[0.5, 24.5])
    lay["yaxis"].update(title="$/MWh", tickprefix="$")
    fig.update_layout(**lay)
    return fig


def chart_soc(res, label):
    """State of Charge profile over 24 hours."""
    hours = list(res["hours"])
    soc   = list(res["soc"])
    ch    = set(res["ch_hours"])
    dis   = set(res["dis_hours"])

    fig = go.Figure()

    # SOC area
    fig.add_trace(go.Scatter(
        x=hours, y=soc,
        mode="lines+markers",
        name="SOC %",
        line=dict(color="#185FA5", width=2.5),
        marker=dict(size=6, color="#185FA5"),
        fill="tozeroy",
        fillcolor="rgba(24,95,165,0.1)",
        hovertemplate="Hr %{x} — SOC: %{y:.1f}%<extra></extra>",
    ))

    # Charge window shading
    for h in sorted(ch):
        fig.add_vrect(x0=h-0.5, x1=h+0.5,
                      fillcolor="rgba(29,158,117,0.12)", layer="below", line_width=0)
    # Discharge window shading
    for h in sorted(dis):
        fig.add_vrect(x0=h-0.5, x1=h+0.5,
                      fillcolor="rgba(200,16,46,0.08)", layer="below", line_width=0)

    # 80% and 20% reference lines
    fig.add_hline(y=80, line_dash="dot", line_color="rgba(100,100,100,0.3)", line_width=1,
                  annotation_text="80%", annotation_font=dict(size=9, color="#9b9b92"))
    fig.add_hline(y=20, line_dash="dot", line_color="rgba(100,100,100,0.3)", line_width=1,
                  annotation_text="20%", annotation_font=dict(size=9, color="#9b9b92"))

    lay = _layout(f"{label} — State of Charge (SOC) Profile", 260)
    lay["xaxis"].update(title="Hour ending", tickmode="linear", dtick=1, range=[0.5, 24.5])
    lay["yaxis"].update(title="SOC (%)", tickprefix="", ticksuffix="%",
                        range=[-5, 108])
    fig.update_layout(**lay)
    return fig


def chart_revenue_waterfall(res2, res4):
    """Side-by-side revenue waterfall comparing 2H and 4H strategies."""
    fig = go.Figure()

    for res, color, label in [
        (res2, "#1D9E75", "2H Storage"),
        (res4, "#185FA5", "4H Storage"),
    ]:
        x_vals = [f"{label}\nCharge cost", f"{label}\nDischarge rev", f"{label}\nNet (after RTE)"]
        y_vals = [-res["charge_cost"], res["discharge_rev"], res["net_revenue"]]
        bar_colors = ["#E24B4A", "#1D9E75", color]
        fig.add_trace(go.Bar(
            x=x_vals, y=y_vals,
            marker_color=bar_colors,
            marker_line_width=0,
            text=[f"${abs(v):,.0f}" for v in y_vals],
            textposition="outside",
            textfont=dict(size=10),
            name=label,
            hovertemplate="%{x}<br>$%{y:,.2f}<extra></extra>",
        ))

    lay = _layout("Revenue Breakdown — 2H vs 4H Storage (per 100 MWh capacity)", 320)
    lay["yaxis"].update(title="$ per cycle", tickprefix="")
    lay["xaxis"].update(tickfont=dict(size=10))
    fig.update_layout(**lay)
    return fig


# ═══════════════════════════════════════════════════════════════════
# MAIN BESS STRATEGY SECTION RENDERER
# ═══════════════════════════════════════════════════════════════════
def render_bess_section(df):
    """
    Full BESS storage strategy analysis section.
    Called after data is loaded. Shows a button to reveal the section.
    """
    st.markdown('<hr style="border-color:#e2e0db;margin:24px 0 16px"/>', unsafe_allow_html=True)

    # ── Section header with expand button ────────────────────────
    col_hd, col_btn = st.columns([4, 1])
    with col_hd:
        st.markdown("""
        <div style="font-family:'DM Mono',monospace;font-size:10px;color:#9b9b92;
             letter-spacing:.14em;text-transform:uppercase;margin-bottom:4px;font-weight:500">
             Battery Storage Strategy Analyser</div>
        <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:700;
             color:#1a1a18;letter-spacing:-0.01em">BESS Dispatch Optimisation</div>
        """, unsafe_allow_html=True)
    with col_btn:
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        show_bess = st.toggle("Run Analysis", key="show_bess_toggle", value=False)

    if not show_bess:
        st.markdown("""
        <div style="background:#f7f7f5;border:1px solid #e2e0db;border-left:4px solid #185FA5;
             border-radius:2px;padding:14px 20px;margin-top:8px">
            <div style="font-family:'DM Sans',sans-serif;font-size:13px;color:#6b6b64;line-height:1.6">
                Toggle <b>Run Analysis</b> to model 2H and 4H battery dispatch strategies on this LMP data.<br>
                Includes: charge/discharge windows · net revenue · RTE impact · hourly SOC profile.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Build hourly profile from data ────────────────────────────
    df2 = df.copy()
    if "datetime" in df2.columns:
        df2["datetime"] = pd.to_datetime(df2["datetime"], errors="coerce")
        df2["_hour_int"] = df2["datetime"].dt.hour + 1
    elif "hourending" in df2.columns:
        def ph(h):
            h = str(h).strip()
            if ":" in h: return int(h.split(":")[0])
            try: return int(float(h))
            except: return 1
        df2["_hour_int"] = df2["hourending"].apply(ph)
    else:
        st.warning("Cannot determine hour column for BESS analysis.")
        return

    hourly = df2.groupby("_hour_int")["lmp"].mean().reset_index()
    hourly.columns = ["Hour", "lmp"]
    hourly = hourly.sort_values("Hour").reset_index(drop=True)

    if len(hourly) < 6:
        st.warning("Not enough hourly data for BESS analysis. Load at least 1 full day.")
        return

    # ── Use-case selector buttons ─────────────────────────────────
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#6b6b64;
         letter-spacing:.14em;text-transform:uppercase;margin:18px 0 10px;font-weight:500">
         Select Storage Strategy</div>
    """, unsafe_allow_html=True)

    uc_col1, uc_col2, uc_col3 = st.columns(3)
    with uc_col1:
        btn_2h = st.button("⚡ 2H Storage\n2.5 hr charge · 2 hr discharge",
                           key="bess_btn_2h", use_container_width=True)
    with uc_col2:
        btn_4h = st.button("🔋 4H Storage\n4.5 hr charge · 4 hr discharge",
                           key="bess_btn_4h", use_container_width=True)
    with uc_col3:
        btn_both = st.button("📊 Compare Both\n2H vs 4H side-by-side",
                             key="bess_btn_both", use_container_width=True)

    if btn_2h:   st.session_state["bess_mode"] = "2h"
    if btn_4h:   st.session_state["bess_mode"] = "4h"
    if btn_both: st.session_state["bess_mode"] = "both"

    mode = st.session_state.get("bess_mode", None)
    if mode is None:
        st.markdown("""
        <div style="background:#f7f7f5;border:1px solid #e2e0db;border-radius:2px;
             padding:12px 18px;margin-top:8px;font-family:'DM Sans',sans-serif;
             font-size:13px;color:#9b9b92;text-align:center">
             Select a strategy above to run the analysis
        </div>""", unsafe_allow_html=True)
        return

    # ── Parameters panel ─────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#6b6b64;
         letter-spacing:.14em;text-transform:uppercase;margin:16px 0 8px;font-weight:500">
         Parameters</div>
    """, unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        rte = st.slider("Round-Trip Efficiency (RTE %)", min_value=70, max_value=98,
                        value=85, step=1, key="bess_rte") / 100.0
    with p2:
        capacity = st.number_input("Battery Capacity (MWh)", min_value=1, max_value=10000,
                                   value=100, step=10, key="bess_capacity")
    with p3:
        power_mw = st.number_input("Power Rating (MW)", min_value=1, max_value=5000,
                                   value=50, step=5, key="bess_power")
    with p4:
        cycles_yr = st.number_input("Cycles per Year", min_value=1, max_value=365,
                                    value=250, step=10, key="bess_cycles")

    # ── Run strategies ─────────────────────────────────────────────
    res2 = bess_strategy(hourly, charge_hrs=2.5, discharge_hrs=2.0,
                         rte=rte, capacity_mwh=capacity)
    res4 = bess_strategy(hourly, charge_hrs=4.5, discharge_hrs=4.0,
                         rte=rte, capacity_mwh=capacity)

    # Annual revenue estimate
    ann2 = round(res2["net_revenue"] * cycles_yr, 0)
    ann4 = round(res4["net_revenue"] * cycles_yr, 0)

    # ── RENDER based on mode ─────────────────────────────────────
    def render_single(res, label, ann_rev):
        # Summary cards
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Charge Window",    f"Hr {min(res['ch_hours'])}–{max(res['ch_hours'])}",
                  f"{res['charge_hrs']} hrs")
        c2.metric("Discharge Window", f"Hr {min(res['dis_hours'])}–{max(res['dis_hours'])}",
                  f"{res['discharge_hrs']} hrs")
        c3.metric("Avg Buy Price",    f"${res['avg_ch']:.2f}/MWh")
        c4.metric("Avg Sell Price",   f"${res['avg_dis']:.2f}/MWh")
        c5.metric("Net Revenue/cycle",f"${res['net_revenue']:.2f}",
                  f"RTE {int(rte*100)}%")
        c6.metric("Est. Annual Rev",  f"${ann_rev:,.0f}",
                  f"{cycles_yr} cycles/yr")

        # RTE detail
        st.markdown(f"""
        <div style="background:#f0efec;border-left:4px solid #185FA5;border-radius:2px;
             padding:10px 16px;margin:10px 0 14px;font-family:'DM Sans',sans-serif;
             font-size:13px;color:#3d3d38;line-height:1.7">
            <b>Round-Trip Efficiency breakdown</b><br>
            Charge cost: <b>${res['charge_cost']:,.2f}</b> ({res['charge_hrs']} hrs × {capacity} MWh × ${res['avg_ch']:.2f}/MWh)
            &nbsp;·&nbsp;
            Discharge revenue: <b>${res['discharge_rev']:,.2f}</b> ({res['discharge_hrs']} hrs × {capacity} MWh × {int(rte*100)}% RTE × ${res['avg_dis']:.2f}/MWh)
            &nbsp;·&nbsp;
            <b>Net = ${res['net_revenue']:.2f}</b> per cycle
            &nbsp;·&nbsp;
            Energy lost to RTE: <b>{round((1-rte)*100,1)}%</b>
            ({round(capacity*(1-rte),1)} MWh per cycle)
        </div>
        """, unsafe_allow_html=True)

        # LMP + SOC charts
        st.plotly_chart(chart_bess_lmp(res, label), use_container_width=True)
        st.plotly_chart(chart_soc(res, label), use_container_width=True)

        # Legend
        st.markdown("""
        <div style="display:flex;gap:18px;font-family:'DM Mono',monospace;font-size:10px;
             color:#6b6b64;padding:6px 0;flex-wrap:wrap">
            <span><span style="display:inline-block;width:12px;height:12px;background:#1D9E75;
                  border-radius:2px;margin-right:5px;vertical-align:middle"></span>Charging window</span>
            <span><span style="display:inline-block;width:12px;height:12px;background:#c8102e;
                  border-radius:2px;margin-right:5px;vertical-align:middle"></span>Discharging window</span>
            <span><span style="display:inline-block;width:12px;height:12px;background:#E24B4A;
                  border-radius:2px;margin-right:5px;vertical-align:middle"></span>Negative LMP (idle)</span>
            <span><span style="display:inline-block;width:12px;height:12px;background:#B5D4F4;
                  border-radius:2px;margin-right:5px;vertical-align:middle"></span>Idle (positive LMP)</span>
        </div>
        """, unsafe_allow_html=True)

        # Data table
        with st.expander("📋 Hourly dispatch table"):
            tbl = pd.DataFrame({
                "Hour":       res["hours"],
                "LMP ($/MWh)":res["lmps"].round(2),
                "Action":    ["🟢 Charging" if h in set(res["ch_hours"])
                               else "🔴 Discharging" if h in set(res["dis_hours"])
                               else "⚪ Idle" for h in res["hours"]],
                "SOC (%)":   res["soc"],
            })
            st.dataframe(tbl, use_container_width=True, height=300,
                column_config={
                    "LMP ($/MWh)": st.column_config.NumberColumn(format="$%.2f"),
                    "SOC (%)":     st.column_config.NumberColumn(format="%.1f%%"),
                })

    if mode == "2h":
        st.markdown("""<div style="font-family:'Playfair Display',serif;font-size:17px;
             font-weight:700;color:#1a1a18;margin:12px 0 8px">⚡ 2H Storage Strategy
             <span style="font-family:'DM Mono',monospace;font-size:11px;font-weight:400;
             color:#6b6b64;margin-left:8px">2.5 hr charge · 2 hr discharge</span></div>""",
             unsafe_allow_html=True)
        render_single(res2, "2H Storage", ann2)

    elif mode == "4h":
        st.markdown("""<div style="font-family:'Playfair Display',serif;font-size:17px;
             font-weight:700;color:#1a1a18;margin:12px 0 8px">🔋 4H Storage Strategy
             <span style="font-family:'DM Mono',monospace;font-size:11px;font-weight:400;
             color:#6b6b64;margin-left:8px">4.5 hr charge · 4 hr discharge</span></div>""",
             unsafe_allow_html=True)
        render_single(res4, "4H Storage", ann4)

    elif mode == "both":
        # Comparison summary table
        st.markdown("""<div style="font-family:'Playfair Display',serif;font-size:17px;
             font-weight:700;color:#1a1a18;margin:12px 0 12px">📊 2H vs 4H Strategy Comparison</div>""",
             unsafe_allow_html=True)

        comp_data = {
            "Metric": [
                "Charge duration", "Discharge duration",
                "Charge window", "Discharge window",
                "Avg buy price", "Avg sell price",
                "Charge cost (per cycle)", "Discharge revenue (per cycle)",
                "Net revenue (per cycle)", "RTE loss per cycle",
                f"Est. annual revenue ({cycles_yr} cycles)",
            ],
            "2H Storage": [
                f"{res2['charge_hrs']} hrs", f"{res2['discharge_hrs']} hrs",
                f"Hr {min(res2['ch_hours'])}–{max(res2['ch_hours'])}",
                f"Hr {min(res2['dis_hours'])}–{max(res2['dis_hours'])}",
                f"${res2['avg_ch']:.2f}/MWh", f"${res2['avg_dis']:.2f}/MWh",
                f"${res2['charge_cost']:,.2f}", f"${res2['discharge_rev']:,.2f}",
                f"${res2['net_revenue']:.2f}", f"{round((1-rte)*capacity,1)} MWh",
                f"${ann2:,.0f}",
            ],
            "4H Storage": [
                f"{res4['charge_hrs']} hrs", f"{res4['discharge_hrs']} hrs",
                f"Hr {min(res4['ch_hours'])}–{max(res4['ch_hours'])}",
                f"Hr {min(res4['dis_hours'])}–{max(res4['dis_hours'])}",
                f"${res4['avg_ch']:.2f}/MWh", f"${res4['avg_dis']:.2f}/MWh",
                f"${res4['charge_cost']:,.2f}", f"${res4['discharge_rev']:,.2f}",
                f"${res4['net_revenue']:.2f}", f"{round((1-rte)*capacity,1)} MWh",
                f"${ann4:,.0f}",
            ],
        }
        st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)

        # Revenue waterfall
        st.plotly_chart(chart_revenue_waterfall(res2, res4), use_container_width=True)

        # Side-by-side LMP charts
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:10px;color:#6b6b64;
                 letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px">2H Storage</div>""",
                 unsafe_allow_html=True)
            st.plotly_chart(chart_bess_lmp(res2, "2H"), use_container_width=True)
            st.plotly_chart(chart_soc(res2, "2H SOC"), use_container_width=True)
        with col_r:
            st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:10px;color:#6b6b64;
                 letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px">4H Storage</div>""",
                 unsafe_allow_html=True)
            st.plotly_chart(chart_bess_lmp(res4, "4H"), use_container_width=True)
            st.plotly_chart(chart_soc(res4, "4H SOC"), use_container_width=True)

        # Legend
        st.markdown("""
        <div style="display:flex;gap:18px;font-family:'DM Mono',monospace;font-size:10px;
             color:#6b6b64;padding:6px 0;flex-wrap:wrap">
            <span><span style="display:inline-block;width:12px;height:12px;background:#1D9E75;
                  border-radius:2px;margin-right:5px;vertical-align:middle"></span>Charging</span>
            <span><span style="display:inline-block;width:12px;height:12px;background:#c8102e;
                  border-radius:2px;margin-right:5px;vertical-align:middle"></span>Discharging</span>
            <span><span style="display:inline-block;width:12px;height:12px;background:#E24B4A;
                  border-radius:2px;margin-right:5px;vertical-align:middle"></span>Negative LMP</span>
            <span><span style="display:inline-block;width:12px;height:12px;background:#B5D4F4;
                  border-radius:2px;margin-right:5px;vertical-align:middle"></span>Idle</span>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# STANDARD LMP CHARTS (unchanged from previous version)
# ═══════════════════════════════════════════════════════════════════
def chart_hourly_timeline(df, bus):
    fig    = go.Figure()
    colors = ["#E24B4A" if v < 0 else "#185FA5" for v in df["lmp"]]
    fig.add_trace(go.Bar(
        x=df["datetime"], y=df["lmp"],
        marker_color=colors, marker_line_width=0,
        name="LMP $/MWh",
        hovertemplate="<b>%{x|%b %d %H:00}</b><br>LMP: $%{y:.2f}/MWh<extra></extra>",
    ))
    if len(df) >= 24:
        roll = df["lmp"].rolling(24, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df["datetime"], y=roll,
            mode="lines", name="24-hr rolling avg",
            line=dict(color="#c8102e", width=2, dash="dot"),
            hovertemplate="Avg: $%{y:.2f}<extra></extra>",
        ))
    lay = _layout(f"Hourly LMP — {bus}", 420)
    lay["xaxis"].update(title="Date / Hour", tickformat="%b %d")
    lay["yaxis"].update(title="LMP ($/MWh)", tickprefix="$")
    fig.update_layout(**lay)
    return fig


def chart_daily_avg(df):
    df2    = df.copy()
    df2["date"] = pd.to_datetime(df2["deliverydate"], errors="coerce")
    daily  = df2.groupby("date")["lmp"].mean().reset_index()
    daily.columns = ["date","avg_lmp"]
    fig = go.Figure(go.Bar(
        x=daily["date"], y=daily["avg_lmp"],
        marker_color=["#E24B4A" if v < 0 else "#185FA5" for v in daily["avg_lmp"]],
        marker_line_width=0,
        text=daily["avg_lmp"].apply(lambda v: f"${v:.1f}"),
        textposition="outside", textfont=dict(size=9),
        hovertemplate="<b>%{x|%b %d}</b><br>Daily avg: $%{y:.2f}/MWh<extra></extra>",
    ))
    lay = _layout("Daily Average LMP", 280)
    lay["xaxis"].update(tickformat="%b %d")
    lay["yaxis"].update(title="$/MWh", tickprefix="$")
    fig.update_layout(**lay)
    return fig


def chart_price_distribution(df):
    fig = go.Figure()
    neg = df[df["lmp"] < 0]["lmp"]
    pos = df[df["lmp"] >= 0]["lmp"]
    if len(pos):
        fig.add_trace(go.Histogram(x=pos, nbinsx=40, name="≥ $0/MWh",
            marker_color="#185FA5", opacity=0.75,
            hovertemplate="$%{x:.0f}: %{y} hrs<extra></extra>"))
    if len(neg):
        fig.add_trace(go.Histogram(x=neg, nbinsx=20, name="< $0/MWh (neg)",
            marker_color="#E24B4A", opacity=0.75,
            hovertemplate="$%{x:.0f}: %{y} hrs<extra></extra>"))
    lay = _layout("LMP Price Distribution", 240)
    lay["xaxis"].update(title="LMP ($/MWh)")
    lay["yaxis"].update(title="Hours", tickprefix="")
    lay["barmode"] = "overlay"
    fig.update_layout(**lay)
    return fig


def chart_hourly_profile(df, months):
    COLORS = ["#185FA5","#1D9E75","#c8102e","#b8860b","#7a1a5a","#5a1a7a"]
    df["month_label"] = pd.to_datetime(df["deliverydate"], errors="coerce").dt.strftime("%b %Y")
    df["_hour_int"]   = df["hourending"].apply(
        lambda h: int(str(h).split(":")[0]) if ":" in str(h) else int(float(h)))
    fig    = go.Figure()
    avail  = [m for m in months if m in df["month_label"].unique()]
    for i, month in enumerate(avail):
        mdf  = df[df["month_label"]==month]
        hpro = mdf.groupby("_hour_int")["lmp"].mean().reset_index()
        hpro.columns = ["hour","avg_lmp"]
        fig.add_trace(go.Scatter(
            x=hpro["hour"], y=hpro["avg_lmp"],
            mode="lines+markers", name=month,
            line=dict(color=COLORS[i%len(COLORS)], width=2.5),
            marker=dict(size=5),
            hovertemplate=f"{month} Hr%{{x}}: $%{{y:.2f}}<extra></extra>",
        ))
    lay = _layout("Average LMP by Hour of Day", 300)
    lay["xaxis"].update(title="Hour ending", tickmode="linear", dtick=1, range=[0.5, 24.5])
    lay["yaxis"].update(title="$/MWh", tickprefix="$")
    fig.update_layout(**lay)
    return fig


def chart_heatmap(df):
    df2       = df.copy()
    df2["date"] = pd.to_datetime(df2["deliverydate"], errors="coerce").dt.date
    df2["_hi"]  = df2["hourending"].apply(
        lambda h: int(str(h).split(":")[0]) if ":" in str(h) else int(float(h)))
    pivot = df2.pivot_table(index="_hi", columns="date", values="lmp", aggfunc="mean").sort_index()
    fig   = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[str(c) for c in pivot.columns],
        y=[f"{h}:00" for h in pivot.index],
        colorscale=[[0,"#E24B4A"],[0.35,"#f7f7f5"],[0.65,"#f7f7f5"],[1,"#185FA5"]],
        zmid=0,
        colorbar=dict(title="$/MWh", tickprefix="$", len=0.7),
        hovertemplate="Date: %{x}<br>Hour: %{y}<br>LMP: $%{z:.2f}<extra></extra>",
    ))
    lay = _layout("LMP Heatmap — Hour × Date", 460)
    lay["xaxis"].update(title="Date", tickangle=-45, tickfont=dict(size=9))
    lay["yaxis"].update(title="Hour ending", tickfont=dict(size=9), tickprefix="")
    fig.update_layout(**lay)
    return fig


# ═══════════════════════════════════════════════════════════════════
# CREDENTIAL FORM
# ═══════════════════════════════════════════════════════════════════
def _render_credentials_form():
    st.markdown("""
    <div style="background:#f7f7f5;border:1px solid #e2e0db;border-left:4px solid #c8102e;
         border-radius:2px;padding:20px 24px;margin-bottom:20px">
        <div style="font-family:'DM Mono',monospace;font-size:10px;color:#c8102e;
             letter-spacing:.14em;text-transform:uppercase;margin-bottom:10px">
            ERCOT API Credentials Required</div>
        <div style="font-family:'DM Sans',sans-serif;font-size:13px;color:#3d3d38;line-height:1.6">
            Enter your ERCOT API credentials below, or add them to
            <code>secrets.toml</code> for permanent storage:<br><br>
            <code>[ercot]<br>username = "your@email.com"<br>
            password = "yourpassword"<br>
            subscription_key = "your_subscription_key"</code>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔑 Enter ERCOT API Credentials", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            u = st.text_input("ERCOT Email", key="_ercot_user_in",
                              value=st.session_state.get("_ercot_user",""),
                              placeholder="you@company.com")
            if u: st.session_state["_ercot_user"] = u
        with c2:
            p = st.text_input("ERCOT Password", key="_ercot_pass_in", type="password",
                              value=st.session_state.get("_ercot_pass",""))
            if p: st.session_state["_ercot_pass"] = p
        with c3:
            sk = st.text_input("Subscription Key", key="_ercot_subkey_in",
                               value=st.session_state.get("_ercot_subkey",""),
                               placeholder="32-char hex key")
            if sk: st.session_state["_ercot_subkey"] = sk

        if st.button("Connect to ERCOT API →", type="primary", key="connect_btn"):
            with st.spinner("Authenticating..."):
                token, err = get_ercot_token(
                    st.session_state.get("_ercot_user",""),
                    st.session_state.get("_ercot_pass",""),
                )
            if token:
                st.session_state["ercot_token"]     = token
                st.session_state["ercot_token_exp"] = time.time() + 3500
                st.success("✅ Connected to ERCOT API")
                st.rerun()
            else:
                st.error(f"Authentication failed: {err}")


# ═══════════════════════════════════════════════════════════════════
# MAIN PAGE
# ═══════════════════════════════════════════════════════════════════
def render_live_lmp_page():
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="tag">ERCOT API · Live Market Data</div>
            <h1>Live LMP <span>Dashboard</span></h1>
        </div>
        <div class="ph-right">DAM Hourly LMP<br>Direct API Pull</div>
    </div>
    """, unsafe_allow_html=True)

    username, password, subscription_key = _get_credentials()
    if not username or not password or not subscription_key:
        _render_credentials_form()
        return

    token, token_err = _ensure_token()
    if token_err == "credentials_missing":
        _render_credentials_form()
        return
    elif token_err:
        st.error(f"Authentication error: {token_err}")
        _render_credentials_form()
        return

    exp_ts    = st.session_state.get("ercot_token_exp", 0)
    mins_left = max(0, int((exp_ts - time.time()) / 60))
    st.markdown(
        f'<div style="font-family:DM Mono,monospace;font-size:10px;color:#1a6a1a;'
        f'background:#e8f5e8;border:1px solid #90c890;border-radius:2px;'
        f'padding:5px 12px;display:inline-block;margin-bottom:16px">'
        f'✓ ERCOT API Connected — token valid {mins_left} min</div>',
        unsafe_allow_html=True,
    )

    # ── Query controls ─────────────────────────────────────────────
    st.markdown(
        '<div style="background:#f7f7f5;border:1px solid #e2e0db;border-radius:2px;'
        'padding:20px 22px;margin-bottom:20px">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
        'letter-spacing:.14em;text-transform:uppercase;margin-bottom:14px;font-weight:500">'
        'Query Parameters</div>',
        unsafe_allow_html=True,
    )

    qc1, qc2, qc3, qc4, qc5 = st.columns([3,2,2,1,1])

    with qc1:
        bus_input = st.text_input(
            "Bus Name",
            value=st.session_state.get("lmp_bus","BOWMAN_A5"),
            placeholder="e.g. BOWMAN_A5, HB_NORTH ...",
            key="lmp_bus_input",
        )
        st.session_state["lmp_bus"] = bus_input.strip()

    with qc2:
        preset = st.selectbox("Date preset",
            ["Last 7 days","Last 30 days","Last 90 days",
             "Last 6 months","Last 1 year","Custom range"],
            key="lmp_preset")

    today   = datetime.now().date()
    PRESETS = {
        "Last 7 days":   (today-timedelta(days=7),   today),
        "Last 30 days":  (today-timedelta(days=30),  today),
        "Last 90 days":  (today-timedelta(days=90),  today),
        "Last 6 months": (today-timedelta(days=182), today),
        "Last 1 year":   (today-timedelta(days=365), today),
        "Custom range":  (today-timedelta(days=30),  today),
    }
    d_from_default, d_to_default = PRESETS[preset]

    with qc3:
        if preset == "Custom range":
            date_range = st.date_input("Date range",
                value=(d_from_default, d_to_default), key="lmp_daterange")
            d_from = str(date_range[0]) if isinstance(date_range, tuple) else str(d_from_default)
            d_to   = str(date_range[1]) if isinstance(date_range, tuple) and len(date_range)>1 else str(d_to_default)
        else:
            d_from = str(d_from_default)
            d_to   = str(d_to_default)
            st.markdown(
                f'<div style="font-family:DM Mono,monospace;font-size:11px;color:#6b6b64;'
                f'padding:8px 0">{d_from} → {d_to}</div>',
                unsafe_allow_html=True,
            )

    with qc4:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        fetch_btn = st.button("Fetch Data →", type="primary",
                              key="fetch_live_btn", use_container_width=True)
    with qc5:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        clear_btn = st.button("Clear", key="clear_lmp_btn", use_container_width=True)

    if clear_btn:
        for k in ["lmp_live_df","lmp_live_bus","lmp_live_from","lmp_live_to","bess_mode"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if fetch_btn:
        bus = st.session_state["lmp_bus"]
        if not bus:
            st.warning("Enter a bus name first")
        else:
            with st.spinner(f"Fetching {bus}  {d_from} → {d_to} …"):
                df_live, err = fetch_dam_lmp(
                    bus_name=bus, date_from=d_from, date_to=d_to,
                    _token=token, subscription_key=subscription_key,
                )
            if err:
                st.error(f"API Error: {err}")
            else:
                st.session_state["lmp_live_df"]   = df_live
                st.session_state["lmp_live_bus"]  = bus
                st.session_state["lmp_live_from"] = d_from
                st.session_state["lmp_live_to"]   = d_to
                st.session_state.pop("bess_mode", None)
                st.success(f"✅ {len(df_live):,} records loaded for {bus}")

    df = st.session_state.get("lmp_live_df")
    if df is None:
        st.markdown("""
        <div class="map-placeholder" style="padding:48px 20px;margin-top:8px">
            <div class="mp-icon">📈</div>
            <div class="mp-title">No data loaded yet</div>
            <div class="mp-sub">Enter a bus name and date range above, then click <b>Fetch Data →</b></div>
        </div>""", unsafe_allow_html=True)
        return

    bus      = st.session_state.get("lmp_live_bus","")
    stats    = compute_stats(df)
    d_from_s = st.session_state.get("lmp_live_from","")
    d_to_s   = st.session_state.get("lmp_live_to","")

    # ── Summary metrics ────────────────────────────────────────────
    st.markdown(
        f'<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
        f'letter-spacing:.14em;text-transform:uppercase;margin:4px 0 10px;font-weight:500">'
        f'{bus}  ·  {d_from_s} → {d_to_s}  ·  {stats["count"]:,} hourly intervals</div>',
        unsafe_allow_html=True,
    )

    m1,m2,m3,m4,m5,m6,m7 = st.columns(7)
    m1.metric("Avg LMP",       f"${stats['avg']}")
    m2.metric("Max LMP",       f"${stats['max']}")
    m3.metric("Min LMP",       f"${stats['min']}")
    m4.metric("P90",           f"${stats['p90']}")
    m5.metric("P10",           f"${stats['p10']}")
    m6.metric("Neg Price Hrs", f"{stats['neg_count']}", f"{stats['neg_pct']}%")
    m7.metric("Spread",        f"${stats['spread']}")

    if stats["spread"] > 80:
        st.success("✅  High merchant spread — strong BESS arbitrage opportunity (spread > $80/MWh)")
    elif stats["neg_pct"] > 20:
        st.error(f"⚠️  {stats['neg_pct']}% negative price hours — HIGH curtailment risk")
    elif stats["neg_pct"] > 5:
        st.warning(f"⚠️  {stats['neg_pct']}% negative price hours — medium curtailment exposure")
    else:
        st.info(f"ℹ️  Avg LMP ${stats['avg']}/MWh · Spread ${stats['spread']}/MWh")

    st.markdown('<hr style="border-color:#e2e0db;margin:14px 0"/>', unsafe_allow_html=True)

    # ── Standard charts ────────────────────────────────────────────
    st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
                'letter-spacing:.14em;text-transform:uppercase;margin-bottom:8px">Hourly LMP Timeline</div>',
                unsafe_allow_html=True)
    st.plotly_chart(chart_hourly_timeline(df, bus), use_container_width=True)

    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
                    'letter-spacing:.14em;text-transform:uppercase;margin-bottom:8px">Daily Average</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_daily_avg(df), use_container_width=True)
    with cc2:
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
                    'letter-spacing:.14em;text-transform:uppercase;margin-bottom:8px">Price Distribution</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_price_distribution(df), use_container_width=True)

    if "deliverydate" in df.columns:
        df["_month_lbl"] = pd.to_datetime(df["deliverydate"], errors="coerce").dt.strftime("%b %Y")
        months_avail     = sorted(
            set(df["_month_lbl"].dropna().unique().tolist()),
            key=lambda m: datetime.strptime(m, "%b %Y"))
        if months_avail:
            st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
                        'letter-spacing:.14em;text-transform:uppercase;margin:8px 0 8px">Avg LMP by Hour of Day (by Month)</div>',
                        unsafe_allow_html=True)
            sel_months = st.multiselect("Select months to compare", options=months_avail,
                default=months_avail[-min(3, len(months_avail)):], key="lmp_months_sel")
            if sel_months:
                df["_hour_int"] = df["hourending"].apply(
                    lambda h: int(str(h).split(":")[0]) if ":" in str(h) else int(float(h)))
                st.plotly_chart(chart_hourly_profile(df, sel_months), use_container_width=True)

    st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
                'letter-spacing:.14em;text-transform:uppercase;margin:8px 0 8px">LMP Heatmap (Hour × Day)</div>',
                unsafe_allow_html=True)
    days_in = df["deliverydate"].nunique() if "deliverydate" in df.columns else 0
    hmap_df = df[df["deliverydate"].isin(sorted(df["deliverydate"].unique())[-60:])] if days_in > 60 else df.copy()
    if days_in > 60:
        st.caption("Heatmap limited to most recent 60 days for readability.")
    st.plotly_chart(chart_heatmap(hmap_df), use_container_width=True)

    if "deliverydate" in df.columns:
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
                    'letter-spacing:.14em;text-transform:uppercase;margin:8px 0 8px">Monthly Price Summary</div>',
                    unsafe_allow_html=True)
        df["_ym"] = pd.to_datetime(df["deliverydate"], errors="coerce").dt.to_period("M")
        monthly   = df.groupby("_ym")["lmp"].agg(
            Avg="mean", Max="max", Min="min",
            P10=lambda x: x.quantile(0.10),
            P90=lambda x: x.quantile(0.90),
            NegHours=lambda x: (x < 0).sum(),
            NegPct=lambda x: round((x < 0).mean() * 100, 1),
        ).reset_index()
        monthly.columns = ["Month","Avg $/MWh","Max $/MWh","Min $/MWh",
                           "P10 $/MWh","P90 $/MWh","Neg Hours","Neg %"]
        monthly["Month"] = monthly["Month"].astype(str)
        for col in ["Avg $/MWh","Max $/MWh","Min $/MWh","P10 $/MWh","P90 $/MWh"]:
            monthly[col] = monthly[col].round(2)
        fig_mth = go.Figure(go.Bar(
            x=monthly["Month"], y=monthly["Avg $/MWh"],
            marker_color=["#E24B4A" if v<0 else "#185FA5" for v in monthly["Avg $/MWh"]],
            marker_line_width=0,
            text=monthly["Avg $/MWh"].apply(lambda v: f"${v:.1f}"),
            textposition="outside", textfont=dict(size=10),
            hovertemplate="<b>%{x}</b><br>Monthly avg: $%{y:.2f}/MWh<extra></extra>",
        ))
        lay_mth = _layout("Monthly Average LMP", 220)
        lay_mth["yaxis"].update(title="$/MWh", tickprefix="$")
        fig_mth.update_layout(**lay_mth)
        st.plotly_chart(fig_mth, use_container_width=True)
        st.dataframe(monthly, use_container_width=True,
            column_config={
                "Avg $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                "Max $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                "Min $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                "P10 $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                "P90 $/MWh": st.column_config.NumberColumn(format="$%.2f"),
                "Neg %":     st.column_config.NumberColumn(format="%.1f%%"),
            },
            height=min(300, 40+len(monthly)*35))

    # ── Raw data + CSV ─────────────────────────────────────────────
    st.markdown('<hr style="border-color:#e2e0db;margin:20px 0"/>', unsafe_allow_html=True)
    with st.expander("📄 Raw Data Table"):
        disp_cols = [c for c in ["deliverydate","hourending","busname","lmp","dstflag"] if c in df.columns]
        st.dataframe(df[disp_cols].reset_index(drop=True), use_container_width=True, height=300)

    csv_bytes = df.to_csv(index=False).encode()
    st.download_button(f"↓ Download {bus} LMP CSV", data=csv_bytes,
        file_name=f"ercot_dam_lmp_{bus}_{d_from_s}_{d_to_s}.csv",
        mime="text/csv", type="primary", key="dl_lmp_csv")

    # ── BESS STRATEGY MODULE ───────────────────────────────────────
    render_bess_section(df)
