from pydantic import BaseModel, Field

class PaperHistoryRequests(BaseModel):
    paperId: int = Field(..., alias="paperId")
