import os
import streamlit as st

class Settings:
    def __init__(self):
        self.default_storage_dir = os.getenv("DEFAULT_STORAGE_DIR", "/user_data")
        # Load settings from environment variables
        self.user_data_path = os.getenv("USER_DATA_PATH", "local:///user_data")
        self.default_llm_model = os.getenv("DEFAULT_LLM_MODEL", "llama3.1:latest")
        self.default_embeddings_model = os.getenv("DEFAULT_EMBEDDINGS_MODEL", "nomic-embed-text:latest")
        self.feature_model_manager = os.getenv("FEATURE_MODEL_MANAGER", "true").lower() == "true"

    def get_user_id(self):
        """Retrieve the user ID from the session state."""
        return st.session_state.get("user_id", "")

    def render_settings_ui(self):
        """Render the settings UI in Streamlit."""
        st.header("Settings")

    def set_user_id(self, user_id):
        # Set user_id in session state
        st.session_state["user_id"] = user_id
