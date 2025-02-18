import whisper
import streamlit as st
import tempfile
import os
import wave
import numpy as np
import torch

# Constants for audio
CHANNELS = 1
RATE = 16000

def init_model():
    """Initialize the Whisper model with error handling"""
    try:
        # Check if CUDA is available and set the device accordingly
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.info(f"Using device: {device}")
        
        # Load the tiny model for better performance
        return whisper.load_model("tiny", device=device)
    except Exception as e:
        st.error(f"Error initializing Whisper model: {str(e)}")
        return None

@st.cache_resource
def get_whisper_model():
    """Get or create the Whisper model instance"""
    if 'whisper_model' not in st.session_state:
        st.session_state.whisper_model = init_model()
    return st.session_state.whisper_model

def transcribe_file(uploaded_file):
    """Transcribe an uploaded audio file"""
    model = get_whisper_model()
    if model is None:
        st.error("Failed to load the transcription model. Please try again.")
        return None

    tmp_path = None
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(uploaded_file.getvalue())
        
        # Transcribe with explicit language setting
        result = model.transcribe(
            tmp_path,
            language='en',
            task='transcribe',
            fp16=False  # Disable half-precision for better compatibility
        )
        return result['text']
    except Exception as e:
        st.error(f"Error processing audio file: {str(e)}")
        return None
    finally:
        # Cleanup temporary file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_data = []

    def start_recording(self):
        self.recording = True
        self.audio_data = []
        
        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_data.append(indata.copy())
        
        self.stream = sd.InputStream(
            channels=CHANNELS,
            samplerate=RATE,
            callback=callback
        )
        self.stream.start()

    def stop_recording(self):
        if hasattr(self, 'stream'):
            self.recording = False
            self.stream.stop()
            self.stream.close()
            return np.concatenate(self.audio_data, axis=0) if self.audio_data else None
        return None

recorder = None

def start_manual_recording():
    global recorder
    try:
        if recorder is None:
            recorder = AudioRecorder()
        recorder.start_recording()
        st.session_state.is_recording = True
    except Exception as e:
        st.error(f"Failed to start recording: {str(e)}")

def stop_manual_recording():
    global recorder
    try:
        if recorder and st.session_state.get("is_recording", False):
            audio_data = recorder.stop_recording()
            st.session_state.is_recording = False
            return audio_data
    except Exception as e:
        st.error(f"Failed to stop recording: {str(e)}")
    return None

def transcribe_audio_manual():
    try:
        if not st.session_state.get("is_recording", False):
            st.error("Recording has not been started.")
            return None

        audio_data = stop_manual_recording()
        if audio_data is None:
            st.error("No audio was recorded.")
            return None

        # Create temporary file
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_path = tmp_file.name
                wavfile.write(tmp_path, RATE, audio_data)

            # Transcribe
            result = model.transcribe(tmp_path)
            return result['text']
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass

    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return None