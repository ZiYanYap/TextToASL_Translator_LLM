import translators as ts

def translate_to_english(text: str) -> str:
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
