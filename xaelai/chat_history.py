from settings import Settings
from datetime import datetime

class ChatHistory:
    def __init__(self, chat_name: str = "unnamed chat", settings: Settings):
        self.user_data_path = settings.user_data_path
        self.file_name = self._generate_file_name(chat_name)

    def _generate_file_name(self, chat_name: str) -> str:
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
        return f"{timestamp}-{chat_name}.json"
    def __init__(self, file_name: str, user_data_path: str):
        self.user_data_path = user_data_path
        self.file_name = file_name