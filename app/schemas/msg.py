from pydantic import BaseModel

class StandardActionResponse(BaseModel):
    detail: str
