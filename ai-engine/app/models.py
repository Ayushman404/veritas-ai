from pydantic import BaseModel
from typing import List, Tuple, Optional

class QueryRequest(BaseModel):
    query: str
    chat_history: List[Tuple[str, str]] = []

class IngestResponse(BaseModel):
    status: str
    chunks_stored: int
    message: str