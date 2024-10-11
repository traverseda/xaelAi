from typing import Any, Dict, Optional, List

from phi.storage.assistant.base import AssistantStorage

class InMemoryStorage(AssistantStorage):
    def __init__(self):
        self.storage = {}

    def create(self, key: str, data: Dict[str, Any]) -> None:
        """Create a new entry in the storage."""
        self.storage[key] = data

    def get_all_run_ids(self) -> List[str]:
        """Get all run IDs from the storage."""
        return list(self.storage.keys())

    def get_all_runs(self) -> List[Dict[str, Any]]:
        """Get all runs from the storage."""
        return list(self.storage.values())

    def read(self, key: str) -> Optional[Dict[str, Any]]:
        """Read an entry from the storage."""
        return self.storage.get(key)

    def upsert(self, key: str, data: Dict[str, Any]) -> None:
        """Update or insert an entry in the storage."""
        self.storage[key] = data

    def delete(self, key: str) -> None:
        """Delete an entry from the storage."""
        if key in self.storage:
            del self.storage[key]
