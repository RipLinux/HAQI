# Local setup

Install Python 3.11+, uv, Node 20+, npm, Docker Desktop, and Git. Copy
`.env.example` to `.env`. For the local stack, run `docker compose up --build`
from the repository root. The API health endpoint is
`http://localhost:8000/api/v1/health`, the frontend is
`http://localhost:5173`, and MLflow is `http://localhost:5000`.

## Run the RAG-backed API locally

From the repository root:

```bash
cd backend
uv sync --extra dev
uv run uvicorn main:app --reload --port 8000
```

This starts `backend/main.py`, which serves the active `/api/v1/chat` RAG flow.
The separate `app.main:app` entry point is the modular foundation API; its
chat route remains a `501 Not Implemented` scaffold.

LLM generation is disabled by default. To enable OpenAI for a local backend
process, set `HAQI_LLM_PROVIDER=openai` and provide `OPENAI_API_KEY` through
the process environment. `HAQI_LLM_MODEL` is optional and defaults to
`gpt-4o-mini`. Provider or validation failures preserve the deterministic
legacy answer. The current Docker Compose backend does not pass the LLM
environment variables to its container.

For frontend-only work, run `cd frontend`, `npm install`, and `npm run dev`.
If containers fail, inspect `docker compose logs <service>` and verify ports
5432, 5000, 5173, and 8000 are available.
