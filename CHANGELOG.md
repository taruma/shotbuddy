# Changelog

## v2.1.0 (September 23, 2025) - by Taruma Sakti

This minor release introduces enhanced backend performance and new reordering capabilities for improved project management workflows. All changes maintain backward compatibility while providing better user experience for shot organization.

### Added
- **Enhanced Shot Reordering**: New modal interface with filtering and drag support for improved project organization workflow
- **Progressive Web App Support**: Added favicon and manifest files for better web app experience

### Changed
- **Backend Architecture**: Refactored thumbnail cache to per-project directories for improved performance and organization
- **Thumbnail Rendering**: Improved aspect ratio handling to preserve original image proportions
- **UI Polish**: Updated grid layout and header styles for better visual consistency

### Technical Updates
- **Performance**: Optimized file handling and caching mechanisms
- **Code Quality**: Enhanced service layer architecture and route handling

### AI Development Attribution
This release was developed with AI assistance using Cline's Plan/Act workflow, powered by a mix of GPT-5 and Qwen3 Coder models. All generated changes were manually reviewed, tested, and refined by the maintainer, Taruma Sakti, to ensure quality and alignment with project goals.

This version focuses on backend improvements and enhanced user experience for shot management workflows.

## v2.0.0 (September 23, 2025) - by Taruma Sakti

This major release extends the original Shotbuddy v1.0.0 by Albert Bozesan with new features focused on enhanced navigation, asset management, and usability for AI filmmaking workflows. All changes are backward-compatible, preserving legacy single-image support while adding project-scoped metadata and modern UI elements.

### Added
- **Table of Shots (TOC) Panel**: Responsive side panel for project overviews in docked or drawer modes. Supports shot filtering, quick navigation, active/archived separation, and highlighting. Integrates with reordering and themes.

- **Drag-and-Drop Shot Reordering**: Reorder shots in the grid with persistent per-project saving. Inline insertion points with "New Shot +" buttons.

- **Shot Archiving**: Toggle shots to hide inactive ones from the main grid while retaining assets. Dedicated archived section with one-click restore.

- **Human-Readable Display Names**: Custom titles for shots (e.g., "Opening Scene" for SH010), editable in grid/TOC. Stored in project-scoped `meta.json` for multi-project support.

- **Action Column with Icon Buttons**: Leftmost grid column for quick actions like archive/unarchive, using accessible SVG icons and tooltips.

- **First/Last Image Variants**: Separate slots for opening/closing frames per shot. Independent versioning, prompts, thumbnails, and promotion; legacy images map to first variant.

- **Asset Version Promotion and Cycling**: Click version badges to cycle/promote finals. Supports images/videos; auto-updates thumbnails and markers for up to 999 versions.

- **Asset Captions**: Editable text under media previews (first/last images, videos). Auto-saves to per-shot `captions.json` for notes or feedback.

- **Auto-Resizing Notes**: Dynamic textarea expansion for shot notes, removing scrollbars for better editing.

- **Light/Dark Theme Toggle**: Header button to switch themes, persisted in localStorage. Full UI overrides for contrast and readability.

- **Refined Header and Menu Layout**: Container-based structure with improved spacing, shadows, and borders.

- **uv Dependency Management**: Support for uv and pyproject.toml for reproducible environments, replacing manual venv/pip setup.

- **Expanded Documentation**: Detailed README with feature guides and GIF demos (reordering, archiving, TOC, display names, versions, variants, captions, notes, themes). Comprehensive AGENTS.md contributor guide (setup, config, layout, PEP8, testing).

### Changed
- **Project-Scoped Metadata**: Shot meta (display names, captions) now stored per-project for robust multi-project handling. Removed legacy app-level files.

- **Footer and Attribution**: Updated index.html footer with maintainer credit, GitHub link, and Cline attribution. Dual copyright in LICENSE.txt (Taruma Sakti / Albert Bozesan).

- **README Structure**: New "New Features in This Fork" section with summarized enhancements and visuals. Updated pyproject.toml authors/URLs.

- **Cursor Styles and Interactions**: Default cursors for non-clickable thumbnails; removed unintended handlers. Pointer cursors for interactive elements.

### Technical Updates
- **API Endpoints**: Added `/reorder`, `/archive`, `/display-name`, `/caption`, `/promote` for new features.
- **File Structure**: New `.shot_order.json` and `.archived_shots.json` per project; image variants use `_first`/`_last` prefixes.
- **Dependencies**: Flask, Flask-CORS, Pillow via pyproject.toml/requirements.txt.
- **No Breaking Changes**: Legacy workflows intact.

### AI Development Attribution
This release was developed with AI assistance using Cline's Plan/Act workflow, powered by a mix of GPT-5 and Qwen3 Coder models. All generated changes were manually reviewed, tested, and refined by the maintainer, Taruma Sakti, to ensure quality and alignment with project goals.

This version streamlines storyboard management for larger projects. For full details and demos, see README.md.
