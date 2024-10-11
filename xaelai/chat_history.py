from settings import Settings

class ChatHistory:
    def __init__(self, file_name: str, settings: Settings):
        self.user_data_path = settings.user_data_path
        self.file_name = file_name
    def __init__(self, file_name: str, user_data_path: str):
        self.user_data_path = user_data_path
        self.file_name = file_name
