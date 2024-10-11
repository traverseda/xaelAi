import os
import streamlit as st

class Settings:
    def __init__(self):
        # Load settings from environment variables
        self.user_data_path = os.getenv("USER_DATA_PATH", "/user_data")
        self.default_llm_model = os.getenv("DEFAULT_LLM_MODEL", "llama3")
        self.default_embeddings_model = os.getenv("DEFAULT_EMBEDDINGS_MODEL", "nomic-embed-text")
        self.feature_model_manager = os.getenv("FEATURE_MODEL_MANAGER", "true").lower() == "true"

    def render_settings_ui(self):
        """Render the settings UI in Streamlit."""
        st.sidebar.header("Settings")
        self.user_data_path = st.sidebar.text_input("User Data Path", value=self.user_data_path)
        self.default_llm_model = st.sidebar.text_input("Default LLM Model", value=self.default_llm_model)
        self.default_embeddings_model = st.sidebar.text_input("Default Embeddings Model", value=self.default_embeddings_model)
        self.feature_model_manager = st.sidebar.checkbox("Enable Model Manager", value=self.feature_model_manager)
        # Load user_id from session state
        return st.session_state.get("user_id", "")

    def set_user_id(self, user_id):
        # Set user_id in session state
        st.session_state["user_id"] = user_id
