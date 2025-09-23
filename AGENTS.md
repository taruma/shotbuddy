# Shotbuddy – Contributor Guide (Agents & Humans)

This repository contains a Flask application for managing AI filmmaking shot assets (images/videos), with automatic versioning and “latest” asset management. Use this document to understand the layout, how to run the app, and contribution conventions.

## Directory overview

- app/ – Main application package
  - routes/ – Flask route blueprints
  - services/ – File, project, and shot management logic
  - config/ – App-level constants and configuration helpers
  - templates/ – HTML templates
  - static/ – Static files and generated thumbnails
    - css/, js/, icons/, thumbnails/
  - utils.py – Small helper utilities
- run.py – Entry point to launch the Flask server (auto-opens browser when ready)
- shotbuddy.cfg – Optional server configuration (INI)
- README.md – User-facing documentation and features
- pyproject.toml – Project metadata (Python ≥ 3.9), uv config
- requirements.txt / requirements.in – Pinned and source dependency specs
- LICENSE.txt, THIRD_PARTY_LICENSES.md – Licensing information
- AGENTS.md – This guide

Note: A tests/ directory is not present at the moment.

## Getting started

Preferred (uv):
1) Install uv (see https://docs.astral.sh/uv/)
2) Create environment and install dependencies:
   uv sync
3) Run the development server:
   uv run run.py
4) Open your browser:
   The app will auto-open; default URL is http://127.0.0.1:5001/ unless configured.

Alternative (pip/venv):
1) Create and activate a virtual environment
   - Windows (PowerShell):
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
   - macOS/Linux:
     python3 -m venv .venv
     source .venv/bin/activate
2) Install dependencies:
   pip install -r requirements.txt
3) Run:
   python run.py

## Configuration

Server settings can be specified in shotbuddy.cfg (INI) and/or environment variables. Environment variables override the file.

shotbuddy.cfg:
[server]
host = 0.0.0.0
port = 5001

Environment variables:
- SHOTBUDDY_UPLOAD_FOLDER – temporary uploads directory (default: uploads)
- SHOTBUDDY_HOST – server bind address (default: 127.0.0.1)
- SHOTBUDDY_PORT – port (default: 5001)
- SHOTBUDDY_DEBUG – 1/true/yes to enable Flask debug

## Project media layout (runtime)

Each project maintains a shots/ directory:
shots/
  wip/
    SH###/
      images/   # versioned stills
      videos/   # versioned videos
      lipsync/  # placeholder for future lipsync clips
  latest_images/  # auto-maintained current image per shot
  latest_videos/  # auto-maintained current video per shot

See README.md for screenshots and workflow details.

## Coding guidelines

- Follow PEP 8 for Python. Keep route logic in app/routes/ and business logic in app/services/.
- Use helpers in app.utils for path handling to avoid traversal and to keep paths consistent.
- Store new static assets and templates under app/static/ and app/templates/, respectively.
- Keep configuration separate from code. Prefer shotbuddy.cfg and env vars; do not hardcode ports/paths.
- Update README.md and this AGENTS.md if you change setup, configuration, or top-level structure.

## Testing

There are currently no automated tests. Running:
pytest -q
should complete successfully (0 tests) and verifies the environment is set up. If/when tests are added, place them under tests/ and ensure they are runnable with pytest.

## AI assistance and tooling
Parts of the codebase were produced with AI assistance:
- Cline (Plan/Act workflow)
- Model mix: GPT‑5 and Qwen3 Coder

All AI-assisted changes are reviewed and tested before merging.

This AGENTS.md applies to the entire repository.
