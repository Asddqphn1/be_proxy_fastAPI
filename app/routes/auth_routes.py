import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
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
async def login(services: AuthServicesDep, redis_client: redis.Redis = Depends(get_redis)): # Inject service di sini
    oauth_state = str(uuid.uuid4())
    await redis_client.set(
        f"oauth_state:{oauth_state}",
        "1",
        ex=security_settings.OAUTH_STATE_TTL_SECONDS,
    )

    # 1. Minta URL ke Service (Router gak perlu tau cara rakit URL)
    target_url = services.get_sso_login_url(oauth_state)

    # 2. Debugging dikit (Opsional)
    print(f"Redirecting User to: {target_url}")

    # 3. Lakukan aksi HTTP (Redirect)
    redirect_resp = RedirectResponse(url=target_url)
    redirect_resp.set_cookie(
        key="oauth_state",
        value=oauth_state,
        httponly=True,
        samesite=security_settings.COOKIE_SAMESITE,
        secure=security_settings.COOKIE_SECURE,
        max_age=security_settings.OAUTH_STATE_TTL_SECONDS,
    )
    return redirect_resp

@router.get("/callback")
async def callback(
    code: str,
    state: str,
    request: Request,
    services: AuthServicesDep,
    redis_client: redis.Redis = Depends(get_redis),
):
    cookie_state = request.cookies.get("oauth_state")
    if not cookie_state or cookie_state != state:
        raise HTTPException(status_code=400, detail="OAuth state tidak valid")

    state_exists = await redis_client.get(f"oauth_state:{state}")
    if not state_exists:
        raise HTTPException(status_code=400, detail="OAuth state expired / tidak ditemukan")

    await redis_client.delete(f"oauth_state:{state}")

    # 1. Tukar Code jadi Token lewat Service
    token_data = await services.exchange_code_for_token(code)
    
    if not token_data:
        raise HTTPException(status_code=400, detail="Gagal menukar token ke Keycloak")

    # 2. (Sementara) Tampilkan Token di layar biar kelihatan hasilnya
    session_id = str(uuid.uuid4())
    await redis_client.set(
        f"session:{session_id}",
        json.dumps(token_data),
        ex=security_settings.SESSION_TTL_SECONDS,
    )
    
    # 4. Buat Redirect Response ke Frontend
    # Ganti URL ini sesuai alamat Frontend React kamu
    redirect_resp = RedirectResponse(url=security_settings.FRONTEND_URL)
    
    # 5. Tempel Cookie Aman di Redirect itu
    redirect_resp.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,  # PENTING: JavaScript gak bisa baca ini (Anti-XSS)
        samesite=security_settings.COOKIE_SAMESITE,
        secure=security_settings.COOKIE_SECURE,
        max_age=security_settings.SESSION_TTL_SECONDS,
    )
    redirect_resp.delete_cookie("oauth_state")
    
    return redirect_resp

@router.get("/me", response_model=UserProfile)
async def me(user: CurrentUserDep):
    return user


@router.post("/logout")
async def logout(request: Request, redis_client: redis.Redis = Depends(get_redis)):
    session_id = request.cookies.get("session_id")
    if session_id:
        await redis_client.delete(f"session:{session_id}")

    resp = JSONResponse({"message": "Logout berhasil"})
    resp.delete_cookie("session_id")
    return resp

