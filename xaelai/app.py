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

from assistant import get_rag_assistant  # type: ignore

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
    # User identification
    user_id = st.sidebar.text_input("Enter User ID")
    if not user_id:
        st.sidebar.warning("Please enter a User ID to continue.")
        return

    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Chat", "Configuration"])
    user_data_path = os.getenv("USER_DATA_PATH", "/user_data")
    user_dir = os.path.join(user_data_path, user_id)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        st.sidebar.success(f"User directory created at {user_dir}")
    with tab2:
        models = []
        chat_history_dir = os.path.join(user_dir, "chat_history")
        if not os.path.exists(chat_history_dir):
            os.makedirs(chat_history_dir)
        for m in ollama.list()['models']:
            models.append(m["name"])

        default_llm_model = os.getenv("DEFAULT_LLM_MODEL", "llama3")
        llm_model = st.selectbox("Select Model", options=models, index=models.index(default_llm_model) if default_llm_model in models else 0)
        # Model management feature toggle
        feature_model_manager = os.getenv("FEATURE_MODEL_MANAGER", "true").lower() == "true"

        if feature_model_manager:
            with st.expander("Model Management", expanded=False):
                download_model_name = st.text_input("Enter Model Name to Download")
                if st.button("Download Model"):
                    if download_model_name:
                        try:
                            ollama.pull(download_model_name)
                            st.success(f"Model '{download_model_name}' downloaded successfully.")
                        except Exception as e:
                            st.error(f"Failed to download model: {e}")
                    else:
                        st.warning("Please enter a model name to download.")

                if st.button("Delete Model"):
                    try:
                        selected_model = st.session_state["llm_model"]
                        ollama.delete(selected_model)
                        st.success(f"Model '{selected_model}' deleted successfully.")
                    except Exception as e:
                        st.error(f"Failed to delete model: {e}")
    with tab2:
        if "llm_model" not in st.session_state:
            st.session_state["llm_model"] = llm_model
        # Restart the assistant if assistant_type has changed
        elif st.session_state["llm_model"] != llm_model:
            st.session_state["llm_model"] = llm_model
            restart_assistant()

        # Get available embeddings models
        available_embeddings_models = ["nomic-embed-text", "llama3", "openhermes", "phi3"]
        default_embeddings_model = os.getenv("DEFAULT_EMBEDDINGS_MODEL", "nomic-embed-text")
        embeddings_model_input = st.text_input("Enter Embeddings Model", value=default_embeddings_model)
        if embeddings_model_input not in available_embeddings_models:
            st.warning(f"Model '{embeddings_model_input}' is not available. Using default '{default_embeddings_model}'.")
            embeddings_model = default_embeddings_model
        else:
            embeddings_model = embeddings_model_input
        # Set assistant_type in session state
        if "embeddings_model" not in st.session_state:
            st.session_state["embeddings_model"] = embeddings_model
        # Restart the assistant if assistant_type has changed
        elif st.session_state["embeddings_model"] != embeddings_model:
            st.session_state["embeddings_model"] = embeddings_model
            st.session_state["embeddings_model_updated"] = True
            restart_assistant()

    # Get the assistant
    rag_assistant: Assistant
    if "rag_assistant" not in st.session_state or st.session_state["rag_assistant"] is None:
        logger.info(f"---*--- Creating {llm_model} Assistant ---*---")
        rag_assistant = get_rag_assistant(llm_model=llm_model, embeddings_model=embeddings_model)
        st.session_state["rag_assistant"] = rag_assistant
    else:
        rag_assistant = st.session_state["rag_assistant"]

    # Create assistant run (i.e. log to database) and save run_id in session state
    try:
        st.session_state["rag_assistant_run_id"] = rag_assistant.create_run()
    except Exception:
        st.warning("Could not create assistant, is the database running?")
        return

    # Chat name input
    chat_name = st.sidebar.text_input("Chat Name", value="default_chat")
    if "suggested_chat_name" not in st.session_state:
        st.session_state["suggested_chat_name"] = None
    chat_files = [f for f in os.listdir(chat_history_dir) if f.endswith('.json')]
    selected_chat_file = st.sidebar.selectbox("Load Previous Chat", options=chat_files)
    if st.sidebar.button("Load Chat"):
        with open(os.path.join(chat_history_dir, selected_chat_file), 'r') as f:
            st.session_state["messages"] = json.load(f)
        st.sidebar.success(f"Loaded chat from {selected_chat_file}")
    if "messages" not in st.session_state or not st.session_state["messages"]:
        assistant_chat_history = rag_assistant.memory.get_chat_history()
        if len(assistant_chat_history) > 0:
            logger.debug("Loading chat history")
            st.session_state["messages"] = assistant_chat_history
            rag_assistant.memory.set_chat_history(st.session_state["messages"])
        else:
            logger.debug("No chat history found")
            st.session_state["messages"] = [{"role": "assistant", "content": ""}]
            rag_assistant.memory.set_chat_history(st.session_state["messages"])

    # Prompt for user input
    if prompt := st.chat_input():
        st.session_state["messages"].append({"role": "user", "content": prompt})

    # Display existing chat messages
    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Save chat history to a file
    def save_chat_history():
        import json
        from datetime import datetime

        chat_file = os.path.join(chat_history_dir, f"{chat_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(chat_file, 'w') as f:
            json.dump(st.session_state["messages"], f, indent=2)
    # Suggest a chat name after the first user message
    if len(st.session_state["messages"]) == 1 and st.session_state["messages"][0]["role"] == "user":
        first_message = st.session_state["messages"][0]["content"]
        with st.spinner("Suggesting a chat name..."):
            suggested_name = rag_assistant.run(f"Suggest a chat name based on this message: {first_message}")
            st.session_state["suggested_chat_name"] = suggested_name.strip()
            chat_name = st.sidebar.text_input("Chat Name", value=st.session_state["suggested_chat_name"])
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
            save_chat_history()

    # Load knowledge base
    if rag_assistant.knowledge_base:
        # -*- Add websites to knowledge base
        if "url_scrape_key" not in st.session_state:
            st.session_state["url_scrape_key"] = 0

        input_url = st.sidebar.text_input(
            "Add URL to Knowledge Base", type="default", key=st.session_state["url_scrape_key"]
        )
        add_url_button = st.sidebar.button("Add URL")
        if add_url_button:
            if input_url is not None:
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

        # Add PDFs to knowledge base
        if "file_uploader_key" not in st.session_state:
            st.session_state["file_uploader_key"] = 100

        uploaded_file = st.sidebar.file_uploader(
            "Add a PDF :page_facing_up:", type="pdf", key=st.session_state["file_uploader_key"]
        )
        if uploaded_file is not None:
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

    if rag_assistant.knowledge_base and rag_assistant.knowledge_base.vector_db:
        if st.sidebar.button("Clear Knowledge Base"):
            rag_assistant.knowledge_base.vector_db.clear()
            st.sidebar.success("Knowledge base cleared")

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
