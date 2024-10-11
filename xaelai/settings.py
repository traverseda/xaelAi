import os
import streamlit as st

class Settings:
    def __init__(self):
        # Load settings from environment variables
        self.user_data_path = os.getenv("USER_DATA_PATH", "/user_data")
        self.default_llm_model = os.getenv("DEFAULT_LLM_MODEL", "llama3")
        self.default_embeddings_model = os.getenv("DEFAULT_EMBEDDINGS_MODEL", "nomic-embed-text")
        self.feature_model_manager = os.getenv("FEATURE_MODEL_MANAGER", "true").lower() == "true"

    def get_user_id(self):
        # Load user_id from session state
        return st.session_state.get("user_id", "")

    def set_user_id(self, user_id):
        # Set user_id in session state
        st.session_state["user_id"] = user_id