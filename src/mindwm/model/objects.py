from pydantic import BaseModel
from typing import List

class IoDocument(BaseModel):
    input: str
    output: str
    ps1: str

class Touch(BaseModel):
    ids: List[int]

class LLMAnswer(BaseModel):
    codesnippet : str
    description: str
