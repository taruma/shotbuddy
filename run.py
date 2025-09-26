import os
import socket
import threading
import time
import webbrowser
from configparser import ConfigParser
from pathlib import Path
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()


def load_server_config():
    """Load server host and port from shotbuddy.cfg if it exists."""
    cfg_path = Path(__file__).with_name("shotbuddy.cfg")
    host = None
    port = None
    if cfg_path.exists():
        parser = ConfigParser()
        parser.read(cfg_path)
        if parser.has_section("server"):
            host = parser.get("server", "host", fallback=None)
            port = parser.getint("server", "port", fallback=None)
    return host, port


app = create_app()

if __name__ == "__main__":
    cfg_host, cfg_port = load_server_config()
    host = os.environ.get("SHOTBUDDY_HOST", cfg_host or "127.0.0.1")
    port = int(os.environ.get("SHOTBUDDY_PORT", cfg_port or 5001))
    debug = os.environ.get("SHOTBUDDY_DEBUG", "0").lower() in {"1", "true", "yes"}

    def _open_browser_when_ready(url):
        while True:
            try:
                with socket.create_connection((host, port), timeout=1):
                    break
            except OSError:
                time.sleep(0.1)
        webbrowser.open_new(url)

    threading.Thread(
        target=_open_browser_when_ready,
        args=(f"http://{host}:{port}/",),
        daemon=True,
    ).start()

    app.run(debug=debug, host=host, port=port)
