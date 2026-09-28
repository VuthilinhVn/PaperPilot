from pydantic import BaseModel, Field

class FavoriteRequests(BaseModel):
    paperId: int = Field(..., alias="paperId")