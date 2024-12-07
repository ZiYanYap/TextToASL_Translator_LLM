import os
from dotenv import load_dotenv
import requests
from langdetect import detect
from typing import Dict

# Load environment variables
load_dotenv()
api_token = os.getenv("HUGGINGFACE_TOKEN")
if not api_token:
    raise ValueError("HUGGINGFACE_TOKEN not found in environment variables")

# Configuration
API_URL = "https://api-inference.huggingface.co/models/facebook/nllb-200-distilled-600M"
headers = {"Authorization": f"Bearer {api_token}"}

# Mapping of langdetect codes to NLLB codes
LANG_CODE_MAP: Dict[str, str] = {
    'en': 'eng_Latn',
    'fr': 'fra_Latn',
    'es': 'spa_Latn',
    'de': 'deu_Latn',
    'it': 'ita_Latn',
    'pt': 'por_Latn',
    'nl': 'nld_Latn',
    'ru': 'rus_Cyrl',
    'ar': 'ara_Arab',
    'hi': 'hin_Deva',
    'zh-cn': 'zho_Hans',
    'zh-tw': 'zho_Hant',
    'ja': 'jpn_Jpan',
    'ko': 'kor_Hang',
    'vi': 'vie_Latn',
    'th': 'tha_Thai',
    'id': 'ind_Latn',
    'tr': 'tur_Latn'
}

def detect_language(text: str) -> str:
    """
    Detect the language of the input text and return the corresponding NLLB code
    """
    try:
        detected_lang = detect(text)
        nllb_code = LANG_CODE_MAP.get(detected_lang, 'eng_Latn')  # Default to English if language not in map
        print(f"Detected language: {detected_lang} (NLLB code: {nllb_code})")
        return nllb_code
    except Exception as e:
        print(f"Language detection error: {e}")
        return 'eng_Latn'  # Default to English on error

def translate_to_english(text: str) -> str:
    """
    Translate any text to English using NLLB with automatic language detection
    Args:
        text (str): Text to translate in any language
    Returns:
        str: Translated text in English
    """
    try:
        # Detect source language
        src_lang = detect_language(text)

        # Prepare the payload with detected source language and English as target
        payload = {
            "inputs": text,
            "parameters": {
                "src_lang": src_lang,
                "tgt_lang": "eng_Latn"
            }
        }

        # Make API request
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        
        # Check if the response contains a translation
        if isinstance(result, list) and len(result) > 0:
            translated_text = result[0].get('translation_text', '')
            print("Translation successful!")
            return translated_text
        else:
            print(f"Unexpected API response: {result}")
            return ""

    except Exception as e:
        print(f"Translation error: {e}")
        return ""
