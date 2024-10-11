from typing import Optional, List
from pathlib import Path
import yaml
from phi.assistant.run import AssistantRun

from phi.storage.assistant.base import AssistantStorage

class InMemoryStorage(AssistantStorage):
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create(self, run_id: str) -> None:
        """Create a new YAML file for the given run_id."""
        file_path = self.storage_dir / f"{run_id}.yaml"
        file_path.touch(exist_ok=True)

    def get_all_run_ids(self, user_id: Optional[str] = None) -> List[str]:
        """Get all run IDs from the storage."""
        return [f.stem for f in self.storage_dir.glob("*.yaml")]

    def get_all_runs(self, user_id: Optional[str] = None) -> List[AssistantRun]:
        """Get all runs from the storage."""
        runs = []
        for file_path in self.storage_dir.glob("*.yaml"):
            with file_path.open('r') as file:
                data = yaml.safe_load(file)
                runs.append(AssistantRun(**data))
        return runs

    def read(self, run_id: str) -> Optional[AssistantRun]:
        """Read an entry from the storage."""
        file_path = self.storage_dir / f"{run_id}.yaml"
        if file_path.exists():
            with file_path.open('r') as file:
                data = yaml.safe_load(file)
                return AssistantRun(**data)
        return None

    def upsert(self, row: AssistantRun) -> Optional[AssistantRun]:
        """Update or insert an entry in the storage."""
        file_path = self.storage_dir / f"{row.run_id}.yaml"
        with file_path.open('w') as file:
            yaml.safe_dump(row.__dict__, file)
        return row
        return row

    def delete(self, run_id: str) -> None:
        """Delete an entry from the storage."""
        file_path = self.storage_dir / f"{run_id}.yaml"
        if file_path.exists():
            file_path.unlink()
