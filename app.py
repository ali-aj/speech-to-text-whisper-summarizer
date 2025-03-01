import streamlit as st
st.set_page_config(page_title="Voice Notes App", layout="wide", initial_sidebar_state="expanded")

from src.voice_recognition import transcribe_file, start_manual_recording, stop_manual_recording, transcribe_audio_manual
from src.note_manager import NoteManager
from src.summary import generate_summary
from datetime import datetime

# Sidebar
with st.sidebar:
    st.title("🎙️ Voice Notes Transcriber")
    st.markdown("---")
    st.write("Upload audio files or record directly")
    st.markdown("---")
    search = st.text_input("🔍 Search Notes")

# Main content
tab1, tab2, tab3 = st.tabs(["📝 Upload Audio", "🎤 Record Audio", "📚 View Notes"])

# Upload tab
with tab1:
    st.header("Upload Audio File")
    
    uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3', 'm4a'])
    note_title = st.text_input("Note Title (optional)", key="upload_title")
    
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

# Recording tab - new tab
with tab2:
    st.header("Record Audio")
    
    record_note_title = st.text_input("Note Title (optional)", key="record_title")
    
    col1, col2 = st.columns(2)
    
    # Initialize session state for recording status if not exists
    if "is_recording" not in st.session_state:
        st.session_state.is_recording = False
    
    with col1:
        if st.button("🎙️ Start Recording"):
            start_manual_recording()
            st.session_state.is_recording = True
    
    with col2:
        if st.button("⏹️ Stop Recording & Transcribe"):
            if st.session_state.get("is_recording", False):
                with st.spinner("Processing and transcribing..."):
                    transcribed_text = transcribe_audio_manual()
                    if transcribed_text:
                        note_manager = NoteManager()
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        note_data = {
                            "title": record_note_title or f"Recording {timestamp}",
                            "text": transcribed_text,
                            "timestamp": timestamp
                        }
                        note_manager.add_note(note_data)
                        st.success("Recording transcribed successfully!")
                        st.write("Transcribed Text:")
                        st.write(transcribed_text)
                        
                        with st.expander("View Summary"):
                            summary = generate_summary(note_data)
                            st.write(summary)

    # Display recording status
    if st.session_state.get("is_recording", False):
        st.markdown("🔴 **Recording in progress...**")
    else:
        st.markdown("⚪ Ready to record")

# View notes tab (renamed from tab2 to tab3)
with tab3:
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