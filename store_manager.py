# store_manager.py

import json
import os

STORE_FILE = "store_list.json"

class StoreManager:
    def __init__(self):
        if not os.path.exists(STORE_FILE):
            self.store_data = {}
            self.save()
        else:
            self.load()

    def load(self):
        with open(STORE_FILE, 'r', encoding='utf-8') as f:
            self.store_data = json.load(f)

    def save(self):
        with open(STORE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.store_data, f, ensure_ascii=False, indent=2)

    def get_stores(self, server_id):
        server_id = str(server_id)
        if server_id not in self.store_data:
            self.store_data[server_id] = ["その他"]
            self.save()
        return self.store_data[server_id]

    def add_store(self, server_id, store_name):
        server_id = str(server_id)
        if server_id not in self.store_data:
            self.store_data[server_id] = ["その他"]
        if store_name not in self.store_data[server_id]:
            stores = self.store_data[server_id]
            if "その他" in stores:
                idx = stores.index("その他")
                stores.insert(idx, store_name)
            else:
                stores.append(store_name)
            self.save()

    def remove_store(self, server_id, store_name):
        server_id = str(server_id)
        if server_id in self.store_data and store_name in self.store_data[server_id]:
            self.store_data[server_id].remove(store_name)
            if not self.store_data[server_id]:
                self.store_data[server_id] = ["その他"]
            self.save()
