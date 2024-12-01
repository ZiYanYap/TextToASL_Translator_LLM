from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from text_restructuring.asl_converter import convert_to_asl

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment variable
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)
db = client["asl_project"]
collection = db["word_metadata"]

# Define the video save path
video_save_path = os.path.join("data", "sign_videos")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_text = request.form.get("input_text")
        if not original_text:
            return jsonify({"error": "No input text provided"}), 400

        try:
            # Generate ASL Gloss
            asl_translation = convert_to_asl(original_text)
            return render_template("index.html", original_text=original_text, asl_translation=asl_translation)
        except Exception as e:
            return render_template("index.html", error=f"Error: {str(e)}")

    return render_template("index.html", original_text=None, asl_translation=None)

@app.route("/scrape", methods=["GET", "POST"])
def metadata():
    if request.method == "POST":
        word_names = request.form.get("word_name").lower().split(",")  # Split by comma
        meanings = request.form.getlist("meanings[]")
        video_urls = request.form.getlist("video_urls[]")

        # Prepare the data for MongoDB
        meanings_data = []
        for meaning, video_url in zip(meanings, video_urls):
            video_filename = os.path.basename(video_url)
            video_path = os.path.join(video_save_path, video_filename)

            meanings_data.append({
                "meaning": meaning,
                "video_url": video_url,
                "video_path": video_path
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
    return render_template("words.html", words=words)

if __name__ == "__main__":
    app.run(debug=True)
