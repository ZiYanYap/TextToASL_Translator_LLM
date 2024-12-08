from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from text_restructuring.asl_converter import convert_to_asl
from speech_to_text.speech_to_text_converter import record_and_transcribe
from langdetect import detect
from multilingual_translation.multilingual_translator import translate_to_english
from sign_synthesis.video_matcher import prepare_display_data

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment variable
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)
db = client["asl_project"]
collection = db["word_metadata"]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_text = request.form.get("input_text")
        if not original_text:
            return jsonify({"error": "No input text provided"}), 400

        try:
            # Detect language
            detected_lang = detect(original_text)
            print(f"Detected language: {detected_lang}")  # Debugging line
            
            # Translate to English if not already in English
            if detected_lang != 'en':
                english_text = translate_to_english(original_text)
                print(f"Translated text: {english_text}")  # Debugging line
                text_for_asl = english_text
            else:
                text_for_asl = original_text
            
            # Generate ASL Gloss from the English text
            asl_translation = convert_to_asl(text_for_asl)
            
            # Get video paths and merged video
            video_data, merged_video_path = prepare_display_data(asl_translation, context=text_for_asl)
            
            return render_template("index.html", 
                                 original_text=original_text,
                                 asl_translation=asl_translation,
                                 video_data=video_data)
                                 
        except Exception as e:
            return render_template("index.html", error=f"Error: {str(e)}")

    return render_template("index.html", 
                         original_text=None,
                         asl_translation=None,
                         video_data=None)

@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    try:
        # Call the record_and_transcribe function
        transcription = record_and_transcribe()
        
        if not transcription:
            return jsonify({"success": False, "error": "No speech detected"}), 400
            
        return jsonify({
            "success": True,
            "text": transcription
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/scrape", methods=["GET", "POST"])
def metadata():
    if request.method == "POST":
        word_names = request.form.get("word_name").lower().split(",")  # Split by comma
        meanings = request.form.getlist("meanings[]")
        video_urls = request.form.getlist("video_urls[]")

        # Prepare the data for MongoDB
        meanings_data = []
        for meaning, video_url in zip(meanings, video_urls):
            meanings_data.append({
                "meaning": meaning,
                "video_url": video_url
            })

        # Create or update the document for related words
        word_data = {
            "words": [word.strip() for word in word_names],
            "definitions": meanings_data
        }

        # Insert or replace the current word data into MongoDB
        collection.create_index("words", unique=True)  # Ensure unique index on words

        try:
            collection.replace_one({"words": {"$in": word_data["words"]}}, word_data, upsert=True)
            return render_template("scrape.html", metadata="Word added successfully!", error=None)
        except Exception as e:
            return render_template("scrape.html", metadata=None, error=f"Error inserting or replacing document: {e}")

    return render_template("scrape.html", metadata=None, error=None)  # Placeholder for metadata

@app.route("/words", methods=["GET"])
def words_list():
    # Fetch all words from the MongoDB collection
    words_data = collection.find({}, {"words": 1})  # Only retrieve the 'words' field
    words = [word["words"] for word in words_data]
    
    # Sort the words alphabetically
    sorted_words = sorted(words, key=lambda x: x[0].lower())  # Sort by the first letter, case insensitive
    
    return render_template("words.html", words=sorted_words)

if __name__ == "__main__":
    app.run(debug=True)
