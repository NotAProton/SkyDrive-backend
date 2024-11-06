from fastapi import APIRouter, Depends, HTTPException
from ....db.client import supabase
from pydantic import BaseModel

router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

class UserSignUp(UserLogin):
    pass

@router.post("/signup")
async def signup(user: UserSignUp):
    try:
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(user: UserLogin):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
async def logout():
    try:
        response = supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
