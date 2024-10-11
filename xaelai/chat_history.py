from pathlib import Path
from settings import Settings
from datetime import datetime

class ChatHistory:
    def __init__(self, settings: Settings, chat_name: str = "unnamed chat"):
        self.user_data_path = Path(settings.user_data_path)
        self.chat_history_dir = self.user_data_path / "chat_history"
        self.chat_history_dir.mkdir(parents=True, exist_ok=True)
        self.file_name = self._generate_file_name(chat_name)

    def rename(self, new_chat_name: str):
        """Rename the chat history file, keeping the date the same but changing the name."""
        old_file_path = self.chat_history_dir / self.file_name
        new_file_name = self._generate_file_name(new_chat_name)
        new_file_path = self.chat_history_dir / new_file_name

        # Assert that the file operations are within the chat_history directory
        assert old_file_path.is_relative_to(self.chat_history_dir)
        assert new_file_path.is_relative_to(self.chat_history_dir)

        old_file_path.rename(new_file_path)
        self.file_name = new_file_name
    def __init__(self, settings: Settings, chat_name: str = "unnamed chat"):
        self.user_data_path = Path(settings.user_data_path)
        self.chat_history_dir = self.user_data_path / "chat_history"
        self.chat_history_dir.mkdir(parents=True, exist_ok=True)
        self.file_name = self._generate_file_name(chat_name)
