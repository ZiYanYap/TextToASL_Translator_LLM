from huggingface_hub import InferenceClient
from app.config import HUGGINGFACE_TOKEN, LLM_MODEL_NAME

client = InferenceClient(token=HUGGINGFACE_TOKEN())

def query_llm(messages, temperature=0.5, max_tokens=50, top_p=0.7):
    """
    Queries the language model with the provided messages and parameters.

    Args:
        messages: The messages to send to the language model.
        temperature: The sampling temperature.
        max_tokens: The maximum number of tokens to generate.
        top_p: The nucleus sampling probability.

    Returns:
        The generated text from the language model.
    """
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=False
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error querying LLM: {e}")
        return ""
