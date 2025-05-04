import os, asyncio
from telethon import TelegramClient

API_ID    = int(os.getenv("API_ID"))
API_HASH  = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE    = os.getenv("SOURCE")
TARGET    = os.getenv("TARGET")

async def main():
    client = TelegramClient('user', API_ID, API_HASH)
    bot    = TelegramClient('bot',  API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)
    await client.start()

    with open("last_id.txt") as f:
        last_id = int(f.read().strip() or 0)

    msgs = await client.get_messages(SOURCE, min_id=last_id, limit=50)
    msgs = sorted(msgs, key=lambda m: m.id)
    new_last = last_id

    for m in msgs:
        try:
            await bot.forward_messages(TARGET, m)
            new_last = m.id
            print(f"✅ Forwarded {m.id}")
        except Exception as e:
            print(f"❌ Error {m.id}: {e}")

    with open("last_id.txt", "w") as f:
        f.write(str(new_last))

if __name__ == "__main__":
    asyncio.run(main())

