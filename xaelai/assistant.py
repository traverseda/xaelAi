import os
from typing import Optional

from phi.assistant import Assistant
from phi.knowledge import AssistantKnowledge
from phi.llm.ollama import Ollama
from phi.embedder.ollama import OllamaEmbedder
from phi.tools.duckduckgo import DuckDuckGo
from phi.vectordb.pgvector import PgVector2
from phi.storage.assistant.postgres import PgAssistantStorage
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

    """Get a Local RAG Assistant."""
    assistant = Assistant(
        name="local_rag_assistant",
        run_id=run_id,
        user_id=user_id,
        llm=Ollama(model=llm_model, host=ollama_host),
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
        knowledge_base=knowledge_base,
        add_references_to_prompt=True,
        add_datetime_to_instructions=True,
        )
    assistant.knowledge_base.load(recreate=False)

    return assistant


