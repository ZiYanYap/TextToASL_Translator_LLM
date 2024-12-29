import os
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import yt_dlp
from app.services.utils.mongo_utils import init_mongo_client
from app.services.utils.video_utils import construct_video_path
from app.config import STATIC_VIDEO_PATH

collection = init_mongo_client()

def download_video(url, save_path):
    """
    Downloads a video from the given URL and saves it to the specified path.

    Args:
        url (str): The URL of the video.
        save_path (str): The path where the video will be saved.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    if os.path.exists(save_path):
        print(f"Skipping {save_path} - already exists")
        return
    
    try:
        if "youtube.com" in url or "youtu.be" in url:
            ydl_opts = {
                'format': 'best',
                'outtmpl': save_path,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"Successfully downloaded: {save_path}")
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            file_size = int(response.headers.get('content-length', 0))
            progress = tqdm(total=file_size, unit='iB', unit_scale=True, desc=os.path.basename(save_path))
            
            with open(save_path, 'wb') as file:
                for data in response.iter_content(chunk_size=1024):
                    size = file.write(data)
                    progress.update(size)
            progress.close()
            print(f"Successfully downloaded: {save_path}")
        
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        if os.path.exists(save_path):
            os.remove(save_path)

def process_document(doc, executor, current_video_paths):
    """
    Processes a document to download videos for each definition.

    Args:
        doc (dict): The document containing video URLs.
        executor (ThreadPoolExecutor): The executor for managing threads.
        current_video_paths (set): A set to keep track of current video paths.
    """
    for definition in doc.get('definitions', []):
        video_url = definition.get('video_url')
        if video_url:
            print(f"\nProcessing word(s): {doc['words']}")
            video_path = construct_video_path(video_url)
            current_video_paths.add(video_path)
            executor.submit(download_video, video_url, video_path)

def scrape_videos():
    """
    Scrapes videos from the database and downloads them.
    """
    documents = collection.find({})
    futures = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        current_video_paths = set()
        
        for doc in documents:
            process_document(doc, executor, current_video_paths)
        
        for future in as_completed(futures):
            future.result()
    
    clean_up_old_videos(current_video_paths)

def clean_up_old_videos(current_video_paths):
    """
    Cleans up old videos that are no longer in the current video paths.

    Args:
        current_video_paths (set): A set of current video paths.
    """
    existing_videos = set(os.path.normpath(os.path.join(STATIC_VIDEO_PATH, f)) for f in os.listdir(STATIC_VIDEO_PATH) if f.endswith('.mp4'))
    videos_to_delete = existing_videos - current_video_paths
    
    for video in videos_to_delete:
        os.remove(video)
        print(f"Deleted old video: {video}")

if __name__ == "__main__":
    print("Starting video scraping process...")
    scrape_videos()
    print("\nVideo scraping completed!")
