# Voice-Based Note-Taking Application

This project is a voice-based note-taking application that allows users to capture, manage, and summarize their notes using voice input. The application is built using Streamlit and leverages various libraries for voice recognition and text summarization.

## Features

- Voice recognition for capturing notes
- Storage and retrieval of notes
- Summarization of notes for quick review

## Project Structure

```
voice-notes-app
├── app.py                # Entry point of the application
├── requirements.txt      # Project dependencies
├── src
│   ├── voice_recognition.py  # Functions for voice input processing
│   ├── note_manager.py       # Note storage and retrieval management
│   └── summary.py            # Note summarization functionality
└── README.md             # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd voice-notes-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage Guidelines

- Use the voice input feature to take notes by speaking clearly into your microphone.
- Access your saved notes and use the summarization feature to get quick insights.