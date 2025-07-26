# FastAPI Template

## Quickstart

1. Install dependencies:
   ```bash
   pip install -r base_requirements.txt
   ```
2. Run the app:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

- `app/main.py` - FastAPI entry point
- `app/api/` - API routers
- `app/core/` - Core settings/config
- `app/models/` - Pydantic models
- `app/schemas/` - Request/response schemas
- `app/dependencies/` - Dependency injection
