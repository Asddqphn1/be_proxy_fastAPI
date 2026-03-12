from typing import Annotated
from fastapi import Depends, HTTPException, Request
from app.schemas.auth_schemas import UserProfile
from app.services.auth_services import AuthService
from app.database import get_redis  
import redis.asyncio as redis

# Factory function untuk bikin instance AuthService
def get_auth_services(redis_client: redis.Redis = Depends(get_redis)) -> AuthService:
    return AuthService(redis_client)


# Type Alias biar codingan di Router pendek
AuthServicesDep = Annotated[AuthService, Depends(get_auth_services)]

async def get_current_user(
    request: Request, 
    service: AuthServicesDep 
):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Belum Login (No Cookie)")
    
    # Panggil logic di Service
    return await service.get_user_from_session(session_id)

CurrentUserDep = Annotated[UserProfile, Depends(get_current_user)]

