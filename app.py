from flask import Flask, render_template, request, jsonify
from text_restructuring.asl_converter import convert_to_asl

app = Flask(__name__)

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

    # GET request (initial load)
    return render_template("index.html", original_text=None, asl_translation=None)

if __name__ == "__main__":
    app.run(debug=True)
