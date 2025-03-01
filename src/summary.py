import os
from dotenv import load_dotenv
import streamlit as st
import requests

load_dotenv()

def generate_summary_gemini(text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Gemini API key not found. Please check your .env file.")
        return ""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": text}]}]}

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            st.error(f"Gemini API error {response.status_code}: {response.text}")
            return ""
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return ""
    except Exception as e:
        st.error(f"Summarization error: {str(e)}")
        return ""

def generate_summary(note_data):
    text = note_data.get("text", "") if isinstance(note_data, dict) else (note_data or "")
    text = "Summarize this text: " + text
    return generate_summary_gemini(text)
