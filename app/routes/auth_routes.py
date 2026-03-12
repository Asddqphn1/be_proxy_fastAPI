import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
import redis.asyncio as redis
from app.core.depedencies import AuthServicesDep, CurrentUserDep 
from app.config import security_settings
from app.database import get_redis
from app.schemas.auth_schemas import UserProfile


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.get("/login")
async def login(services: AuthServicesDep): # Inject service di sini
    # 1. Minta URL ke Service (Router gak perlu tau cara rakit URL)
    target_url = services.get_sso_login_url()

    # 2. Debugging dikit (Opsional)
    print(f"Redirecting User to: {target_url}")

    # 3. Lakukan aksi HTTP (Redirect)
    return RedirectResponse(url=target_url)

@router.get("/callback")
async def callback(code: str, services: AuthServicesDep, redis_client: redis.Redis = Depends(get_redis)):
    # 1. Tukar Code jadi Token lewat Service
    token_data = await services.exchange_code_for_token(code)
    
    if not token_data:
        raise HTTPException(status_code=400, detail="Gagal menukar token ke Keycloak")

    # 2. (Sementara) Tampilkan Token di layar biar kelihatan hasilnya
    session_id = str(uuid.uuid4())
    await redis_client.set(f"session:{session_id}", json.dumps(token_data), ex=1800)
    
    # 4. Buat Redirect Response ke Frontend
    # Ganti URL ini sesuai alamat Frontend React kamu
    redirect_resp = RedirectResponse(url=security_settings.FRONTEND_URL)
    
    # 5. Tempel Cookie Aman di Redirect itu
    redirect_resp.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,  # PENTING: JavaScript gak bisa baca ini (Anti-XSS)
        samesite="lax",
        secure=False    # Set True kalau udah HTTPS (Production)
    )
    
    return redirect_resp

@router.get("/me", response_model=UserProfile)
async def me(user: CurrentUserDep):
    return user

