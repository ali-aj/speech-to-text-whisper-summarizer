import streamlit as st
st.set_page_config(page_title="Voice Notes App", layout="wide", initial_sidebar_state="expanded")

from src.voice_recognition import transcribe_audio_manual, transcribe_file, start_manual_recording
from src.note_manager import NoteManager
from src.summary import generate_summary
from datetime import datetime

# Sidebar
with st.sidebar:
    st.title("🎙️ Summarize Voice Notes")
    st.markdown("---")
    st.write("Developed By Muhammad Ali Mustafa using Whisper")
    st.markdown("---")
    # Add search/filter
    search = st.text_input("🔍 Search Notes")

# Main content
tab1, tab2 = st.tabs(["📝 Take Notes", "📚 View Notes"])

with tab1:
    st.header("Record New Note")
    col1, col2 = st.columns([3, 1])
    with col1:
        note_title = st.text_input("Note Title", placeholder="Enter note title (optional)")
    with col2:
        folder = st.selectbox("Folder", ["General", "Work", "Personal", "Study"])
    
    st.markdown("---")
    
    record_col, upload_col = st.columns([2, 1])
    
    with record_col:
        st.subheader("Record Audio")
        btn_col1, btn_col2 = st.columns([1, 1])
        
        with btn_col1:
            if st.button("🎤 Start Recording", use_container_width=True, type="primary"):
                start_manual_recording()
                st.session_state.recording = True
        
        with btn_col2:
            if st.button("⏹️ Stop Recording", use_container_width=True, 
                        type="secondary", disabled=not st.session_state.get("recording", False)):
                with st.spinner("Processing recording..."):
                    audio_data = transcribe_audio_manual()
                    if audio_data:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        note_data = {
                            "title": note_title or f"Note {timestamp}",
                            "content": audio_data,
                            "timestamp": timestamp,
                            "folder": folder,
                            "source": "recording"
                        }
                        note_manager = NoteManager()
                        note_manager.add_note(note_data)
                        st.success("✅ Note recorded successfully!")
                st.session_state.recording = False
        
        # Recording indicator
        if st.session_state.get("recording", False):
            st.markdown("🔴 Recording in progress...")
    
    with upload_col:
        st.subheader("Upload Audio")
        uploaded_file = st.file_uploader("Upload audio file", 
                                       type=['wav', 'mp3', 'm4a', 'ogg'],
                                       help="Supported formats: WAV, MP3, M4A, OGG")
        
        if uploaded_file:
            with st.spinner("Processing uploaded audio..."):
                audio_data = transcribe_file(uploaded_file)
                if audio_data:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    note_data = {
                        "title": note_title or uploaded_file.name,
                        "content": audio_data['text'],
                        "timestamp": timestamp,
                        "folder": folder,
                        "language": audio_data['language'],
                        "source": "upload"
                    }
                    note_manager = NoteManager()
                    note_manager.add_note(note_data)
                    st.success("✅ Audio file processed successfully!")

with tab2:
    st.header("Your Notes")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Title"])
    with col2:
        filter_folder = st.multiselect("Filter by folder", ["General", "Work", "Personal", "Study"])
    
    note_manager = NoteManager()
    notes = note_manager.get_notes()

    # Apply search filter
    if search:
        notes = [n for n in notes if search.lower() in n['title'].lower() or search.lower() in n['content'].lower()]
    
    # Apply folder filter
    if filter_folder:
        notes = [n for n in notes if n.get('folder', 'General') in filter_folder]
    
    # Apply sorting
    if sort_by == "Newest First":
        notes.sort(key=lambda x: x['timestamp'], reverse=True)
    elif sort_by == "Oldest First":
        notes.sort(key=lambda x: x['timestamp'])
    else:  # Sort by Title
        notes.sort(key=lambda x: x['title'].lower())

    # Display filtered and sorted notes
    for idx, note in enumerate(notes):
        with st.expander(f"📝 {note['title']}", expanded=idx == 0):
            metadata_col, action_col = st.columns([3, 1])
            
            with metadata_col:
                st.markdown(f"**Recorded:** {note['timestamp']}")
                st.markdown(f"**Folder:** {note.get('folder', 'General')}")
            
            with action_col:
                if st.button("🗑️", key=f"del_{idx}", help="Delete note"):
                    note_manager.delete_note(idx)
                    st.rerun()
            
            st.markdown("---")
            st.markdown(f"**Content:**\n{note['content']}")
            
            sum_col, trans_col = st.columns([1, 1])
            with sum_col:
                if st.button("📊 Summarize", key=f"sum_{idx}"):
                    with st.spinner("Generating summary..."):
                        summary = generate_summary(note['content'])
                        st.info(f"**Summary:**\n{summary}")

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