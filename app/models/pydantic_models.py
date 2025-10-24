from pydantic import BaseModel, EmailStr, AnyHttpUrl
from typing import Optional, Dict, Literal


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProjectCreate(BaseModel):
    name: str
    type: Literal["HTTP", "TCP", "ICMP"]
    url: Optional[AnyHttpUrl] = None
    host: Optional[str] = None
    port: Optional[int] = None
    headers: Optional[Dict[str, str]] = {}
    interval_s: int = 60
    timeout_s: int = 10
    stop_on_error: bool = True


class ProjectOut(BaseModel):
    id: str
    name: str
    type: str
    url: Optional[str]
    interval_s: int
    status: str
