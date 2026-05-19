# QC Charts Made Easier
### Sex Steroid Hormone Panel — Internal Quality Control System

---

## Setup & Installation

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Features

- **15 hormone panel** with pre-loaded ±2SD acceptance limits
- **SST entry form** — initials, email, hormone selector, value input
- **Auto QC check** — immediately checks if value is within ±2SD
- **Levey-Jennings chart** — per hormone, updates with every new entry
- **Data table** — full log with initials, date/time, SST value, pass/fail status
- **Email alerts** — automatic email when SST value fails (configure SMTP in sidebar)
- **CSV export** — download filtered data at any time

---

## Email Alert Setup (Gmail example)

1. In the sidebar, enter:
   - SMTP Server: `smtp.gmail.com`
   - SMTP Port: `587`
   - Sender Email: your Gmail address
   - Sender Password: your Gmail **App Password** (not your regular password)

2. To create a Gmail App Password:
   - Go to your Google Account → Security → 2-Step Verification → App Passwords
   - Generate a password for "Mail"

---

## Hormones in the panel

| # | Hormone |
|---|---------|
| 1 | 11-deoxycorticosterone |
| 2 | 11-deoxycortisol |
| 3 | 17-OHP |
| 4 | 21-deoxycortisol |
| 5 | Aldosterone |
| 6 | Androstenedione |
| 7 | Corticosterone |
| 8 | Cortisol |
| 9 | Cortisone |
| 10 | Dexamethasone |
| 11 | DHEA |
| 12 | DHEA-S |
| 13 | DHT |
| 14 | Progesterone |
| 15 | Testosterone |

---

## Data storage

All entries are saved to `qc_data.csv` in the same folder as `app.py`.
This file is created automatically on first use.

---

*Developed for internal laboratory quality control use.*
