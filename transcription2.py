import openai
import json
import redis
import os
from datetime import datetime, timezone
from wavtovcon import create_vcon_from_wav  # Ensure this is the correct path
from pymongo import MongoClient
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog

# Set your OpenAI API key
openai.api_key = "sk-proj-xxx"  # Replace with a valid key

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Connect to MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["vcons"]
collection = db["vcons"]

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

# Create and enrich vCon with transcription and metadata
def create_and_enrich_vcon(audio_path, participants):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file '{audio_path}' does not exist.")

    # Initialize vCon
    vcon = Vcon.build_new()

    # Add parties to the vCon
    for participant in participants:
        party = Party(name=participant["name"], role=participant["role"])
        vcon.add_party(party)

    # Add audio metadata as a dialog
    start_time = datetime.now(timezone.utc)
    dialog = Dialog(
        type="audio",
        start=start_time.isoformat(),
        parties=[i for i in range(len(participants))],
        originator=0,  # Assuming the first participant is the originator
        mimetype="audio/wav",
        body=f"Audio recorded at {start_time.isoformat()}", # replace with url
    )
    vcon.add_dialog(dialog)

    # Transcribe audio and add transcription to the vCon
    transcription = transcribe_audio(audio_path) # take this to line 73 out and add transcript as analysis, posting to conserver
    if transcription:
        transcript_dialog = Dialog(
            type="transcription",
            start=start_time.isoformat(),
            parties=[i for i in range(len(participants))],
            originator=0,  # Assuming transcription pertains to the first speaker
            mimetype="text/plain",
            body=transcription,
        )
        vcon.add_dialog(transcript_dialog)

    # Add transcription as an attachment
    vcon.add_attachment(body=transcription, type="transcript", encoding="none") # change to add analysis

    return vcon

# Push vCon to Redis
#def push_vcon_to_redis(vcon, key="vcon:1"):
    try:
        redis_client.set(key, json.dumps(vcon))
        print(f"vCon pushed to Redis with key: {key}")
    except Exception as e:
        print(f"Error pushing to Redis: {e}")

# Store vCon in MongoDB
def store_vcon_in_mongo(vcon):
    try:
        vcon_dict = json.loads(vcon.to_json())
        result = collection.insert_one(vcon_dict)
        print(f"vCon stored in MongoDB with ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error storing in MongoDB: {e}")

if __name__ == "__main__":
    participants = [
        {"name": "Quandale", "role": "caller"},
        {"name": "Bingleton", "role": "receiver"},
    ]
    audio_path = "/Users/benjigifford/Downloads/nyashvcon_fixed.wav"

    try:
        vcon = create_and_enrich_vcon(audio_path, participants)
        print(vcon.to_json())  # Output the final vCon as JSON
        store_vcon_in_mongo(vcon)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# publish wav file for deepgram
# use conserver chain to make analysis
