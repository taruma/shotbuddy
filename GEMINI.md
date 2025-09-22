# Shotbuddy - Gemini's Guide

This document serves as a guide for Gemini when interacting with the Shotbuddy codebase.

## 1. Project Overview

Shotbuddy is an application designed to manage AI-driven image-to-video filmmaking workflows. It provides structured organization, versioning, and annotation capabilities for generated stills and videos, optimizing the process for AI filmmakers.

## 2. Key Technologies

The project is built primarily with Python and utilizes the following key libraries and frameworks:

*   **Flask**: A micro web framework for Python, used for the application's backend and routing.
*   **Flask-CORS**: A Flask extension for handling Cross-Origin Resource Sharing (CORS), enabling cross-domain requests.
*   **Pillow**: The friendly PIL (Python Imaging Library) fork, used for image processing tasks.
*   **Pytest**: A testing framework for Python, used for writing and running tests.

## 3. Project Structure

The core application logic resides within the `app/` directory:

*   `app/`: The main application package.
    *   `__init__.py`: Initializes the Flask application and registers blueprints.
    *   `utils.py`: Contains utility functions used across the application.
    *   `config/`: Configuration files.
        *   `constants.py`: Defines application-wide constants.
    *   `routes/`: Defines the application's API endpoints and web routes.
        *   `project_routes.py`: Routes related to project management.
        *   `shot_routes.py`: Routes related to individual shots.
    *   `services/`: Contains business logic and service-layer components.
        *   `file_handler.py`: Handles file system operations.
        *   `project_manager.py`: Manages project-level operations.
        *   `prompt_importer.py`: Handles importing prompts.
        *   `shot_manager.py`: Manages individual shot operations.
    *   `static/`: Static assets (CSS, JavaScript, images).
        *   `css/`: Stylesheets.
        *   `icons/`: Icons.
        *   `js/`: JavaScript files.
        *   `thumbnails/`: Placeholder for generated thumbnails.
    *   `templates/`: HTML templates for the web interface.
        *   `index.html`: The main application template.

Other important files in the project root:

*   `run.py`: The entry point for running the Flask development server.
*   `shotbuddy.cfg`: Configuration file for server settings (host, port).
*   `requirements.txt`: Lists Python dependencies.
*   `README.md`: General project information and setup instructions.

## 4. Setup and Running

For detailed instructions on setting up the development environment and running the application, please refer to the `README.md` file.

In summary, the steps involve:
1.  Installing Python 3.
2.  Cloning the repository.
3.  Creating and activating a Python virtual environment.
4.  Installing dependencies using `pip install -r requirements.txt`.
5.  Running the development server with `python run.py`.

The application will typically be accessible at `http://127.0.0.1:5001/`.

## 5. Development Notes for Gemini

When making changes or analyzing the codebase, Gemini should:

*   **Adhere to existing conventions**: Pay close attention to coding style, naming conventions, and architectural patterns already present in the project.
*   **Utilize existing services**: Leverage the `services/` layer for business logic and file operations.
*   **Test thoroughly**: If making changes to core logic, ensure existing tests pass and consider adding new tests where appropriate. The project uses `pytest`.
*   **Configuration**: Be aware that server settings can be found in `shotbuddy.cfg` and can be overridden by environment variables.
*   **File Management**: The application has specific logic for managing `shots/` directories, including versioning of images and videos. Understand this logic before modifying file-related operations.
