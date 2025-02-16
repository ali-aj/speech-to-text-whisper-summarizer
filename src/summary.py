import os
from dotenv import load_dotenv
import streamlit as st
import requests

load_dotenv()

# Adjust to read from the .env file
def generate_summary_gemini(text):
    api_key = os.getenv("GEMINI_API_KEY")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": text}]}]}

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(response)
        if response.status_code == 200:
            data = response.json()
            return data.get('contents', [{}])[0].get('parts', [{}])[0].get('text', '')
        else:
            st.error(f"Gemini API error {response.status_code}: {response.text}")
            return ""
    except Exception as e:
        st.error(f"Summarization error: {str(e)}")
        return ""

def generate_summary(note_data):
    text = note_data.get("text", "") if isinstance(note_data, dict) else (note_data or "")
    text = "Summarize this text into its language: " + text
    return generate_summary_gemini(text)
