from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.models.pg_models import User
from app.db.pg import get_db

router = APIRouter()


@router.get("/")
async def get_users(db=Depends(get_db)):
    res = await db.execute(select(User))
    users = res.scalars().all()
    return {"users": users}


@router.get("/user/{user_id}")
async def get_user_by_id(user_id: str, db=Depends(get_db)):
    res = await db.execute(select(User).where(User.id == user_id))
    return {"user": res.scalar().first()}
