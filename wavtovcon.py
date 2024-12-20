# Basic script that converts .wav files into vCons(json format)
# Does not transribe audio. See transcription.py for transcription

import wave
import json
from datetime import datetime
import uuid

# Function to create a vCon from WAV file
def create_vcon_from_wav(file_path, participants):
    # Read WAV file metadata
    with wave.open(file_path, "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        duration = n_frames / frame_rate

    # Create a unique ID for the vCon
    vcon_id = str(uuid.uuid4())

    # Build the vCon structure
    vcon = {
        "id": vcon_id,
        "type": "vCon",
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "participants": participants,
        "media": [
            {
                "type": "audio/wav",
                "duration": duration,
                "channels": channels,
                "sample_width": sample_width,
                "frame_rate": frame_rate,
                "payload": file_path,  # This would be a reference or base64 of the file in production
            }
        ],
        "transcripts": [],
    }
    return vcon

# Example Usage
participants = [
    {"name": "Quandale", "role": "caller"},
    {"name": "Bingletom", "role": "receiver"},
]

vcon = create_vcon_from_wav("/path/to/your/audio.wav", participants)
print(json.dumps(vcon, indent=4))

