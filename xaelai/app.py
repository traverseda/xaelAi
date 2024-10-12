import os
import json
import shutil
from typing import List
from datetime import datetime

import streamlit as st
from phi.assistant import Assistant
from phi.document import Document
from phi.document.reader.pdf import PDFReader
from phi.document.reader.website import WebsiteReader
from phi.utils.log import logger

from settings import Settings
from storage.yaml_storage import YamlStorage
from assistant import get_rag_assistant  # type: ignore
from file_manager import file_manager_ui

settings = Settings()

from ollama import Client

ollama_host = os.getenv("OLLAMA_HOST", "ollama")
ollama = Client(host=ollama_host)

st.set_page_config(
    page_title="Xael AI",
    page_icon=":large_blue_circle:",
)
# st.title("Local RAG with Ollama and PgVector")
# st.markdown("##### :orange_heart: built using [phidata](https://github.com/phidatahq/phidata)")


def restart_assistant():
    st.session_state["rag_assistant"] = None
    st.session_state["rag_assistant_run_id"] = None
    if "url_scrape_key" in st.session_state:
        st.session_state["url_scrape_key"] += 1
    if "file_uploader_key" in st.session_state:
        st.session_state["file_uploader_key"] += 1
    st.rerun()


def main() -> None:
    """Main function to run the Xael AI application."""

    main_tab, file_manager_tab, settings_tab = st.tabs(["Main", "File Manager", "Settings"])

    with main_tab:
        # Retrieve headers and access the "Username"
        headers = st.context.headers
        username = headers.get("Username", None)
        if username is None:
            st.sidebar.error("Username is missing. Please ensure you are properly authenticated.")
            raise ValueError("Username is missing. Please ensure you are properly authenticated.")
        # Authenticate the user or perform other actions
        st.sidebar.success(f"User '{username}' authenticated.")

        # Display previous sessions
        display_previous_sessions()

        # Retrieve llm_model from session state
        llm_model = st.session_state.get("llm_model", settings.default_llm_model)

        # Embeddings model selection
        embeddings_model = st.session_state.get("embeddings_model", settings.default_embeddings_model)

        # Initialize or retrieve the assistant
        rag_assistant = initialize_assistant(llm_model, embeddings_model)

        # Create assistant run and handle chat messages
        handle_chat_interaction(rag_assistant)

        # Load and manage knowledge base
        manage_knowledge_base(rag_assistant)

        # Handle assistant runs
        handle_assistant_runs(rag_assistant, llm_model, embeddings_model)

    with settings_tab:
        # Render settings UI
        settings.render_settings_ui()
        # Embeddings model selection
        embeddings_model = select_embeddings_model()

        # Model selection and management
        llm_model = select_llm_model()
        manage_models(llm_model)


    with file_manager_tab:
        file_manager_ui()


def select_llm_model() -> str:
    """Select the LLM model from available options."""
    models = [m["name"] for m in ollama.list()['models']]
    default_llm_model = settings.default_llm_model
    if default_llm_model not in models:
        st.warning(f"Default model '{default_llm_model}' not found. Downloading...")
        download_model(default_llm_model)
        models = [m["name"] for m in ollama.list()['models']]  # Refresh the model list

    llm_model = st.selectbox("Select Model", options=models, index=models.index(default_llm_model))
    if "llm_model" not in st.session_state or st.session_state["llm_model"] != llm_model:
        st.session_state["llm_model"] = llm_model
        restart_assistant()
    return llm_model


def manage_models(llm_model: str) -> None:
    """Manage model download and deletion."""
    if settings.feature_model_manager:
        download_model_name = st.text_input("Enter Model Name to Download")
        if st.button("Download Model"):
            download_model(download_model_name)
        if st.button("Delete Model"):
            delete_model(llm_model)


download_progress = {}

def download_model(model_name: str) -> None:
    """Download a model by name with resumable progress."""
    if model_name:
        try:
            if model_name not in download_progress:
                download_progress[model_name] = 0

            with st.spinner(f"Downloading model '{model_name}'..."):
                progress_bar = st.progress(0)
                current_digest = ''
                progress_message = st.empty()
                total = 0

                for progress in ollama.pull(model_name, stream=True):
                    digest = progress.get('digest', '')
                    if digest != current_digest:
                        current_digest = digest
                        total = progress.get('total', 0)

                    if not digest:
                        st.write(progress.get('status'))
                        continue

                    completed = progress.get('completed', 0)
                    if total > 0:
                        progress_bar.progress(completed / total)
                        completed_gb = completed / (1024 ** 3)
                        total_gb = total / (1024 ** 3)
                        progress_message.write(f"Downloaded {completed_gb:.2f} GB of {total_gb:.2f} GB ({completed / total:.2%})")

            st.success(f"Model '{model_name}' downloaded successfully.")
            del download_progress[model_name]
        except Exception as e:
            st.error(f"Failed to download model: {e}")
    else:
        st.warning("Please enter a model name to download.")


def delete_model(model_name: str) -> None:
    """Delete a model by name."""
    try:
        ollama.delete(model_name)
        st.success(f"Model '{model_name}' deleted successfully.")
    except Exception as e:
        st.error(f"Failed to delete model: {e}")


def select_embeddings_model() -> str:
    """Select the embeddings model from available options."""
    models = [m["name"] for m in ollama.list()['models']]
    default_embeddings_model = settings.default_embeddings_model
    if default_embeddings_model not in models:
        st.warning(f"Default embeddings model '{default_embeddings_model}' not found. Downloading...")
        download_model(default_embeddings_model)
        models = [m["name"] for m in ollama.list()['models']]  # Refresh the model list

    embeddings_model = st.selectbox("Select Embeddings Model", options=models, index=models.index(default_embeddings_model))
    if "embeddings_model" not in st.session_state or st.session_state["embeddings_model"] != embeddings_model:
        st.session_state["embeddings_model"] = embeddings_model
        restart_assistant()
    return embeddings_model


def initialize_assistant(llm_model: str, embeddings_model: str) -> Assistant:
    """Initialize or retrieve the RAG assistant."""
    if "rag_assistant_run_id" not in st.session_state or st.session_state["rag_assistant_run_id"] is None:
        st.session_state["rag_assistant_run_id"] = datetime.now().isoformat()
        logger.info(f"---*--- Creating {llm_model} Assistant ---*---")
        rag_assistant = get_rag_assistant(llm_model=llm_model, embeddings_model=embeddings_model)
        st.session_state["rag_assistant"] = rag_assistant
    elif "rag_assistant" in st.session_state:
        rag_assistant = st.session_state["rag_assistant"]
    else:
        rag_assistant = get_rag_assistant(llm_model=llm_model, embeddings_model=embeddings_model)
        st.session_state["rag_assistant"] = rag_assistant
    return rag_assistant


def handle_chat_interaction(rag_assistant: Assistant) -> None:
    """Handle chat interactions with the assistant."""
    # Initialize chat history if not present
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display existing messages
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Input for new message
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to session state
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Get response from assistant
        with st.chat_message("assistant"):
            response = ""
            resp_container = st.empty()
            for delta in rag_assistant.run(prompt):
                response += delta  # type: ignore
                resp_container.markdown(response)
            # Add assistant response to session state
            st.session_state["messages"].append({"role": "assistant", "content": response})



def manage_knowledge_base(rag_assistant: Assistant) -> None:
    """Manage the knowledge base by adding URLs and PDFs."""
    if rag_assistant.knowledge_base:
        add_urls_to_knowledge_base(rag_assistant)
        add_pdfs_to_knowledge_base(rag_assistant)

    if rag_assistant.knowledge_base and rag_assistant.knowledge_base.vector_db:
        if st.sidebar.button("Clear Knowledge Base"):
            rag_assistant.knowledge_base.vector_db.clear()
            st.sidebar.success("Knowledge base cleared")


def add_urls_to_knowledge_base(rag_assistant: Assistant) -> None:
    """Add URLs to the knowledge base."""
    if "url_scrape_key" not in st.session_state:
        st.session_state["url_scrape_key"] = 0

    input_url = st.sidebar.text_input("Add URL to Knowledge Base", type="default", key=st.session_state["url_scrape_key"])
    if st.sidebar.button("Add URL") and input_url:
        alert = st.sidebar.info("Processing URLs...", icon="ℹ️")
        if f"{input_url}_scraped" not in st.session_state:
            scraper = WebsiteReader(max_links=2, max_depth=1)
            web_documents: List[Document] = scraper.read(input_url)
            if web_documents:
                rag_assistant.knowledge_base.load_documents(web_documents, upsert=True)
            else:
                st.sidebar.error("Could not read website")
            st.session_state[f"{input_url}_uploaded"] = True
        alert.empty()


def add_pdfs_to_knowledge_base(rag_assistant: Assistant) -> None:
    """Add PDFs to the knowledge base."""
    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 100

    uploaded_file = st.sidebar.file_uploader("Add a PDF :page_facing_up:", type="pdf", key=st.session_state["file_uploader_key"])
    if uploaded_file:
        alert = st.sidebar.info("Processing PDF...", icon="🧠")
        rag_name = uploaded_file.name.split(".")[0]
        if f"{rag_name}_uploaded" not in st.session_state:
            reader = PDFReader()
            rag_documents: List[Document] = reader.read(uploaded_file)
            if rag_documents:
                rag_assistant.knowledge_base.load_documents(rag_documents, upsert=True)
            else:
                st.sidebar.error("Could not read PDF")
            st.session_state[f"{rag_name}_uploaded"] = True
        alert.empty()


def display_previous_sessions() -> None:
    """Display previous sessions in the sidebar and allow restoring them."""
    user_id = settings.get_user_id()
    user_data_dir = os.path.join(settings.default_storage_dir, user_id or "default_user", "chat_history")
    storage = YamlStorage(storage_dir=user_data_dir)
    session_ids = storage.get_all_run_ids()
    session_details = [(session_id, storage.read(session_id)) for session_id in session_ids]

    if session_ids:
        session_options = [
            f"{session.run_name} - {session.run_id.split('T')[0]}" if session else session_id
            for session_id, session in session_details
        ]
        selected_index = st.sidebar.selectbox("Restore Session", options=range(len(session_options)), format_func=lambda i: session_options[i])
        selected_session = session_ids[selected_index]
        selected_session_data = session_details[selected_index][1]

        if selected_session_data:
            new_run_name = st.sidebar.text_input("Update Run Name", value=selected_session_data.run_name)
            if st.sidebar.button("Update Name") and new_run_name:
                selected_session_data.run_name = new_run_name
                storage.upsert(selected_session_data)
                st.sidebar.success("Run name updated successfully.")
                
            if st.sidebar.button("Restore"):
                st.session_state["rag_assistant_run_id"] = selected_session
                st.session_state["rag_assistant"] = None
                st.session_state["messages"] = getattr(selected_session_data, "messages", [])
                st.rerun()
        else:
            st.sidebar.warning("Selected session data is not available.")

def handle_assistant_runs(rag_assistant: Assistant, llm_model: str, embeddings_model: str) -> None:
    """Handle different assistant runs and allow for new runs."""

    if st.sidebar.button("New Run"):
        restart_assistant()


main()
