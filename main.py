# main.py

import asyncio
from bot import bot
import config

async def main():
    async with bot:
        await bot.load_extension("bot")  # bot.py のファイル名が bot.py なので "bot"
        await bot.start(config.DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
