from pydantic import BaseModel
from typing import Optional, List

class QuestionRequest(BaseModel):
    """Request body for the `/qa` endpoint.

    The PRD specifies a single field named `question` that contains
    the user's natural language question about the vector databases paper.
    """

    question: str
    session_id: Optional[str] = None 


class QAResponse(BaseModel):
    """Response body for the `/qa` endpoint.

    From the API consumer's perspective we only expose the final,
    verified answer plus some metadata (e.g. context snippets).
    Internal draft answers remain inside the agent pipeline.
    """

    answer: str
    context: str
    plan: str | None 
    sub_questions: list[str] | None 
    session_id:str
