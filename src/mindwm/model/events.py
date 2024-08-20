from typing import Annotated, Literal, Optional, Type, TypeVar, Union

from pydantic import BaseModel, Field

from .objects import IoDocument, LLMAnswer, ShowMessage, Touch, TypeText


class BaseEvent(BaseModel):

    def model_dump(self):
        """
        This Overrides the default model dump method to exclude None values
        """
        return super().model_dump(exclude_none=True)

    def model_dump_json(self):
        """
        This Overrides the default model dump method to exclude None values
        """
        return super().model_dump_json(exclude_none=True)


class IoDocumentEvent(BaseEvent):
    data: IoDocument
    type: Literal['iodocument'] = 'iodocument'


class TouchEvent(BaseEvent):
    data: Touch
    type: Literal['touch'] = 'touch'


class LLMAnswerEvent(BaseEvent):
    data: LLMAnswer
    type: Literal['llmanswer'] = 'llmanswer'


class ShowMessageEvent(BaseEvent):
    data: ShowMessage
    type: Literal['showmessage'] = 'showmessage'


class TypeTextEvent(BaseEvent):
    data: TypeText
    type: Literal['typetextevent'] = 'typetextevent'


Obj = TypeVar("Obj", IoDocument, Touch, LLMAnswer, ShowMessage, TypeText)

ObjEvent = TypeVar("ObjEvent", IoDocumentEvent, TouchEvent, LLMAnswerEvent,
                   ShowMessageEvent, TypeTextEvent)


class CloudEvent(BaseEvent):
    id: str
    source: str
    specversion: str = "1.0"
    data: Annotated[Union[IoDocumentEvent, TouchEvent, LLMAnswerEvent,
                          ShowMessageEvent, TypeTextEvent],
                    Field(discriminator='type')]
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

    @classmethod
    def make_obj_event(cls, obj: Type[Obj]) -> Type[ObjEvent]:
        match obj:
            case Touch():
                return TouchEvent(data=obj)
            case IoDocument():
                return IoDocumentEvent(data=obj)
            case LLMAnswer():
                return LLMAnswerEvent(data=obj)
            case ShowMessage():
                return ShowMessageEvent(data=obj)
            case TypeText():
                return TypeTextEvent(data=obj)
            case _:
                msg = f"unknown object type: {obj}"
                raise TypeError(msg)
