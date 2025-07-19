from pathlib import Path


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
