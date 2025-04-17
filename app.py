# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 17:03:38 2025

@author: tehre
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import core
import os

app = Flask(__name__)
CORS(app)

@app.route("/mental-health", methods=["POST"])
def mental_health():
    data = request.json
    urdu_text = data.get("text", "").strip()

    if not urdu_text:
        return jsonify({"error": "Missing Urdu text"}), 400

    english_text = core.translate_urdu_to_english(urdu_text)

    if core.is_query_mental_health_related(english_text):
        english_response = core.generate_response(english_text)
        audio_file = core.azure_tts_urdu(english_response)
    else:
        english_response = "I'm sorry, I can only assist with mental health topics."
        audio_file = core.azure_tts_urdu(english_response)

    return jsonify({
        "urdu_input": urdu_text,
        "english_translation": english_text,
        "response": english_response,
        "audio_file": f"/responses/{audio_file}" if audio_file else None
    })

@app.route("/responses/<filename>")
def serve_audio(filename):
    return send_from_directory(core.RESPONSE_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
