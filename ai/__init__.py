import dotenv
import logging
import nest_asyncio
import vertexai

from . import paths


def create_folders():
    print("Creating folders if not exist.")
    folders_to_be_created_if_not_exist = [
        paths.RESOURCES_DIR,
        paths.TEMP_DIR,
        paths.STATIC_RESOURCES_DIR,
        paths.DATA_DIR
    ]
    for dirpath in folders_to_be_created_if_not_exist:
        dirpath.mkdir(exist_ok=True)
    print("Folders were ensured to be existing")

def initialize() -> None:
    print("Initialization process started!")
    print("Setting up logging level")
    logging.basicConfig(level=logging.DEBUG)
    print("Loading environment variables from env file")
    
    create_folders()

    dotenv.load_dotenv(paths.ENV_FILE)
    print("Setting up interactive kernal for async functionality testing..")
    nest_asyncio.apply()
    
    print("Initiating Vertex AI..")
    from .constants import VERTEX_PROJECT_ID, VERTEX_LOCATION
    vertexai.init(project=VERTEX_PROJECT_ID, location=VERTEX_LOCATION)

    print("Completed initialization process")
    return

initialize()
from . import constants

__all__ = ["paths", "constants"]
