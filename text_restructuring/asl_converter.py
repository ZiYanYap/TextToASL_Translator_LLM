import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from text_restructuring.prompt_template import SYSTEM_PROMPT
from typing import Optional

# Initialize global variables
load_dotenv()
api_token = os.getenv("HUGGINGFACE_TOKEN")
if not api_token:
    raise ValueError("HUGGINGFACE_TOKEN not found in environment variables")

client = InferenceClient(token=api_token)
model = "Qwen/Qwen2.5-72B-Instruct"
system_message = {"role": "system", "content": SYSTEM_PROMPT}

def convert_to_asl(input_text: str) -> Optional[str]:
    if not input_text.strip():
        return None

    try:
        messages = [
            system_message,
            {"role": "user", "content": "'" + input_text + "'"}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=1024,
            top_p=0.95,
            stream=False
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error converting text to ASL: {str(e)}")
        return None
