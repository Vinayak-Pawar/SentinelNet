# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

SentinelNet is an AI-powered multi-cloud resilience platform (Python 3.9+). It has three runnable services — all are Python processes with no external database or container dependencies:

| Service | Command | Port | Notes |
|---------|---------|------|-------|
| FastAPI API | `sentinelnet api` | 8000 | Main backend; AlertManager webhooks, REST API |
| Streamlit Dashboard | `sentinelnet dashboard` | 8501 | Interactive web UI |
| Prometheus Metrics | `sentinelnet monitor` | 8001 | Exposes `/metrics` endpoint |

SQLite (embedded, file at `data/sentinelnet.db`) is the only datastore — no external DB server needed.

### Known gotchas

- **`.env` must only contain top-level `Settings` fields.** Pydantic-settings v2 rejects extra keys. The `.env` file should contain only `ENVIRONMENT` and `DEBUG` (and optionally `AI_OPENAI_API_KEY` etc. using the sub-config prefixed names). Do NOT put bare `OPENAI_API_KEY`, `GOOGLE_CLOUD_PROJECT`, or `LOG_LEVEL` in `.env` — they conflict with the strict `Settings` model.
- **API lifespan blocks on orchestration loop.** The `lifespan` in `sentinelnet/api/main.py` awaits `start_orchestration_loop()` which never returns, preventing the server from accepting requests. To run the API, bypass the lifespan at runtime:
  ```python
  python3 -c "
  from sentinelnet.api.main import app
  from contextlib import asynccontextmanager
  @asynccontextmanager
  async def noop_lifespan(a):
      yield
  app.router.lifespan_context = noop_lifespan
  import uvicorn
  uvicorn.run(app, host='0.0.0.0', port=8000)
  "
  ```
- **`~/.local/bin` must be on PATH** for the `sentinelnet` CLI and other pip-installed scripts. Run `export PATH="$HOME/.local/bin:$PATH"` or ensure it's in `~/.bashrc`.
- **`pytest-cov` is required** but not listed in `pyproject.toml` dependencies. Install it separately (`pip install pytest-cov`) before running `pytest`.
- The app runs in **demo/development mode** without AI API keys — all cloud integrations fall back to mock data.

### Standard commands

See `README.md` for the full command reference. Key development commands:

- **Install:** `pip install -e ".[dev]"` then `pip install pytest-cov`
- **Lint:** `black --check sentinelnet/`, `isort --check-only sentinelnet/`, `flake8 sentinelnet/ --max-line-length=100`
- **Test:** `python3 -m pytest tests/ -v`
- **Run API:** see lifespan workaround above
