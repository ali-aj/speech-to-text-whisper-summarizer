import whisper
import streamlit as st
import tempfile
import os
import pyaudio
import wave
import numpy as np
from array import array
import threading
import time

# Constants for audio recording
CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 16000

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("turbo")

model = load_whisper_model()

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False

    def callback(self, in_data, frame_count, time_info, status):
        if self.is_recording:
            self.frames.append(np.frombuffer(in_data, dtype=np.float32))
        return (in_data, pyaudio.paContinue)

    def start_recording(self):
        self.frames = []
        self.is_recording = True
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self.callback
        )
        self.stream.start_stream()

    def stop_recording(self):
        if self.stream:
            self.is_recording = False
            time.sleep(0.5)  # Allow final chunks to be processed
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            return np.concatenate(self.frames) if self.frames else None
        return None

    def close(self):
        if self.stream:
            self.stream.close()
        self.audio.terminate()

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

            # Write audio data
            with wave.open(tmp_path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(4)
                wf.setframerate(RATE)
                wf.writeframes(audio_data.tobytes())

            # Transcribe
            result = model.transcribe(tmp_path)
            return {
                'text': result['text'],
                'language': result.get('language', 'unknown')
            }
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass

    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return None

def transcribe_file(uploaded_file):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(uploaded_file.getvalue())
        
        result = model.transcribe(tmp_path)
        return {
            'text': result['text'],
            'language': result.get('language', 'unknown')
        }
    except Exception as e:
        st.error(f"Error processing audio file: {str(e)}")
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass