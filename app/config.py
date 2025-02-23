import os
from dotenv import load_dotenv
import logging

load_dotenv()

def get_env_var(var_name):
    """
    Retrieves an environment variable and validates it.
    
    :param var_name: The name of the environment variable to retrieve.
    :return: The value of the environment variable.
    :raises EnvironmentError: If the environment variable is missing.
    """
    value = os.getenv(var_name)
    if not value:
        logging.error(f"Environment variable '{var_name}' is missing and required for the application.")
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value

HUGGINGFACE_TOKEN = lambda: get_env_var("HUGGINGFACE_TOKEN")
ASR_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
LLM_MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"

MONGODB_URI = lambda: get_env_var("MONGODB_URI")
DB_NAME = lambda: get_env_var("DB_NAME")
COLLECTION_NAME = lambda: get_env_var("COLLECTION_NAME")

STATIC_VIDEO_PATH = os.path.normpath(os.path.join("static", "sign_videos"))
TEMP_VIDEO_PATH = os.path.normpath(os.path.join("static", "temp"))
MERGED_VIDEO_FILENAME = "merged_video.mp4"
OUTPUT_VIDEO_FILENAME = "output_video.mp4"
MERGED_VIDEO_PATH = os.path.normpath(os.path.join(TEMP_VIDEO_PATH, MERGED_VIDEO_FILENAME))
OUTPUT_VIDEO_PATH = os.path.normpath(os.path.join(TEMP_VIDEO_PATH, OUTPUT_VIDEO_FILENAME))

MAX_TOKENS = 50
TARGET_LANGUAGE = "en"
RECORD_DURATION = 5  # Recording duration in seconds
DRAW_COLOR = (48, 255, 48)  # Pose landmarks drawing color