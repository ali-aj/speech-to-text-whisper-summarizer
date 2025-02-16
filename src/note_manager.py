import streamlit as st

class NoteManager:
    def __init__(self):
        if "notes" not in st.session_state:
            st.session_state["notes"] = []

    def add_note(self, note):
        st.session_state["notes"].append(note)

    def delete_note(self, index):
        if 0 <= index < len(st.session_state["notes"]):
            st.session_state["notes"].pop(index)
            return True
        return False

    def get_notes(self):
        return st.session_state.get("notes", [])