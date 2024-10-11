import os
import streamlit as st
from streamlit_file_browser import st_file_browser

def file_manager_ui():
    """Render the file management UI."""
    st.header("File Manager")

    # Use streamlit-file-browser for file management
    user_data_path = os.path.join(st.session_state.get("user_data_path", "/user_data"), st.session_state.get("user_id", "default_user"))
    os.makedirs(user_data_path, exist_ok=True)

    event = st_file_browser(
        path=user_data_path,
        key="file_browser",
        show_choose_file=True,
        show_delete_file=True,
        show_upload_file=True,
        show_new_folder=True
    )
    st.write(event)
