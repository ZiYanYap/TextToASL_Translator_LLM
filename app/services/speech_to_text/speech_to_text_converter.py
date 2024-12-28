import os
import requests
import sounddevice as sd
import soundfile as sf
import tempfile
import numpy as np
from app.config import ASR_API_URL, RECORD_DURATION, TARGET_LANGUAGE, HUGGINGFACE_TOKEN

SAMPLE_RATE = 16000

def query(filename):
    """
    Sends an audio file to the Hugging Face API for transcription.

    Args:
        filename: The path to the audio file.

    Returns:
        The JSON response from the API.
    """
    with open(filename, "rb") as f:
        data = f.read()

    params = {
        "language": TARGET_LANGUAGE,
        "task": "automatic-speech-recognition",
        "forced_language": TARGET_LANGUAGE
    }

    response = requests.post(
        ASR_API_URL,
        headers={"Authorization": f"Bearer {HUGGINGFACE_TOKEN()}"},
        params=params,
        data=data
    )
    return response.json()

def record_and_transcribe():
    """
    Records audio from the microphone and transcribes it using the Whisper API.

    Returns:
        The transcribed text.
    """
    try:
        audio_data = sd.rec(
            int(SAMPLE_RATE * RECORD_DURATION),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='float32'
        )
        sd.wait()

        audio_data = np.squeeze(audio_data)
        audio_level = np.abs(audio_data).mean()
        
        if audio_level < 0.005:
            print("Audio level too low")
            return ""

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            audio_data = audio_data / np.max(np.abs(audio_data))
            sf.write(temp_audio.name, audio_data, SAMPLE_RATE)
            temp_audio_path = temp_audio.name
            print(f"Audio saved to {temp_audio_path}")

        try:
            result = query(temp_audio_path)
            
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
            if os.path.exists(temp_audio_path):
                try:
                    os.unlink(temp_audio_path)
                except Exception as e:
                    print(f"Error deleting temporary file: {e}")

    except Exception as e:
        print(f"Recording error: {e}")
        return ""
