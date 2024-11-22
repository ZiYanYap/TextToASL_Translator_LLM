import os
import requests
import csv
from bs4 import BeautifulSoup

# Define output directories
VIDEO_DIR = "data/videos"
METADATA_FILE = "data/metadata.csv"

# Ensure directories exist
os.makedirs(VIDEO_DIR, exist_ok=True)

# Function to download video
def download_video(url, output_path):
    try:
        print(f"Downloading video from {url}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(output_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Video saved to {output_path}")
        else:
            print(f"Failed to download {url} - Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading video: {e}")

# Function to scrape data
def scrape_videos(base_url, word_list):
    metadata = []
    for word in word_list:
        try:
            # Example: Construct video URL (modify based on the actual website)
            video_url = f"{base_url}/{word}.mp4"
            output_path = os.path.join(VIDEO_DIR, f"{word}.mp4")
            
            # Download the video
            download_video(video_url, output_path)
            
            # Record metadata
            metadata.append({"word": word, "video_url": video_url})
        except Exception as e:
            print(f"Error processing word '{word}': {e}")
    
    # Save metadata to CSV
    with open(METADATA_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["word", "video_url"])
        writer.writeheader()
        writer.writerows(metadata)
    print("Metadata saved.")

if __name__ == "__main__":
    # Example: Base URL of the website (https://www.handspeak.com/word/a/aga/again.mp4)
    BASE_URL = "https://www.handspeak.com/word"
    
    # List of words to scrape
    WORD_LIST = ["YOU", "HOW", "TODAY", "FIND", "HELP", "WORK"]
    
    scrape_videos(BASE_URL, WORD_LIST)