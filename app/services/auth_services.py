import json
import urllib.parse

from fastapi import HTTPException
import httpx
import jwt
import redis.asyncio as redis
from app.config import security_settings
from app.schemas.auth_schemas import UserProfile

class AuthService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def get_sso_login_url(self, state: str) -> str:
        # 1. Tentukan endpoint auth Keycloak
        auth_endpoint = f"{security_settings.KEYCLOAK_ISSUER}/protocol/openid-connect/auth"

        # 2. Siapkan parameter
        params = {
            "client_id": security_settings.KEYCLOAK_CLIENT_ID,
            "response_type": "code",      
            "redirect_uri": security_settings.KEYCLOAK_REDIRECT_URI,
            "scope": "openid profile email",
            "state": state,
        }

        # 3. Encode jadi URL string
        full_url = f"{auth_endpoint}?{urllib.parse.urlencode(params)}"
        
        return full_url

    async def exchange_code_for_token(self, code: str):
        """
        Tukar Authorization Code dengan Access Token ke Keycloak
        """
        token_endpoint = f"{security_settings.KEYCLOAK_ISSUER}/protocol/openid-connect/token"
        
        payload = {
            "grant_type": "authorization_code",
            "client_id": security_settings.KEYCLOAK_CLIENT_ID,
            "client_secret": security_settings.KEYCLOAK_CLIENT_SECRET,
            "redirect_uri": security_settings.KEYCLOAK_REDIRECT_URI,
            "code": code
        }

        # Nembak ke Keycloak (Back-channel)
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(token_endpoint, data=payload)
            
            if response.status_code != 200:
                # Kalau gagal, return Error atau Raise Exception
                return None
            
            # Kalau sukses, return JSON Tokennya (Access Token, ID Token, dll)
            return response.json()
        
    async def get_user_from_session(self, session_id: str) -> UserProfile:
        """
        Ambil data user dari Redis berdasarkan Session ID
        """
        # 1. Cek Redis
        token_data_raw = await self.redis.get(f"session:{session_id}")
        if not token_data_raw:
            raise HTTPException(status_code=401, detail="Session Expired / Tidak Ditemukan")

        # 2. Parse JSON
        try:
            token_data = json.loads(token_data_raw)
            id_token = token_data.get("id_token")
            
            if not id_token:
                raise HTTPException(status_code=401, detail="Token data corrupt")

            # 3. Decode Token (Tanpa Verify Signature karena ambil dari Redis sendiri)
            payload = jwt.decode(id_token, options={"verify_signature": False})

            return UserProfile(
                name=payload.get("name", "Unknown"),
                email=payload.get("email", ""),
                nim=payload.get("preferred_username", ""),
                role="mahasiswa" # Atau ambil dari payload['realm_access']['roles']
            )
        except Exception as e:
            print(f"Error decode: {e}")
            raise HTTPException(status_code=401, detail="Gagal membaca identitas user")

    async def get_access_token(self, session_id: str) -> str:
        """Ambil murni Bearer / Access Token dari Redis"""
        token_data_raw = await self.redis.get(f"session:{session_id}")
        if not token_data_raw:
            return None
            
        token_data = json.loads(token_data_raw)
        return token_data.get("access_token")