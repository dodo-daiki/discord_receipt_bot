import json
import os

class ServerSettingsManager:
    def __init__(self):
        self.filename = "server_settings.json"
        self.settings = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            except json.JSONDecodeError:
                print("❌ JSON読み込みエラー: ファイルが壊れている可能性があります")
                self.settings = {}
        else:
            self.settings = {}

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def refresh(self):
        self.load()

    def get_settings(self, guild_id):
        return self.settings.get(str(guild_id), {})

    def set_account_channel(self, guild_id, channel_id):
        gid = str(guild_id)
        if gid not in self.settings:
            self.settings[gid] = {}
        self.settings[gid]['account_channel_id'] = channel_id
        self.save()

    def set_sheet_id(self, guild_id, sheet_id):
        gid = str(guild_id)
        if gid not in self.settings:
            self.settings[gid] = {}
        self.settings[gid]['spreadsheet_id'] = sheet_id
        self.save()

    def set_folder_id(self, guild_id, folder_id):
        gid = str(guild_id)
        if gid not in self.settings:
            self.settings[gid] = {}
        self.settings[gid]['folder_id'] = folder_id
        self.save()
