from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from .db.client import supabase, supabase_admin

security = HTTPBearer()


class SessionsResponseData(BaseModel):
    user_id: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    try:
        # lookup token from sessions table
        token = credentials.credentials
        response = (
            supabase_admin.table("sessions")
            .select("user_id")
            .eq("token", token)
            .execute()
        )
        data = SessionsResponseData(**response.data[0])
        return data.user_id
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
