# AGENTS.md

## Project Overview
UK Multimodal Public Transport System optimization. Flask backend + React frontend + Valhalla routing engine.

## Architecture
- `app/` - Flask backend (Python 3.10)
  - `api/routes.py` - API endpoints (registered under `/api` prefix)
  - `algorithm_engine/` - Core routing algorithms
  - `utils/settings.py` - Config with dotenv loading
- `frontend/` - React 19 + Vite + TailwindCSS v4
- `routing_engine/` - Valhalla Docker container for routing

## Developer Commands

### Backend
```bash
source .venv/bin/activate          # activate venv (not .venv\Scripts\activate)
pip install -r requirements.txt
export FLASK_APP=run.py             # required env var
flask run                           # or: python run.py
```
Server runs on `127.0.0.1:5000`.

### Frontend
```bash
cd frontend
npm install
npm run dev                        # http://127.0.0.1:5173
npm run build                       # production build
npm run lint                       # eslint
```

### Routing Engine (Valhalla)
```bash
cd routing_engine
docker compose up -d                # starts Valhalla on port 8002
docker start valhalla              # restart
docker stop valhalla               # stop
```

## Linting

### Python
- Black: `black --check --diff .` (line-length: 100 in pyproject.toml)
- Flake8: `flake8 .` (max-line-length: 120 in .flake8, ignores F401)
- CI runs both on every push/PR

### JavaScript (frontend only)
```bash
cd frontend && npm run lint
```

## Testing
No test suite exists.

## Key Files
- `run.py` - Flask entry point (calls `create_app()` from `app/__init__.py`)
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Valhalla routing service config
- `bus_graph.graphml` - Large graph data file (gitignored)
- `app/data/roads_only.osm.pbf` - OSM road data for Greater Manchester

## Environment
- Python 3.10.4 (see `.python-version`)
- Flask + flask-cors enabled
- `.env` file required (SECRET_KEY) - gitignored
