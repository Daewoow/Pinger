from fastapi import APIRouter

from app.models.pg_models import User

router = APIRouter()


@router.post("/")
async def create_user():
    pass


@router.get("/")
async def get_users():
    pass


@router.get("/user/{id}")
async def get_user_by_id(id: str):
    return await User.get_user_by_id(id)
    pass
