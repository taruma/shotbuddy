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

## New features in this fork

Quickly rearrange the sequence directly in the grid. Drag a shot to a new position to reflect the intended order without touching your source assets. The new order is saved with the project so it stays consistent across sessions.
![](https://github.com/user-attachments/assets/54f8adad-a111-4189-a390-426fb770943a)

When a shot is not active but you want to keep all its assets, archive it. Archived shots are hidden from the main grid but remain fully preserved and can be restored at any time.
![](https://github.com/user-attachments/assets/8c1172ea-a78b-4020-90df-e8234ab3d6c4)

Use the TOC panel to scan your project at a glance and jump to any shot instantly. It provides a compact overview, improves navigation for larger projects, and pairs well with reordering and archiving.
![](https://github.com/user-attachments/assets/c61cf6d3-c1c6-4f4a-ac97-d6c69afcf233)

Give any shot a friendly title separate from its technical code. Display names improve readability in the grid and TOC and make collaboration easier without changing how files are stored.
![](https://github.com/user-attachments/assets/91683e86-46b5-4541-bcd0-2c98a17aa86f)

Choose which version should be treated as the “latest” for downstream tools, and quickly cycle through versions in the UI. This makes auditioning iterations and locking the chosen take fast and traceable.
![](https://github.com/user-attachments/assets/82471148-69ba-449f-8a06-ac9e1165820c)

Mark representative “first” and “last” frames to communicate shot intent and transitions. These variants are handy for storyboards, reviews, or cut-in/out references.
![](https://github.com/user-attachments/assets/b25e1f6a-b3f4-4463-82ae-095b4aab172b)

Add short captions to assets to capture intent, context, or review notes. Captions are stored with each shot’s metadata and can be surfaced in the UI for quick reference. The notes field automatically expands to fit longer comments, so you can write comfortably without manual resizing.
![](https://github.com/user-attachments/assets/c8b89756-fa3f-4394-b7fa-e843df87d1ae)

Switch between themes for different environments and preferences. The header and menu layout have been streamlined for clarity and faster navigation.
![](https://github.com/user-attachments/assets/b7c44d15-0d0c-4c6d-8b6a-a659335d4f6b)

Other improvements (developer experience & docs)
- Shot metadata is now stored and managed at the project level, making multi‑project work more robust while keeping each project’s state self‑contained.
- Uses uv and pyproject.toml for simpler, reproducible environments (uv sync, uv run).
- Documentation cleanups and footer/attribution updates for clearer guidance.

## Attribution
- Forked from Shotbuddy by Albert Bozesan: https://github.com/albozes/shotbuddy (MIT License).
- Maintained and extended by Taruma Sakti.

## AI assistance
This project is maintained by Taruma Sakti and developed with AI assistance:
- Cline (Plan/Act workflow)
- Model mix: GPT‑5 and Qwen3 Coder

All AI-assisted changes are reviewed and tested by the maintainer.

## License
This project is licensed under the [MIT License](./LICENSE.txt).
Some third-party assets (e.g., icons) are included under their own licenses, as detailed in the [THIRD_PARTY_LICENSES](./THIRD_PARTY_LICENSES.md) file.
