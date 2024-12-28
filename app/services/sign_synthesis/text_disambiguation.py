import re
from app.services.utils.llm_query import query_llm

def query_named_entities(asl_gloss, original_sentence):
    """
    Analyze the ASL gloss sentence with reference to the original English sentence to classify each word.
    Identify whether each word is a proper noun and return a list of proper noun words.

    Args:
        asl_gloss (str): The ASL gloss sentence.
        original_sentence (str): The original English sentence.

    Returns:
        list: A list of proper noun words.
    """
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "Be a disambiguation assistant, whatever you receive as input, make sure to only give back a response following the example output strictly.\n\n"
                    "Analyze the following ASL gloss sentence with reference to the original English sentence to classify each word. Identify whether each word is a proper noun and return only a list of proper noun words.\n\n"
                    "Example:\n"
                    "ASL Gloss: \"MY NAME BRAND\"\n"
                    "Original English Sentence: \"My name is Brand.\"\n\n"
                    "Example Output:\n[\"BRAND\"]\n\n"
                    "Output:"
                )
            },
            {
                "role": "user",
                "content": (
                    f"ASL Gloss: \"{asl_gloss}\"\n"
                    f"Original English Sentence: \"{original_sentence}\""
                )
            }
        ]

        raw_response = query_llm(messages, max_tokens=50)
        return eval(raw_response)  # Convert stringified list to actual list
    except Exception as e:
        print(f"Error querying Qwen LLM for named entities: {e}")
        return []

def query_wsd(word, sentence, meanings):
    """
    Based on the context provided in the sentence, identify which meaning of the word is most appropriate.
    Return only the number corresponding to the correct meaning.

    Args:
        word (str): The word to disambiguate.
        sentence (str): The sentence providing context.
        meanings (list): A list of possible meanings for the word.

    Returns:
        str: The number corresponding to the correct meaning.
    """
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an assistant for word sense disambiguation tasks.\n\n"
                    "Instructions:\n"
                    "Based on the context provided in the sentence, identify which meaning of the word is most appropriate.\n"
                    "Return only the number corresponding to the correct meaning."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Word: \"{word}\"\n"
                    f"Sentence: \"{sentence}\"\n\n"
                    f"Meanings:\n"
                    f"{chr(10).join([f'{i + 1}. {meaning}' for i, meaning in enumerate(meanings)])}"
                )
            }
        ]

        raw_response = query_llm(messages, max_tokens=10)
        return re.sub(r'[^\w\s]', '', raw_response)  # Remove punctuation
    except Exception as e:
        print(f"Error querying Qwen LLM for WSD: {e}")
        return ""