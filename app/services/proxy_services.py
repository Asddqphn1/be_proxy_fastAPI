import httpx
from fastapi import Request, Response
from app.core.depedencies import AuthServicesDep
from app.config import security_settings


async def forward_to_gateway(request: Request, path: str, service: AuthServicesDep):
    # 1. Cek KTP (Cookie)
    session_id = request.cookies.get("session_id")
    
    # 2. Siapkan Bawaan (Headers & Body)
    headers = dict(request.headers)
    headers.pop("host", None)           # Hapus host asli biar httpx gak bingung
    headers.pop("content-length", None) # Hapus ini biar httpx kalkulasi ulang otomatis
    
    # 3. Ambil Kunci Gudang (Bearer Token) dari Redis
    if session_id:
        access_token = await service.get_access_token(session_id)
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

    # 4. Tujuan Akhir (API Gateway)
    target_url = f"{security_settings.API_GATEWAY_URL}/{path}"

    # 5. Berangkat! (Forward request menggunakan HTTPX)
    async with httpx.AsyncClient() as client:
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