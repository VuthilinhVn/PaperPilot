from pydantic import BaseModel, Field

class AIRequests(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    history: list = []
    stream: bool = False