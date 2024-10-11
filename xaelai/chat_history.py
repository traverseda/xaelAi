from settings import Settings
from datetime import datetime

class ChatHistory:
    def __init__(self, settings: Settings, chat_name: str = "unnamed chat"):
        self.user_data_path = settings.user_data_path
        self.file_name = self._generate_file_name(chat_name)

    def rename(self, new_chat_name: str):
        """Rename the chat history file, keeping the date the same but changing the name."""
        old_file_path = os.path.join(self.user_data_path, self.file_name)
        new_file_name = self._generate_file_name(new_chat_name)
        new_file_path = os.path.join(self.user_data_path, new_file_name)
        os.rename(old_file_path, new_file_path)
        self.file_name = new_file_name
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
        return f"{timestamp}-{chat_name}.json"
    def __init__(self, file_name: str, user_data_path: str):
        self.user_data_path = user_data_path
        self.file_name = file_name
