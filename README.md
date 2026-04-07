# PlanSync

PlanSync is a full-stack planner for students and young professionals who need one place for tasks, events, reminders, recurring routines, and a clear weekly view. The project works as a practical product even without AI or Google Calendar, while Mistral-based parsing and optional Google sync extend the workflow instead of replacing the manual planner.

## Overview

PlanSync solves the common student problem of fragmented planning:

- deadlines live in one app
- events live in another
- reminders are easy to forget
- free-text plans are quick to write but messy to structure

The app combines manual planning with optional AI-assisted extraction:

1. the user writes natural language text
2. the backend sends it to Mistral
3. the backend validates and normalizes structured output
4. the frontend shows an editable confirmation form
5. the item is saved only after explicit confirmation

Raw LLM output is never auto-saved.

## End User

- students managing deadlines, lectures, study sessions, and routines
- users who prefer a weekly calendar-style overview
- users who want AI to speed up data entry, but not control their planner

## Problem Solved

- combines tasks and events in one planning surface
- supports recurring study routines and repeated reminders
- reduces manual form-filling with AI parsing
- keeps AI safe by requiring confirmation before persistence
- stays useful when AI and Google integrations are disabled

## Main Features

- multi-user planner with strict per-user data isolation
- registration and login
- secure password hashing
- JWT-based auth with refresh session support
- manual create, edit, delete for tasks and events
- recurring items: daily, weekly, monthly
- multiple reminders per item
- weekly planner view
- completion tracking for recurring and non-recurring items
- AI-assisted parsing through Mistral only
- editable draft confirmation flow before save
- optional Google Calendar synchronization for events
- Docker Compose deployment
- Alembic migrations

## Tech Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, TanStack Query, React Hook Form
- Backend: FastAPI, Python 3.12, Pydantic v2, SQLAlchemy 2, Alembic
- Database: PostgreSQL
- Auth: password hashing via `pwdlib[bcrypt]`, JWT cookies, refresh sessions
- AI: Mistral API, structured extraction only
- Deployment: Docker Compose, Nginx, VM-friendly `.env` configuration

## Architecture Overview

### Frontend

- authentication pages: login and register
- protected planner dashboard with weekly view
- manual item modal for create/edit
- AI parse panel for free-text input
- draft confirmation page for reviewing parsed data before save
- integrations page for Google Calendar connect/disconnect status

### Backend

- `auth` endpoints for register/login/me/logout/refresh
- `items` endpoints for CRUD and completion state
- `planner` endpoint for weekly planner aggregation
- `reminders` endpoint for due reminders
- `ai` endpoints for parse draft, fetch draft, confirm draft, delete draft
- `integrations` endpoints for Google Calendar status, connect, disconnect, sync

### Data model

- `User`
- `AuthSession`
- `PlannerItem`
- `Reminder`
- `RecurrenceRule`
- `OccurrenceState`
- `ParsedDraft`
- `IntegrationMetadata`
- `SyncState`

## Project Structure

```text
StudyFlow/
├─ backend/
│  ├─ app/
│  │  ├─ api/v1/endpoints/
│  │  ├─ core/
│  │  ├─ db/
│  │  ├─ integrations/
│  │  ├─ models/
│  │  ├─ schemas/
│  │  ├─ services/
│  │  └─ utils/
│  ├─ alembic/
│  └─ tests/
├─ frontend/
│  ├─ src/app/
│  ├─ src/components/
│  ├─ src/features/
│  ├─ src/lib/
│  ├─ src/pages/
│  └─ public/
├─ docs/
├─ docker-compose.yml
└─ .env.example
```

## Setup

1. Copy `.env.example` to `.env`
2. Fill at least:
   - `SECRET_KEY`
   - `DATABASE_URL`
3. Optionally configure:
   - `MISTRAL_API_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REDIRECT_URI`

## Environment Variables

| Variable | Purpose | Required |
|---|---|---|
| `POSTGRES_DB` | PostgreSQL database name | for Docker |
| `POSTGRES_USER` | PostgreSQL username | for Docker |
| `POSTGRES_PASSWORD` | PostgreSQL password | for Docker |
| `DATABASE_URL` | SQLAlchemy connection string | yes |
| `APP_ENV` | runtime mode | no |
| `APP_HOST` | backend bind host | no |
| `APP_PORT` | backend bind port | no |
| `SECRET_KEY` | JWT/signing secret | yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | access token lifetime | no |
| `REFRESH_TOKEN_EXPIRE_DAYS` | refresh token lifetime | no |
| `COOKIE_SECURE` | secure cookie flag | no |
| `BACKEND_CORS_ORIGINS` | allowed frontend origins | no |
| `FRONTEND_URL` | frontend base URL | no |
| `API_BASE_URL` | frontend-to-backend API prefix for Docker build | no |
| `SEED_DEMO_USER` | create demo user on startup | no |
| `DEMO_USER_EMAIL` | demo user email | no |
| `DEMO_USER_PASSWORD` | demo user password | no |
| `DEMO_USER_FULL_NAME` | demo user display name | no |
| `DEMO_USER_TIMEZONE` | demo user timezone | no |
| `MISTRAL_API_KEY` | enables Mistral parsing | optional |
| `MISTRAL_MODEL` | Mistral model name | optional |
| `GOOGLE_CLIENT_ID` | OAuth client id | optional |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret | optional |
| `GOOGLE_REDIRECT_URI` | Google OAuth callback | optional |
| `GOOGLE_CALENDAR_SCOPES` | Google Calendar scopes | optional |

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```

Backend API docs:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend development URL:

```text
http://localhost:5173
```

Vite is configured to proxy `/api` requests to `http://localhost:8000`.

## Docker Startup

```bash
docker compose up --build
```

URLs:

- frontend: `http://localhost:8080`
- backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

Detached mode:

```bash
docker compose up -d --build
```

Stop:

```bash
docker compose down
```

## Migrations

Create database schema:

```bash
cd backend
alembic upgrade head
```

Create a new migration:

```bash
cd backend
alembic revision --autogenerate -m "describe_change"
```

## Mistral Integration Notes

- PlanSync uses Mistral only for structured extraction
- the app is not a chatbot
- raw LLM output is normalized and validated on the backend
- parsed data is stored as a draft first
- the frontend always shows confirmation before saving
- if Mistral is not configured or fails, heuristic fallback keeps the planner usable

Typical AI flow:

1. user enters free text
2. backend calls Mistral
3. backend extracts JSON and normalizes fields
4. draft is returned to frontend
5. user edits fields in confirmation form
6. only confirmed data becomes a planner item

## Google Calendar Integration Notes

- integration is optional
- the planner remains fully usable without Google Calendar
- current sync scope is practical MVP export/sync behavior for planner events
- items can still be created and edited manually without any Google account

To enable Google sync:

1. create Google OAuth credentials
2. add client id, secret, and redirect URI to `.env`
3. open the integrations page in the app
4. connect Google Calendar

## VM Deployment Notes

This project is suitable for a student VM deployment:

- all major services are defined in `docker-compose.yml`
- configuration is driven through `.env`
- frontend is served by Nginx
- backend runs migrations at container start
- PostgreSQL persists data via Docker volume

Recommended production hardening:

- use a strong `SECRET_KEY`
- set `COOKIE_SECURE=true`
- move real secrets out of committed/local shared files
- put the app behind HTTPS reverse proxy
- use a managed PostgreSQL backup strategy

## Version 1 Scope

Version 1 is the core planner product:

- auth
- manual tasks and events
- reminders
- recurrence
- weekly planner view
- multi-user isolation

## Version 2 Scope

Version 2 extends Version 1 with:

- Mistral AI parsing
- free-text reminder extraction
- confirmation flow before save
- optional Google Calendar sync
- UX polish around planner and integrations

## Final Delivered Scope

The delivered project includes:

- complete backend on FastAPI + SQLAlchemy + Alembic
- complete frontend on React + TypeScript + Vite
- PostgreSQL-ready data model
- secure auth flow
- planner CRUD
- reminders and recurrence
- weekly planner UI
- Mistral draft parsing with strict confirmation before persistence
- optional Google Calendar sync
- Docker Compose deployment
- backend tests for auth, planner creation, recurrence, reminder-related flows, Google sync behavior, AI parsing, and draft confirmation save flow

## Testing

### Automated backend tests

Run:

```bash
cd backend
.venv\Scripts\python -m pytest
```

Included coverage areas:

- authentication basics
- planner item creation and update
- recurring weekly items in planner view
- reminder extraction/handling in planner payloads
- AI parse draft creation
- AI parse schema normalization
- confirmation save flow
- Google sync behavior

### Frontend verification

Automated frontend tests are light in this version, so use the following manual flows:

1. Register a new user and verify redirect to planner.
2. Log out and log back in.
3. Create a manual task with at least two reminders.
4. Create a recurring event and verify it appears in the weekly planner.
5. Parse free text through AI panel and confirm that no item appears before explicit confirmation.
6. Edit the AI draft and confirm it creates the corrected item.
7. Open integrations page and verify Google status with and without credentials.

## Final Verification Notes

Verified locally:

- backend tests passed
- frontend production build passed
- backend `ruff` lint passed
- Docker images for backend and frontend built successfully
- `docker compose up -d` started the full stack
- backend health endpoint responded with `{"status":"ok"}`
- frontend responded on port `8080`

## Future Improvements

- drag-and-drop rescheduling in weekly planner
- richer recurrence exceptions and skip-one-occurrence UX
- email or push reminder channels
- background worker for more robust reminder delivery
- Google two-way sync with conflict handling
- stronger audit logging for AI draft lifecycle
- frontend component tests and e2e flows
- per-user locale/i18n support
