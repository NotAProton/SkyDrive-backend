from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
import redis

from app.config import settings

security = HTTPBearer()

r = redis.Redis.from_url(settings.REDIS_URL)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    try:
        token = credentials.credentials
        # lookup token from redis
        res = r.get(token)
        print(res)
        if not res:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return res.decode()  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
