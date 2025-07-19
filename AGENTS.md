# Guidelines for Codex Agents

This repository contains a Flask application for managing film shot assets. Use this document to quickly understand the project layout and common tasks.

## Directory overview

- `app/` – Main application package
  - `routes/` – Flask route blueprints
  - `services/` – Logic for file handling, project and shot management
  - `config/` – App-level constants
  - `utils.py` – Small helper utilities
  - `templates/` – HTML templates
  - `static/` – Static files and generated thumbnails
- `run.py` – Entry point to launch the Flask server
- `tests/` – Sample data and placeholder test directory (no active tests)

## Getting started

1. Install dependencies with `pip install -r requirements.txt`.
2. Start the development server using `python run.py`.

## Testing

Run `pytest -q` from the repository root. There are currently no automated tests, but this command should complete successfully and is used to verify the environment.

## Contributing

- Follow standard PEP 8 style when modifying Python code.
- Keep route logic in `app/routes/` and business logic in `app/services/`.
- When adding thumbnails or uploads, ensure paths are resolved using helpers in `app.utils` to avoid path traversal.
- Store new static or template assets within their respective directories.

This `AGENTS.md` applies to the entire repository.
