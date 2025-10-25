from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from pydantic import BaseModel
from app.db.pg import get_db
from sqlalchemy import update
from app.models.pg_models import User
from httpx import AsyncClient, RequestError, HTTPStatusError
from app.config import settings


router = APIRouter()


class LinkRequest(BaseModel):
    chat_id: str


@router.post("/chat/{user_name}")
async def get_chat_id(user_name: str):
    async with AsyncClient() as client:
        try:
            print("Fetching Telegram updates...")
            response = await client.get(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
            )
            response.raise_for_status()
            data = response.json()
            print(f"Telegram API response: {data}")

            if not data.get("ok") or not data.get("result"):
                raise HTTPException(status_code=404, detail="No updates found")

            for item in data["result"]:
                message = item.get("message") or item.get("edited_message")
                if message and message.get("chat", {}).get("username") == user_name:
                    chat_id = message["chat"]["id"]
                    return {
                        "chat_id": str(chat_id),
                        "username": user_name
                    }

            raise HTTPException(status_code=404, detail=f"User {user_name} not found in recent Telegram updates")
        except HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Telegram API error: {e.response.text}")
        except RequestError as e:
            print(f"Request error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to connect to Telegram API: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post('/link')
async def link_telegram(payload: LinkRequest, user=Depends(get_current_user), db=Depends(get_db)):
    stmt = update(User).where(User.id == user.id).values(telegram_chat_id=payload.chat_id)
    await db.execute(stmt)
    await db.commit()
    return {"ok": True}
