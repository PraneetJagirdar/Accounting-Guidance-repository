
# Accounting & Regulatory Standards – India (Starter)

Static portal with curated official links and an updates panel driven by `data/amendments.json`.

## Quick start

1. Serve locally:
   ```bash
   cd accounting-standards-portal
   python -m http.server 8000
   # open http://localhost:8000
   ```
2. Deploy on GitHub Pages:
   - Create a repo and push this folder.
   - In repo Settings → Pages → Source: `main` / root.

## Auto-updates (optional)
- Add logic in `scripts/fetch_updates.py` to scrape or read RSS from:
  - RBI Notifications / RSS
  - SEBI Circulars
  - MCA Ind AS Rules notifications
  - CBDT Circulars
  - CBIC GST updates
- The provided GitHub Action runs daily and commits `data/amendments.json`.

## Structure
- `index.html` – main page
- `assets/` – CSS & JS
- `data/amendments.json` – updates data store
- `scripts/fetch_updates.py` – fill this to fetch updates
- `.github/workflows/fetch_updates.yml` – schedule

---
This is a starter—you can extend sections, add state-specific GST links, or include internal policies.
