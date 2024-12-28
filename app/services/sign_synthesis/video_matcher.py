import os
from moviepy import VideoFileClip, concatenate_videoclips
from app.services.sign_synthesis.text_disambiguation import *
from app.services.utils.mongo_utils import fetch_document
from app.services.utils.video_utils import construct_video_path
from app.config import TEMP_VIDEO_PATH, MERGED_VIDEO_PATH

def merge_video_files(video_paths):
    """
    Merges multiple video files into a single video file.
    
    Args:
        video_paths (list): List of file paths to the video files to be merged.
    """
    clips = [VideoFileClip(path, target_resolution=(480,360)) for path in video_paths]
    final_clip = concatenate_videoclips(clips, method="compose")
    os.makedirs(TEMP_VIDEO_PATH, exist_ok=True)
    final_clip.write_videofile(MERGED_VIDEO_PATH, codec='libx264', audio_codec='aac', preset='medium', fps=30, logger=None)
    for clip in clips:
        clip.close()
    final_clip.close()

def handle_definitions(definitions, word, context):
    """
    Handles multiple definitions of a word and returns the video mapping.
    
    Args:
        definitions (list): List of definitions for the word.
        word (str): The word being processed.
        context (str): The context in which the word is used.
        
    Returns:
        list: List of tuples containing the word and its corresponding video path.
    """
    word_video_map = []
    if len(definitions) > 1 and context:
        print(f'Handling ambiguity for "{word}"')
        meanings = [d.get("meaning") for d in definitions]
        response = query_wsd(word, context, meanings)

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

def parse_llm_response(response, num_definitions):
    """
    Parses the response from the LLM to determine the selected definition.
    
    Args:
        response (str): The response from the LLM.
        num_definitions (int): The number of definitions available.
        
    Returns:
        int: The index of the selected definition.
    """
    try:
        selected_index = int(response.strip()) - 1
        return max(0, min(selected_index, num_definitions - 1))
    except ValueError:
        return 0

def fingerspell_word(collection, word):
    """
    Generates a video mapping for fingerspelling a word.
    
    Args:
        collection: The MongoDB collection to fetch data from.
        word (str): The word to be fingerspelled.
        
    Returns:
        list: List of tuples containing each character and its corresponding video path.
    """
    word_video_map = []
    for char in word:
        char_doc = fetch_document(collection, char)
        if char_doc and char_doc.get("definitions"):
            video_url = char_doc["definitions"][0].get("video_url")
            if video_url:
                video_path = construct_video_path(video_url)
                word_video_map.append((char, video_path))
    return word_video_map

def get_word_video_mapping(collection, word, context=None):
    """
    Retrieves the video mapping for a given word.
    
    Args:
        collection: The MongoDB collection to fetch data from.
        word (str): The word to be mapped to a video.
        context (str, optional): The context in which the word is used.
        
    Returns:
        list: List of tuples containing the word and its corresponding video path.
    """
    words_to_check = []
    for token in word.split():
        if '?' in token:
            token = token.replace('?', '')
            if token:
                words_to_check.append(token)
            words_to_check.append('?')
        else:
            words_to_check.append(token)

    processed_words = []
    for w in words_to_check:
        if '-' in w and not fetch_document(collection, w):
            processed_words.extend(w.replace('-', ' ').split())
        else:
            processed_words.append(w)

    word_video_map = []
    for w in processed_words:
        document = fetch_document(collection, w)
        if document:
            word_video_map.extend(handle_definitions(document.get("definitions", []), w, context))
        else:
            word_video_map.extend(fingerspell_word(collection, w))

    return word_video_map

def prepare_display_data(asl_translation, context=None, collection=None):
    """
    Prepares the display data for the ASL translation.
    
    Args:
        asl_translation (str): The ASL translation text.
        context (str, optional): The context in which the translation is used.
        collection: The MongoDB collection to fetch data from.
        
    Returns:
        bool: True if the display data was prepared successfully, False otherwise.
    """
    if not asl_translation:
        return False

    named_entities = query_named_entities(asl_translation, context)
    normalized_named_entities = [pn.lower().strip() for pn in named_entities]
    print(f'Named entities detected: {normalized_named_entities}')

    display_data = []
    normalized_translation = [word.lower().strip() for word in asl_translation.split()]
    for normalized_word in normalized_translation:
        if (normalized_word in normalized_named_entities):
            display_data.extend(fingerspell_word(collection, normalized_word))
        else:
            word_mapping = get_word_video_mapping(collection, normalized_word, context=context)
            display_data.extend(word_mapping)

    video_paths = [path for _, path in display_data]
    merge_video_files(video_paths)

    return True
