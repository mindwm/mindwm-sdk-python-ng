from pydantic import BaseModel, Field
from typing import Annotated, Union, Literal, Optional, Type, TypeVar
from .objects import IoDocument, Touch, LLMAnswer, ShowMessage, TypeText


class IoDocumentEvent(BaseModel):
    data: IoDocument
    type: Literal['iodocument'] = 'iodocument'

class TouchEvent(BaseModel):
    data: Touch
    type: Literal['touch'] = 'touch'

class LLMAnswerEvent(BaseModel):
    data: LLMAnswer
    type: Literal['llmanswer'] = 'llmanswer'

class ShowMessageEvent(BaseModel):
    data: ShowMessage
    type: Literal['showmessage'] = 'showmessage'

class TypeTextEvent(BaseModel):
    data: TypeText
    type: Literal['typetextevent'] = 'typetextevent'

Obj = TypeVar(
    "Obj",
    IoDocument,
    Touch,
    LLMAnswer,
    ShowMessage,
    TypeText
    )

ObjEvent = TypeVar(
    "ObjEvent",
    IoDocumentEvent,
    TouchEvent,
    LLMAnswerEvent,
    ShowMessageEvent,
    TypeTextEvent
    )

class CloudEvent(BaseModel):
    id: str
    source: str
    specversion: str = "1.0"
    data: Annotated[
        Union[
            IoDocumentEvent,
            TouchEvent,
            LLMAnswerEvent,
            ShowMessageEvent,
            TypeTextEvent
        ], Field(discriminator='type')
    ]
    type: Optional[str] = None
    datacontenttype: Optional[str] = None
    dataschema: Optional[str] = None
    subject: Optional[str] = None
    time: Optional[str] = None
    data_base64: Optional[str] = None
    knativebrokerttl: Optional[str] = "255"
    traceparent: Optional[str] = None
    tracestate: Optional[str] = None
    knativearrivaltime: Optional[str] = None

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
