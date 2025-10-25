from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.db.pg import get_db
from app.models.pydantic_models import UserCreate, TokenResponse
from app.models.pg_models import User
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token
from app.config import settings


router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(u: UserCreate, db=Depends(get_db)):
    stmt = select(User).filter_by(email=u.email)
    res = await db.execute(stmt)

    if res.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=u.email, password_hash=hash_password(u.password))

    db.add(user)
    await db.commit()
    token = create_access_token(str(user.id))
    return {"access_token": token}


@router.post("/login", response_model=TokenResponse)
async def login(u: UserCreate, db=Depends(get_db)):
    stmt = select(User).filter_by(email=u.email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user or not verify_password(u.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(str(user.id))
    return {"access_token": token}
