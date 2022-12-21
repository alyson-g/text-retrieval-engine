from typing import List

from pydantic import BaseModel


class SimilarDocs(BaseModel):
    documents: List[str]
