import os
import json
import shutil
from typing import List

import streamlit as st
from phi.assistant import Assistant
from phi.document import Document
from phi.document.reader.pdf import PDFReader
from phi.document.reader.website import WebsiteReader
from phi.utils.log import logger

from settings import Settings
from chat_history import ChatHistory
from assistant import get_rag_assistant  # type: ignore

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
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Main", "Settings"])

    with tab1:
        # User identification
        user_id = st.sidebar.text_input("Enter User ID", value=settings.get_user_id())
        settings.set_user_id(user_id)
        if not user_id:
            st.sidebar.warning("Please enter a User ID to continue.")
            return

        # Initialize chat history
        from chat_history import ChatHistory
        chat_name = st.sidebar.text_input("Chat Name", value="unnamed chat")
        chat_history = initialize_chat_history(user_id, chat_name)


        # Embeddings model selection
        embeddings_model = select_embeddings_model()

        # Retrieve llm_model from session state
        llm_model = st.session_state.get("llm_model", settings.default_llm_model)

        # Initialize or retrieve the assistant
        rag_assistant = initialize_assistant(llm_model, embeddings_model)

        # Create assistant run and handle chat messages
        handle_chat_interaction(rag_assistant)

        # Load and manage knowledge base
        manage_knowledge_base(rag_assistant)

        # Handle assistant runs
        handle_assistant_runs(rag_assistant, llm_model, embeddings_model)

    with tab2:
        # Render settings UI
        settings.render_settings_ui()
        # Model selection and management
        llm_model = select_llm_model()
        manage_models(llm_model)


def initialize_chat_history(user_id: str, chat_name: str) -> ChatHistory:
    """Initialize chat history for the user."""
    user_data_path = settings.user_data_path
    user_dir = os.path.join(user_data_path, user_id)
    os.makedirs(user_dir, exist_ok=True)
    chat_history = ChatHistory(settings=settings, chat_name=chat_name)
    if "chat_name" not in st.session_state:
        st.session_state["chat_name"] = chat_name
    elif st.session_state["chat_name"] != chat_name:
        chat_history.rename(chat_name)
        st.session_state["chat_name"] = chat_name
    return chat_history


def select_llm_model() -> str:
    """Select the LLM model from available options."""
    models = [m["name"] for m in ollama.list()['models']]
    default_llm_model = settings.default_llm_model
    llm_model = st.selectbox("Select Model", options=models, index=models.index(default_llm_model) if default_llm_model in models else 0)
    if "llm_model" not in st.session_state or st.session_state["llm_model"] != llm_model:
        st.session_state["llm_model"] = llm_model
        restart_assistant()
    return llm_model


def manage_models(llm_model: str) -> None:
    """Manage model download and deletion."""
    if settings.feature_model_manager:
        with st.expander("Model Management", expanded=False):
            download_model_name = st.text_input("Enter Model Name to Download")
            if st.button("Download Model"):
                download_model(download_model_name)
            if st.button("Delete Model"):
                delete_model(llm_model)


def download_model(model_name: str) -> None:
    """Download a model by name."""
    if model_name:
        try:
            ollama.pull(model_name)
            st.success(f"Model '{model_name}' downloaded successfully.")
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
    available_embeddings_models = ["nomic-embed-text", "llama3", "openhermes", "phi3"]
    default_embeddings_model = settings.default_embeddings_model
    embeddings_model_input = st.text_input("Enter Embeddings Model", value=default_embeddings_model)
    embeddings_model = default_embeddings_model if embeddings_model_input not in available_embeddings_models else embeddings_model_input
    if "embeddings_model" not in st.session_state:
        st.session_state["embeddings_model"] = embeddings_model
    elif st.session_state["embeddings_model"] != embeddings_model:
        st.session_state["embeddings_model"] = embeddings_model
        st.session_state["embeddings_model_updated"] = True
        restart_assistant()
    return embeddings_model


def initialize_assistant(llm_model: str, embeddings_model: str) -> Assistant:
    """Initialize or retrieve the RAG assistant."""
    if "rag_assistant" not in st.session_state or st.session_state["rag_assistant"] is None:
        logger.info(f"---*--- Creating {llm_model} Assistant ---*---")
        rag_assistant = get_rag_assistant(llm_model=llm_model, embeddings_model=embeddings_model)
        st.session_state["rag_assistant"] = rag_assistant
    else:
        rag_assistant = st.session_state["rag_assistant"]
    return rag_assistant


def handle_chat_interaction(rag_assistant: Assistant) -> None:
    """Handle chat interactions with the assistant."""
    try:
        st.session_state["rag_assistant_run_id"] = rag_assistant.create_run()
    except Exception:
        st.warning("Could not create assistant, is the database running?")
        return

    if "messages" not in st.session_state or not st.session_state["messages"]:
        assistant_chat_history = rag_assistant.memory.get_chat_history()
        st.session_state["messages"] = assistant_chat_history if assistant_chat_history else [{"role": "assistant", "content": ""}]

    if prompt := st.chat_input():
        st.session_state["messages"].append({"role": "user", "content": prompt})

    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])

    last_message = st.session_state["messages"][-1]
    if last_message.get("role") == "user":
        question = last_message["content"]
        with st.chat_message("assistant"):
            response = ""
            resp_container = st.empty()
            for delta in rag_assistant.run(question):
                response += delta  # type: ignore
                resp_container.markdown(response)
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


def handle_assistant_runs(rag_assistant: Assistant, llm_model: str, embeddings_model: str) -> None:
    """Handle different assistant runs and allow for new runs."""
    if rag_assistant.storage:
        rag_assistant_run_ids: List[str] = rag_assistant.storage.get_all_run_ids()
        new_rag_assistant_run_id = st.sidebar.selectbox("Run ID", options=rag_assistant_run_ids)
        if st.session_state["rag_assistant_run_id"] != new_rag_assistant_run_id:
            logger.info(f"---*--- Loading {llm_model} run: {new_rag_assistant_run_id} ---*---")
            st.session_state["rag_assistant"] = get_rag_assistant(
                llm_model=llm_model, embeddings_model=embeddings_model, run_id=new_rag_assistant_run_id
            )
            st.rerun()

    if st.sidebar.button("New Run"):
        restart_assistant()


main()
