from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader

app = Flask(__name__)
CORS(app)

pdf_text_storage = ""  # stores extracted PDF text


# -------------------------
# Upload PDF
# -------------------------
@app.route("/api/upload_pdf", methods=["POST"])
def upload_pdf():
    global pdf_text_storage
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Invalid file format"}), 400

    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        pdf_text_storage = text.strip()
        return jsonify({"text": pdf_text_storage[:500]})  # return preview

    except Exception as e:
        return jsonify({"error": f"Failed to process PDF: {str(e)}"}), 500


# -------------------------
# Ask Question
# -------------------------
@app.route("/api/ask", methods=["POST"])
def ask():
    global pdf_text_storage
    data = request.json
    question = data.get("question", "").lower()

    if not pdf_text_storage:
        return jsonify({"answer": "Please upload a PDF first."}), 400

    # Split into sentences
    sentences = pdf_text_storage.split(".")
    matches = [s.strip() for s in sentences if question in s.lower()]

    if matches:
        return jsonify({"answer": " ".join(matches[:3])})
    else:
        return jsonify({"answer": "Sorry, I couldn't find an answer."})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
