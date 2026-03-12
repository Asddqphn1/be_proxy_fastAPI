
from fastapi import APIRouter, Request
from app.core.depedencies import AuthServicesDep
from app.services.proxy_services import forward_to_gateway

router = APIRouter(
    tags=["Proxy"],
)

@router.api_route("/setoran-dev-f3ca4a/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_setoran(request: Request, path: str, service: AuthServicesDep):
    return await forward_to_gateway(request, f"setoran-dev-f3ca4a/v1/{path}", service)

@router.api_route("/public-imemoraise-dev/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_public(request: Request, path: str, service: AuthServicesDep):
    return await forward_to_gateway(request, f"public-imemoraise-dev/v1/{path}", service)

@router.api_route("/kp-dev/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_kp(request: Request, path: str, service: AuthServicesDep):
    return await forward_to_gateway(request, f"kp-dev/v1/{path}", service)