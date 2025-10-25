from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from pydantic import BaseModel
from app.db.pg import get_db
from sqlalchemy import update
from app.models.pg_models import User


router = APIRouter()


class LinkRequest(BaseModel):
    chat_id: str


@router.post('/link')
async def link_telegram(payload: LinkRequest, user=Depends(get_current_user), db=Depends(get_db)):
    stmt = update(User).where(User.id == user.id).values(telegram_chat_id=payload.chat_id)
    await db.execute(stmt)
    await db.commit()
    return {"ok": True}