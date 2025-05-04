# Перед запуском установите зависимости:
#    pip install telethon nest_asyncio

import asyncio
import nest_asyncio
import tempfile
import os
import mimetypes
from telethon import TelegramClient, events

# ── ПАРАМЕТРЫ ───────────────────────────
API_ID    = 27819996
API_HASH  = "9aa1ffc6d32be6a87a3267baeee79cb9"
BOT_TOKEN = "7893214668:AAGnPX-zf9g1VvaRi7YgRXbJ_LVPBYz69HQ"
SOURCE    = "lostestos"     # канал-источник без @
TARGET    = "@vqurse_1"     # канал-приёмник с @
# ────────────────────────────────────────

# Патчим event loop (для Jupyter/Colab)
nest_asyncio.apply()

# Создаём клиентов без файловых сессий, чтобы избежать блокировки
user_client = TelegramClient(None, API_ID, API_HASH)
bot_client  = TelegramClient(None, API_ID, API_HASH)

async def main():
    # Старт бота с токеном
    await bot_client.start(bot_token=BOT_TOKEN)
    # Старт клиента-пользователя
    await user_client.start()
    print(f"🔔 Forwarding from @{SOURCE} to {TARGET}…")

    # Получаем entity целевого канала
    target_entity = await bot_client.get_input_entity(TARGET)

    @user_client.on(events.NewMessage(chats=SOURCE))
    async def handler(event):
        msg = event.message
        text = msg.text or ''
        try:
            if msg.media:
                # Определяем MIME и расширение
                mime_type = None
                if hasattr(msg.media, 'document') and msg.media.document.mime_type:
                    mime_type = msg.media.document.mime_type
                elif hasattr(msg.media, 'photo'):
                    mime_type = 'image/jpeg'
                ext = mimetypes.guess_extension(mime_type) or ''
                # Создаём временный файл с нужным расширением
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    path = tmp.name
                # Скачиваем медиа в файл
                await user_client.download_media(msg.media, file=path)
                # Отправляем файл ботом
                await bot_client.send_file(target_entity, path, caption=text)
                # Удаляем временный файл
                os.remove(path)
            else:
                # Просто пересылаем текст
                await bot_client.send_message(target_entity, text)
            print(f"✅ Forwarded message {msg.id}")
        except Exception as e:
            print(f"❌ Error forwarding {msg.id}: {e}")

    # Запуск слущателя
    await user_client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
