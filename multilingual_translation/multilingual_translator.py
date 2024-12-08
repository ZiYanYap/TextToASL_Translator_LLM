import translators as ts

def translate_to_english(text: str) -> str:
    """
    Translate any text to English
    Args:
        text (str): Text to translate in any language
    Returns:
        str: Translated text in English
    """
    try:
        translated = ts.translate_text(
            query_text=text,
            translator='google',
            from_language='auto',
            to_language='en',
            timeout=10
        )
        return translated.strip()

    except Exception as e:
        print(f"Translation error: {e}")
        return ""
