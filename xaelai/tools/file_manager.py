import os
from pathlib import Path

class FileManager:
    def __init__(self, base_dir: str = str(Path.home())):
        self.base_dir = Path(base_dir)

    def list_files(self):
        """List all files in the base directory."""
        return [f for f in self.base_dir.iterdir() if f.is_file()]

    def read_file(self, file_name: str) -> str:
        """Read the contents of a file."""
        file_path = self.base_dir / file_name
        if file_path.exists() and file_path.is_file():
            with file_path.open('r') as file:
                return file.read()
        else:
            raise FileNotFoundError(f"File {file_name} not found in {self.base_dir}")

    def delete_file(self, file_name: str) -> None:
        """Delete a file."""
        file_path = self.base_dir / file_name
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
        else:
            raise FileNotFoundError(f"File {file_name} not found in {self.base_dir}")
