from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth_routes, proxy_routes
from app.config import security_settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=security_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(proxy_routes.router)

@app.get("/")
async def root():
    return {"message": "BFF FastAPI is Running!"}