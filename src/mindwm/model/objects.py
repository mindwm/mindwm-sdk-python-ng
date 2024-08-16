from pydantic import BaseModel, Field
from typing import List

class IoDocument(BaseModel):
    uuid: str
    input: str
    output: str
    ps1: str

class Touch(BaseModel):
    ids: List[int]

class LLMAnswer(BaseModel):
    iodoc_uuid: str = Field(description = 'An original IoDocument uuid')
    codesnippet : str
    description: str
