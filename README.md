# AI Agents Surplus Food Distribution  

Tech stack: **Python** (frontend+backend), **Flask** (UI), **MySQL**, **HTML5/CSS**, **AI Agents (Python classes)**.

## Features
- Registration/login with email as the **primary key**.
- Strict geo-guard:   pincodes only.
- Donor: post surplus food (veg/non-veg auto-categorized input).
- Recipient: request meals with veg preference.
- AI Matching Agent computes compatibility scores.
- Logistics Agent assigns vehicles and builds a nearest-neighbor route.
- Monitoring Agent sends **Gmail** email updates (match/status).
- Simple Ops Dashboard to create matches and manage deliveries.

## Setup
1. Create and activate a Python 3.11+ virtual env.
2. `pip install -r requirements.txt`
3. Create MySQL database food_NGO (or set another name in `.env`).
4. Copy `.env.sample` → `.env` and fill values.
5. `python app.py` and open `http://localhost:5000`.

## Notes
- Vehicles seed on first run for demo.
- Email uses Gmail SMTP with an **App Password**.
