# DevStats

Backend that authenticates via GitHub OAuth, syncs recent pull requests for a developer, and computes a lightweight score from activity and review signals.

## Prerequisites
- Python 3.11+ and `pip`
- PostgreSQL 14+ (or use the included `docker-compose.yml`)
- GitHub OAuth app (set callback to your API host, e.g., `http://localhost:8000/docs/oauth2-redirect`)

## Environment
Copy `.env.example` to `.env` and set:
- `DATABASE_URL` – async SQLAlchemy URL, e.g. `postgresql+asyncpg://user:pass@localhost:5432/db`
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` – from your GitHub OAuth app
- `JWT_SECRET` – any strong random string; used for signing and token encryption

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Start Postgres (optionally via Docker):
```bash
docker-compose up -d postgres
```
Run migrations:
```bash
cd backend
alembic upgrade head
```
Start the API:
```bash
uvicorn app.main:app --reload
```
Docs: http://localhost:8000/docs

## Auth flow (manual)
1) `GET /auth/login` → receive `authorization_url` + `state`
2) Open the URL, authorize with GitHub
3) Exchange the returned `code` via `POST /auth/callback` (body: `{"code": "...", "state": "..."}`) to get a JWT
4) Use `Authorization: Bearer <token>` for authenticated endpoints

## Scoring flow
- `POST /score/refresh` (auth required) fetches recent PRs from GitHub (defaults: last 30 days, up to 20 PRs), stores them, scores each PR, and returns totals + PR breakdown.
- `GET /users/me` returns your stored GitHub profile details.

## Key endpoints
- `GET /health` – service check
- `GET /auth/login` – GitHub OAuth URL + state
- `POST /auth/callback` – exchange code, upsert user, return JWT
- `GET /users/me` – current user (Bearer token)
- `POST /score/refresh` – sync PRs and return score (Bearer token)

## Repo layout (backend/)
- `app/main.py` – FastAPI app + routers
- `app/api/routes/` – auth, user, score endpoints
- `app/services/` – GitHub sync and scoring logic
- `app/integrations/` – GitHub API client
- `app/models/` – SQLAlchemy models
- `app/schemas/` – Pydantic schemas
- `alembic/` – database migrations

## Notes and caveats
- OAuth state is currently returned but not persisted/validated; add state storage before production use.
- GitHub rate limits apply; for higher volumes, add caching and conditional requests.
- Scoring is heuristic (merged status, additions/deletions, files, reviews, CI); tweak in `app/services/scoring_service.py`.

## Testing
Pytest is available; add a test DB URL and seed data before running:
```bash
pytest
```
