import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from moviepy import VideoFileClip, concatenate_videoclips

# Load environment variables
load_dotenv()
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)
db = client["asl_project"]
collection = db["word_metadata"]

# Define base path for videos
BASE_VIDEO_PATH = os.path.join("static", "sign_videos")

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_TOKEN')}"}

def get_video_path(video_url):
    """
    Generate the video path based on the video URL
    """
    try:
        if not video_url:
            return None
        if "youtube.com" in video_url or "youtu.be" in video_url:
            # Handle YouTube URLs
            video_filename = video_url.split('/')[-1] if 'youtu.be' in video_url else video_url.split('v=')[-1]
            return os.path.join(BASE_VIDEO_PATH, f"{video_filename}.mp4")
        else:
            # Handle direct video URLs
            return os.path.join(BASE_VIDEO_PATH, video_url.split('/')[-1])
    except Exception as e:
        print(f"Error generating video path for {video_url}: {str(e)}")
        return None

def query_llm(prompt):
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    # Remove any punctuation from the response text
    return ''.join(c for c in response.json()[0]["generated_text"] if c.isalnum())

def get_word_video_mapping(word, context=None):
    """
    Fetch the specified word and its corresponding video paths from the MongoDB collection.
    Returns a list of tuples mapping words/chars to their video paths.
    If multiple definitions exist, uses context to select the appropriate video path.
    If the word is not found, uses fingerspelling for the letters of the word.
    """
    # Normalize input
    word = word.lower().strip()
    
    # Handle special characters
    if '-' in word and not collection.find_one({"words": word}):
        word = word.replace('-', ' ')
    
    # Split by spaces and handle '?'
    words_to_check = []
    for w in word.split():
        if w:
            # Handle question marks anywhere in the word
            if '?' in w:
                w = w.replace('?', '')
                words_to_check.extend([w, '?'] if w else ['?'])
            else:
                words_to_check.append(w)

    word_video_map = []
    
    for w in words_to_check:
        # Fetch the document for the specified word
        document = collection.find_one({"words": w})
        
        if document:
            definitions = document.get("definitions", [])
            if len(definitions) > 1 and context:
                # Prepare descriptions for LLM more concisely
                descriptions = [f"{i + 1}. {d.get('meaning')}" for i, d in enumerate(definitions)]
                prompt = (
                    f'Which description describes the word "{w.upper()}" best in the following context?\n\n'
                    f'Descriptions:\n{", ".join(descriptions)}\n\n'
                    f'Context: "{context}".\n\nAnswer (1 or 2):'
                )
                response = query_llm(prompt)
                try:
                    selected_index = int(response.strip()) - 1  # Subtract 1 to convert to 0-based index
                    if not 0 <= selected_index < len(definitions):
                        selected_index = 0  # Default to first if out of range
                except ValueError:
                    selected_index = 0  # Default to first definition if parsing fails
                
                if video_url := definitions[selected_index].get("video_url"):
                    video_path = get_video_path(video_url)
                    if video_path and os.path.exists(video_path):
                        word_video_map.append((w, video_path))
            else:
                # Use first available video URL if no context or single definition
                for definition in definitions:
                    if video_url := definition.get("video_url"):
                        video_path = get_video_path(video_url)
                        if video_path and os.path.exists(video_path):
                            word_video_map.append((w, video_path))
                            break
        else:
            # Fingerspelling for non-existent words
            for char in w:
                # Look up the character in MongoDB
                char_doc = collection.find_one({"words": char})
                if char_doc and char_doc.get("definitions"):
                    video_url = char_doc["definitions"][0].get("video_url")
                    if video_url:
                        video_path = get_video_path(video_url)
                        word_video_map.append((char, video_path))

    return word_video_map

def merge_videos(video_paths):
    """
    Merge multiple video files into a single video file.
    Args:
        video_paths (list): List of paths to video files to merge
    Returns:
        str: Path to the merged video file
    """
    clips = []
    for path in video_paths:
        # Explicitly set the video size and ensure proper loading
        clip = VideoFileClip(path, target_resolution=(480, 360))
        clips.append(clip)
    
    final_clip = concatenate_videoclips(clips, method="compose")
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join('static', 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save merged video with specific codec settings
    output_path = os.path.join(temp_dir, 'merged_video.mp4')
    final_clip.write_videofile(output_path, 
                             codec='libx264', 
                             audio_codec='aac',
                             preset='medium',
                             fps=30)
    
    # Close all clips
    for clip in clips:
        clip.close()
    final_clip.close()
    
    return output_path

def prepare_display_data(asl_translation, context=None):
    """
    Prepare the display data by matching the ASL translation words with their video paths.
    Returns a tuple containing:
        - List of tuples (word, video_path)
        - Path to merged video
    """
    if not asl_translation:
        return [], None
    
    display_data = []
    for word in asl_translation.split():
        display_data.extend(get_word_video_mapping(word, context=context))
    
    # Get video paths and merge them
    video_paths = [os.path.join('static', path.replace('static\\', '').replace('\\', '/')) 
                  for _, path in display_data]
    merged_video_path = merge_videos(video_paths)
    
    return display_data, merged_video_path
