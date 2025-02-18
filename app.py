import streamlit as st
st.set_page_config(page_title="Voice Notes App", layout="wide", initial_sidebar_state="expanded")

from src.voice_recognition import transcribe_file
from src.note_manager import NoteManager
from src.summary import generate_summary
from datetime import datetime

# Sidebar
with st.sidebar:
    st.title("🎙️ Voice Notes Transcriber")
    st.markdown("---")
    st.write("Upload audio files for transcription")
    st.markdown("---")
    search = st.text_input("🔍 Search Notes")

# Main content
tab1, tab2 = st.tabs(["📝 Upload Audio", "📚 View Notes"])

with tab1:
    st.header("Upload Audio File")
    
    uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3', 'm4a'])
    note_title = st.text_input("Note Title (optional)")
    
    if uploaded_file and st.button("Transcribe"):
        with st.spinner("Transcribing..."):
            transcribed_text = transcribe_file(uploaded_file)
            if transcribed_text:
                note_manager = NoteManager()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                note_data = {
                    "title": note_title or uploaded_file.name,
                    "text": transcribed_text,
                    "timestamp": timestamp
                }
                note_manager.add_note(note_data)
                st.success("Transcription completed!")
                st.write("Transcribed Text:")
                st.write(transcribed_text)
                
                with st.expander("View Summary"):
                    summary = generate_summary(note_data)
                    st.write(summary)

with tab2:
    note_manager = NoteManager()
    notes = note_manager.get_notes()
    
    if search:
        notes = [note for note in notes if search.lower() in 
                note.get("text", "").lower() or 
                search.lower() in note.get("title", "").lower()]
    
    for i, note in enumerate(notes):
        with st.expander(f"{note.get('title')} - {note.get('timestamp')}"):
            st.write(note.get("text", ""))
            if st.button(f"Delete Note {i}", key=f"delete_{i}"):
                note_manager.delete_note(i)
                st.rerun()

# Custom CSS for better UI
st.markdown("""
    <style>
        .stButton button {
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .stProgress .st-bo {
            background-color: #4CAF50;
        }
        .stAlert {
            border-radius: 10px;
        }
        /* Dark theme support */
        @media (prefers-color-scheme: dark) {
            .stButton button {
                background-color: #2E7D32;
            }
        }
    </style>
""", unsafe_allow_html=True)