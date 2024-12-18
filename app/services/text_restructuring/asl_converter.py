from huggingface_hub import InferenceClient
from app.services.text_restructuring.prompt_template import SYSTEM_PROMPT
import logging
from app.config import HUGGINGFACE_TOKEN, ASL_CONVERTER_MODEL_NAME, MAX_TOKENS

client = InferenceClient(token=HUGGINGFACE_TOKEN())
system_message = {"role": "system", "content": SYSTEM_PROMPT}

# Define WH words as a constant
WH_WORDS = {
    "what", "where", "who", "when", "why", 
    "which", "whom", "how", "whose"
}

def post_process_asl_response(response: str) -> str:
    """Post-process the ASL response to clean it and handle WH words."""
    # Clean the response: remove quotes and trailing punctuation
    cleaned_response = response.strip().strip('"').rstrip('.,')

    # Split the response into words and get the last word
    words = cleaned_response.split()
    last_word = words[-1].rstrip('?')  # Remove '?' if present

    # Remove question mark if the last word is a WH word
    if last_word.lower() in WH_WORDS and cleaned_response.endswith('?'):
        cleaned_response = cleaned_response[:-1]  # Remove the question mark

    return cleaned_response

def convert_to_asl(input_text: str):
    if not input_text.strip():
        return None

    try:
        messages = [
            system_message,
            {"role": "user", "content": f"'{input_text}'"}
        ]

        response = client.chat.completions.create(
            model=ASL_CONVERTER_MODEL_NAME,
            messages=messages,
            temperature=0.2,
            max_tokens=MAX_TOKENS,
            top_p=0.8,
            stream=False
        )

        # Post-process the ASL response
        return post_process_asl_response(response.choices[0].message.content)

    except Exception as e:
        logging.error(f"Error converting text to ASL: {str(e)}")
        return None
