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
        st.subheader("Environment Variables (Read-Only)")
        st.text(f"Default Storage Directory: {self.default_storage_dir}")
        st.text(f"User Data Path: {self.user_data_path}")
        st.text(f"Default LLM Model: {self.default_llm_model}")
        st.text(f"Default Embeddings Model: {self.default_embeddings_model}")
        st.text(f"Feature Model Manager Enabled: {self.feature_model_manager}")

    def set_user_id(self, user_id):
        # Set user_id in session state
        st.session_state["user_id"] = user_id
