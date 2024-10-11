import os
import yaml
from typing import Any, Dict, Optional, List

from phi.storage.assistant.base import AssistantStorage

class YamlStorage(AssistantStorage):
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_file_path(self, key: str) -> str:
        return os.path.join(self.storage_dir, f"{key}.yaml")

    def create(self, key: str, data: Dict[str, Any]) -> None:
        """Create a new entry in the storage."""
        self.save(key, data)

    def get_all_run_ids(self) -> List[str]:
        """Get all run IDs from the storage."""
        return [f.stem for f in os.scandir(self.storage_dir) if f.is_file() and f.name.endswith('.yaml')]

    def get_all_runs(self) -> List[Dict[str, Any]]:
        """Get all runs from the storage."""
        return [self.load(f.stem) for f in os.scandir(self.storage_dir) if f.is_file() and f.name.endswith('.yaml')]

    def read(self, key: str) -> Optional[Dict[str, Any]]:
        """Read an entry from the storage."""
        return self.load(key)

    def upsert(self, key: str, data: Dict[str, Any]) -> None:
        """Update or insert an entry in the storage."""
        file_path = self._get_file_path(key)
        with open(file_path, 'w') as file:
            yaml.dump(data, file)

    def load(self, key: str) -> Optional[Dict[str, Any]]:
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def delete(self, key: str) -> None:
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            os.remove(file_path)
