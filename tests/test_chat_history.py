import unittest
from pathlib import Path
from xaelai.chat_history import ChatHistory
from xaelai.settings import Settings

class TestChatHistory(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()
        self.chat_name = "test_chat"
        self.chat_history = ChatHistory(settings=self.settings, chat_name=self.chat_name)

    def test_generate_file_name(self):
        file_name = self.chat_history._generate_file_name(self.chat_name)
        self.assertTrue(file_name.startswith(self.chat_name))
        self.assertTrue(file_name.endswith(".json"))

    def test_rename(self):
        new_chat_name = "renamed_chat"
        old_file_name = self.chat_history.file_name
        self.chat_history.rename(new_chat_name)
        new_file_name = self.chat_history.file_name
        self.assertNotEqual(old_file_name, new_file_name)
        self.assertTrue(new_file_name.startswith(new_chat_name))

if __name__ == "__main__":
    unittest.main()
