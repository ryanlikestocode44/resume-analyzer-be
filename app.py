from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

from resume_parser import ResumeParser
from error_handlers import register_error_handlers

app = Flask(__name__)
CORS(app)
register_error_handlers(app)

@app.route("/upload", methods=["GET", "POST"])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['resume']
    if not file or file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    try:
        # Baca file langsung dari memori (RAM)
        file_bytes = file.read()
        if not file_bytes:
            return jsonify({"error": "Uploaded file is empty"}), 400

        # Proses resume langsung dari bytes
        parser = ResumeParser(file_bytes=file_bytes)
        data = parser.get_extracted_data()

        if not data:
            return jsonify({"error": "Failed to parse resume"}), 500

        # Bangun respons JSON
        response = data

        return jsonify(response), 200

    except Exception as e:
        traceback.print_exc()  # Log error details to console
        return jsonify({"Error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
