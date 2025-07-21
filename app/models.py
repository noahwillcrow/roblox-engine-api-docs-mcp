from pydantic import BaseModel
from typing import List, Dict, Any

class RetrievalRequest(BaseModel):
    """
    Pydantic model for the retrieval request body.
    """
    query: str

class RetrievedDocument(BaseModel):
    """
    Pydantic model for a single retrieved document.
    """
    source: str
    content: str
    metadata: Dict[str, Any]

class RetrievalResponse(BaseModel):
    """
    Pydantic model for the retrieval response body.
    """
    answer: str
    documents: List[RetrievedDocument]