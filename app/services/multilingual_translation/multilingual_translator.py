import translators as ts
from app.config import TARGET_LANGUAGE

def translate_to_english(text: str) -> str:
    try:
        translated = ts.translate_text(
            query_text=text,
            translator='google',
            from_language='auto',
            to_language=TARGET_LANGUAGE,
            timeout=10
        )
        return translated.strip()

    except Exception as e:
        print(f"Translation error: {e}")
        return ""
