import openai
import json
from datetime import datetime
from wavtovcon import create_vcon_from_wav  # Ensure this is the correct path
import os

# Set your OpenAI API key
openai.api_key = "sk-xxx"  # Replace with a valid key

# Transcribe audio using OpenAI Whisper
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        try:
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                response_format="json"
            )
            return response["text"]
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None

# Update vCon with transcription
def update_vcon_with_transcription(vcon, file_path):
    transcription = transcribe_audio(file_path)
    if transcription:
        vcon["transcripts"].append({
            "type": "transcription",
            "service": "OpenAI Whisper",
            "text": transcription,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
    return vcon

# Example Usage
if __name__ == "__main__":
    participants = [
        {"name": "Quandale", "role": "caller"}, 
        {"name": "Bingletom", "role": "receiver"}, 
    ]
    audio_path = "/path/to/your/audio.wav"

    if not os.path.exists(audio_path):
        print(f"Error: File '{audio_path}' does not exist.")
    else:
        vcon = create_vcon_from_wav(audio_path, participants)
        vcon = update_vcon_with_transcription(vcon, audio_path)
        print(json.dumps(vcon, indent=4))
