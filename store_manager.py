# store_manager.py

import json
import os

STORE_FILE = "store_list.json"

class StoreManager:
    def __init__(self):
        if not os.path.exists(STORE_FILE):
            self.store_list = ["その他"]
            self.save()
        else:
            self.load()

    def load(self):
        with open(STORE_FILE, 'r', encoding='utf-8') as f:
            self.store_list = json.load(f)

    def save(self):
        with open(STORE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.store_list, f, ensure_ascii=False, indent=2)

    def get_stores(self):
        return self.store_list

    def add_store(self, store_name):
        if store_name not in self.store_list:
            self.store_list.insert(-1, store_name)  # 「その他」の前に追加
            self.save()
