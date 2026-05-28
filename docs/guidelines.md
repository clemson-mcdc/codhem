# Project Structure for CODHEM

## Summary

The application uses Streamlit's multipage model. The repository root contains `main.py` as the Streamlit entrypoint, a `pages/` directory for the major user-facing screens, and a top-level `codhem/` package for core application code.

The structure favors readability and maintainability for future non-CS maintainers. Database access and ML model execution remain outside page files, but page files may contain light data shaping, plotting preparation, and simple workflow glue. This keeps the backend boundary clear without making the project overly abstract.

## Implementation Structure

Root:

- `main.py`
- `pages/`
- `codhem/`
- `docs/guidelines.md`
- `.streamlit/`
- `pyproject.toml`

Application package:

- `codhem/config/` for settings and constants
- `codhem/services/` for data retrieval workflows, model execution workflows, and shared session-state helpers
- `codhem/models/` for domain types, filter objects, and model input/output schemas
- `codhem/components/` for reusable Streamlit UI building blocks
- `codhem/db/` for database client setup, repositories, and query definitions
- `codhem/utils/` for small shared helpers

Pages:

- `pages/` contains one file per screen, beginning with data filtering, plotting, and ML models, using normal snake_case module names.
- Sidebar order and labels are controlled explicitly from `main.py` using Streamlit navigation, rather than filename prefixes.
- Pages may perform light reshaping of already-fetched data for display and plotting.
- Pages must not own direct database access or direct model execution logic.
- The repository keeps the importable application package at the repo root so Streamlit entrypoints can import it directly without extra path setup.

## Interface and Naming Conventions

- Use `main.py` rather than `app.py`.
- Use `components` rather than `views` or `ui` for reusable Streamlit building blocks.
- Keep Streamlit code thin enough to read easily, but do not force all display-oriented shaping into service modules.
- Treat plots as page behavior, not as a separate subsystem.
- Keep imports at the top level of the module rather than inside functions or conditional blocks, unless there is a specific technical need.
- Infer return types wherever practical instead of annotating every function explicitly.
- Do not add `-> None` when the return type is obvious and can be inferred by the linter.

## Testing

- No initial test structure is added in the first project-structure pass.
- Testing will be introduced later, after the core application flow and module boundaries are established.

## Assumptions and Defaults

- The Python package name remains `codhem`.
- The project uses Streamlit multipage navigation from the start.
- The initial planning document lives at `docs/guidelines.md`.
- Future maintainers may be scientific or domain-focused rather than software-focused, so clarity and low indirection take priority over stricter layering.
