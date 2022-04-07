from pydantic import BaseModel

class Event(BaseModel):
    name: str
    description: str
    date: str
    time: str
    duration: str
    completed: bool
    points: int
