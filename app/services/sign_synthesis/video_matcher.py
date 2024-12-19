import os
import requests
from moviepy import VideoFileClip, concatenate_videoclips
from app.services.tools.mongo_client import init_mongo_client
from app.config import WSD_API_URL, STATIC_VIDEO_PATH, TEMP_VIDEO_PATH, MERGED_VIDEO_PATH, HF_HEADERS

# Get video path based on URL
def construct_video_path(video_url):
    if not video_url:
        return None
    if "youtube.com" in video_url or "youtu.be" in video_url:
        video_filename = video_url.split('/')[-1] if 'youtu.be' in video_url else video_url.split('v=')[-1]
        return os.path.normpath(os.path.join(STATIC_VIDEO_PATH, f"{video_filename}.mp4"))
    return os.path.normpath(os.path.join(STATIC_VIDEO_PATH, video_url.split('/')[-1]))

# Query the LLM API
def query_llm(prompt):
    response = requests.post(WSD_API_URL, headers=HF_HEADERS, json={"inputs": prompt})
    if response.status_code != 200:
        print(f"Error querying LLM: {response.status_code} - {response.text}")
        return ""
    return ''.join(c for c in response.json()[0]["generated_text"] if c.isalnum())

# Fetch word document from MongoDB
def fetch_word_document(collection, word):
    return collection.find_one({"words": word})

# Fetch character document from MongoDB
def fetch_character_document(collection, char):
    return collection.find_one({"words": char})

# Merge video files
def merge_video_files(video_paths):
    clips = [VideoFileClip(path, target_resolution=(480,360)) for path in video_paths]
    final_clip = concatenate_videoclips(clips, method="compose")
    os.makedirs(TEMP_VIDEO_PATH, exist_ok=True)
    final_clip.write_videofile(MERGED_VIDEO_PATH, codec='libx264', audio_codec='aac', preset='medium', fps=30, logger=None)
    for clip in clips:
        clip.close()
    final_clip.close()

# Handle definitions and return video mapping
def handle_definitions(definitions, word, context):
    word_video_map = []
    if len(definitions) > 1 and context:
        print(f'Handling ambiguity for "{word}"')
        descriptions = [f"{i + 1}. {d.get('meaning')}" for i, d in enumerate(definitions)]
        prompt = (
            f'Word Sense Disambiguation Task:\n\n'
            f'Word: "{word.upper()}"\n'
            f'Sentence: "{context}"\n\n'
            f'Meanings:\n'
            f'{chr(10).join([f"{description}" for description in descriptions])}\n\n'
            f'Instructions:\n'
            f'Based on the context provided in the sentence, identify which meaning of the word "{word.upper()}" is most appropriate.\n'
            f'Return the number corresponding to the correct meaning.'
        )
        response = query_llm(prompt)

        selected_index = parse_llm_response(response, len(definitions))
        video_url = definitions[selected_index].get("video_url")
        video_path = construct_video_path(video_url)
        if video_path and os.path.exists(video_path):
            word_video_map.append((word, video_path))
    else:
        for definition in definitions:
            video_url = definition.get("video_url")
            video_path = construct_video_path(video_url)
            if video_path and os.path.exists(video_path):
                word_video_map.append((word, video_path))
                break
    return word_video_map

# Parse LLM response
def parse_llm_response(response, num_definitions):
    try:
        selected_index = int(response.strip()) - 1
        return max(0, min(selected_index, num_definitions - 1))  # Ensure within bounds
    except ValueError:
        return 0  # Default to first definition if parsing fails

# Fingerspell a word
def fingerspell_word(collection, word):
    word_video_map = []
    for char in word:
        char_doc = fetch_character_document(collection, char)
        if char_doc and char_doc.get("definitions"):
            video_url = char_doc["definitions"][0].get("video_url")
            if video_url:
                video_path = construct_video_path(video_url)
                word_video_map.append((char, video_path))
    return word_video_map

# Get video mapping for a word
def get_word_video_mapping(collection, word, context=None):
    word = word.lower().strip()

    # Step 1: Handle question mark and split if necessary
    words_to_check = []
    for token in word.split():
        if '?' in token:
            token = token.replace('?', '')
            if token:  # Add the word only if it's not empty
                words_to_check.append(token)
            words_to_check.append('?')  # Add the question mark separately
        else:
            words_to_check.append(token)

    # Step 2: Handle hyphenated words only after question mark handling
    processed_words = []
    for w in words_to_check:
        if '-' in w and not fetch_word_document(collection, w):
            processed_words.extend(w.replace('-', ' ').split())
        else:
            processed_words.append(w)

    # Step 3: Map words to their video paths
    word_video_map = []
    for w in processed_words:
        document = fetch_word_document(collection, w)
        if document:
            word_video_map.extend(handle_definitions(document.get("definitions", []), w, context))
        else:
            word_video_map.extend(fingerspell_word(collection, w))

    return word_video_map

# Prepare display data
def prepare_display_data(asl_translation, context=None):
    if not asl_translation:
        return False
    
    display_data = []
    collection = init_mongo_client()
    for word in asl_translation.split():
        word_mapping = get_word_video_mapping(collection, word, context=context)
        display_data.extend(word_mapping)
    
    video_paths = [path for _, path in display_data]
    merge_video_files(video_paths)

    return True
