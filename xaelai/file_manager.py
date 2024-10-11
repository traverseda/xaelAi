import os
import streamlit as st

def file_manager_ui():
    """Render the file management UI."""
    st.header("File Manager")

    # Display files in the user data directory
    user_data_path = st.session_state.get("user_data_path", "/user_data")
    files = os.listdir(user_data_path)
    st.write("Files in user data directory:")
    for file in files:
        st.write(file)

    # File upload
    uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "json"])
    if uploaded_file:
        with open(os.path.join(user_data_path, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {uploaded_file.name}")

    # File deletion
    file_to_delete = st.selectbox("Select a file to delete", options=files)
    if st.button("Delete File"):
        os.remove(os.path.join(user_data_path, file_to_delete))
        st.success(f"Deleted {file_to_delete}")
