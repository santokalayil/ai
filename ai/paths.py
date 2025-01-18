from pathlib import Path

MAIN_DIR = Path(__file__).parent.parent
ENV_FILE = str(MAIN_DIR / ".env")
RESOURCES_DIR = MAIN_DIR / "resources"

TEMP_DIR = RESOURCES_DIR / "temp"
STATIC_RESOURCES_DIR = RESOURCES_DIR / "static"
DATA_DIR = RESOURCES_DIR / "data"
