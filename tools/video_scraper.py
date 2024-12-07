import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import yt_dlp

# Load environment variables
load_dotenv()

# MongoDB connection
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)
db = client["asl_project"]
collection = db["word_metadata"]

# Define base path for videos
BASE_VIDEO_PATH = os.path.join("static", "sign_videos")

def get_video_path(video_url):
    """
    Generate the video path based on the video URL
    """
    if "youtube.com" in video_url or "youtu.be" in video_url:
        # Handle YouTube URLs
        video_filename = video_url.split('/')[-1] if 'youtu.be' in video_url else video_url.split('v=')[-1]
        return os.path.join(BASE_VIDEO_PATH, f"{video_filename}.mp4")
    else:
        # Handle direct video URLs
        return os.path.join(BASE_VIDEO_PATH, video_url.split('/')[-1])

def download_video(url, save_path):
    """
    Download video from URL and save to specified path
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Skip if file already exists
    if os.path.exists(save_path):
        print(f"Skipping {save_path} - already exists")
        return
    
    try:
        if "youtube.com" in url or "youtu.be" in url:
            # Download YouTube video using yt-dlp
            ydl_opts = {
                'format': 'best',
                'outtmpl': save_path,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"Successfully downloaded: {save_path}")
        else:
            # For other video URLs
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            
            # Get file size for progress bar
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
        # Remove partially downloaded file if it exists
        if os.path.exists(save_path):
            os.remove(save_path)

def scrape_videos():
    """
    Main function to scrape videos from metadata
    """
    # Get all documents from MongoDB
    documents = collection.find({})
    
    # Create a list to hold the futures
    futures = []
    
    # Use ThreadPoolExecutor for concurrency
    with ThreadPoolExecutor(max_workers=5) as executor:
        for doc in documents:
            for definition in doc.get('definitions', []):
                video_url = definition.get('video_url')
                
                if video_url:
                    print(f"\nProcessing word(s): {doc['words']}")
                    # Generate video path
                    video_path = get_video_path(video_url)
                    # Submit the download task to the executor
                    futures.append(executor.submit(download_video, video_url, video_path))
        
        # Wait for all futures to complete
        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    print("Starting video scraping process...")
    scrape_videos()
    print("\nVideo scraping completed!")
