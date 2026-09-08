# SURAKSHA AI — Full-stack hackathon build

This repository contains a React/Vite frontend and FastAPI backend for SURAKSHA AI.

## What is functional
- Live Open-Meteo weather retrieval
- USGS real-time earthquake GeoJSON feed
- Explainable AI-assisted weather/seismic risk scoring
- Combined hazard score
- Rescue priority calculation
- Resource-demand estimation
- PostgreSQL/SQLite persistence
- SOS persistence
- Disaster reports
- Volunteer registration
- Live Leaflet/OpenStreetMap map
- Geolocation
- Dark/light theme persistence
- English/Telugu/Hindi UI switching (architecture is ready for the remaining languages)
- Responsive mobile layout

## Important safety boundary
This project does **not** claim guaranteed prediction of disasters. Weather-derived risk is an explainable assessment from forecast variables, and the earthquake component is a recent-event seismic signal. Official government warnings must take priority.

## Local run

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
copy .env.example .env   # Windows
npm run dev
```

Open http://localhost:5173.

## Render
1. Push this folder to GitHub.
2. Create the PostgreSQL database first.
3. Deploy `backend` as a Docker web service, with `DATABASE_URL` and `CORS_ORIGINS`.
4. Deploy `frontend` as a Static Site and set `VITE_API_URL` to the backend URL.
5. Do not put database credentials in frontend code.

## Data sources
- Open-Meteo Forecast API: weather forecasts.
- USGS Earthquake GeoJSON: real-time earthquake feed.
- OpenStreetMap tiles for the map.

The code intentionally keeps source/freshness/disclaimer information visible so judges can distinguish live external data from demo/simulation data.
