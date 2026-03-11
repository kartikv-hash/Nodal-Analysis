# ⚡ ERCOT Bus · Substation Lookup

A fast Streamlit app for looking up ERCOT settlement points — built for **SunStripe's** renewable energy project development workflow.

> **Part of the SunStripe tool suite** alongside the [ERCOT BESS Dashboard](https://ercot-bess-dashboard-nhh9eztsqeuqxxuz97kacu.streamlit.app/) and [SiteIQ Fatal Flaw Analyser](https://fatal-flaw-o7aks4agtoffgyydbvrguj.streamlit.app/).

---

## Features

| Mode | Description |
|---|---|
| **Bus → Substation** | Search any electrical bus name → get substation, voltage, zone, PSSE info |
| **Substation → Buses** | Find all buses at any given substation |
| **Browse All** | Filter the full 19,056-row dataset by zone, kV, resource node status |
| **Detail Cards** | Exact-match summary cards with all metadata |
| **Export CSV** | Download any filtered result set |

### Dataset
- **19,056** ERCOT settlement points
- **4,959** unique substations
- All 4 load zones: LZ_NORTH, LZ_SOUTH, LZ_WEST, LZ_HOUSTON
- Voltage levels: 500 / 345 / 230 / 138 / 69 / 34.5 / 13.8 kV
- Source: ERCOT Settlement Points — February 20, 2026

---

## Repo Structure

```
ercot-bus-lookup/
├── app.py                                      # Main Streamlit app
├── Settlement_Points_02202026_094122.csv       # ERCOT data (committed to repo)
├── requirements.txt                            # Python dependencies
├── .streamlit/
│   └── config.toml                             # Dark theme config
└── README.md
```

---

## Deploy to Streamlit Community Cloud

1. **Fork / push this repo to GitHub**

2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**

3. Set:
   - **Repository**: `your-username/ercot-bus-lookup`
   - **Branch**: `main`
   - **Main file path**: `app.py`

4. Click **Deploy** — live in ~2 minutes ✅

---

## Run Locally

```bash
git clone https://github.com/your-username/ercot-bus-lookup.git
cd ercot-bus-lookup
pip install -r requirements.txt
streamlit run app.py
```

---

## Updating the Data

When ERCOT publishes a new settlement points CSV:

1. Replace the CSV file in the repo root
2. Update the filename reference in `app.py` (line ~38):
   ```python
   df = pd.read_csv("Settlement_Points_NEWDATE.csv", dtype=str).fillna("")
   ```
3. Commit & push → Streamlit Cloud auto-redeploys

---

*Built by SunStripe · ERCOT BESS & Solar Project Development*
