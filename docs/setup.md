# Local setup

Install Python 3.11+, uv, Node 20+, npm, Docker Desktop, and Git. Copy `.env.example` to `.env`. For the complete local stack run `docker compose up --build`; API health is `http://localhost:8000/api/v1/health`, frontend is `http://localhost:5173`, MLflow is `http://localhost:5000`.

For backend-only work, run `cd backend`, `uv sync --extra dev`, then `uv run uvicorn app.main:app --reload`. For frontend-only work, run `cd frontend`, `npm install`, and `npm run dev`. If containers fail, inspect `docker compose logs <service>` and verify ports 5432, 5000, 5173, and 8000 are available.
