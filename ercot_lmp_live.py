# ═══════════════════════════════════════════════════════════════════
# ERCOT LIVE LMP ENGINE — Drop-in module for SunStripe Nodal Platform
# ═══════════════════════════════════════════════════════════════════
#
# HOW TO USE:
# 1. Save this file as  ercot_lmp_live.py  in your repo root
# 2. In your main app.py, add to the sidebar radio:
#       "📈 Live LMP Dashboard"
# 3. Add the elif block at the bottom of your page routing:
#       elif page == "📈 Live LMP Dashboard":
#           from ercot_lmp_live import render_live_lmp_page
#           render_live_lmp_page()
#
# GITHUB → STREAMLIT CLOUD DEPLOYMENT:
# 1. Push this file to your GitHub repo
# 2. Add secrets in Streamlit Cloud dashboard:
#       [ercot]
#       username = "your@email.com"
#       password = "yourpassword"
#       subscription_key = "your_32char_subscription_key"
# 3. The app auto-refreshes tokens — no Postman needed
#
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json

# ─────────────────────────────────────────────────────────────────
# ERCOT AUTH — Auto-managed token (1-hour TTL)
# ─────────────────────────────────────────────────────────────────

TOKEN_URL = (
    "https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com"
    "/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token"
)
CLIENT_ID = "fec253ea-0d06-4272-a5e6-b478baeecd70"
SCOPE     = f"openid+{CLIENT_ID}+offline_access"
API_BASE  = "https://api.ercot.com/api/public-reports"


def _get_credentials():
    """Pull credentials from Streamlit secrets or session-state manual entry."""
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


def get_ercot_token(username: str, password: str) -> tuple[str | None, str | None]:
    """POST to ERCOT B2C and return (id_token, error)."""
    params = {
        "username":      username,
        "password":      password,
        "grant_type":    "password",
        "scope":         SCOPE,
        "client_id":     CLIENT_ID,
        "response_type": "id_token",
    }
    try:
        r = requests.post(TOKEN_URL, params=params, timeout=20,
                          headers={"Content-Type": "application/x-www-form-urlencoded"})
        if r.status_code == 200:
            data = r.json()
            token = data.get("id_token") or data.get("access_token")
            if token:
                return token, None
            return None, f"Token not in response: {list(data.keys())}"
        return None, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return None, str(e)


def _ensure_token():
    """Return a valid Bearer token, refreshing if expired or missing."""
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
        st.session_state["ercot_token_exp"] = now + 3500   # ~58 min
        return token, None
    return None, err


# ─────────────────────────────────────────────────────────────────
# ERCOT API CALLS
# ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_dam_lmp(
    bus_name: str,
    date_from: str,
    date_to: str,
    _token: str,
    subscription_key: str,
    max_pages: int = 20,
) -> tuple[pd.DataFrame | None, str | None]:
    """
    Fetch DAM Hourly LMP for a single bus across a date range.
    Paginates automatically (max_pages × 1000 records = up to 20,000 rows).
    Returns (DataFrame, error_string_or_None).
    """
    endpoint = f"{API_BASE}/np4-183-cd/dam_hourly_lmp"
    headers  = {
        "Authorization":          f"Bearer {_token}",
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Accept":                 "application/json",
    }
    all_rows = []
    page     = 1

    while page <= max_pages:
        params = {
            "deliveryDateFrom": date_from,
            "deliveryDateTo":   date_to,
            "busName":          bus_name,
            "size":             1000,
            "page":             page,
        }
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

        # Handle both flat array and nested {data:{data:[]}} shapes
        raw = body.get("data", [])
        if isinstance(raw, dict):
            raw = raw.get("data", [])
        if not isinstance(raw, list):
            raw = []

        all_rows.extend(raw)

        meta       = body.get("_meta", {})
        total_pgs  = meta.get("totalPages", 1)
        if page >= total_pgs:
            break
        page += 1

    if not all_rows:
        return None, "No data returned — verify bus name and date range"

    # Parse fields from response
    fields = body.get("fields", [])
    if fields:
        col_names = [f["name"] for f in fields]
    else:
        # Fallback column order for DAM Hourly LMP
        col_names = ["deliveryDate", "hourEnding", "busName", "LMP", "DSTFlag"]

    df = pd.DataFrame(all_rows, columns=col_names[: len(all_rows[0])] if all_rows else col_names)

    # Normalise column names
    df.columns = [c.lower().strip() for c in df.columns]
    lmp_col    = next((c for c in df.columns if c in ("lmp", "settlementpointprice", "price")), None)
    if lmp_col and lmp_col != "lmp":
        df = df.rename(columns={lmp_col: "lmp"})

    df["lmp"] = pd.to_numeric(df["lmp"], errors="coerce")

    # Build datetime
    if "deliverydate" in df.columns and "hourending" in df.columns:
        df["hourending"] = df["hourending"].astype(str)
        # Handle "01:00", "1", "1.0" etc.
        def parse_hour(h):
            h = str(h).strip()
            if ":" in h:
                return int(h.split(":")[0])
            try:
                return int(float(h))
            except Exception:
                return 1
        df["_hour_int"] = df["hourending"].apply(parse_hour)
        df["datetime"]  = (
            pd.to_datetime(df["deliverydate"], errors="coerce")
            + pd.to_timedelta(df["_hour_int"] - 1, unit="h")
        )
    else:
        df["datetime"] = pd.NaT

    df = df.sort_values("datetime").reset_index(drop=True)
    return df, None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_rtm_spp(
    settlement_point: str,
    date_from: str,
    date_to: str,
    _token: str,
    subscription_key: str,
) -> tuple[pd.DataFrame | None, str | None]:
    """Fetch RTM 15-min Settlement Point Prices."""
    endpoint = f"{API_BASE}/np6-785-cd/rtm_spp"
    headers  = {
        "Authorization":             f"Bearer {_token}",
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Accept":                    "application/json",
    }
    params = {
        "deliveryDateFrom": date_from,
        "deliveryDateTo":   date_to,
        "settlementPoint":  settlement_point,
        "size":             1000,
        "page":             1,
    }
    try:
        r = requests.get(endpoint, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        body = r.json()
        raw  = body.get("data", [])
        if isinstance(raw, dict):
            raw = raw.get("data", [])
        if not raw:
            return None, "No RTM data returned"
        fields = [f["name"].lower() for f in body.get("fields", [])]
        df = pd.DataFrame(raw, columns=fields[: len(raw[0])] if raw else fields)
        price_col = next((c for c in df.columns if "price" in c or "spp" in c), None)
        if price_col:
            df = df.rename(columns={price_col: "price"})
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        return df, None
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────────

def _layout(title="", height=420):
    return dict(
        title=dict(text=title, font=dict(family="Playfair Display", size=15, color="#1a1a18"), x=0.01),
        height=height,
        paper_bgcolor="#ffffff", plot_bgcolor="#f7f7f5",
        font=dict(family="DM Sans", color="#1a1a18", size=11),
        xaxis=dict(gridcolor="#e2e0db", linecolor="#d0cdc6",
                   tickfont=dict(size=10, color="#6b6b64")),
        yaxis=dict(gridcolor="#e2e0db", linecolor="#d0cdc6",
                   tickfont=dict(size=10, color="#6b6b64"), tickprefix="$"),
        legend=dict(bgcolor="rgba(247,247,245,0.96)", bordercolor="#e2e0db",
                    borderwidth=1, font=dict(size=10),
                    orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=20, t=55, b=50),
        hovermode="x unified",
    )


def chart_hourly_timeline(df: pd.DataFrame, bus: str) -> go.Figure:
    """Full time-series — one bar per hour, red=negative, blue=positive."""
    fig = go.Figure()
    colors = ["#E24B4A" if v < 0 else "#185FA5" for v in df["lmp"]]

    fig.add_trace(go.Bar(
        x=df["datetime"], y=df["lmp"],
        marker_color=colors, marker_line_width=0,
        name="LMP $/MWh",
        hovertemplate="<b>%{x|%b %d %H:00}</b><br>LMP: $%{y:.2f}/MWh<extra></extra>",
    ))

    # Rolling 24-hr average overlay
    if len(df) >= 24:
        roll = df["lmp"].rolling(24, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df["datetime"], y=roll,
            mode="lines", name="24-hr rolling avg",
            line=dict(color="#c8102e", width=2, dash="dot"),
            hovertemplate="Avg: $%{y:.2f}<extra></extra>",
        ))

    lay = _layout(f"Hourly LMP — {bus}", 460)
    lay["xaxis"].update(title="Date / Hour", tickformat="%b %d")
    lay["yaxis"].update(title="LMP ($/MWh)")
    fig.update_layout(**lay)
    return fig


def chart_daily_avg(df: pd.DataFrame) -> go.Figure:
    """Daily average LMP bar chart."""
    df["date"] = pd.to_datetime(df["deliverydate"], errors="coerce")
    daily = df.groupby("date")["lmp"].mean().reset_index()
    daily.columns = ["date", "avg_lmp"]

    fig = go.Figure(go.Bar(
        x=daily["date"], y=daily["avg_lmp"],
        marker_color=["#E24B4A" if v < 0 else "#185FA5" for v in daily["avg_lmp"]],
        marker_line_width=0,
        text=daily["avg_lmp"].apply(lambda v: f"${v:.1f}"),
        textposition="outside",
        textfont=dict(size=9),
        hovertemplate="<b>%{x|%b %d}</b><br>Daily avg: $%{y:.2f}/MWh<extra></extra>",
    ))

    lay = _layout("Daily Average LMP", 300)
    lay["xaxis"].update(tickformat="%b %d")
    lay["yaxis"].update(title="$/MWh")
    fig.update_layout(**lay)
    return fig


def chart_hourly_profile(df: pd.DataFrame, months: list[str]) -> go.Figure:
    """Average LMP by hour-of-day, one line per calendar month."""
    COLORS = ["#185FA5", "#1D9E75", "#c8102e", "#b8860b", "#7a1a5a", "#5a1a7a"]
    df["month_label"] = pd.to_datetime(df["deliverydate"], errors="coerce").dt.strftime("%b %Y")
    df["_hour_int"]   = df["_hour_int"] if "_hour_int" in df.columns else (
        df["hourending"].apply(lambda h: int(str(h).split(":")[0]) if ":" in str(h) else int(float(h)))
    )

    fig  = go.Figure()
    avail = [m for m in months if m in df["month_label"].unique()]
    for i, month in enumerate(avail):
        mdf  = df[df["month_label"] == month]
        hpro = mdf.groupby("_hour_int")["lmp"].mean().reset_index()
        hpro.columns = ["hour", "avg_lmp"]
        fig.add_trace(go.Scatter(
            x=hpro["hour"], y=hpro["avg_lmp"],
            mode="lines+markers", name=month,
            line=dict(color=COLORS[i % len(COLORS)], width=2.5),
            marker=dict(size=5),
            hovertemplate=f"{month} Hr%{{x}}: $%{{y:.2f}}<extra></extra>",
        ))

    lay = _layout("Average LMP by Hour of Day", 320)
    lay["xaxis"].update(title="Hour ending", tickmode="linear", dtick=1, range=[0.5, 24.5])
    lay["yaxis"].update(title="$/MWh")
    fig.update_layout(**lay)
    return fig


def chart_price_distribution(df: pd.DataFrame) -> go.Figure:
    """LMP frequency histogram with negative price shading."""
    fig = go.Figure()
    neg = df[df["lmp"] < 0]["lmp"]
    pos = df[df["lmp"] >= 0]["lmp"]

    if len(pos):
        fig.add_trace(go.Histogram(
            x=pos, nbinsx=40, name="≥ $0/MWh",
            marker_color="#185FA5", opacity=0.75,
            hovertemplate="$%{x:.0f}: %{y} hrs<extra></extra>",
        ))
    if len(neg):
        fig.add_trace(go.Histogram(
            x=neg, nbinsx=20, name="< $0/MWh (neg)",
            marker_color="#E24B4A", opacity=0.75,
            hovertemplate="$%{x:.0f}: %{y} hrs<extra></extra>",
        ))

    lay = _layout("LMP Price Distribution — Frequency Histogram", 260)
    lay["xaxis"].update(title="LMP ($/MWh)")
    lay["yaxis"].update(title="Hours", tickprefix="")
    lay["barmode"] = "overlay"
    fig.update_layout(**lay)
    return fig


def chart_heatmap(df: pd.DataFrame) -> go.Figure:
    """Hour-of-day × Date heatmap."""
    df["date"]    = pd.to_datetime(df["deliverydate"], errors="coerce").dt.date
    df["_hi"]     = df["hourending"].apply(
        lambda h: int(str(h).split(":")[0]) if ":" in str(h) else int(float(h))
    )
    pivot = df.pivot_table(index="_hi", columns="date", values="lmp", aggfunc="mean")
    pivot = pivot.sort_index()

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[str(c) for c in pivot.columns],
        y=[f"{h}:00" for h in pivot.index],
        colorscale=[
            [0.0, "#E24B4A"], [0.35, "#f7f7f5"],
            [0.65, "#f7f7f5"], [1.0, "#185FA5"],
        ],
        zmid=0,
        colorbar=dict(title="$/MWh", tickprefix="$", len=0.7),
        hovertemplate="Date: %{x}<br>Hour: %{y}<br>LMP: $%{z:.2f}<extra></extra>",
    ))

    lay = _layout("LMP Heatmap — Hour × Date", 480)
    lay["xaxis"].update(title="Date", tickangle=-45, tickfont=dict(size=9))
    lay["yaxis"].update(title="Hour ending", tickfont=dict(size=9), tickprefix="")
    fig.update_layout(**lay)
    return fig


# ─────────────────────────────────────────────────────────────────
# STATS HELPER
# ─────────────────────────────────────────────────────────────────

def compute_stats(df: pd.DataFrame) -> dict:
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


# ─────────────────────────────────────────────────────────────────
# CREDENTIAL ENTRY UI (shown if secrets not configured)
# ─────────────────────────────────────────────────────────────────

def _render_credentials_form():
    st.markdown("""
    <div style="background:#f7f7f5;border:1px solid #e2e0db;border-left:4px solid #c8102e;
         border-radius:2px;padding:20px 24px;margin-bottom:20px">
        <div style="font-family:'DM Mono',monospace;font-size:10px;color:#c8102e;
             letter-spacing:.14em;text-transform:uppercase;margin-bottom:10px">
            ERCOT API Credentials Required
        </div>
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


# ─────────────────────────────────────────────────────────────────
# MAIN PAGE RENDERER
# ─────────────────────────────────────────────────────────────────

def render_live_lmp_page():
    """
    Full Live LMP Dashboard page.
    Call this from your main app's page routing:
        elif page == "📈 Live LMP Dashboard":
            from ercot_lmp_live import render_live_lmp_page
            render_live_lmp_page()
    """

    # ── Page header ────────────────────────────────────────────────
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="tag">ERCOT API · Live Market Data</div>
            <h1>Live LMP <span>Dashboard</span></h1>
        </div>
        <div class="ph-right">DAM Hourly LMP<br>Direct API Pull</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Check / collect credentials ────────────────────────────────
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

    # ── Token status badge ─────────────────────────────────────────
    exp_ts  = st.session_state.get("ercot_token_exp", 0)
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

    qc1, qc2, qc3, qc4, qc5 = st.columns([3, 2, 2, 1, 1])

    with qc1:
        bus_input = st.text_input(
            "Bus Name",
            value=st.session_state.get("lmp_bus", "BOWMAN_A5"),
            placeholder="e.g. BOWMAN_A5, HB_NORTH, ...",
            key="lmp_bus_input",
            help="Exact ERCOT electrical bus name (case-sensitive)",
        )
        st.session_state["lmp_bus"] = bus_input.strip()

    with qc2:
        preset = st.selectbox(
            "Date preset",
            ["Last 7 days", "Last 30 days", "Last 90 days",
             "Last 6 months", "Last 1 year", "Custom range"],
            key="lmp_preset",
        )

    today   = datetime.now().date()
    PRESETS = {
        "Last 7 days":    (today - timedelta(days=7),   today),
        "Last 30 days":   (today - timedelta(days=30),  today),
        "Last 90 days":   (today - timedelta(days=90),  today),
        "Last 6 months":  (today - timedelta(days=182), today),
        "Last 1 year":    (today - timedelta(days=365), today),
        "Custom range":   (today - timedelta(days=30),  today),
    }
    d_from_default, d_to_default = PRESETS[preset]

    with qc3:
        if preset == "Custom range":
            date_range = st.date_input(
                "Date range",
                value=(d_from_default, d_to_default),
                key="lmp_daterange",
            )
            d_from = str(date_range[0]) if isinstance(date_range, tuple) else str(d_from_default)
            d_to   = str(date_range[1]) if isinstance(date_range, tuple) and len(date_range) > 1 else str(d_to_default)
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
        for k in ["lmp_live_df", "lmp_live_bus", "lmp_live_from", "lmp_live_to"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Trigger fetch ──────────────────────────────────────────────
    if fetch_btn:
        bus = st.session_state["lmp_bus"]
        if not bus:
            st.warning("Enter a bus name first")
        else:
            with st.spinner(f"Fetching {bus}  {d_from} → {d_to} …"):
                df_live, err = fetch_dam_lmp(
                    bus_name=bus,
                    date_from=d_from,
                    date_to=d_to,
                    _token=token,
                    subscription_key=subscription_key,
                )
            if err:
                st.error(f"API Error: {err}")
            else:
                st.session_state["lmp_live_df"]   = df_live
                st.session_state["lmp_live_bus"]  = bus
                st.session_state["lmp_live_from"] = d_from
                st.session_state["lmp_live_to"]   = d_to
                st.success(f"✅ {len(df_live):,} records loaded for {bus}")

    # ── Display ────────────────────────────────────────────────────
    df = st.session_state.get("lmp_live_df")
    if df is None:
        st.markdown("""
        <div class="map-placeholder" style="padding:48px 20px;margin-top:8px">
            <div class="mp-icon">📈</div>
            <div class="mp-title">No data loaded yet</div>
            <div class="mp-sub">
                Enter a bus name and date range above, then click <b>Fetch Data →</b><br>
                The dashboard will auto-populate with 6 charts and full statistics.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    bus       = st.session_state.get("lmp_live_bus", "")
    stats     = compute_stats(df)
    d_from_s  = st.session_state.get("lmp_live_from", "")
    d_to_s    = st.session_state.get("lmp_live_to",   "")

    # ── Summary metric cards ───────────────────────────────────────
    st.markdown(
        '<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
        'letter-spacing:.14em;text-transform:uppercase;margin:4px 0 10px;font-weight:500">'
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

    # ── Price signal banner ────────────────────────────────────────
    if stats["spread"] > 80:
        st.success("✅  High merchant spread detected — strong Battery / Arbitrage opportunity (spread > $80/MWh)")
    elif stats["neg_pct"] > 20:
        st.error(f"⚠️  {stats['neg_pct']}% negative price hours — HIGH curtailment risk for solar / wind at this bus")
    elif stats["neg_pct"] > 5:
        st.warning(f"⚠️  {stats['neg_pct']}% negative price hours — medium curtailment exposure")
    else:
        st.info(f"ℹ️  Avg LMP ${stats['avg']}/MWh · Spread ${stats['spread']}/MWh")

    st.markdown('<hr style="border-color:#e2e0db;margin:14px 0"/>', unsafe_allow_html=True)

    # ── CHART 1 — Full hourly timeline ────────────────────────────
    st.markdown(
        '<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
        'letter-spacing:.14em;text-transform:uppercase;margin-bottom:8px">Hourly LMP Timeline</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(chart_hourly_timeline(df, bus), use_container_width=True)

    # ── CHARTS 2 + 3 side by side ─────────────────────────────────
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown(
            '<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
            'letter-spacing:.14em;text-transform:uppercase;margin-bottom:8px">Daily Average</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(chart_daily_avg(df), use_container_width=True)
    with cc2:
        st.markdown(
            '<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
            'letter-spacing:.14em;text-transform:uppercase;margin-bottom:8px">Price Distribution</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(chart_price_distribution(df), use_container_width=True)

    # ── CHART 4 — Hourly profile by month ─────────────────────────
    if "deliverydate" in df.columns:
        df["_month_lbl"] = pd.to_datetime(df["deliverydate"], errors="coerce").dt.strftime("%b %Y")
        months_avail     = df["_month_lbl"].dropna().unique().tolist()
        months_avail     = sorted(set(months_avail),
                                  key=lambda m: datetime.strptime(m, "%b %Y"))
        if len(months_avail) >= 1:
            st.markdown(
                '<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
                'letter-spacing:.14em;text-transform:uppercase;margin:8px 0 8px">Avg LMP by Hour of Day (by Month)</div>',
                unsafe_allow_html=True,
            )
            sel_months = st.multiselect(
                "Select months to compare",
                options=months_avail,
                default=months_avail[-min(3, len(months_avail)):],
                key="lmp_months_sel",
            )
            if sel_months:
                df["_hour_int"] = df["hourending"].apply(
                    lambda h: int(str(h).split(":")[0]) if ":" in str(h) else int(float(h))
                )
                st.plotly_chart(chart_hourly_profile(df, sel_months), use_container_width=True)

    # ── CHART 5 — Heatmap ─────────────────────────────────────────
    st.markdown(
        '<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
        'letter-spacing:.14em;text-transform:uppercase;margin:8px 0 8px">LMP Heatmap (Hour × Day)</div>',
        unsafe_allow_html=True,
    )
    days_in_data = df["deliverydate"].nunique() if "deliverydate" in df.columns else 0
    if days_in_data > 60:
        st.caption("Heatmap limited to most recent 60 days for readability.")
        recent_dates = sorted(df["deliverydate"].unique())[-60:]
        hmap_df      = df[df["deliverydate"].isin(recent_dates)]
    else:
        hmap_df = df.copy()
    st.plotly_chart(chart_heatmap(hmap_df), use_container_width=True)

    # ── CHART 6 — Monthly summary table ───────────────────────────
    if "deliverydate" in df.columns:
        st.markdown(
            '<div style="font-family:DM Mono,monospace;font-size:10px;color:#9b9b92;'
            'letter-spacing:.14em;text-transform:uppercase;margin:8px 0 8px">Monthly Price Summary</div>',
            unsafe_allow_html=True,
        )
        df["_ym"] = pd.to_datetime(df["deliverydate"], errors="coerce").dt.to_period("M")
        monthly = df.groupby("_ym")["lmp"].agg(
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

        # Mini bar chart of monthly avg
        fig_mth = go.Figure(go.Bar(
            x=monthly["Month"], y=monthly["Avg $/MWh"],
            marker_color=["#E24B4A" if v < 0 else "#185FA5" for v in monthly["Avg $/MWh"]],
            marker_line_width=0,
            text=monthly["Avg $/MWh"].apply(lambda v: f"${v:.1f}"),
            textposition="outside",
            textfont=dict(size=10),
            hovertemplate="<b>%{x}</b><br>Monthly avg: $%{y:.2f}/MWh<extra></extra>",
        ))
        lay_mth = _layout("Monthly Average LMP", 240)
        lay_mth["yaxis"].update(title="$/MWh")
        fig_mth.update_layout(**lay_mth)
        st.plotly_chart(fig_mth, use_container_width=True)

        st.dataframe(
            monthly,
            use_container_width=True,
            column_config={
                "Avg $/MWh":  st.column_config.NumberColumn(format="$%.2f"),
                "Max $/MWh":  st.column_config.NumberColumn(format="$%.2f"),
                "Min $/MWh":  st.column_config.NumberColumn(format="$%.2f"),
                "P10 $/MWh":  st.column_config.NumberColumn(format="$%.2f"),
                "P90 $/MWh":  st.column_config.NumberColumn(format="$%.2f"),
                "Neg %":      st.column_config.NumberColumn(format="%.1f%%"),
            },
            height=min(300, 40 + len(monthly) * 35),
        )

    # ── Raw data table + CSV export ────────────────────────────────
    st.markdown('<hr style="border-color:#e2e0db;margin:20px 0"/>', unsafe_allow_html=True)
    with st.expander("📄 Raw Data Table"):
        disp_cols = [c for c in ["deliverydate","hourending","busname","lmp","dstflag"]
                     if c in df.columns]
        st.dataframe(df[disp_cols].reset_index(drop=True),
                     use_container_width=True, height=300)

    csv_bytes = df.to_csv(index=False).encode()
    st.download_button(
        f"↓ Download {bus} LMP CSV",
        data=csv_bytes,
        file_name=f"ercot_dam_lmp_{bus}_{d_from_s}_{d_to_s}.csv",
        mime="text/csv",
        type="primary",
        key="dl_lmp_csv",
    )
