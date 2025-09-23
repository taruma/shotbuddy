from flask import Blueprint, request, jsonify, render_template, current_app
from pathlib import Path
from datetime import datetime
import logging
import sys

logger = logging.getLogger(__name__)

from app.services.shot_manager import get_shot_manager, clear_shot_manager_cache

project_bp = Blueprint('project', __name__)

@project_bp.route("/")
def index():
    return render_template("index.html")

@project_bp.route("/api/project/current")
def get_current_project():
    try:
        project_manager = current_app.config['PROJECT_MANAGER']
        project = project_manager.get_current_project()
        if project:
            project_path = Path(project["path"])
            path_str = str(project_path)
            last_scanned = project_manager.projects.get("last_scanned", {}).get(path_str)
            folder_mtime = project_path.stat().st_mtime

            if (not last_scanned or
                    folder_mtime > datetime.fromisoformat(last_scanned).timestamp()):
                clear_shot_manager_cache()
                get_shot_manager(path_str).get_shots()
                project_manager.projects.setdefault("last_scanned", {})[path_str] = (
                    datetime.fromtimestamp(folder_mtime).isoformat()
                )
                project_manager.save_projects()
            return jsonify({"success": True, "data": project})
        return jsonify({"success": False, "error": "No current project"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@project_bp.route("/api/project/recent")
def get_recent_projects():
    try:
        project_manager = current_app.config['PROJECT_MANAGER']
        recent_projects = []
        for project_path in project_manager.projects.get('recent_projects', []):
            p = Path(project_path)
            shots_dir = p / 'shots'
            if shots_dir.exists():
                created = datetime.fromtimestamp(p.stat().st_ctime).isoformat()
                recent_projects.append({
                    "name": p.name,
                    "path": str(p.resolve()),
                    "created": created,
                    "shots": []
                })
        return jsonify({"success": True, "data": recent_projects})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@project_bp.route("/api/project/open", methods=["POST"])
def open_project():
    try:
        project_manager = current_app.config['PROJECT_MANAGER']
        data = request.get_json()
        project_path = data.get("path")
        if not project_path:
            return jsonify({"success": False, "error": "Project path required"}), 400
        from app.utils import sanitize_path
        project_path = sanitize_path(project_path).resolve()
        path_str = str(project_path)
        shots_dir = project_path / "shots"

        logger.debug("Received raw path from frontend: %s", request.get_json())
        logger.debug("Looking at path: %s", project_path)
        logger.debug("shots/ folder exists? %s", shots_dir.exists())

        if not shots_dir.exists():
            return jsonify({"success": False, "error": "No recognizable project structure"}), 400

        project_info = {
            "name": project_path.name,
            "path": path_str,
            "created": datetime.fromtimestamp(project_path.stat().st_ctime).isoformat(),
            "shots": []
        }

        # Ensure new folder layout exists
        (shots_dir / "wip").mkdir(parents=True, exist_ok=True)
        (shots_dir / "latest_images").mkdir(exist_ok=True)
        (shots_dir / "latest_videos").mkdir(exist_ok=True)

        # Update project manager state
        path_str = str(project_path)
        project_manager.projects['current_project'] = path_str
        if path_str not in project_manager.projects['recent_projects']:
            project_manager.projects['recent_projects'].insert(0, path_str)
            project_manager.projects['recent_projects'] = project_manager.projects['recent_projects'][:5]

        last_scanned = project_manager.projects.get('last_scanned', {}).get(path_str)
        folder_mtime = project_path.stat().st_mtime
        if (not last_scanned or
                folder_mtime > datetime.fromisoformat(last_scanned).timestamp()):
            clear_shot_manager_cache()
            shot_manager = get_shot_manager(path_str)
            shot_manager.get_shots()
            project_manager.projects.setdefault('last_scanned', {})[path_str] = (
                datetime.fromtimestamp(folder_mtime).isoformat()
            )
        project_manager.save_projects()

        return jsonify({"success": True, "data": project_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@project_bp.route("/api/project/create", methods=["POST"])
def create_project():
    try:
        project_manager = current_app.config['PROJECT_MANAGER']
        data = request.get_json()
        project_name = data.get("name", "Untitled Project")
        selected_folder = data.get("path", ".")
        from app.utils import sanitize_path
        folder_path = sanitize_path(selected_folder).resolve()

        project_dir = folder_path / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        shots_dir = project_dir / "shots"
        shots_dir.mkdir(exist_ok=True)
        (shots_dir / "wip").mkdir(parents=True, exist_ok=True)
        (shots_dir / "latest_images").mkdir(exist_ok=True)
        (shots_dir / "latest_videos").mkdir(exist_ok=True)
        (project_dir / "_legacy").mkdir(exist_ok=True)

        resolved_dir = project_dir.resolve()
        project_info = {
            "name": project_name,
            "path": str(resolved_dir),
            "created": datetime.now().isoformat(),
            "shots": []
        }

        # Defensive state update
        path_str = str(resolved_dir)
        project_manager.projects['current_project'] = path_str
        project_manager.projects['recent_projects'] = [path_str]
        project_manager.save_projects()

        # Optional: sanity check (useful in dev)
        assert project_manager.get_current_project() is not None

        return jsonify({"success": True, "data": project_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@project_bp.route("/api/system/browse-folder")
def browse_folder():
    """Open a native folder picker dialog and return the selected path"""
    try:
        # Try to use tkinter for native folder dialog first
        try:
            from tkinter import Tk
            from tkinter import filedialog
            
            # Create and hide the root window
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)  # Bring dialog to front
            
            # Open folder dialog
            folder_path = filedialog.askdirectory(title="Select Project Folder")
            root.destroy()
            
            if not folder_path:
                return jsonify({"success": False, "error": "No folder selected"}), 400
                
            return jsonify({"success": True, "data": {"path": folder_path}})
            
        except ImportError:
            logger.info("Tkinter not available, trying alternative methods")
        except Exception as e:
            logger.warning("Tkinter failed: %s", e)
        
        # Fallback: Return the user's home directory as a starting point
        # This allows the UI to show a sensible default and let the user manually edit the path
        import os
        home_dir = os.path.expanduser("~")
        return jsonify({
            "success": True, 
            "data": {"path": home_dir},
            "warning": "Native folder dialog not available. Please manually edit the path or use the manual input fallback."
        })
        
    except Exception as e:
        logger.error("Error in browse_folder: %s", e)
        return jsonify({"success": False, "error": f"Failed to open folder dialog: {str(e)}"}), 500
