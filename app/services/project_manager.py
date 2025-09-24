# project_manager.py

from pathlib import Path
import json
from datetime import datetime
import logging
from app.config.constants import PROJECTS_FILE

logger = logging.getLogger(__name__)

class ProjectManager:
    def __init__(self):
        self.projects_file = Path(PROJECTS_FILE).resolve()
        self.projects = {
            'current_project': None,
            'recent_projects': [],
            'last_scanned': {}
        }
        self.ensure_config_dir()
        self.load_projects()

    def ensure_config_dir(self):
        config_dir = self.projects_file.parent
        config_dir.mkdir(parents=True, exist_ok=True)

    def load_projects(self):
        if self.projects_file.exists():
            try:
                with self.projects_file.open('r') as f:
                    self.projects = json.load(f)
                    if self.projects.get('current_project'):
                        self.projects['current_project'] = str(Path(self.projects['current_project']).resolve())
                    self.projects['recent_projects'] = [
                        str(Path(p).resolve()) for p in self.projects.get('recent_projects', [])
                    ][:3]  # Limit to 3 recent projects
                    loaded_scanned = self.projects.get('last_scanned', {})
                    self.projects['last_scanned'] = {
                        str(Path(p).resolve()): ts for p, ts in loaded_scanned.items()
                    }
            except Exception as e:
                logger.warning("Failed to load projects.json: %s", e)
        logger.info("Loaded current project: %s", self.projects.get('current_project'))

    def save_projects(self):
        try:
            with self.projects_file.open('w') as f:
                json.dump(self.projects, f, indent=2)
            logger.info("Saved current project: %s", self.projects.get('current_project'))
        except Exception as e:
            logger.warning("Failed to save projects.json: %s", e)

    def get_project_info_file_path(self, project_path):
        """Return the path to the project info file."""
        # Convert to Path object if it's a string
        project_path = Path(project_path)
        return project_path / 'project_info.json'

    def create_project_info(self, project_path, project_name):
        """Create project info file with default information."""
        # Convert to Path object if it's a string
        project_path = Path(project_path)
        project_info_path = self.get_project_info_file_path(project_path)
        
        # Create default project information
        project_info = {
            'title': project_name,
            'description': '',
            'tags': [],
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        # Save the project info file
        with open(project_info_path, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, indent=2, ensure_ascii=False)
        
        return project_info

    def load_project_info(self, project_path):
        """Load project information from file."""
        # Convert to Path object if it's a string
        project_path = Path(project_path)
        project_info_path = self.get_project_info_file_path(project_path)
        
        if project_info_path.exists():
            try:
                with open(project_info_path, 'r', encoding='utf-8') as f:
                    project_info = json.load(f)
                    # Ensure all fields are present
                    defaults = {
                        'title': project_path.name,
                        'description': '',
                        'tags': [],
                        'created': datetime.now().isoformat(),
                        'updated': datetime.now().isoformat(),
                        'version': '1.0.0'
                    }
                    for key, value in defaults.items():
                        if key not in project_info:
                            project_info[key] = value
                    return project_info
            except Exception as e:
                logger.error("Failed to load project info: %s", e)
                # Return default project info if loading fails
                return {
                    'title': project_path.name,
                    'description': '',
                    'tags': [],
                    'created': datetime.now().isoformat(),
                    'updated': datetime.now().isoformat(),
                    'version': '1.0.0'
                }
        else:
            # Create a default project info file if it doesn't exist yet
            return self.create_project_info(project_path, project_path.name)

    def save_project_info(self, project_path, info_data):
        """Save project information to file."""
        # Convert to Path object if it's a string
        project_path = Path(project_path)
        project_info_path = self.get_project_info_file_path(project_path)

        # Add/update the 'updated' timestamp
        info_data['updated'] = datetime.now().isoformat()

        # Ensure all required fields are present
        defaults = {
            'title': project_path.name,
            'description': '',
            'tags': [],
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        for key, value in defaults.items():
            if key not in info_data:
                info_data[key] = value

        # Write to file
        with open(project_info_path, 'w', encoding='utf-8') as f:
            json.dump(info_data, f, indent=2, ensure_ascii=False)

        return info_data

    def update_project_timestamp(self, project_path):
        """Update only the 'updated' timestamp for a project. Best-effort operation."""
        try:
            # Convert to Path object if it's a string
            project_path = Path(project_path)
            project_info_path = self.get_project_info_file_path(project_path)

            # Load existing project info or create defaults
            if project_info_path.exists():
                try:
                    with open(project_info_path, 'r', encoding='utf-8') as f:
                        project_info = json.load(f)
                except Exception as e:
                    logger.warning("Failed to load existing project info for timestamp update: %s", e)
                    # Create default structure
                    project_info = {
                        'title': project_path.name,
                        'description': '',
                        'tags': [],
                        'created': datetime.now().isoformat(),
                        'updated': datetime.now().isoformat(),
                        'version': '1.0.0'
                    }
            else:
                # Create default structure
                project_info = {
                    'title': project_path.name,
                    'description': '',
                    'tags': [],
                    'created': datetime.now().isoformat(),
                    'updated': datetime.now().isoformat(),
                    'version': '1.0.0'
                }

            # Update only the timestamp
            project_info['updated'] = datetime.now().isoformat()

            # Write back to file
            with open(project_info_path, 'w', encoding='utf-8') as f:
                json.dump(project_info, f, indent=2, ensure_ascii=False)

            logger.debug("Updated project timestamp for: %s", project_path)
        except Exception as e:
            logger.warning("Failed to update project timestamp for %s: %s", project_path, e)
            # Don't raise - timestamp updates are best-effort

    def create_project(self, project_path, project_name):
        from app.utils import sanitize_path
        project_dir = sanitize_path(project_path).resolve() / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        shots_dir = project_dir / 'shots'
        shots_dir.mkdir(exist_ok=True)
        (shots_dir / 'wip').mkdir(parents=True, exist_ok=True)
        (shots_dir / 'latest_images').mkdir(exist_ok=True)
        (shots_dir / 'latest_videos').mkdir(exist_ok=True)
        (project_dir / '_legacy').mkdir(exist_ok=True)

        resolved_dir = project_dir.resolve()
        project_info = {
            'name': project_name,
            'path': str(resolved_dir),
            'created': datetime.now().isoformat(),
            'shots': []
        }

        # Create project information file
        self.create_project_info(resolved_dir, project_name)

        self.set_current_project(project_dir)
        return project_info

    def set_current_project(self, path: Path):
        from app.utils import sanitize_path
        path = sanitize_path(path).resolve()
        path_str = str(path)
        self.projects['current_project'] = path_str

        # Always move the project to the front of recent projects
        if path_str in self.projects['recent_projects']:
            self.projects['recent_projects'].remove(path_str)
        self.projects['recent_projects'].insert(0, path_str)
        self.projects['recent_projects'] = self.projects['recent_projects'][:3]

        # Update the last_scanned timestamp
        self.projects['last_scanned'][path_str] = datetime.now().isoformat()

        self.save_projects()

    def get_current_project(self):
        project_path = self.projects.get('current_project')
        if not project_path:
            logger.warning("No current project path set.")
            return None
        from app.utils import sanitize_path
        project_path = sanitize_path(project_path).resolve()
        shots_dir = project_path / 'shots'

        if shots_dir.exists():
            created = datetime.fromtimestamp(project_path.stat().st_ctime).isoformat()
            # Load project information
            project_info = self.load_project_info(project_path)
            return {
                'name': project_path.name,
                'path': str(project_path),
                'created': created,
                'info': project_info,
                'shots': []
            }

        for recent in self.projects.get('recent_projects', []):
            recent_path = sanitize_path(recent).resolve()
            if (recent_path / 'shots').exists():
                logger.info("Falling back to recent project: %s", recent_path)
                self.set_current_project(recent_path)
                created = datetime.fromtimestamp(recent_path.stat().st_ctime).isoformat()
                # Load project information
                project_info = self.load_project_info(recent_path)
                return {
                    'name': recent_path.name,
                    'path': str(recent_path),
                    'created': created,
                    'info': project_info,
                    'shots': []
                }

        logger.error("No valid project found.")
        return None
