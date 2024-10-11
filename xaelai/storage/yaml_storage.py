from typing import Any, Dict, Optional, List
from phi.assistant.run import AssistantRun

from phi.storage.assistant.base import AssistantStorage

class InMemoryStorage(AssistantStorage):
    def __init__(self):
        self.storage = {}

    def create(self, run_id: str) -> None:
        """Create a new entry in the storage."""
        self.storage[run_id] = {}

    def get_all_run_ids(self, user_id: Optional[str] = None) -> List[str]:
        """Get all run IDs from the storage."""
        return list(self.storage.keys())

    def get_all_runs(self, user_id: Optional[str] = None) -> List[AssistantRun]:
        """Get all runs from the storage."""
        return [AssistantRun(**data) for data in self.storage.values()]

    def read(self, run_id: str) -> Optional[AssistantRun]:
        """Read an entry from the storage."""
        data = self.storage.get(run_id)
        return AssistantRun(**data) if data else None

    def upsert(self, row: AssistantRun) -> Optional[AssistantRun]:
        """Update or insert an entry in the storage."""
        self.storage[run.run_id] = run.__dict__
        return run

    def delete(self, run_id: str) -> None:
        """Delete an entry from the storage."""
        if run_id in self.storage:
            del self.storage[run_id]
