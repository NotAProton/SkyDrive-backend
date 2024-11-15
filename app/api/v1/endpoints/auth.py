import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ....db.client import supabase, supabase_admin
import redis
from ....config import settings


router = APIRouter()

r = redis.Redis.from_url(settings.REDIS_URL)


class UserLogin(BaseModel):
    email: str
    password: str


class UserSignUp(UserLogin):
    username: str


@router.post("/signup")
async def signup(user: UserSignUp):
    try:
        user_exists = supabase_admin.rpc(
            "get_user_id_by_email", {"email": user.email}
        ).execute()
        if user_exists.data:
            raise HTTPException(status_code=400, detail="User already exists")

        response = supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password,
                "options": {"data": {"username": user.username}},
            }
        )
        print(response)
        if response.user is None:
            raise HTTPException(status_code=400, detail="User creation failed")
        signup_response = {
            "message": "Account created successfully",
            "userId": response.user.id,
        }
        return signup_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(user: UserLogin):
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": user.email, "password": user.password}
        )

        if response.user is None:
            raise HTTPException(status_code=400, detail="Login failed")

        token = secrets.token_urlsafe(32)
        r.set(token, response.user.id)
        login_response = {
            "message": "Login successful",
            "token": token,
            "userId": response.user.id,
            "username": response.user.user_metadata.get("username"),
        }
        return login_response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout():
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
