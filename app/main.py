from fastapi import FastAPI, Depends
from app.database import get_redis
import redis.asyncio as redis

from app.routes import auth_routes, proxy_routes

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(proxy_routes.router)

@app.get("/")
async def root():
    return {"message": "BFF FastAPI is Running!"}

@app.get("/test-redis")
async def test_redis(r: redis.Redis = Depends(get_redis)):
    # Coba simpan data ke Redis
    await r.set("tes", "Halo Redis!")
    # Coba ambil lagi
    nilai = await r.get("tes")
    return {"redis_response": nilai}