from pydantic import BaseModel

class Interest(BaseModel):
    name: str
    source: str
    source_type: str
