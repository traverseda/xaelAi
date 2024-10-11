import os
import streamlit as st

def file_manager_ui():
    """Render the file management UI."""
    st.header("File Manager")

    # Initialize current directory in session state
    if "current_dir" not in st.session_state:
        st.session_state["current_dir"] = os.path.join(st.session_state.get("user_data_path", "/user_data"), st.session_state.get("user_id", "default_user"))
    
    current_dir = st.session_state["current_dir"]
    os.makedirs(current_dir, exist_ok=True)

    # Display current directory and navigation
    st.write(f"Current Directory: {current_dir}")
    if st.button("Go Up"):
        st.session_state["current_dir"] = os.path.dirname(current_dir)
        st.rerun()

    # List directories and files
    entries = os.listdir(current_dir)
    directories = [d for d in entries if os.path.isdir(os.path.join(current_dir, d))]
    files = [f for f in entries if os.path.isfile(os.path.join(current_dir, f))]

    # Directory navigation using buttons
    st.subheader("Directories")
    for directory in directories:
        if st.button(f"Open {directory}"):
            st.session_state["current_dir"] = os.path.join(current_dir, directory)
            st.rerun()

    # File selection and editing using buttons
    st.subheader("Files")
    for file in files:
        if st.button(f"Edit {file}"):
            file_path = os.path.join(current_dir, file)
            with open(file_path, "r") as f:
                file_content = f.read()
            new_content = st.text_area(f"Edit {file}", value=file_content, height=300)
            if st.button(f"Save Changes to {file}"):
                with open(file_path, "w") as f:
                    f.write(new_content)
                st.success(f"Saved changes to {file}")

    # File upload
    uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "json"])
    if uploaded_file:
        with open(os.path.join(current_dir, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {uploaded_file.name}")

    # File deletion
    file_to_delete = st.selectbox("Select a file to delete", options=[""] + files)
    if file_to_delete and st.button("Delete File"):
        os.remove(os.path.join(current_dir, file_to_delete))
        st.success(f"Deleted {file_to_delete}")
