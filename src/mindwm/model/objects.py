from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class MindwmObject(BaseModel):
    traceparent: Optional[str] = None
    tracestate: Optional[str] = None

    def to_json(self):
        return self.model_dump_json()

    def model_dump(self, **kwargs):
        """
        This Overrides the default model dump method to exclude None values
        """
        return super().model_dump(exclude_none=True)

    def model_dump_json(self, **kwargs):
        """
        This Overrides the default model dump method to exclude None values
        """
        return super().model_dump_json(exclude_none=True)


class IoDocument(MindwmObject):
    uuid: str = Field(description="uniq action id",
                      default_factory=lambda: uuid4().hex)
    input: str
    output: str
    ps1: str


class Touch(MindwmObject):
    ids: List[int]


class LLMAnswer(MindwmObject):
    iodoc_uuid: str = Field(description='An original IoDocument uuid')
    codesnippet: str
    description: str


class Ping(MindwmObject):
    uuid: str = Field(description="uniq action id",
                      default_factory=lambda: uuid4().hex)
    payload: Optional[str] = None


class Pong(MindwmObject):
    payload: Optional[str] = None
    uuid: str


# Actions
class Action(MindwmObject):
    uuid: str = Field(description="uniq action id",
                      default_factory=lambda: uuid4().hex)
    parent_uuid: str = Field(description="uuid of a parent document")
    targets: List[str] = Field(
        description=
        "non-empty list of targets to execute the action on. I.e. identifier of tmux pane"
    )


class ShowMessage(Action):
    title: str
    message: str


class TypeText(Action):
    title: str
    description: str
    snippet: str
