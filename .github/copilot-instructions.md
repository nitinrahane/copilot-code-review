# Project Guidelines

## Architecture
- Backend API entrypoint: `src/app.py`.
- API routes live in `src/backend/routers/`.
- Data access and seed data live in `src/backend/database.py`.
- Frontend assets live in `src/static/` and are served by FastAPI under `/static`.
- Keep route handlers focused on request/response orchestration. Move reusable logic into shared helper functions/modules when duplication appears.

## Build And Test
- Install dependencies: `pip install -r requirements.txt`.
- In this dev container, MongoDB is started by scripts in `.devcontainer/`.
- Run the app from repo root: `uvicorn src.app:app --reload`.
- Use API docs for manual verification: `http://localhost:8000/docs`.
- There is no established automated test command yet. If adding tests, keep them fast and deterministic.

## Security Requirements
- Treat all request input as untrusted. Validate and sanitize path, query, and body values before database reads/writes.
- Do not send credentials or sensitive values in query parameters. Use request bodies for login and auth headers/cookies for session credentials.
- Do not authorize write operations by username alone. Require verifiable authentication/authorization checks.
- Minimize user data exposure in API responses (for example, avoid returning full participant email lists unless required).
- Prefer loading configurable content from the database. If that is not feasible, use environment variables or a non-committed config file.
- Avoid hardcoded credentials, secrets, or production-like account data in source files.
- Prefer explicit error handling and clear failure paths over silent fallbacks.

## Code Quality
- Use consistent naming conventions (`snake_case` in Python, consistent naming style in frontend code).
- Prioritize readability and maintainability over premature optimization.
- Reduce duplication by extracting shared validation, auth checks, and update logic into helpers.
- For methods used frequently, optimize only after confirming they are hot paths.
- Keep error messages explicit and actionable while avoiding leakage of sensitive internals.

## Conventions And References
- API behavior and endpoint expectations: `src/README.md`.
- Exercise and repository context: `README.md`.
- Frontend-specific standards are defined in `.github/instructions/frontend.instructions.md`.
- Link to existing docs instead of duplicating long guidance in instruction files.