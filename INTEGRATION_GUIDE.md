# ERCOT Live LMP Dashboard — Integration Guide

## What This Adds to SunStripe

A new **📈 Live LMP Dashboard** page that:

- Pulls data **directly from the ERCOT API** (no Postman needed)
- Auto-manages Bearer Token refresh (1-hour TTL)
- Shows **6 charts** for any bus + date range you query
- Deploys to Streamlit Cloud via GitHub in 3 steps

---

## Files to Add to Your GitHub Repo

```
your-repo/
├── app.py                  ← your existing file (edit 2 lines)
├── ercot_lmp_live.py       ← NEW — drop this in repo root
├── .streamlit/
│   └── secrets.toml        ← NEW — add your ERCOT credentials
└── Settlement_Points_...csv
```

---

## Step 1 — Add `ercot_lmp_live.py` to your repo

Copy the file exactly as provided. No edits needed.

---

## Step 2 — Edit `app.py` (2 changes only)

### Change A — Sidebar radio (add one line)

Find this section in your sidebar:
```python
page = st.radio("", [
    "🗺️ Infrastructure Map",
    "⚡ Node & Hub Selector",
    "🔍 Bus Lookup",
    "🏭 Substation Lookup",
    "📋 Browse All",
], label_visibility="collapsed")
```

Change to:
```python
page = st.radio("", [
    "🗺️ Infrastructure Map",
    "⚡ Node & Hub Selector",
    "📈 Live LMP Dashboard",      # ← ADD THIS LINE
    "🔍 Bus Lookup",
    "🏭 Substation Lookup",
    "📋 Browse All",
], label_visibility="collapsed")
```

### Change B — Page routing (add one elif block)

At the very bottom of `app.py`, after the last `elif page == "📋 Browse All":` block, add:

```python
elif page == "📈 Live LMP Dashboard":
    from ercot_lmp_live import render_live_lmp_page
    render_live_lmp_page()
```

That's it. Two changes, ~4 lines total.

---

## Step 3 — Add ERCOT credentials to Streamlit Cloud

### Option A — Streamlit Cloud Secrets (recommended for deployment)

In your Streamlit Cloud dashboard:
1. Go to your app → **Settings → Secrets**
2. Add:

```toml
[ercot]
username = "your-ercot-email@example.com"
password = "your-ercot-password"
subscription_key = "5e31d09c11be47489c87dc89d07b89a1"
```

### Option B — Local `.streamlit/secrets.toml` (for local dev)

Create the file `.streamlit/secrets.toml` in your repo root:
```toml
[ercot]
username = "your-ercot-email@example.com"
password = "your-ercot-password"
subscription_key = "5e31d09c11be47489c87dc89d07b89a1"
```

> ⚠️ Add `.streamlit/secrets.toml` to your `.gitignore` — never commit credentials to GitHub.

If you don't add secrets, the dashboard shows a credential entry form where users can type them in manually at runtime.

---

## GitHub → Streamlit Cloud Deployment

```
1. git add ercot_lmp_live.py
2. git commit -m "Add Live LMP Dashboard"
3. git push origin main
```

Streamlit Cloud auto-redeploys on every push. Your new page appears within ~60 seconds.

---

## What the Dashboard Shows

| Chart | Description |
|---|---|
| **Hourly LMP Timeline** | Full bar chart of every hour — red=negative, blue=positive, with 24-hr rolling avg overlay |
| **Daily Average** | Daily avg LMP bar chart with color coding |
| **Price Distribution** | Frequency histogram — positive vs negative price hours |
| **Hourly Profile by Month** | Avg LMP by hour-of-day, one line per month — shows solar duck curve clearly |
| **LMP Heatmap** | Hour × Day heatmap — visual pattern of when prices are high/low |
| **Monthly Summary** | Monthly avg/max/min/P10/P90 + negative hour count table |

---

## How Authentication Works (No Postman Needed)

```
User clicks "Fetch Data →"
        ↓
ercot_lmp_live.py checks session_state for valid token
        ↓
If missing/expired → POST to ERCOT B2C OAuth endpoint
with username + password from secrets.toml
        ↓
Stores Bearer Token in session_state (valid 58 min)
        ↓
Makes paginated GET requests to:
https://api.ercot.com/api/public-reports/np4-183-cd/dam_hourly_lmp
with token + subscription key headers
        ↓
Returns DataFrame → charts render instantly
```

Token refresh is fully automatic. No manual Postman token copying ever again.

---

## Example Queries

| Bus Name | What it shows |
|---|---|
| `BOWMAN_A5` | Your current bus |
| `HB_NORTH` | North Hub — benchmark pricing |
| `HB_SOUTH` | South Hub |
| `HB_HOUSTON` | Houston Hub |
| `HB_WEST` | West Hub (wind country) |

---

## Requirements

Add these to your `requirements.txt` if not already present:

```
streamlit>=1.32
requests>=2.31
pandas>=2.0
plotly>=5.18
fpdf2>=2.7
folium>=0.15
streamlit-folium>=0.15
```
