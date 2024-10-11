from typing import Optional, List
from upath import UPath
import yaml
import json
from phi.assistant.run import AssistantRun

from phi.storage.assistant.base import AssistantStorage

class GenericFileStorageBase(AssistantStorage):
    """
    GenericFileStorageBase is a base class for managing assistant runs using file storage.
    Subclasses should implement specific serialization and deserialization methods.
    """

    def __init__(self, storage_dir: str, file_extension: str):
        self.storage_dir = UPath(storage_dir)
        self.file_extension = file_extension
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create(self, run_id: str) -> None:
        """
        Create a new file for the given run_id.

        :param run_id: The unique identifier for the run.
        """
        file_path = self.storage_dir / f"{run_id}.{self.file_extension}"
        file_path.touch(exist_ok=True)

    def get_all_run_ids(self, user_id: Optional[str] = None) -> List[str]:
        """
        Get all run IDs from the storage.

        :param user_id: Optional user identifier to filter runs.
        :return: A list of run IDs.
        """
        return [f.stem for f in self.storage_dir.glob(f"*.{self.file_extension}")]

    def get_all_runs(self, user_id: Optional[str] = None) -> List[AssistantRun]:
        """
        Get all runs from the storage.

        :param user_id: Optional user identifier to filter runs.
        :return: A list of AssistantRun objects.
        """
        runs = []
        for file_path in self.storage_dir.glob(f"*.{self.file_extension}"):
            with file_path.open('r') as file:
                data = self.deserialize(file)
                runs.append(AssistantRun(**data))
        return runs

    def read(self, run_id: str) -> Optional[AssistantRun]:
        """
        Read an entry from the storage.

        :param run_id: The unique identifier for the run.
        :return: An AssistantRun object if found, otherwise None.
        """
        file_path = self.storage_dir / f"{run_id}.{self.file_extension}"
        if file_path.exists():
            with file_path.open('r') as file:
                data = self.deserialize(file)
                return AssistantRun(**data)
        return None

    def upsert(self, row: AssistantRun) -> Optional[AssistantRun]:
        """
        Update or insert an entry in the storage.

        :param row: The AssistantRun object to upsert.
        :return: The upserted AssistantRun object.
        """
        file_path = self.storage_dir / f"{row.run_id}.{self.file_extension}"
        with file_path.open('w') as file:
            self.serialize(row.__dict__, file)
        return row

    def delete(self, run_id: str) -> None:
        """
        Delete an entry from the storage.

        :param run_id: The unique identifier for the run to delete.
        """
        file_path = self.storage_dir / f"{run_id}.{self.file_extension}"
        if file_path.exists():
            file_path.unlink()

    def serialize(self, data: dict, file) -> None:
        """
        Serialize data to a file. To be implemented by subclasses.

        :param data: The data to serialize.
        :param file: The file object to write to.
        """
        raise NotImplementedError

    def deserialize(self, file) -> dict:
        """
        Deserialize data from a file. To be implemented by subclasses.

        :param file: The file object to read from.
        :return: The deserialized data.
        """
        raise NotImplementedError
    def __init__(self, storage_dir: str):
        self.storage_dir = UPath(storage_dir)
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
class YamlStorage(GenericFileStorageBase):
    """
    YamlStorage is a subclass of GenericFileStorageBase that uses YAML for serialization.
    """

    def __init__(self, storage_dir: str):
        super().__init__(storage_dir, "yaml")

    def serialize(self, data: dict, file) -> None:
        yaml.safe_dump(data, file)

    def deserialize(self, file) -> dict:
        return yaml.safe_load(file)


class JsonStorage(GenericFileStorageBase):
    """
    JsonStorage is a subclass of GenericFileStorageBase that uses JSON for serialization.
    """

    def __init__(self, storage_dir: str):
        super().__init__(storage_dir, "json")

    def serialize(self, data: dict, file) -> None:
        json.dump(data, file)

    def deserialize(self, file) -> dict:
        return json.load(file)
