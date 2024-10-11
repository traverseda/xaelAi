import os
from typing import Optional
from datetime import datetime

from phi.assistant import Assistant
from phi.knowledge import AssistantKnowledge
from phi.llm.ollama import Ollama
from phi.embedder.ollama import OllamaEmbedder
from phi.tools.duckduckgo import DuckDuckGo
from phi.vectordb.pgvector import PgVector2
from storage.yaml_storage import YamlStorage
from settings import Settings
from phi.tools.website import WebsiteTools
from phi.tools.arxiv_toolkit import ArxivToolkit
from phi.knowledge.text import TextKnowledgeBase
from phi.embedder.ollama import OllamaEmbedder

db_url = "postgresql+psycopg://ai:ai@pgvector:5432/ai"

ollama_host = os.getenv("OLLAMA_HOST", "ollama")

from tools.utils import utils
from tools.homeassistant import homeassistant_tool

def get_rag_assistant(
    llm_model: str = "llama3",
    embeddings_model: str = "nomic-embed-text",
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Assistant:

    settings = Settings()
    if run_id is None:
        run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    embedder = OllamaEmbedder(model=embeddings_model, dimensions=4096)

    knowledge_base = TextKnowledgeBase(
        path="data/docs",
        # Table name: ai.text_documents
        vector_db=PgVector2(
            collection="text_documents",
            embedder=embedder,
            db_url=db_url,
        ),
    )

    # Set up YAML storage for the assistant
    user_name = settings.get_user_name()  # Assuming there's a method to get the user name
    user_data_dir = os.path.join(settings.default_storage_dir, user_name or "default_user", "chat_history")
    storage = YamlStorage(storage_dir=user_data_dir)
    assistant = Assistant(
        name="local_rag_assistant",
        run_id=run_id,
        user_id=user_id,
        llm=Ollama(model=llm_model, host=ollama_host),
        storage=storage,
        tools=[
            *utils,
            # *homeassistant_tool,
            DuckDuckGo(),
        ],
        show_tool_calls=True,
        debug_mode=debug_mode,
        markdown=True,
        read_chat_history=True,
        prevent_hallucinations=True,
        # add_chat_history_to_messages=True,
        # knowledge_base=knowledge_base,
        add_references_to_prompt=True,
        add_datetime_to_instructions=True,
        )
    # assistant.knowledge_base.load(recreate=False)

    return assistant


