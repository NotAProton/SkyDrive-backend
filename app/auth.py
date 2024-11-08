from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .db.client import supabase

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        # the token is acc_token+ref_token
        acc, ref = credentials.credentials.split("+")
        supabase.auth.access_token = acc

        user = supabase.auth.set_session(acc,ref)
        user = user["user"]
        return user
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
