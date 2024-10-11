import os
import yaml
from typing import Any, Dict, Optional

class YamlStorage:
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_file_path(self, key: str) -> str:
        return os.path.join(self.storage_dir, f"{key}.yaml")

    def save(self, key: str, data: Dict[str, Any]) -> None:
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
