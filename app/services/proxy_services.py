import httpx
from fastapi import HTTPException, Request, Response
from app.core.depedencies import AuthServicesDep
from app.config import security_settings


ALLOWED_REQUEST_HEADERS = {
    "accept",
    "accept-language",
    "content-type",
    "user-agent",
    "x-requested-with",
}
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


async def forward_to_gateway(request: Request, path: str, service: AuthServicesDep):
    if request.method.upper() in UNSAFE_METHODS:
        origin = request.headers.get("origin")
        if not origin or origin not in security_settings.cors_origins:
            raise HTTPException(status_code=403, detail="Origin tidak diizinkan")

    # 1. Cek KTP (Cookie)
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Belum login")
    
    # 2. Siapkan Bawaan (Headers & Body)
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() in ALLOWED_REQUEST_HEADERS
    }
    
    # 3. Ambil Kunci Gudang (Bearer Token) dari Redis
    access_token = await service.get_access_token(session_id)
    if not access_token:
        raise HTTPException(status_code=401, detail="Session tidak valid / expired")

    headers["Authorization"] = f"Bearer {access_token}"

    # 4. Tujuan Akhir (API Gateway)
    target_url = f"{security_settings.API_GATEWAY_URL}/{path}"

    # 5. Berangkat! (Forward request menggunakan HTTPX)
    async with httpx.AsyncClient(timeout=30.0) as client:
        body = await request.body()
        req = client.build_request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params, # Bawa parameter kayak ?page=1
            content=body
        )
        
        resp = await client.send(req)
        
        # 6. Balik lagi ngasih paket ke Frontend
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            media_type=resp.headers.get("content-type")
        )