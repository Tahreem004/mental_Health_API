# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 17:02:44 2025

@author: tehre
"""

import os
import uuid
import requests
from deep_translator import GoogleTranslator

# Azure + LM Studio settings
AZURE_TTS_KEY = "5hLz8c1SpUvWuruisUMtFZEROsgujtGCCHyonwCtza6AFJnOD1EEJQQJ99BDACqBBLyXJ3w3AAAYACOGvI2D"
AZURE_REGION = "southeastasia"
AZURE_TRANSLATOR_KEY = "BOOpV2mHXV44rGFAVdDME76Qd69rNj26gIEkqC6sohJ6qCHpsdyzJQQJ99BDACqBBLyXJ3w3AAAbACOG4Ij2"
AZURE_TRANSLATOR_REGION = "southeastasia"
LM_STUDIO_URL = "http://localhost:1234/v1/completions"
TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"

RESPONSE_DIR = "responses"
os.makedirs(RESPONSE_DIR, exist_ok=True)

def translate_urdu_to_english(text):
    return GoogleTranslator(source="ur", target="en").translate(text)

def translate_english_to_urdu(text):
    url = f"{TRANSLATOR_ENDPOINT}/translate?api-version=3.0&from=en&to=ur"
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': AZURE_TRANSLATOR_REGION,
        'Content-type': 'application/json'
    }
    body = [{'text': text}]
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()[0]['translations'][0]['text']

def is_query_mental_health_related(text):
    headers = {"Content-Type": "application/json"}
    prompt = (
        "You are a classifier. Respond only with 'Yes' or 'No'.\n"
        f"Is the following text related to mental health?\n\nText: \"{text}\"\nAnswer:"
    )
    payload = {
        "prompt": prompt,
        "max_tokens": 10,
        "temperature": 0.0,
        "stop": ["\n"]
    }
    response = requests.post(LM_STUDIO_URL, headers=headers, json=payload)
    return "yes" in response.json()['choices'][0]['text'].strip().lower()

def generate_response(english_text):
    headers = {"Content-Type": "application/json"}
    prompt = (
        f"You are a mental health therapist. A patient says: \"{english_text}\". "
        f"Provide a supportive, understanding, and concise response."
    )
    payload = {
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 0.7
    }
    response = requests.post(LM_STUDIO_URL, headers=headers, json=payload)
    return response.json()['choices'][0]['text'].strip()

def azure_tts_urdu(text):
    translated_urdu = translate_english_to_urdu(text)
    ssml = f"""
    <speak version='1.0' xml:lang='ur-PK'>
        <voice xml:lang='ur-PK' xml:gender='Male' name='ur-PK-AsadNeural'>
            {translated_urdu}
        </voice>
    </speak>
    """
    tts_url = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TTS_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
        "User-Agent": "UrduMentalHealthBot"
    }
    response = requests.post(tts_url, headers=headers, data=ssml.encode("utf-8"))
    if response.status_code == 200:
        filename = f"response_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(RESPONSE_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)
        return filename
    else:
        print("Azure TTS Error:", response.status_code, response.text)
        return None
