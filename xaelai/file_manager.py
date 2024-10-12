import os
import streamlit as st
from settings import Settings

def file_manager_ui():
    """Render the file management UI."""
    st.header("File Manager")

    # Use streamlit-file-browser for file management
    settings = Settings()
    user_id = st.session_state.get("user_id", "default_user")
    user_data_path = settings.get_user_data_dir(user_id)
    user_data_path.mkdir(parents=True, exist_ok=True)

    event = st_file_browser(
        path=user_data_path,
        key="file_browser",
        show_choose_file=True,
        show_delete_file=True,
        show_upload_file=True,
        show_new_folder=True
    )
    st.write(event)
