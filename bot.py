import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os
import re
import requests
import base64
from datetime import datetime, timezone, timedelta
import config
from server_settings_manager import ServerSettingsManager
from store_manager import StoreManager

# --- 初期設定 ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SAVE_DIR = "tmp"
settings_manager = ServerSettingsManager()
store_manager = StoreManager()

# --- ユーティリティ関数 ---
def extract_sheet_id(url):
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    return match.group(1) if match else None

def extract_folder_id(url):
    match = re.search(r'/folders/([a-zA-Z0-9-_]+)', url)
    return match.group(1) if match else None

def send_to_gas_with_base64(timestamp, user_name, store_name, amount, image_path, sheet_id, folder_id):
    url = config.GAS_WEBHOOK_URL
    with open(image_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')

    data = {
        'timestamp': timestamp,
        'user_name': user_name,
        'store_name': store_name,
        'amount': amount,
        'image_base64': encoded_string,
        'filename': os.path.basename(image_path),
        'spreadsheet_id': sheet_id,
        'folder_id': folder_id
    }

    try:
        response = requests.post(url, data=data)
        return response.status_code == 200 and response.text.strip() == "OK"
    except Exception as e:
        print(f"❌ 通信エラー: {e}")
        return False

# --- UIクラス ---
class OpenStoreSelectView(discord.ui.View):
    @discord.ui.button(label="情報入力をする", style=discord.ButtonStyle.primary)
    async def open_store_select(self, interaction: discord.Interaction, button: discord.ui.Button):
        server_id = interaction.guild.id
        stores = store_manager.get_stores(server_id)

        options = [discord.SelectOption(label=store, value=store) for store in stores]

        select = discord.ui.Select(placeholder="購入先を選んでください", options=options)

        async def select_callback(select_interaction: discord.Interaction):
            selected = select.values[0]
            if selected == "その他":
                await select_interaction.response.send_modal(StoreInputModal(server_id))
            else:
                await select_interaction.response.send_modal(AmountInputModal(selected))

        select.callback = select_callback

        view = discord.ui.View()
        view.add_item(select)

        await interaction.response.send_message("購入先を選択してください！", view=view, ephemeral=True)

class StoreInputModal(discord.ui.Modal, title="新しい購入先を入力してください"):
    def __init__(self, server_id):
        super().__init__()
        self.server_id = server_id
        self.store_name = discord.ui.TextInput(label="購入先店舗名", placeholder="例: 自由入力", required=True)
        self.add_item(self.store_name)

    async def on_submit(self, interaction: discord.Interaction):
        new_store = self.store_name.value.strip()
        store_manager.add_store(self.server_id, new_store)

        # 登録完了後にボタンを出す
        view = AmountInputButton(new_store)
        await interaction.response.send_message(
            f"✅ 新しい購入先 **{new_store}** を登録しました！\n続けて合計金額を入力してください。",
            view=view,
            ephemeral=True
        )

class AmountInputButton(discord.ui.View):
    def __init__(self, store_name):
        super().__init__()
        self.store_name = store_name

    @discord.ui.button(label="合計金額を入力する", style=discord.ButtonStyle.success)
    async def open_amount_input(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AmountInputModal(self.store_name))

class AmountInputModal(discord.ui.Modal):
    def __init__(self, store_name):
        super().__init__(title=f"{store_name} の合計金額を入力してください")
        self.store_name = store_name
        self.amount = discord.ui.TextInput(label="合計金額（数字のみ）", required=True)
        self.add_item(self.amount)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        amount_value = self.amount.value.strip()
        if not re.fullmatch(r"\d+", amount_value):
            await interaction.followup.send("❌ 金額は数字のみで入力してください。", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        config_data = settings_manager.get_settings(guild_id)
        if not config_data:
            await interaction.followup.send("❌ サーバー設定がされていません。管理者に連絡してください。", ephemeral=True)
            return

        sheet_id = config_data.get('spreadsheet_id')
        folder_id = config_data.get('folder_id')

        member = await interaction.guild.fetch_member(interaction.user.id)
        nickname = member.nick if member.nick else interaction.user.display_name

        jst = timezone(timedelta(hours=9))
        now = datetime.now(jst)
        timestamp = now.strftime('%Y/%m/%d %H:%M:%S')

        try:
            latest_file = sorted(
                [f for f in os.listdir(SAVE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
                key=lambda x: os.path.getmtime(os.path.join(SAVE_DIR, x))
            )[-1]
            image_path = os.path.join(SAVE_DIR, latest_file)
        except IndexError:
            await interaction.followup.send("❌ レシート画像が見つかりませんでした。", ephemeral=True)
            return

        success = send_to_gas_with_base64(timestamp, nickname, self.store_name, amount_value, image_path, sheet_id, folder_id)

        if success:
            await interaction.followup.send(
                f"✅ 提出日時: **{timestamp}**\n"
                f"✅ 購入者: **{nickname}**\n"
                f"✅ 購入先: **{self.store_name}**\n"
                f"✅ 合計金額: **{amount_value}円**",
                ephemeral=True
            )
            os.remove(image_path)
        else:
            await interaction.followup.send("❌ データ送信時に問題が発生しました。", ephemeral=True)

# --- イベントハンドラ ---
@bot.event
async def on_ready():
    print("🌟 Bot起動成功、コマンド同期開始")
    try:
        synced = await bot.tree.sync()
        print(f"✅ コマンド同期成功: {len(synced)}個登録されました")
    except Exception as e:
        print(f"❌ コマンド同期エラー: {e}")

@bot.event
async def on_message(message):
    try:
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)
        config_data = settings_manager.get_settings(guild_id)
        if not config_data:
            print(f"❌ このサーバー({guild_id})に設定データがありません")
            return

        if message.channel.id != int(config_data.get('account_channel_id', 0)):
            return

        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                    if not os.path.exists(SAVE_DIR):
                        os.makedirs(SAVE_DIR)

                    file_path = os.path.join(SAVE_DIR, attachment.filename)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as resp:
                            if resp.status == 200:
                                with open(file_path, 'wb') as f:
                                    f.write(await resp.read())

                    view = OpenStoreSelectView()
                    await message.channel.send(
                        content=f"{message.author.mention} レシート画像を受信しました！情報入力をお願いします！",
                        view=view
                    )

    except Exception as e:
        print(f"❌ on_messageエラー: {e}")

# --- Cog（設定コマンド） ---
class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="set_account_channel", description="このチャンネルを会計チャンネルに設定")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_account_channel(self, interaction: discord.Interaction):
        settings_manager.set_account_channel(interaction.guild.id, interaction.channel.id)
        await interaction.response.send_message("✅ このチャンネルを会計チャンネルに設定しました！", ephemeral=True)

    @app_commands.command(name="set_sheet_url", description="スプレッドシートの共有URLを設定")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_sheet_url(self, interaction: discord.Interaction, url: str):
        sheet_id = extract_sheet_id(url)
        if sheet_id:
            settings_manager.set_sheet_id(interaction.guild.id, sheet_id)
            await interaction.response.send_message("✅ スプレッドシートIDを設定しました！", ephemeral=True)
        else:
            await interaction.response.send_message("❌ URLからIDを抽出できませんでした。", ephemeral=True)

    @app_commands.command(name="set_folder_url", description="Google Driveフォルダの共有URLを設定")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_folder_url(self, interaction: discord.Interaction, url: str):
        folder_id = extract_folder_id(url)
        if folder_id:
            settings_manager.set_folder_id(interaction.guild.id, folder_id)
            await interaction.response.send_message("✅ フォルダIDを設定しました！", ephemeral=True)
        else:
            await interaction.response.send_message("❌ URLからIDを抽出できませんでした。", ephemeral=True)

    @app_commands.command(name="show_settings", description="現在登録されている設定を表示")
    async def show_settings(self, interaction: discord.Interaction):
        config_data = settings_manager.get_settings(interaction.guild.id)
        if config_data:
            await interaction.response.send_message(
                f"✅ 現在の設定内容:\n"
                f"- 会計チャンネルID: {config_data.get('account_channel_id')}\n"
                f"- スプレッドシートID: {config_data.get('spreadsheet_id')}\n"
                f"- DriveフォルダID: {config_data.get('folder_id')}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ このサーバーにはまだ設定が登録されていません。", ephemeral=True)

# --- Cog登録 ---
async def setup(bot):
    await bot.add_cog(Settings(bot))
