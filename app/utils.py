from pathlib import Path
import tomllib


def sanitize_path(path_str: str) -> Path:
    """Return a Path object from a potentially quoted string."""
    if path_str is None:
        return None
    cleaned = str(path_str).strip()
    if (
        (cleaned.startswith("'") and cleaned.endswith("'"))
        or (cleaned.startswith('"') and cleaned.endswith('"'))
    ):
        cleaned = cleaned[1:-1]
    return Path(cleaned).expanduser()


def get_app_version():
    """Get the application version from pyproject.toml"""
    try:
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"
        
        if pyproject_path.exists():
            with open(pyproject_path, 'rb') as f:
                data = tomllib.load(f)
                return data.get('project', {}).get('version', 'Unknown')
        return 'Unknown'
    except Exception:
        return 'Unknown'
