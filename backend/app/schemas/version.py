from pydantic import BaseModel

class VersionResponse(BaseModel):
    version: str
    environment: str
    build: str
