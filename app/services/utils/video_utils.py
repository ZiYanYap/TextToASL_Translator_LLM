import os
from app.config import STATIC_VIDEO_PATH

def construct_video_path(video_url):
    """
    Constructs the file path for a video based on its URL.
    
    Args:
        video_url (str): The URL of the video.
        
    Returns:
        str: The file path of the video.
    """
    if not video_url:
        return None
    if "youtube.com" in video_url or "youtu.be" in video_url:
        video_filename = video_url.split('/')[-1] if 'youtu.be' in video_url else video_url.split('v=')[-1]
        return os.path.normpath(os.path.join(STATIC_VIDEO_PATH, f"{video_filename}.mp4"))
    return os.path.normpath(os.path.join(STATIC_VIDEO_PATH, video_url.split('/')[-1]))