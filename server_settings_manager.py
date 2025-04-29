import json
import os

class ServerSettingsManager:
    SETTINGS_FILE = "server_settings.json"

    def __init__(self):
        if not os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, 'w') as f:
                json.dump({}, f)

        with open(self.SETTINGS_FILE, 'r') as f:
            self.settings = json.load(f)

    def save(self):
        with open(self.SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def set_account_channel(self, guild_id, channel_id):
        guild_id = str(guild_id)
        if guild_id not in self.settings:
            self.settings[guild_id] = {}
        self.settings[guild_id]['account_channel_id'] = str(channel_id)
        self.save()

    def set_sheet_id(self, guild_id, sheet_id):
        guild_id = str(guild_id)
        if guild_id not in self.settings:
            self.settings[guild_id] = {}
        self.settings[guild_id]['spreadsheet_id'] = sheet_id
        self.save()

    def set_folder_id(self, guild_id, folder_id):
        guild_id = str(guild_id)
        if guild_id not in self.settings:
            self.settings[guild_id] = {}
        self.settings[guild_id]['folder_id'] = folder_id
        self.save()

    def get_settings(self, guild_id):
        return self.settings.get(str(guild_id))
