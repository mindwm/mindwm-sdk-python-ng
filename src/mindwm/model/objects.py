from pydantic import BaseModel, Field
from typing import List, Literal
from uuid import uuid4

class IoDocument(BaseModel):
    uuid: str = Field(
        description="uniq action id",
        default_factory=lambda: uuid4().hex)
    input: str
    output: str
    ps1: str

class Touch(BaseModel):
    ids: List[int]

class LLMAnswer(BaseModel):
    iodoc_uuid: str = Field(description = 'An original IoDocument uuid')
    codesnippet : str
    description: str

class Action(BaseModel):
    uuid: str = Field(
        description="uniq action id",
        default_factory=lambda: uuid4().hex)
    parent_uuid: str = Field(description="uuid of a parent document")
    targets: List[str] = Field(
        description="non-empty list of targets to execute the action on. I.e. identifier of tmux pane")

class ShowMessage(Action):
    title: str
    message: str
    type: Literal['showmessage'] = 'showmessage'

class TypeText(Action):
    title: str
    description: str
    snippet: str
    type: Literal['typetext'] = 'typetext'
