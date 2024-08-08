from pydantic import BaseModel, Field
from typing import Annotated, Union, Literal, Optional, List

class IoDocument(BaseModel):
    input: str
    output: str
    ps1: str

class IoDocumentEvent(BaseModel):
    data: IoDocument
    type: Literal['iodocument'] = 'iodocument'

class Touch(BaseModel):
    ids: List[int]

class TouchEvent(BaseModel):
    data: Touch
    type: Literal['touch'] = 'touch'

class CloudEvent(BaseModel):
    id: str
    source: str
    specversion: str = "1.0"
    data: Annotated[
        Union[
            IoDocumentEvent,
            TouchEvent
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
