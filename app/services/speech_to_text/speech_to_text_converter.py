import os
from dotenv import load_dotenv
import requests
import sounddevice as sd
import soundfile as sf
import tempfile
import numpy as np

# Load environment variables
load_dotenv()
api_token = os.getenv("HUGGINGFACE_TOKEN")
if not api_token:
    raise ValueError("HUGGINGFACE_TOKEN not found in environment variables")

# Configuration
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
headers = {"Authorization": f"Bearer {api_token}"}
SAMPLE_RATE = 16000  # Whisper model's required sample rate
DURATION = 5  # Recording duration in seconds

def query(filename):
    """
    Send audio file to Hugging Face API for transcription
    """
    with open(filename, "rb") as f:
        data = f.read()

    params = {
    "language": "en",  # Preferred transcription language
    "task": "automatic-speech-recognition",  # Ensure transcription-only
    "forced_language": "en"  # Enforce English
    }

    response = requests.post(
        API_URL,
        headers=headers,
        params=params,  # Send parameters as query parameters
        data=data
    )
    return response.json()


def record_and_transcribe():
    """
    Records audio from the microphone and transcribes it using Whisper API.
    Returns the transcribed text.
    """
    try:
        # Record audio
        audio_data = sd.rec(
            int(SAMPLE_RATE * DURATION),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='float32'
        )
        sd.wait()  # Wait until recording is finished

        # Normalize audio data
        audio_data = np.squeeze(audio_data)  # Remove extra dimension if present
        
        # Check if there's actual audio content
        audio_level = np.abs(audio_data).mean()
        
        if audio_level < 0.001:  # Adjust this threshold as needed
            print("Audio level too low")
            return ""

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            # Normalize audio to prevent it from being too quiet
            audio_data = audio_data / np.max(np.abs(audio_data))
            sf.write(temp_audio.name, audio_data, SAMPLE_RATE)
            temp_audio_path = temp_audio.name
            print(f"Audio saved to {temp_audio_path}")

        try:
            # Send to API for transcription
            result = query(temp_audio_path)
            
            # Extract text from response
            if isinstance(result, dict) and 'text' in result:
                transcription = result['text'].strip()
                return transcription
            else:
                print(f"Unexpected API response: {result}")
                return ""

        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                try:
                    os.unlink(temp_audio_path)
                except Exception as e:
                    print(f"Error deleting temporary file: {e}")

    except Exception as e:
        print(f"Recording error: {e}")
        return ""
