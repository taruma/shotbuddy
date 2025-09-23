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
- Shot reordering to rearrange the sequence (drag-and-drop) (94967e0).
- Shot archiving to declutter the working grid without deleting assets (4d6e2b7).
- Table of Shots (TOC) side panel for quick navigation and context (1f96f6b).
- Action column with icon buttons in the shot grid for common operations (9306c3e).
- Display name per shot (human‑readable title independent of shot code) (9092027).
- Asset version promotion and in‑UI cycling through versions (e346fdb).
- First/last image variants per shot (3610507).
- Captions for assets (images/videos) stored with shot metadata (8f06ae5).
- Notes textarea auto‑resize for better editing UX (f15ae81, 5ea73f0).
- Light theme with toggle; header/menu layout refinements (ca49a7d, 9178fc5).
- Project‑scoped shot metadata handling for multi‑project support (d8c8c43).

Other improvements:
- Switched to uv with pyproject.toml for environment/dependency management (ca72d2d, pyproject added).
- Documentation updates (Gemini guide, contributor guide), footer and attribution cleanups (e0880f6, 02f1460, 0319e56, ee5bbd4, c6229ef).

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
