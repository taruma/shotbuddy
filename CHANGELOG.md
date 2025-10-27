# Changelog

## v3.4.0 (October 27, 2025) - by Taruma Sakti

This minor release introduces enhanced navigation capabilities, improved shot management workflows, and refined user experience for media browsing and project organization.

### Added
- **Gap-Filling Shot Numbering System**: Implemented intelligent shot numbering that fills gaps in sequences rather than using fixed increments, starting from 1 instead of 10 and supporting up to 999 shots for more efficient organization.
- **Enhanced Drag-and-Drop UI**: Added grippy handle to reorder items with improved visual feedback, animations, and better spacing for more intuitive shot organization.
- **Video Loop Playback**: Added loop attribute to video player for continuous automatic replay, improving user experience by providing uninterrupted playback.
- **Video Modal Navigation**: Added navigation arrows and keyboard support (arrow keys) for browsing between shots in video modal without closing the interface.
- **Image Modal Navigation**: Added keyboard navigation and arrow buttons for seamless browsing between images in the modal interface.
- **Version Detection Improvements**: Enhanced shot manager to detect existing versions for accurate version tracking, preventing conflicts when assets already exist and showing orange badges when multiple versions are available.

### AI Development Attribution
This release was developed with AI assistance using Cline's Plan/Act workflow, powered by the Deepseek v3.1 model. All generated changes were manually reviewed, tested, and refined by the maintainer, Taruma Sakti, to ensure quality and alignment with project goals.

This version enhances media browsing experience and shot organization efficiency while maintaining backward compatibility.

## v3.3.0 (October 6, 2025) - by Taruma Sakti

This minor release introduces enhanced media serving capabilities, improved UI responsiveness, and code quality refinements for better user experience and maintainability.

### Added
- **Image and Video Serving Endpoints**: Added new routes `/image/<shot_name>` and `/video/<shot_name>` to serve promoted media files from latest_images and latest_videos directories with proper validation and error handling.
- **Media Modal UI**: Enhanced modal interfaces for both images and videos with responsive design, light theme support, and improved user experience for viewing shot assets.
- **Cache-Busting Parameters**: Added timestamp query parameters to media URLs to prevent browser caching issues and ensure users always see the latest versions.
- **Shot Order Persistence Helpers**: Extracted shot order loading and saving into dedicated `_load_shot_order` and `_save_shot_order` methods with improved error handling and duplicate removal.

### Changed
- **CSS Restructuring**: Reorganized main stylesheet with improved organization and maintainability, including reordering and grouping related styles, removing duplicates, and consolidating similar rules.
- **Server Reload Integration**: Replaced local shot updates with server reloads after creating new shots to ensure UI displays fresh data including server-side additions.
- **TOC Auto-Refresh**: Enhanced Table of Contents to automatically update after saving shot order changes for better UI consistency.
- **Code Formatting**: Improved code readability by removing excessive leading whitespace and maintaining consistent formatting across the codebase.

### Fixed
- **Shot Order Integration**: Fixed shot order persistence when creating new shots between existing ones by integrating order management into `create_shot_between` method.

### AI Development Attribution
This release was developed with AI assistance using Cline's Plan/Act workflow, powered by the Grok-4-Fast, Deepseek v3.1, and GPT-5 model. All generated changes were manually reviewed, tested, and refined by the maintainer, Taruma Sakti, to ensure quality and alignment with project goals.

This version enhances media viewing capabilities and code maintainability while improving overall user experience.

## v3.2.0 (September 26, 2025) - by Taruma Sakti

This minor release focuses on code quality improvements, security enhancements, and UI/UX refinements for file uploads and exports.

### Added
- **Ruff Linting Configuration**: Added Ruff linting setup with custom rules (line-length=120, target-version=py313, select=E,F,I,UP,S; ignore=E501,S603) to enforce code style and security standards.

### Changed
- **Server Configuration**: Bound the Flask server to localhost (127.0.0.1) for local-only access, improving security in development environments.
- **Import Organization**: Reorganized imports across the codebase for better structure and maintainability.

### Fixed
- **Linting and Security Issues**: Resolved Ruff violations including formatting, empty try-except blocks, and subprocess security warnings (suppressed S603 for trusted calls). Auto-fixed imports where possible.
- **Upload UI Enhancements** (fix #5): Added loading states and immediate UI updates in `uploadFile` for shots, reducing perceived latency during asset uploads.
- **Export Summary Details** (fix #4): Enhanced export summaries in `shot_manager` to include project metadata (e.g., title, version) for better context in exported files.

### AI Development Attribution
This release was developed with AI assistance using Cline's Plan/Act workflow, powered by the Grok-4-Fast model. All generated changes were manually reviewed, tested, and refined by the maintainer, Taruma Sakti, to ensure quality and alignment with project goals.

This version improves development hygiene and user feedback loops without introducing breaking changes.

## v3.1.0 (September 25, 2025) - by Taruma Sakti

This minor release introduces enhancements for project management and macOS compatibility.

### Added
- **Project Created Timestamp Preservation**: Implemented functionality to preserve and backfill project creation timestamps using folder ctime (fix #1).
- **macOS Folder Browser Support**: Enhanced folder browser with macOS support and debug hooks (fix #2).

### AI Development Attribution
This release was developed with AI assistance using various tools including Qwen Code, GPT-5, Grok Code Fast 1, and Code Supernova, with primary workflow using Qwen Code initial development followed by refinement through Cline with GPT-5 and Code Supernova. All generated changes were manually reviewed, tested, and refined by the maintainer, Taruma Sakti, to ensure quality and alignment with project goals.

## v3.0.0 (September 24, 2025) - by Taruma Sakti

This major release introduces comprehensive project information management, enhanced export capabilities, UI/UX refinements including improved theming, and performance optimizations. All changes maintain backward compatibility while modernizing the application for professional AI filmmaking workflows.

### Added
- **Project Location Memory**: Added functionality to store and retrieve the last project location used during project creation. This improves user experience by providing a default location in the UI. Changes include backend storage in ProjectManager, a new API endpoint for fetching the location, and frontend updates to prefill the project location input.
- **Light Theme Styles for Export Modal**: Added CSS rules for the light theme in the export modal, including header colors, borders, backgrounds, and checkbox styles to ensure visual consistency with the overall light theme design.
- **Project Version and Subtitle Display**: Enhanced project header to show version and subtitle alongside title. Added CSS styles for layout, typography, and light/dark theme support. Updated JavaScript to dynamically populate and hide elements based on project info. Modified HTML structure for better semantic organization. This improves user experience by providing more context about the current project directly in the interface.
- **Compact Project Info Modal**: Updated CSS to reduce padding, margins, and input sizes for a tighter layout. Changed short description from textarea to text input for brevity. Added inline styling for version field to align label and input horizontally. This improves user experience by making the modal less cluttered and more efficient to fill out.
- **Project Info Metadata Fields**: Introduced 'short_description' and 'notes' fields in project info defaults across creation, loading, and saving methods. Implemented backward compatibility by mirroring 'description' to 'notes' when 'notes' is empty. Updated frontend modal to display and edit 'short_description', 'notes', and 'version' fields for better project metadata management.
- **Automatic Project Timestamp Updates**: Added calls to `project_manager.update_project_timestamp()` after successful operations like shot creation, file uploads, saving notes, captions, prompts, renames, reorders, promotions, and archiving in `shot_routes.py`. This ensures project timestamps are updated to track recent changes accurately.
- **Enhanced Export Modal with Media Selection**: Added comprehensive CSS styles for export modal, including form layout, custom checkboxes, and button enhancements for improved UI consistency. Updated JavaScript logic in confirmExport to handle new image and video selection checkboxes, determining export type dynamically. Enhanced HTML template with new form elements for export options, enabling users to select specific media types for export.
- **Export Latest Assets Endpoint**: Added a new POST /export route that enables exporting the latest images and videos for non-archived shots in custom order. The endpoint accepts parameters for export name, type (images/videos/all), inclusion of display name in filenames, and metadata generation. Implemented the export_latest_assets method to handle the logic: create an export directory, sanitize filenames, copy assets with ordered prefixes, and optionally generate metadata. This feature improves asset management by providing a structured way to export project assets for external use or backup.
- **SVG Button Icons and Styles**: Updated UI buttons to use scalable SVG icons instead of emojis for better consistency and accessibility. Added new CSS classes for icon buttons in main.css and light theme overrides in styles.css. Replaced TOC toggle icon in main.js with SVG for uniformity.
- **Back to Menu Button in Header**: Added a 'Back to Menu' button to the project header for improved navigation.
- **Project Info Management System**: Added project information management with CRUD operations. Project routes now include loading and creating project info files, plus new endpoints for retrieving and updating project metadata. The project manager service now handles project info file operations including creation, loading, and saving with proper error handling. Project info includes title, description, tags, creation/update timestamps, and version information stored in project_info.json files within each project directory.
- **Prompt Tooltips on Thumbnails**: Introduced tooltip functionality to display prompt text when hovering over preview or video thumbnails. Added corresponding CSS styles for tooltips, initializes tooltips on DOMContentLoaded, and ensures tooltips are reinitialized after TOC rendering. Enhances user experience by providing quick access to prompt information.
- **App Version Display on Index Page**: Added a utility function to read the app version from pyproject.toml and updated the index route and template to display the version alongside the logo. This improves visibility of the current application version for users.
- **Back to Top Button**: Introduced a floating Back to Top button with CSS styling, JavaScript scroll behavior, and markup in index.html. The button appears after scrolling down and smoothly scrolls the page to the top when clicked.
- **Collapsible Archived Section**: Introduces a collapsible 'Archived' section in the shot list with persistent open/close state, updated styling for both dark and light themes, and improved accessibility.
- **Native Folder Picker**: Introduces a native folder picker endpoint using tkinter with a fallback to the user's home directory. Updates the frontend to support opening and creating projects via dialogs, adds recent projects display, and refines the setup and modal UI for improved usability. Also updates the Python version requirement to >=3.13.1 in documentation and pyproject.toml.
- **Python-dotenv Integration**: Added python-dotenv to dependencies and updated run.py to load environment variables from a .env file at startup. This enables configuration via environment variables for improved flexibility.
- **GitHub Funding Configuration**: Created FUNDING.yml file for GitHub sponsors support.

### Changed
- **Project Routes Refactoring**: Refactored the create_project function to delegate directory creation and state management to the project_manager service. This centralizes logic, ensures consistent handling of recent projects, and reduces code duplication for better maintainability.
- **Recent Projects Management**: Updated logic to ensure current project is always first in recent projects list, even if already present, by removing and re-inserting at index 0, then limiting to 3 items. Added timestamp update for last_scanned to record when the project was last accessed. Reduced the maximum number of recent projects stored from 5 to 3 to streamline the list.
- **Shot Display Styling**: Shot display names in the table of contents are now wrapped in a span with the 'shot-display-name' class and styled as bold for better visibility. CSS rules for '.shot-display-name' have been added to ensure consistent bold styling across themes.
- **Shot Grid Layout Improvements**: Reduced the 'Shot Name' column width and adjusted padding for better layout. Changed white-space handling to allow wrapping, and updated drag handle info styling and placement for improved readability in both CSS and HTML.
- **Shot Version Update Optimization**: Replaces full shot row re-rendering with a targeted update of the specific drop zone when switching asset versions. This improves UI performance and reduces unnecessary DOM updates by updating only the relevant elements (version badge, thumbnail, and prompt button) for the changed asset.
- **Project State Persistence**: Adds logic to track whether the user is currently in a project using sessionStorage. This prevents auto-loading the last project on first load and ensures the correct UI is shown after refreshes or navigation.
- **Event Handling Refactoring**: Replaces inline onclick attributes with data attributes and adds event listeners for better code maintainability and to avoid escaping issues.
- **Modal and UI Layout Improvements**: Refactors manual path input controls for better layout and usability, including a link-style toggle button. Updates modal button styles and spacing for consistency.

### Fixed
- **Light Mode Theming Issues**: Replace inline styles with CSS classes for better theme support. Add proper light theme overrides for labels and input fields. Make 'Created' and 'Last Updated' fields properly adapt to light mode. Improve form structure with semantic CSS classes. Ensure all form elements have proper visibility in both themes.
- **Light Mode Text Contrast**: Fixed light mode text contrast and implemented floating theme toggle.
- **Code Cleanup**: Deleted the empty .action-header selector from main.css as it was not providing any styles and is no longer needed.

### Documentation
- **AGENTS.md Update**: Rewrote AGENTS.md to serve as a comprehensive project context document, replacing the contributor guide with sections on project overview, key features, technology stack, development tooling, project structure, and build instructions.
- **QWEN.md Addition**: Introduced QWEN.md with an overview of the Shotbuddy project, including features, technology stack, project structure, setup instructions, configuration options, development conventions, and descriptions of key components.
- **uv Dependency Management Documentation**: Added a section detailing the use of `uv` as the primary tool for dependency management, script execution, and virtual environment handling. Updated instructions and notes throughout to emphasize avoiding direct use of `pip install` in favor of `uv` commands.

### Technical Updates
- **Performance Improvements**: Optimized caching and file handling mechanisms; targeted DOM updates for better UI responsiveness.
- **Python Version Requirement**: Updated to >=3.13.1 in documentation and pyproject.toml for native folder picker support.

### AI Development Attribution
This release was developed with AI assistance using various tools including Qwen Code, GPT-5, Grok Code Fast 1, and Code Supernova, with primary workflow using Qwen Code initial development followed by refinement through Cline with GPT-5 and Code Supernova. All generated changes were manually reviewed, tested, and refined by the maintainer, Taruma Sakti, to ensure quality and alignment with project goals.

This version significantly enhances project organization, export capabilities, and user experience for professional AI filmmaking workflows.

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
