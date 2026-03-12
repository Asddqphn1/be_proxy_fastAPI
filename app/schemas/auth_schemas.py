from typing import Optional
from pydantic import BaseModel

class UserProfile(BaseModel):
    name: str
    email: str
    nim: Optional[str] = None
    role: Optional[str] = "mahasiswa"