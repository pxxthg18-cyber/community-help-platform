# Community Help and Support Platform

A small educational Flask application for posting local community help requests and coordinating volunteer responses.

## Features
- Submit help requests in Education, Food, Transportation, and Emergency Assistance categories.
- Browse and filter requests by category and status.
- Volunteers can accept open requests.
- Accepted requests can be marked completed.
- Dashboard counts and a health endpoint.
- SQLite storage, input validation, automated tests, and Docker Compose support.

> **Safety note:** This is a learning prototype, not an emergency-response service. Do not submit sensitive personal information. For immediate danger, contact local emergency services.

## Requirements
- Python 3.10+ (or Docker Desktop with Docker Compose).

## Run locally (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```
If PowerShell blocks activation, run `py -m pip install -r requirements.txt` and `py app.py` without activating.
Open http://127.0.0.1:5000.

## Run tests
```powershell
python -m pytest -v
```

## Run with Docker
```powershell
docker compose up --build
```
Open http://localhost:5000. Stop with Ctrl+C. The named Docker volume preserves the SQLite database.

## Main routes
- `/` — dashboard
- `/requests` — browse/filter help requests
- `/request-help` — submit a request
- `/health` — health check

## Suggested Git workflow
Use meaningful commits, e.g.:
1. `chore: create Flask project structure`
2. `feat: add help request submission`
3. `feat: add volunteer request workflow`
4. `test: cover request and status workflows`
5. `docs: document setup and review findings`

Only report commits and test results that you actually performed.

## Limitations
This prototype has no authentication, role-based access control, email/SMS alerts, moderation, or verified emergency workflow. Names are display labels, not verified identities. Do not deploy for real emergency handling without a security and privacy review.
