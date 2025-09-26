import json
import logging
import re
from pathlib import Path

from PIL import Image

from app.config.constants import (
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    THUMBNAIL_SIZE,
    get_project_thumbnail_cache_dir,
)
from app.services.project_manager import ProjectManager

logger = logging.getLogger(__name__)

# Shot names may optionally contain a single underscore followed by another
# three-digit number (e.g. ``SH001_050``).  Deeper nesting with multiple
# underscores is not allowed.
SHOT_NAME_RE = re.compile(r"^SH\d{3}(?:_\d{3})?$")


def validate_shot_name(name):
    if not SHOT_NAME_RE.match(name):
        raise ValueError(f"Invalid shot name: {name}")
    if name == "SH000":
        raise ValueError("Invalid shot name: SH000")


def _parse_shot_parts(name):
    """Return the numeric segments for a shot name."""
    return [int(p) for p in name[2:].split("_")]


def _format_shot_parts(parts):
    """Format numeric segments back into a shot name."""
    base = f"SH{parts[0]:03d}"
    for p in parts[1:]:
        base += f"_{p:03d}"
    return base


def _meta_file(shot_name):
    """Return path to the meta JSON for a shot."""
    return Path("shots") / "wip" / shot_name / "meta.json"


def _project_meta_file(project_path, shot_name):
    """Return path to the project-scoped meta JSON for a shot."""
    return Path(project_path) / "shots" / "wip" / shot_name / "meta.json"


def load_meta(shot_name):
    """Load meta dict for a shot."""
    validate_shot_name(shot_name)
    path = _meta_file(shot_name)
    try:
        if path.exists():
            with path.open('r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except Exception:
        logger.exception("Error loading shot meta")
    return {}


def save_display_name(shot_name, display_name):
    """Persist display name for a shot."""
    validate_shot_name(shot_name)
    path = _meta_file(shot_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('w', encoding='utf-8') as f:
            json.dump({"display_name": display_name}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise ValueError(f"Failed to save display name: {str(e)}")


class ShotManager:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.shots_dir = self.project_path / 'shots'
        self.wip_dir = self.shots_dir / 'wip'
        self.latest_images_dir = self.shots_dir / 'latest_images'
        self.latest_videos_dir = self.shots_dir / 'latest_videos'
        self.legacy_dir = self.project_path / '_legacy'
        self.order_file = self.shots_dir / '.shot_order.json'
        self.archive_file = self.shots_dir / '.archived_shots.json'

        self.wip_dir.mkdir(parents=True, exist_ok=True)
        self.latest_images_dir.mkdir(parents=True, exist_ok=True)
        self.latest_videos_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnail_cache_dir = get_project_thumbnail_cache_dir(self.project_path)

    def _load_archived(self):
        """Load archived shot names from JSON file."""
        import json
        try:
            if self.archive_file.exists():
                with self.archive_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return set(data)
        except Exception:
            logger.exception("Error loading archived shots")
        return set()

    def _save_archived(self, names: set):
        """Persist archived shot names to JSON file."""
        import json
        try:
            self.shots_dir.mkdir(parents=True, exist_ok=True)
            with self.archive_file.open('w', encoding='utf-8') as f:
                json.dump(sorted(list(names)), f)
        except Exception:
            logger.warning("Failed to save archived shots file")

    def archive_shot(self, shot_name, archived: bool):
        """Toggle archived state for a shot and return updated shot info."""
        validate_shot_name(shot_name)
        shot_dir = self.wip_dir / shot_name
        if not shot_dir.exists():
            raise ValueError(f"Shot {shot_name} does not exist")

        names = self._load_archived()
        if archived:
            names.add(shot_name)
        else:
            names.discard(shot_name)
        self._save_archived(names)
        return self.get_shot_info(shot_name)

    @staticmethod
    def _normalize_path(path):
        """Return a POSIX-style absolute path string or ``None``."""
        if not path:
            return None
        return str(Path(path).resolve()).replace("\\", "/")

    def rename_shot(self, old_name, new_name):
        """Rename a shot and all associated files."""
        validate_shot_name(old_name)
        validate_shot_name(new_name)
        old_dir = self.wip_dir / old_name
        new_dir = self.wip_dir / new_name

        if not old_dir.exists():
            raise ValueError(f"Shot {old_name} does not exist")
        if new_dir.exists():
            raise ValueError(f"Shot {new_name} already exists")

        old_dir.rename(new_dir)

        for sub in ["images", "videos"]:
            d = new_dir / sub
            if d.exists():
                # Legacy pattern (e.g., SH001_v001.png) and new image patterns (e.g., SH001_first_v001.png)
                for f in d.glob(f"{old_name}_v*.*"):
                    f.rename(d / f.name.replace(old_name, new_name, 1))
                for f in d.glob(f"{old_name}_*_v*.*"):
                    f.rename(d / f.name.replace(old_name, new_name, 1))

        lipsync_dir = new_dir / "lipsync"
        if lipsync_dir.exists():
            for part in ["driver", "target", "result"]:
                for ext in ALLOWED_VIDEO_EXTENSIONS:
                    src = lipsync_dir / f"{old_name}_{part}{ext}"
                    if src.exists():
                        src.rename(lipsync_dir / f"{new_name}_{part}{ext}")
                for f in lipsync_dir.glob(f"{old_name}_{part}_v*.*"):
                    f.rename(lipsync_dir / f.name.replace(old_name, new_name, 1))

        for ext in ALLOWED_IMAGE_EXTENSIONS:
            # Legacy single-image final
            src = self.latest_images_dir / f"{old_name}{ext}"
            if src.exists():
                src.rename(self.latest_images_dir / f"{new_name}{ext}")
            # New first/last finals
            src_first = self.latest_images_dir / f"{old_name}_first{ext}"
            if src_first.exists():
                src_first.rename(self.latest_images_dir / f"{new_name}_first{ext}")
            src_last = self.latest_images_dir / f"{old_name}_last{ext}"
            if src_last.exists():
                src_last.rename(self.latest_images_dir / f"{new_name}_last{ext}")
        # Rename image version markers if present
        img_marker = self.latest_images_dir / f"{old_name}.version"
        if img_marker.exists():
            img_marker.rename(self.latest_images_dir / f"{new_name}.version")
        img_marker_first = self.latest_images_dir / f"{old_name}_first.version"
        if img_marker_first.exists():
            img_marker_first.rename(self.latest_images_dir / f"{new_name}_first.version")
        img_marker_last = self.latest_images_dir / f"{old_name}_last.version"
        if img_marker_last.exists():
            img_marker_last.rename(self.latest_images_dir / f"{new_name}_last.version")

        for ext in ALLOWED_VIDEO_EXTENSIONS:
            src = self.latest_videos_dir / f"{old_name}{ext}"
            if src.exists():
                src.rename(self.latest_videos_dir / f"{new_name}{ext}")
        # Rename video version marker if present
        vid_marker = self.latest_videos_dir / f"{old_name}.version"
        if vid_marker.exists():
            vid_marker.rename(self.latest_videos_dir / f"{new_name}.version")

        if self.thumbnail_cache_dir.exists():
            for thumb in self.thumbnail_cache_dir.glob(f"{old_name}_*_thumb.jpg"):
                thumb.rename(self.thumbnail_cache_dir / thumb.name.replace(old_name, new_name, 1))
            for vthumb in self.thumbnail_cache_dir.glob(f"{old_name}_*_vthumb.jpg"):
                vthumb.rename(self.thumbnail_cache_dir / vthumb.name.replace(old_name, new_name, 1))

        # Preserve archived state across rename
        try:
            names = self._load_archived()
            if old_name in names:
                names.discard(old_name)
                names.add(new_name)
                self._save_archived(names)
        except Exception:
            logger.exception("Error updating archived state during rename")

        return self.get_shot_info(new_name)

    def create_shot_structure(self, shot_name):
        """Create folder structure for a shot."""
        validate_shot_name(shot_name)
        shot_dir = self.wip_dir / shot_name
        shot_dir.mkdir(parents=True, exist_ok=True)

        # Create subfolders
        (shot_dir / 'images').mkdir(exist_ok=True)
        (shot_dir / 'videos').mkdir(exist_ok=True)
        (shot_dir / 'lipsync').mkdir(exist_ok=True)

        self.latest_images_dir.mkdir(parents=True, exist_ok=True)
        self.latest_videos_dir.mkdir(parents=True, exist_ok=True)

        return shot_dir

    def get_next_shot_number(self):
        """Get next available shot number."""
        existing_shots = []
        if self.wip_dir.exists():
            for shot_dir in self.wip_dir.iterdir():
                if shot_dir.is_dir() and shot_dir.name.startswith('SH'):
                    try:
                        existing_shots.append(int(shot_dir.name[2:]))
                    except ValueError:
                        continue

        return (max(existing_shots) + 10) if existing_shots else 10

    def get_shots(self):
        """Get all shots in the project."""
        if not self.wip_dir.exists():
            return []

        shot_dirs = [d for d in self.wip_dir.iterdir() if d.is_dir() and d.name.startswith('SH')]
        
        if self.order_file.exists():
            import json
            with self.order_file.open('r') as f:
                ordered_names = json.load(f)
            
            # Create a map of name to directory for quick lookup
            dir_map = {d.name: d for d in shot_dirs}
            
            # Reorder shot_dirs based on the loaded order
            ordered_dirs = [dir_map[name] for name in ordered_names if name in dir_map]
            
            # Add any new shots that are not in the order file yet
            existing_ordered_names = set(ordered_names)
            new_dirs = [d for d in shot_dirs if d.name not in existing_ordered_names]
            
            shot_dirs = ordered_dirs + sorted(new_dirs) # Sort new dirs by name
        else:
            shot_dirs = sorted(shot_dirs)

        shots = [self.get_shot_info(shot_dir.name) for shot_dir in shot_dirs]
        return shots

    def save_shot_order(self, shot_order):
        """Save the order of shots."""
        import json
        with self.order_file.open('w') as f:
            json.dump(shot_order, f)

    def create_shot_between(self, after_shot=None):
        """Create a new shot between existing shots.

        Parameters
        ----------
        after_shot : str or None
            Name of the shot after which the new shot should be inserted. If
            ``None`` the new shot is inserted before the first existing one.

        Returns
        -------
        dict
            Shot information for the newly created shot.
        """

        if after_shot:
            validate_shot_name(after_shot)

        existing = [s["name"] for s in self.get_shots()]

        if not after_shot:
            # Insert before the first shot using the original numeric scheme
            if not existing:
                new_number = 10
            else:
                first_number = min(int(s[2:]) for s in existing)
                candidate = max(first_number // 2, 1)
                existing_numbers = {int(s[2:]) for s in existing}
                while candidate in existing_numbers and candidate > 1:
                    candidate -= 1
                if candidate in existing_numbers:
                    raise ValueError("No available shot numbers before first shot")
                new_number = candidate
            shot_name = f"SH{new_number:03d}"
        else:
            base_shot = after_shot.split('_')[0]

            if '_' in after_shot:
                # After a sub-shot: simply append a new sub-shot for the same base
                shot_name = self._create_subshot_name(base_shot, existing)
            else:
                after_num = int(base_shot[2:])
                next_numbers = sorted(
                    n for n in (int(s[2:5]) for s in existing if '_' not in s) if n > after_num
                )

                if next_numbers:
                    next_num = next_numbers[0]
                    if next_num - after_num > 1:
                        new_number = after_num + ((next_num - after_num) // 2)
                        shot_name = f"SH{new_number:03d}"
                    else:
                        shot_name = self._create_subshot_name(base_shot, existing)
                else:
                    new_number = after_num + 10
                    shot_name = f"SH{new_number:03d}"

        validate_shot_name(shot_name)
        if shot_name in existing:
            raise ValueError(f"Shot {shot_name} already exists")

        self.create_shot_structure(shot_name)
        return self.get_shot_info(shot_name)

    def _create_subshot_name(self, base_shot, existing):
        """Return a new sub-shot name under ``base_shot``.

        ``base_shot`` should be a top-level shot name (no underscore).  The new
        name will use a three-digit sub-shot number starting at ``050`` and
        increasing in steps of 10.  Only a single underscore level is allowed.
        """

        if '_' in base_shot:
            raise ValueError('Nested sub-shots are not supported')

        prefix = base_shot + '_'
        sub_numbers = []
        for name in existing:
            if name.startswith(prefix) and '_' not in name[len(prefix):]:
                try:
                    sub_numbers.append(int(name.split('_')[1]))
                except ValueError:
                    continue

        next_num = (max(sub_numbers) + 10) if sub_numbers else 50
        if next_num > 999:
            raise ValueError('No available sub-shot numbers')

        return f"{base_shot}_{next_num:03d}"

    def load_meta(self, shot_name):
        """Load meta dict for a shot from project path, with fallback to app-level."""
        validate_shot_name(shot_name)
        project_path = getattr(self, 'project_path', None)
        if project_path:
            path = _project_meta_file(project_path, shot_name)
            try:
                if path.exists():
                    with path.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            return data
            except Exception:
                logger.exception("Error loading project meta")
        # Fallback to app-level meta (for legacy data)
        return load_meta(shot_name)

    def save_display_name(self, shot_name, display_name):
        """Persist display name for a shot in project path."""
        validate_shot_name(shot_name)
        project_path = getattr(self, 'project_path', None)
        if not project_path:
            raise ValueError("Project path not set")
        path = _project_meta_file(project_path, shot_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open('w', encoding='utf-8') as f:
                json.dump({"display_name": display_name}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save display name: {str(e)}")

    def get_shot_info(self, shot_name):
        """Get information about a specific shot."""
        validate_shot_name(shot_name)
        shot_dir = self.wip_dir / shot_name

        # Load notes
        notes = ''
        notes_file = shot_dir / 'notes.txt'
        if notes_file.exists():
            try:
                with open(notes_file, encoding='utf-8') as f:
                    notes = f.read().strip()
            except Exception:
                logger.exception("Error loading shot notes")


        # First/Last images
        # New naming for first frame
        first_image_path, first_max_version = self._get_latest_asset(
            self.latest_images_dir, shot_dir / 'images',
            f'{shot_name}_first', ALLOWED_IMAGE_EXTENSIONS
        )
        # Backward compatibility for first frame (legacy single image)
        legacy_image_path, legacy_max_version = self._get_latest_asset(
            self.latest_images_dir, shot_dir / 'images',
            shot_name, ALLOWED_IMAGE_EXTENSIONS
        )
        use_legacy_for_first = (not first_image_path and first_max_version == 0 and (legacy_image_path or legacy_max_version > 0))
        if use_legacy_for_first:
            first_image_path = legacy_image_path
            first_max_version = legacy_max_version

        # New naming for last frame
        last_image_path, last_max_version = self._get_latest_asset(
            self.latest_images_dir, shot_dir / 'images',
            f'{shot_name}_last', ALLOWED_IMAGE_EXTENSIONS
        )

        first_image_path = self._normalize_path(first_image_path)
        last_image_path = self._normalize_path(last_image_path)

        current_first_version = self.get_current_version(shot_name, 'first_image', first_max_version)
        first_prompt = self.load_prompt(shot_name, 'first_image', current_first_version) if current_first_version > 0 else ''

        current_last_version = self.get_current_version(shot_name, 'last_image', last_max_version)
        last_prompt = self.load_prompt(shot_name, 'last_image', current_last_version) if current_last_version > 0 else ''

        # Latest video
        latest_video, max_video_version = self._get_latest_asset(
            self.latest_videos_dir, shot_dir / 'videos',
            shot_name, ALLOWED_VIDEO_EXTENSIONS
        )
        latest_video = self._normalize_path(latest_video)
        current_video_version = self.get_current_version(shot_name, 'video', max_video_version)
        video_prompt = ''
        if current_video_version > 0:
            video_prompt = self.load_prompt(shot_name, 'video', current_video_version)

        # Lipsync videos
        lipsync_dir = shot_dir / 'lipsync'
        lipsync = {}
        for part in ['driver', 'target', 'result']:
            file_path, ver = self._get_latest_asset(
                lipsync_dir, lipsync_dir,
                f'{shot_name}_{part}', ALLOWED_VIDEO_EXTENSIONS
            )
            file_path = self._normalize_path(file_path)
            prompt_text = ''
            if ver > 0:
                prompt_text = self.load_prompt(shot_name, part, ver)
            lipsync[part] = {
                'file': file_path,
                'version': ver,
                'thumbnail': None,  # will be replaced with video thumb below
                'prompt': prompt_text,
            }

        # Thumbnails
        first_thumb = self.get_thumbnail_path(Path(first_image_path), shot_name) if first_image_path else None
        last_thumb = self.get_thumbnail_path(Path(last_image_path), shot_name) if last_image_path else None
        video_thumb = self.get_video_thumbnail_path(Path(latest_video), shot_name) if latest_video else None

        for part_name, info in lipsync.items():
            info['thumbnail'] = self.get_video_thumbnail_path(Path(info['file']), f"{shot_name}_{part_name}") if info['file'] else None

        logger.debug("%s -> First image thumbnail: %s", shot_name, first_thumb)
        logger.debug("%s -> Last image thumbnail: %s", shot_name, last_thumb)
        logger.debug("%s -> Video thumbnail: %s", shot_name, video_thumb)

        captions = self.load_captions(shot_name)

        # Compose response with backward-compatible 'image' alias pointing to first_image
        first_image_dict = {
            'file': first_image_path,
            'current_version': current_first_version,
            'max_version': first_max_version,
            'thumbnail': first_thumb,
            'prompt': first_prompt,
            'caption': captions.get('first_image', ''),
        }
        last_image_dict = {
            'file': last_image_path,
            'current_version': current_last_version,
            'max_version': last_max_version,
            'thumbnail': last_thumb,
            'prompt': last_prompt,
            'caption': captions.get('last_image', ''),
        }

        meta = self.load_meta(shot_name)
        return {
            'name': shot_name,
            'display_name': meta.get('display_name', ''),
            'notes': notes,
            'first_image': first_image_dict,
            'last_image': last_image_dict,
            'image': first_image_dict,  # backward compatibility
            'video': {
                'file': latest_video,
                'current_version': current_video_version,
                'max_version': max_video_version,
                'thumbnail': video_thumb,
                'prompt': video_prompt,
                'caption': captions.get('video', ''),
            },
            'lipsync': lipsync,
            'archived': (shot_name in self._load_archived())
        }


    def _get_latest_asset(self, final_dir, wip_dir, shot_name, extensions):
        """Helper for finding the latest final or highest versioned WIP asset."""
        latest_final = None
        if final_dir.exists():
            for ext in extensions:
                candidate = final_dir / f'{shot_name}{ext}'
                if candidate.exists():
                    latest_final = str(candidate)
                    break

        version = 0
        if wip_dir.exists():
            wip_files = []
            for ext in extensions:
                wip_files.extend(wip_dir.glob(f'{shot_name}_v*{ext}'))

            versions = []
            for f in wip_files:
                try:
                    version_str = f.stem.split('_v')[1]
                    versions.append(int(version_str))
                except (IndexError, ValueError):
                    continue

            if versions:
                version = max(versions)

        return latest_final, version

    def _version_marker_path(self, asset_type, shot_name):
        if asset_type == 'image':
            # Legacy single-image marker (pre-split)
            return self.latest_images_dir / f"{shot_name}.version"
        elif asset_type == 'first_image':
            return self.latest_images_dir / f"{shot_name}_first.version"
        elif asset_type == 'last_image':
            return self.latest_images_dir / f"{shot_name}_last.version"
        elif asset_type == 'video':
            return self.latest_videos_dir / f"{shot_name}.version"
        elif asset_type in {'driver', 'target', 'result'}:
            return (self.wip_dir / shot_name / 'lipsync') / f"{shot_name}_{asset_type}.version"
        else:
            raise ValueError('Invalid asset type')

    def get_current_version(self, shot_name, asset_type, max_version):
        """Read the currently promoted version from a marker file. Fallback to max_version."""
        def _read_marker(p):
            try:
                if p.exists():
                    v = int(p.read_text(encoding='utf-8').strip())
                    if max_version == 0:
                        return v
                    if 1 <= v <= max_version:
                        return v
            except Exception:
                logger.exception("Error reading version marker")
            return None

        marker = self._version_marker_path(asset_type, shot_name)
        v = _read_marker(marker)
        if v is not None:
            return v

        # Backward-compatibility: first_image falls back to legacy 'image' marker
        if asset_type == 'first_image':
            legacy_marker = self._version_marker_path('image', shot_name)
            v = _read_marker(legacy_marker)
            if v is not None:
                return v

        return max_version

    def set_current_version(self, shot_name, asset_type, version):
        """Persist the currently promoted version to a marker file."""
        marker = self._version_marker_path(asset_type, shot_name)
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(str(int(version)), encoding='utf-8')

    def promote_asset(self, shot_name, asset_type, version):
        """Promote a specific WIP version to be the current final for image variants/video."""
        validate_shot_name(shot_name)
        if asset_type not in {'image', 'first_image', 'last_image', 'video'}:
            raise ValueError('Invalid asset type')

        shot_dir = self.wip_dir / shot_name

        import shutil as _shutil

        if asset_type in {'image', 'first_image', 'last_image'}:
            slot = 'first' if asset_type in {'image', 'first_image'} else 'last'
            wip_dir = shot_dir / 'images'
            if not wip_dir.exists():
                raise ValueError(f"No image WIP directory for shot {shot_name}")

            # Find source: prefer new naming, then legacy (for first slot)
            src = None
            for ext in ALLOWED_IMAGE_EXTENSIONS:
                candidate = wip_dir / f'{shot_name}_{slot}_v{int(version):03d}{ext}'
                if candidate.exists():
                    src = candidate
                    break
            if src is None and slot == 'first':
                for ext in ALLOWED_IMAGE_EXTENSIONS:
                    legacy = wip_dir / f'{shot_name}_v{int(version):03d}{ext}'
                    if legacy.exists():
                        src = legacy
                        break
            if src is None:
                raise ValueError(f"Version v{int(version):03d} not found for {shot_name} {asset_type}")

            final_dir = self.latest_images_dir
            final_dir.mkdir(parents=True, exist_ok=True)

            # Remove existing finals for this slot
            for existing in final_dir.glob(f"{shot_name}_{slot}.*"):
                try:
                    existing.unlink()
                except Exception:
                    logger.exception("Error unlinking existing final image")

            final_path = final_dir / f"{shot_name}_{slot}{src.suffix}"
            _shutil.copy2(str(src), str(final_path))

            # Update marker and regenerate thumbnail
            self.set_current_version(shot_name, 'first_image' if slot == 'first' else 'last_image', int(version))
            try:
                final_stem = Path(final_path).stem
                thumb_filename = f"{shot_name}_{final_stem}_thumb.jpg"
                old_thumb = self.thumbnail_cache_dir / thumb_filename
                if old_thumb.exists():
                    old_thumb.unlink()
            except Exception:
                logger.exception("Error unlinking old image thumbnail")

            _ = self.get_thumbnail_path(final_path, shot_name)
            return self._normalize_path(final_path)

        # Video
        wip_dir = shot_dir / 'videos'
        if not wip_dir.exists():
            raise ValueError(f"No video WIP directory for shot {shot_name}")

        src = None
        for ext in ALLOWED_VIDEO_EXTENSIONS:
            candidate = wip_dir / f'{shot_name}_v{int(version):03d}{ext}'
            if candidate.exists():
                src = candidate
                break
        if not src:
            raise ValueError(f"Version v{int(version):03d} not found for {shot_name} video")

        final_dir = self.latest_videos_dir
        final_dir.mkdir(parents=True, exist_ok=True)

        for existing in final_dir.glob(f"{shot_name}.*"):
            try:
                existing.unlink()
            except Exception:
                logger.exception("Error unlinking existing final video")

        final_path = final_dir / f"{shot_name}{src.suffix}"
        _shutil.copy2(str(src), str(final_path))

        self.set_current_version(shot_name, 'video', int(version))
        try:
            final_stem = Path(final_path).stem
            thumb_filename = f"{shot_name}_{final_stem}_vthumb.jpg"
            old_thumb = self.thumbnail_cache_dir / thumb_filename
            if old_thumb.exists():
                old_thumb.unlink()
        except Exception:
            logger.exception("Error unlinking old video thumbnail")

        _ = self.get_video_thumbnail_path(final_path, shot_name)
        return self._normalize_path(final_path)

    def save_shot_notes(self, shot_name, notes):
        """Save notes for a shot."""
        validate_shot_name(shot_name)
        shot_dir = self.wip_dir / shot_name
        if not shot_dir.exists():
            raise ValueError(f"Shot {shot_name} does not exist")

        notes_file = shot_dir / 'notes.txt'
        try:
            with open(notes_file, 'w', encoding='utf-8') as f:
                f.write(notes)
        except Exception as e:
            raise ValueError(f"Failed to save notes: {str(e)}")

    def _captions_file(self, shot_name):
        """Return path to the captions JSON for a shot."""
        return (self.wip_dir / shot_name) / 'captions.json'

    def load_captions(self, shot_name):
        """Load captions dict for a shot."""
        validate_shot_name(shot_name)
        path = self._captions_file(shot_name)
        try:
            import json
            if path.exists():
                with path.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception:
            logger.exception("Error loading shot captions")
        return {}

    def save_caption(self, shot_name, asset_type, caption):
        """Persist caption text for given asset type for a shot."""
        validate_shot_name(shot_name)
        if asset_type not in {'first_image', 'last_image', 'video'}:
            raise ValueError('Invalid asset type')
        shot_dir = self.wip_dir / shot_name
        if not shot_dir.exists():
            raise ValueError(f"Shot {shot_name} does not exist")
        captions = self.load_captions(shot_name)
        captions[asset_type] = caption or ''
        try:
            import json
            with self._captions_file(shot_name).open('w', encoding='utf-8') as f:
                json.dump(captions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save caption: {str(e)}")

    def _prompt_file_path(self, shot_name, asset_type, version):
        """Return the path to the prompt file for a specific asset version."""
        shot_dir = self.wip_dir / shot_name
        if asset_type in {'image', 'first_image'}:
            base_dir = shot_dir / 'images'
            if asset_type == 'image':
                filename = f'{shot_name}_v{version:03d}_image_prompt.txt'
            else:
                filename = f'{shot_name}_first_v{version:03d}_image_prompt.txt'
        elif asset_type == 'last_image':
            base_dir = shot_dir / 'images'
            filename = f'{shot_name}_last_v{version:03d}_image_prompt.txt'
        elif asset_type == 'video':
            base_dir = shot_dir / 'videos'
            filename = f'{shot_name}_v{version:03d}_video_prompt.txt'
        elif asset_type in {'driver', 'target', 'result'}:
            base_dir = shot_dir / 'lipsync'
            filename = f'{shot_name}_{asset_type}_v{version:03d}_prompt.txt'
        else:
            raise ValueError('Invalid asset type')
        return base_dir / filename

    def load_prompt(self, shot_name, asset_type, version):
        path = self._prompt_file_path(shot_name, asset_type, version)
        if path.exists():
            try:
                with open(path, encoding='utf-8') as f:
                    return f.read().strip()
            except Exception:
                return ''
        # Backward-compatibility: if first_image not found, try legacy 'image'
        if asset_type == 'first_image':
            legacy_path = self._prompt_file_path(shot_name, 'image', version)
            if legacy_path.exists():
                try:
                    with open(legacy_path, encoding='utf-8') as f:
                        return f.read().strip()
                except Exception:
                    return ''
        return ''

    def save_prompt(self, shot_name, asset_type, version, prompt):
        """Save prompt for a specific asset version."""
        validate_shot_name(shot_name)
        path = self._prompt_file_path(shot_name, asset_type, version)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(prompt)
        except Exception as e:
            raise ValueError(f"Failed to save prompt: {str(e)}")

    def get_prompt_versions(self, shot_name, asset_type):
        """Return a sorted list of prompt versions for the given asset."""
        shot_dir = self.wip_dir / shot_name

        patterns = []
        base_dir = None
        if asset_type in {'image', 'first_image'}:
            base_dir = shot_dir / 'images'
            patterns = [
                f'{shot_name}_v*_image_prompt.txt',          # legacy
                f'{shot_name}_first_v*_image_prompt.txt'     # new first
            ]
        elif asset_type == 'last_image':
            base_dir = shot_dir / 'images'
            patterns = [f'{shot_name}_last_v*_image_prompt.txt']
        elif asset_type == 'video':
            base_dir = shot_dir / 'videos'
            patterns = [f'{shot_name}_v*_video_prompt.txt']
        elif asset_type in {'driver', 'target', 'result'}:
            base_dir = shot_dir / 'lipsync'
            patterns = [f'{shot_name}_{asset_type}_v*_prompt.txt']
        else:
            raise ValueError('Invalid asset type')

        versions = set()
        if base_dir and base_dir.exists():
            for pattern in patterns:
                for f in base_dir.glob(pattern):
                    stem = f.stem
                    if '_v' not in stem:
                        continue
                    try:
                        part = stem.split('_v')[1]
                        ver_str = part.split('_')[0]
                        versions.add(int(ver_str))
                    except (IndexError, ValueError):
                        continue
        return sorted(versions)

    def get_thumbnail_path(self, image_path, shot_name):
        """Return (and create if necessary) the thumbnail for an image."""
        if not image_path:
            return None

        image_path = Path(image_path)
        thumb_filename = f"{shot_name}_{image_path.stem}_thumb.jpg"
        thumb_path = self.thumbnail_cache_dir / thumb_filename

        try:
            if thumb_path.exists() and thumb_path.stat().st_mtime >= image_path.stat().st_mtime:
                return f"/api/shots/thumbnail/{thumb_filename}"
        except Exception:
            logger.exception("Error checking thumbnail timestamp")
        try:
            self.thumbnail_cache_dir.mkdir(parents=True, exist_ok=True)
            with Image.open(image_path) as img:
                img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (64, 64, 64))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                    img = background
                img.save(str(thumb_path), "JPEG", quality=85)
        except Exception as e:
            logger.warning("Error creating thumbnail: %s", e)
            return None

        return f"/api/shots/thumbnail/{thumb_filename}"

    def get_video_thumbnail_path(self, video_path, shot_name):
        """Return (and create if necessary) the thumbnail for a video."""
        if not video_path:
            return None

        import shutil as _shutil
        import subprocess

        video_path = Path(video_path)
        if not video_path.exists():
            logger.warning("Video file does not exist: %s", video_path)
            return None
        thumb_filename = f"{shot_name}_{video_path.stem}_vthumb.jpg"
        thumb_path = self.thumbnail_cache_dir / thumb_filename

        if thumb_path.exists() and thumb_path.stat().st_mtime >= video_path.stat().st_mtime:
            return f"/api/shots/thumbnail/{thumb_filename}"
        if not thumb_path.exists():
            ffmpeg = _shutil.which("ffmpeg")
            if not ffmpeg:
                logger.warning("ffmpeg not found; skipping video thumbnail for %s", video_path)
                return None
            try:
                self.thumbnail_cache_dir.mkdir(parents=True, exist_ok=True)
                tmp_path = thumb_path.with_suffix(".tmp.jpg")
                cmd = [ffmpeg, "-y", "-i", str(video_path), "-frames:v", "1", str(tmp_path)]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)  # noqa: S603
                with Image.open(tmp_path) as img:
                    img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                    if img.mode in ("RGBA", "LA", "P"):
                        background = Image.new("RGB", img.size, (64, 64, 64))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        background.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                        img = background
                    img.save(str(thumb_path), "JPEG", quality=85)
                tmp_path.unlink(missing_ok=True)
            except Exception as e:
                logger.warning("Error creating video thumbnail: %s", e)
                return None

        return f"/api/shots/thumbnail/{thumb_filename}"

    def export_latest_assets(self, export_name=None, export_type='all', include_display_in_filename=True, include_metadata=True):
        """Export latest assets for non-archived shots in custom order."""
        import re
        import shutil
        from datetime import datetime

        # Get non-archived shots in order
        non_archived_shots = [s for s in self.get_shots() if not s['archived']]
        if not non_archived_shots:
            raise ValueError("No non-archived shots found")

        # Load project information
        project_manager = ProjectManager()
        project_info = project_manager.load_project_info(self.project_path)

        # Create export directory
        exports_root = self.project_path / 'exports'
        exports_root.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_dir_name = export_name or f'export_{timestamp}'
        export_dir = exports_root / export_dir_name
        export_dir.mkdir(exist_ok=True)

        # Sanitize filename helper
        def sanitize_filename(name):
            return re.sub(r'[<>:\"/\\|?*]', '_', str(name))[:50] or ''

        # Process each shot in order
        for order, shot in enumerate(non_archived_shots, start=1):
            shot_name = shot['name']
            display_name = shot['display_name'] or ''
            display_suffix = f"_{sanitize_filename(display_name)}" if include_display_in_filename and display_name else ''

            # Get shot info
            info = self.get_shot_info(shot_name)

            # Images
            if 'images' in export_type or export_type == 'all':
                images_dir = export_dir / 'images'
                images_dir.mkdir(exist_ok=True)

                # First image
                if info['first_image']['file']:
                    src = Path(info['first_image']['file'])
                    if src.exists():
                        ext = src.suffix
                        dst = images_dir / f"{order:03d}_{shot_name}{display_suffix}_first{ext}"
                        shutil.copy2(src, dst)

                # Last image
                if info['last_image']['file']:
                    src = Path(info['last_image']['file'])
                    if src.exists():
                        ext = src.suffix
                        dst = images_dir / f"{order:03d}_{shot_name}{display_suffix}_last{ext}"
                        shutil.copy2(src, dst)

            # Videos
            if 'videos' in export_type or export_type == 'all':
                videos_dir = export_dir / 'videos'
                videos_dir.mkdir(exist_ok=True)

                if info['video']['file']:
                    src = Path(info['video']['file'])
                    if src.exists():
                        ext = src.suffix
                        dst = videos_dir / f"{order:03d}_{shot_name}{display_suffix}{ext}"
                        shutil.copy2(src, dst)

        # Generate metadata if requested
        if include_metadata:
            # Collect data for tables and notes
            first_data = []
            last_data = []
            video_data = []
            notes_list = []

            for order, shot in enumerate(non_archived_shots, start=1):
                shot_name = shot['name']
                info = self.get_shot_info(shot_name)

                # First Frame
                if ('images' in export_type or export_type == 'all') and (info['first_image']['caption'] or info['first_image']['prompt']):
                    first_data.append((order, shot_name, info['first_image']['caption'], info['first_image']['prompt']))

                # Last Frame
                if ('images' in export_type or export_type == 'all') and (info['last_image']['caption'] or info['last_image']['prompt']):
                    last_data.append((order, shot_name, info['last_image']['caption'], info['last_image']['prompt']))

                # Video
                if ('videos' in export_type or export_type == 'all') and (info['video']['caption'] or info['video']['prompt']):
                    video_data.append((order, shot_name, info['video']['caption'], info['video']['prompt']))

                # Notes
                if info['notes'].strip():
                    notes_list.append((order, shot_name, info['notes']))

            # Build MD content
            md_lines = [
                f"# {project_info.get('title', self.project_path.name)}",
                "",
                "## Project Information",
            ]

            # Add bullet points for non-empty project fields
            if project_info.get('short_description'):
                md_lines.append(f"- **Short Description:** {project_info.get('short_description')}")

            if project_info.get('notes'):
                md_lines.append(f"- **Project Notes:** {project_info.get('notes')}")

            if project_info.get('tags'):
                md_lines.append(f"- **Tags:** {', '.join(project_info.get('tags'))}")

            md_lines.extend([
                "",
                f"**Export Date:** {timestamp}",
                f"**Export Type:** {export_type}",
                ""
            ])

            # First Frame table
            if first_data:
                md_lines.extend([
                    "## First Frame",
                    "| Order | Shot Name | Captions | Prompts |",
                    "|-------|-----------|----------|---------|"
                ])
                for order, name, caption, prompt in first_data:
                    md_lines.append(f"| {order:03d} | {name} | {caption.replace('|', '\\|').replace('\n', '<br>')} | {prompt.replace('|', '\\|').replace('\n', '<br>')} |")
                md_lines.append("")

            # Last Frame table
            if last_data:
                md_lines.extend([
                    "## Last Frame",
                    "| Order | Shot Name | Captions | Prompts |",
                    "|-------|-----------|----------|---------|"
                ])
                for order, name, caption, prompt in last_data:
                    md_lines.append(f"| {order:03d} | {name} | {caption.replace('|', '\\|').replace('\n', '<br>')} | {prompt.replace('|', '\\|').replace('\n', '<br>')} |")
                md_lines.append("")

            # Video table
            if video_data:
                md_lines.extend([
                    "## Video",
                    "| Order | Shot Name | Captions | Prompts |",
                    "|-------|-----------|----------|---------|"
                ])
                for order, name, caption, prompt in video_data:
                    md_lines.append(f"| {order:03d} | {name} | {caption.replace('|', '\\|').replace('\n', '<br>')} | {prompt.replace('|', '\\|').replace('\n', '<br>')} |")
                md_lines.append("")

            # Notes table
            if notes_list:
                md_lines.extend([
                    "## Notes",
                    "| Order | Shot Name | Notes |",
                    "|-------|-----------|-------|"
                ])
                for order, name, notes in notes_list:
                    md_lines.append(f"| {order:03d} | {name} | {notes.replace('|', '\\|').replace('\n', '<br>')} |")
                md_lines.append("")

            # Write MD file
            md_path = export_dir / "export_summary.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_lines))

        return str(export_dir)

def get_shot_manager(project_path, cache=None):
    """Retrieve a cached ``ShotManager`` for the given path."""
    from flask import current_app

    if cache is None:
        cache = current_app.config.setdefault('SHOT_MANAGER_CACHE', {})

    path_key = str(Path(project_path).resolve())
    if path_key not in cache:
        cache[path_key] = ShotManager(path_key)
    return cache[path_key]


def clear_shot_manager_cache(cache=None):
    """Clear cached ``ShotManager`` instances."""
    from flask import current_app

    if cache is None:
        cache = current_app.config.get('SHOT_MANAGER_CACHE')

    if cache is not None:
        cache.clear()
