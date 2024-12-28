from flask import Flask, render_template, request, jsonify
from app.services.translation.asl_converter import convert_to_asl
from app.services.speech_to_text.speech_to_text_converter import record_and_transcribe
from app.services.translation.multilingual_translator import translate_to_english
from app.services.sign_synthesis.video_matcher import prepare_display_data
from app.services.sign_synthesis.pose_extraction import pose_extraction
from app.services.utils.mongo_utils import init_mongo_client
from app.config import MAX_TOKENS

app = Flask(__name__)

collection = init_mongo_client()

@app.route("/", methods=["GET"])
def render_index():
    """Render the index page."""
    return render_template("index.html", page_title="Text to ASL Translator", max_tokens=MAX_TOKENS)

@app.route("/words", methods=["GET"])
def render_words_list():
    """Render the supported words list page."""
    return render_template("words.html", page_title="Supported Words")

@app.route("/admin/scrape", methods=["GET", "POST"])
def handle_metadata():
    """Handle metadata scraping and insertion into MongoDB."""
    if request.method == "POST":
        word_names = request.form.get("word_name").lower().split(",")
        meanings = request.form.getlist("meanings[]")
        video_urls = request.form.getlist("video_urls[]")

        meanings_data = [{"meaning": meaning, "video_url": video_url} for meaning, video_url in zip(meanings, video_urls)]
        word_data = {
            "words": [word.strip() for word in word_names],
            "definitions": meanings_data
        }

        collection.create_index("words", unique=True)

        try:
            collection.replace_one({"words": {"$in": word_data["words"]}}, word_data, upsert=True)
            return render_template("scrape.html", page_title="Add a Word", metadata="Word added successfully!", error=None)
        except Exception as e:
            return render_template("scrape.html", page_title="Add a Word", metadata=None, error=f"Error inserting or replacing document: {e}")

    return render_template("scrape.html", page_title="Add a Word", metadata=None, error=None)

@app.route("/api/translate-to-english", methods=["POST"])
def translate_to_english_api():
    """API endpoint to translate text to English."""
    original_text = request.json.get("input_text")
    if not original_text:
        return jsonify({"error": "No input text provided"}), 400
    try:
        english_text = translate_to_english(original_text)
        print(f'Translated text: {english_text}')
        return jsonify({"english_text": english_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/convert-to-asl", methods=["POST"])
def convert_to_asl_api():
    """API endpoint to convert English text to ASL."""
    english_text = request.json.get("english_text")
    if not english_text:
        return jsonify({"error": "No English text provided"}), 400
    
    word_count = len(english_text.split())
    if word_count > MAX_TOKENS:
        return jsonify({"error": f"Input too long! Please limit to {MAX_TOKENS} words."}), 400
    
    try:
        asl_translation = convert_to_asl(english_text)
        print(f'ASL Gloss generated: {asl_translation}')
        return jsonify({"asl_translation": asl_translation})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/prepare-video", methods=["POST"])
def prepare_video_api():
    """API endpoint to prepare video for ASL translation."""
    asl_translation = request.json.get("asl_translation")
    context = request.json.get("context")
    if not asl_translation:
        return jsonify({"error": "No ASL translation provided"}), 400
    try:
        if prepare_display_data(asl_translation, context=context, collection=collection):
            print("Video merge complete")
            return jsonify({"video_ready": True})
        else:
            return jsonify({"video_ready": False}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/pose-extraction", methods=["POST"])
def pose_extraction_api():
    """API endpoint to perform pose extraction."""
    try:
        output_path = pose_extraction()
        print("Pose extraction complete")
        return jsonify({"output_path": output_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/speech-to-text", methods=["POST"])
def speech_to_text_api():
    """API endpoint to convert speech to text."""
    try:
        transcription = record_and_transcribe()
        
        if not transcription:
            return jsonify({"success": False, "error": "No speech detected"}), 400
            
        return jsonify({
            "success": True,
            "text": transcription
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/words", methods=["GET"])
def fetch_words_api():
    """API endpoint to fetch all supported words."""
    try:
        words_data = collection.find({}, {"words": 1})
        words = [word["words"] for word in words_data]
        sorted_words = sorted([w for sublist in words for w in sublist])
        return jsonify({"words": sorted_words})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return "Page not found!", 404

if __name__ == "__main__":
    app.run(debug=True)
