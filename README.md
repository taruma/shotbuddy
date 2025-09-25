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
  This project requires Python 3.13.1 or newer.

## Installation

Using uv

1. Install uv

   See https://docs.astral.sh/uv/

4. Clone the repository

   ```bash
   git clone https://github.com/taruma/shotbuddy.git
   ```
   ```bash
   cd shotbuddy
   ```

5. Create the environment and install dependencies

   ```bash
   uv sync
   ```

6. Run the development server

   ```bash
   uv run run.py
   ```

7. Open your browser

   By default, Shotbuddy will be available at http://127.0.0.1:5001/

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

### New Features in this Fork (v2.0.0 to v3.1.0)

<img width="347" height="103" alt="image" src="https://github.com/user-attachments/assets/a5b04523-d584-4958-9e13-8d95eb99aefd" />

This fork significantly enhances Shotbuddy with a focus on improving the user experience for AI filmmaking workflows. 

![](https://github.com/user-attachments/assets/98ec6697-9437-4b44-a1f3-6a34c3b38210)

Key new features include:

**Streamlined Project Management:**
*   **Intuitive Project Information Management:** Easily create, load, and save detailed project information including title, description, tags, and version.
*   **Clear Project Overview:** The project header now displays the project version and subtitle, giving you more context at a glance.

![demo-sb-03](https://github.com/user-attachments/assets/4dd9a394-2110-42db-91f8-a333fbfd948c)

*   **Quick Access to Recent Projects:** Your most recent projects are easily accessible, with the current project always at the top of the list.
*   **Comprehensive Table of Shots (TOC) Panel:** A responsive side panel that provides an overview of all your shots, with filtering, quick navigation, and clear separation of active and archived shots.

![demo-sb-02](https://github.com/user-attachments/assets/e7ce1616-8936-49e8-a3fa-45403cd92203)

*   **Effortless Shot Reordering:** Drag and drop to reorder your shots directly in the grid, with changes saved automatically.

![demo-sb-01](https://github.com/user-attachments/assets/c327eb21-b52d-4163-be52-c5d1c3178bce)

*   **Flexible Shot Archiving:** Easily hide inactive shots from your main view and restore them with a single click from a dedicated archived section. 
*   **Customizable Shot Display Names:** Give your shots human-readable titles (e.g., "Opening Scene" instead of SH010) for better clarity.

![demo-sb-04](https://github.com/user-attachments/assets/0d87067d-def9-4d4e-a140-ee1188288d42)

*   **Project-Specific Data:** All your shot details and captions are now saved within each project, ensuring everything stays organized even when working on multiple projects.

**Enhanced User Interface & Experience:**
*   **Advanced Export Options:** A redesigned export modal allows you to precisely select which images and videos you want to export.

<img width="511" height="702" alt="image" src="https://github.com/user-attachments/assets/d1c0f1bb-d897-464b-bd07-0ca8559d9900" />

*   **Instant Prompt Previews:** Hover over shot thumbnails to instantly see the associated prompt text.

![demo-sb-05](https://github.com/user-attachments/assets/816a40ec-000b-4f6f-807e-51dcd5b305f1)

*   **Seamless Light/Dark Theme Toggle:** Switch between light and dark themes with a single click, with your preference saved automatically.

![demo-sb-06](https://github.com/user-attachments/assets/ec2f3e5e-33a3-4200-89cc-eae3cf70f1c6)

**Powerful Asset Management:**
*   **First/Last Image Variants:** Manage separate opening and closing frames for each shot, each with its own versions, prompts, and thumbnails.
*   **Effortless Asset Versioning:** Easily cycle through and promote different versions of your images and videos, with automatic updates to thumbnails.
*   **Integrated Asset Captions:** Add editable notes or feedback directly under your media previews, saved automatically with each shot.
*   **Dynamic Notes Editor:** Shot notes text areas automatically expand as you type, providing a smoother editing experience.
*   **Optimized Asset Loading:** Faster UI updates when switching between asset versions, improving overall performance.

![demo-sb-07](https://github.com/user-attachments/assets/4286dc1c-7df9-45f0-afd5-acbacf5255da)

## Attribution
- Forked from Shotbuddy by Albert Bozesan: https://github.com/albozes/shotbuddy (MIT License).
- Maintained and extended by Taruma Sakti.

## AI assistance
This project is maintained by Taruma Sakti and developed with AI assistance. For detailed AI development attribution, see the [CHANGELOG.md](./CHANGELOG.md).

## License
This project is licensed under the [MIT License](./LICENSE.txt).
Some third-party assets (e.g., icons) are included under their own licenses, as detailed in the [THIRD_PARTY_LICENSES](./THIRD_PARTY_LICENSES.md) file.
