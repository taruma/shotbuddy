# Shotbuddy
An application for managing AI-driven image-to-video filmmaking workflows, supporting structured organization, versioning, and annotation of generated stills and videos.

## Project folder layout

Each project contains a `shots` directory with the following structure:

```
shots/
    wip/              # per-shot folders
        SH###/
            images/   # versioned stills
            videos/   # versioned videos
            lipsync/  # lipsync clips (not implemented yet)
    latest_images/    # latest image for each shot
    latest_videos/    # latest video for each shot
```

The application automatically manages the latest versions in `latest_images` and `latest_videos` while keeping all historical versions inside the `wip` shot folders.

## Requirements

- **Python**: >= 3.13.1
  This project requires Python 3.13.1 or newer. pip and uv enforce this when installing; attempting to install with an older interpreter will fail with a message referencing the package's requires-python metadata.

## Installation

Using uv

1. Install uv
   See https://docs.astral.sh/uv/

2. Clone the repository

   ```bash
   git clone https://github.com/taruma/shotbuddy.git
   ```
   ```bash
   cd shotbuddy
   ```

3. Create the environment and install dependencies

   ```bash
   uv sync
   ```

4. Run the development server

   ```bash
   uv run run.py
   ```

5. Open your browser

   By default, Shotbuddy will be available at http://127.0.0.1:5001/

## Configuration

Server settings can be defined in the `shotbuddy.cfg` file located in the
repository root. The file uses INI syntax and contains a `[server]` section with
`host` and `port` keys:

```ini
[server]
host = 0.0.0.0
port = 5001
```

Values specified via environment variables override those in `shotbuddy.cfg`.
Available variables are:

- `SHOTBUDDY_UPLOAD_FOLDER` – directory used for temporary uploads (default:
  `uploads`).
- `SHOTBUDDY_HOST` – address the Flask server binds to (default: `127.0.0.1`).
- `SHOTBUDDY_PORT` – port number for the development server (default: `5001`).
- `SHOTBUDDY_DEBUG` – set to `1` to enable Flask debug mode.

## Functionality
Shotbuddy has a straightforward interface, similar to existing shotlist applications, but optimized for AI filmmakers.

![Shotbuddy_00](https://github.com/user-attachments/assets/d5b00bff-a698-4f55-a3ea-d16192e9e8df)

Create new shots and iterate versions with simple drag and drop. Generated images and videos are automatically copied into a clean folder structure and renamed to the correct shot.

![Shotbuddy_01](https://github.com/user-attachments/assets/adffec41-d2fe-4ca8-b45f-35257a411a3b)

![Shotbuddy_02](https://github.com/user-attachments/assets/e35bc530-cb3b-4a76-a8ab-ca5fda5cf1a9)

The most current version of an asset is named after the shot, so it automatically updates further down in the pipeline, so your edit is always up-to-date, no matter where you do it.

![Shotbuddy_05](https://github.com/user-attachments/assets/8cbbb9cb-8842-4182-a3d4-59cfd0fa45b6)

Old versions are archived into the "wip" folder.

![Shotbuddy_06](https://github.com/user-attachments/assets/1b5f9f52-873b-42ce-9bd1-79976c994691)

New shots can be added before or in-between existing ones, due to the flexible three-digit shot naming convention. Should there be a need for even more (between SH011 and SH012, for example), naming continues with an underscore (e.g. SH011_050).

![Shotbuddy_03](https://github.com/user-attachments/assets/8201d548-8086-4956-9464-ba2f2343b43a)

Via the "P" button on each asset thumbnail, prompts can be documented. A version history is available via the dropdown on the top right of the window.

![Shotbuddy_07](https://github.com/user-attachments/assets/6acd7aaa-c611-47a4-b1c8-6b73f6ae8b12)
![Shotbuddy_08](https://github.com/user-attachments/assets/cf0a4e45-734f-4491-b457-766613ca5132)

Notes on individual shots can be made easily.

![Shotbuddy_04](https://github.com/user-attachments/assets/7567416e-3f4b-42d0-888c-b8296b261616)

### New Features in this Fork (v2.0.0 to v3.0.0)

This fork significantly enhances Shotbuddy with a focus on improving the user experience for AI filmmaking workflows. 

![](https://github.com/user-attachments/assets/98ec6697-9437-4b44-a1f3-6a34c3b38210)

Key new features include:

**Streamlined Project Management:**
*   **Intuitive Project Information Management:** Easily create, load, and save detailed project information including title, description, tags, and version.

![](https://github.com/user-attachments/assets/036ea74c-f148-4e9a-93e3-850093bb1241)

*   **Clear Project Overview:** The project header now displays the project version and subtitle, giving you more context at a glance.

![](https://github.com/user-attachments/assets/87a8915e-14f0-461b-8836-a1bda85b0dd3)

*   **Quick Access to Recent Projects:** Your most recent projects are easily accessible, with the current project always at the top of the list.
*   **Comprehensive Table of Shots (TOC) Panel:** A responsive side panel that provides an overview of all your shots, with filtering, quick navigation, and clear separation of active and archived shots.

*   **Effortless Shot Reordering:** Drag and drop to reorder your shots directly in the grid, with changes saved automatically.
*   **Flexible Shot Archiving:** Easily hide inactive shots from your main view and restore them with a single click from a dedicated archived section. 
*   **Customizable Shot Display Names:** Give your shots human-readable titles (e.g., "Opening Scene" instead of SH010) for better clarity.
*   **Project-Specific Data:** All your shot details and captions are now saved within each project, ensuring everything stays organized even when working on multiple projects.

**Enhanced User Interface & Experience:**
*   **Advanced Export Options:** A redesigned export modal allows you to precisely select which images and videos you want to export.
*   **Instant Prompt Previews:** Hover over shot thumbnails to instantly see the associated prompt text.
*   **Convenient "Back to Top" Button:** Quickly scroll to the top of long pages with a floating button.
*   **Seamless Light/Dark Theme Toggle:** Switch between light and dark themes with a single click, with your preference saved automatically.
*   **Improved Shot Readability:** Shot display names in the table of contents are now bold for better visibility.

**Powerful Asset Management:**
*   **First/Last Image Variants:** Manage separate opening and closing frames for each shot, each with its own versions, prompts, and thumbnails.
*   **Effortless Asset Versioning:** Easily cycle through and promote different versions of your images and videos, with automatic updates to thumbnails.
*   **Integrated Asset Captions:** Add editable notes or feedback directly under your media previews, saved automatically with each shot.
*   **Dynamic Notes Editor:** Shot notes text areas automatically expand as you type, providing a smoother editing experience.
*   **Optimized Asset Loading:** Faster UI updates when switching between asset versions, improving overall performance.

**Productivity & Setup:**
*   **Native Folder Selection:** Use your system's native file explorer to open and create projects, making file management more intuitive.

## Attribution
- Forked from Shotbuddy by Albert Bozesan: https://github.com/albozes/shotbuddy (MIT License).
- Maintained and extended by Taruma Sakti.

## AI assistance
This project is maintained by Taruma Sakti and developed with AI assistance. For detailed AI development attribution, see the [CHANGELOG.md].

## License
This project is licensed under the [MIT License](./LICENSE.txt).
Some third-party assets (e.g., icons) are included under their own licenses, as detailed in the [THIRD_PARTY_LICENSES](./THIRD_PARTY_LICENSES.md) file.
