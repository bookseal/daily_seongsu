import json
import os

class DataStorage:
    def __init__(self, file_path):
        self.file_path = file_path
        self._ensure_directory()

    def _ensure_directory(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def save_data(self, data):
        """
        Saves the list of data to a JSON file.
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Successfully saved {len(data)} items to {self.file_path}")
        except Exception as e:
            print(f"Error saving data: {e}")
