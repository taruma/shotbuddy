# Shotbuddy Project Context

## Project Overview
Shotbuddy is an application for managing AI-driven image-to-video filmmaking workflows. It supports structured organization, versioning, and annotation of generated stills and videos. The application provides a web interface for creating, managing, and organizing shots with drag-and-drop functionality.

Key features include:
- Shot management with versioned stills and videos
- Automatic organization of latest versions
- Prompt documentation and version history
- Shot reordering and archiving
- Display names for shots
- Asset promotion and captioning
- Thumbnail generation for images and videos

## Technology Stack
- **Backend**: Python 3.13.1+, Flask
- **Frontend**: HTML/CSS/JavaScript (served by Flask)
- **Dependencies**: flask, flask-cors, pillow, python-dotenv
- **Build Tool**: uv (package manager and virtual environment tool)

## Development Tooling
This project uses `uv` as the primary tool for all Python development tasks including dependency management, running scripts, and virtual environment handling. 

**Important**: Avoid using `pip install` directly. Instead, use `uv` commands for all dependency management:
- Use `uv add package_name` to add new dependencies
- Use `uv remove package_name` to remove dependencies
- Use `uv sync` to install all project dependencies
- Use `uv run script_name.py` to run Python scripts

## Project Structure
```
shotbuddy/
├── app/                    # Main application code
│   ├── __init__.py         # Flask app factory
│   ├── routes/            # API routes (project_routes.py, shot_routes.py)
│   ├── services/          # Business logic (shot_manager.py, file_handler.py)
│   ├── config/            # Configuration (constants.py)
│   └── static/            # Static assets (thumbnails, CSS, JS)
├── shots/                  # Project data directory (created per project)
│   ├── wip/               # Work-in-progress shot folders
│   ├── latest_images/     # Latest image versions
│   └── latest_videos/     # Latest video versions
├── run.py                 # Application entry point
├── shotbuddy.cfg          # Server configuration
├── pyproject.toml         # Project metadata and dependencies
├── requirements.txt       # Legacy dependencies list
└── uploads/               # Temporary upload directory
```

## Building and Running

### Prerequisites
- Python 3.13.1 or newer
- uv package manager

### Installation
1. Install uv: https://docs.astral.sh/uv/
2. Clone the repository
3. Create environment and install dependencies:
   ```bash
   uv sync
   ```
   
**Note**: This project uses `uv` for all dependency management. Do not use `pip install` directly as it may cause dependency conflicts or inconsistencies.

### Running the Application
1. Start the development server:
   ```bash
   uv run run.py
   ```
2. Open browser at http://127.0.0.1:5001/ (default)

### Configuration
Server settings can be configured in `shotbuddy.cfg`:
```ini
[server]
host = 0.0.0.0
port = 5001
```

Environment variables can override config file settings:
- `SHOTBUDDY_UPLOAD_FOLDER` - Upload directory (default: `uploads`)
- `SHOTBUDDY_HOST` - Server host (default: `127.0.0.1`)
- `SHOTBUDDY_PORT` - Server port (default: `5001`)
- `SHOTBUDDY_DEBUG` - Enable Flask debug mode (set to `1`)

## Development Conventions
- Uses Flask blueprints for route organization
- Project-scoped data management with ShotManager service
- JSON-based API responses with success/error structure
- Thumbnail caching in project-specific directories
- Version-controlled shot naming scheme (SH### or SH###_###)
- Asset versioning with _v### suffix
- All development tasks should use `uv` as the primary tool for dependency management and script execution

## Key Components
- **ShotManager**: Core service for shot operations, file management, and metadata handling
- **ProjectManager**: Handles project state, recent projects, and current project tracking
- **FileHandler**: Manages file uploads and asset processing
- **Routes**: REST API endpoints for project and shot operations