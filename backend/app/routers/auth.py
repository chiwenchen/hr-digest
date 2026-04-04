from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
import bcrypt as bcrypt_lib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import User
from app.auth.jwt import create_access_token
from app.auth.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not bcrypt_lib.checkpw(body.password.encode(), user.hashed_password.encode()):
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    token = create_access_token(user.id, user.role)
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax", max_age=86400)
    return {"message": "登入成功", "user": {"id": user.id, "name": user.name, "role": user.role}}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "已登出"}


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role, "email_subscribed": user.email_subscribed}
