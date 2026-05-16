from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenExchangeResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    type: Optional[str] = None
    fpt: Optional[str] = None # Device Fingerprint Hash
