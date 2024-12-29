from app.services.translation.prompt_template import SYSTEM_PROMPT
from app.services.utils.llm_query import query_llm
from app.config import MAX_TOKENS

WH_WORDS = {"what", "where", "who", "when", "why", "which", "whom", "how", "whose", "how-much", "how-many"}

def post_process_asl_response(response: str) -> str:
    """
    Post-process the ASL response to clean it and handle WH words.
    
    Args:
        response (str): The raw response from the ASL conversion.
    
    Returns:
        str: The cleaned and post-processed ASL response.
    """
    # Remove "ASL Gloss:" if it exists
    if response.startswith("ASL Gloss:"):
        response = response[len("ASL Gloss:"):].strip()

    cleaned_response = response.strip().strip('"').rstrip('.,')
    words = cleaned_response.split()
    last_word = words[-1].rstrip('?')

    if last_word.lower() in WH_WORDS and cleaned_response.endswith('?'):
        cleaned_response = cleaned_response[:-1]

    return cleaned_response

def convert_to_asl(input_text: str):
    """
    Convert input text to ASL using a language model.
    
    Args:
        input_text (str): The text to be converted to ASL.
    
    Returns:
        str: The ASL converted text, or None if an error occurs.
    """
    if not input_text.strip():
        return None

    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f'Input Sentence: "{input_text}"'}
        ]

        response_content = query_llm(messages, temperature=0.2, max_tokens=MAX_TOKENS, top_p=0.8)
        return post_process_asl_response(response_content)

    except Exception as e:
        print(f"Error converting text to ASL: {str(e)}")
        return None
