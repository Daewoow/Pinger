import httpx
from app.config import settings
from .singleton_base import SingletonBase


class Notifier(SingletonBase):
    url: str = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    @staticmethod
    async def send_telegram(chat_id: str, text: str):
        if not settings.TELEGRAM_BOT_TOKEN:
            return

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        async with httpx.AsyncClient() as client:
            await client.post(url, json={"chat_id": chat_id, "text": text})
