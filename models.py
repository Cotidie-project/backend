from pydantic import BaseModel

class Task(BaseModel):
    name: str
    description: str
    date: str
    time: int
    duration: int
    completed: bool
    points: int

class UpdateTask(BaseModel):
    name: str
    description: str
    points: int
    completed: bool

class Break(BaseModel):
    name: str
    stime: int
    etime: int

class Plan(BaseModel):
    tasks: list
    breaks: list
