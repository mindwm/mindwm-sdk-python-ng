from typing import Annotated, Any, Literal, Optional, Type, TypeVar, Union
from uuid import uuid4

from fastapi import Body
from pydantic import BaseModel, Field

from .graph import KafkaCdc
from .objects import (IoDocument, LLMAnswer, Ping, Pong, ShowMessage, Touch,
                      TypeText)


class BaseEvent(BaseModel):
    id: str = Field(description="uniq event id",
                    default_factory=lambda: uuid4().hex)
    source: Optional[str] = None
    specversion: str = "1.0"
    data: Optional[Any] = Field(default=None, )
    type: Optional[str] = None
    datacontenttype: Optional[str] = None
    dataschema: Optional[str] = None
    subject: Optional[str] = None
    time: Optional[str] = None
    data_base64: Optional[str] = None
    knativebrokerttl: Optional[str] = "255"
    traceparent: Optional[Annotated[
        str,
        Field(min_length=1,
              description=
              "Contains a version, trace ID, span ID, and trace options"
              )]] = None
    tracestate: Optional[Annotated[
        str,
        Field(min_length=1,
              description="a comma-delimited list of key-value pairs")]] = None
    knativearrivaltime: Optional[str] = None
    key: Optional[str] = None
    knativekafkaoffset: Optional[int] = None
    knativekafkapartition: Optional[int] = None
    partitionkey: Optional[str] = None

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


class IoDocumentEvent(BaseEvent):
    data: IoDocument
    type: Literal['org.mindwm.v1.iodocument'] = 'org.mindwm.v1.iodocumen'


class TouchEvent(BaseEvent):
    data: Touch
    type: Literal['org.mindwm.v1.touch'] = 'org.mindwm.v1.touch'


class LLMAnswerEvent(BaseEvent):
    data: LLMAnswer
    type: Literal['lorg.mindwm.v1.lmanswer'] = 'org.mindwm.v1.llmanswer'


class ShowMessageEvent(BaseEvent):
    data: ShowMessage
    type: Literal['org.mindwm.v1.showmessage'] = 'org.mindwm.v1.showmessage'


class TypeTextEvent(BaseEvent):
    data: TypeText
    type: Literal[
        'org.mindwm.v1.typetextevent'] = 'org.mindwm.v1.typetextevent'


class KafkaCdcEvent(BaseEvent):
    knativearrivaltime: Optional[str] = None
    key: Optional[str] = None
    knativekafkaoffset: Optional[int] = None
    knativekafkapartition: Optional[int] = None
    partitionkey: Optional[str] = None
    data: KafkaCdc
    type: Literal[
        'org.mindwm.v1.kafkacdcevent'] = 'org.mindwm.v1.kafkacdcevent'


class PingEvent(BaseEvent):
    data: Ping
    type: Literal['org.mindwm.v1.ping'] = 'org.mindwm.v1.ping'


class PongEvent(BaseEvent):
    data: Pong
    type: Literal['org.mindwm.v1.pong'] = 'org.mindwm.v1.pong'


MindwmEvent = Annotated[Union[IoDocumentEvent, TouchEvent, LLMAnswerEvent,
                              ShowMessageEvent, TypeTextEvent, KafkaCdcEvent,
                              PingEvent, PongEvent],
                        Body(discriminator="type")]
