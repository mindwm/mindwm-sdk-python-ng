import json
from typing import (Annotated, Any, Dict, Literal, Optional, Type, TypeVar,
                    Union)
from uuid import uuid4

from fastapi import Body, Request, Response
from mindwm import logging
from pydantic import BaseModel, Field, model_serializer

from .graph import (GraphObjectCreated, GraphObjectDeleted, GraphObjectUpdated,
                    KafkaCdc)
from .objects import (IoDocument, LLMAnswer, Ping, Pong, ShowMessage, Touch,
                      TypeText, Clipboard)

logger = logging.getLogger(__name__)


class MindwmEvent(BaseModel):
    id: str = Field(description="uniq event id",
                    default_factory=lambda: uuid4().hex)
    source: Optional[str] = None
    specversion: str = "1.0"
    data: Annotated[Union[IoDocument, Touch, LLMAnswer, ShowMessage, TypeText,
                          KafkaCdc, GraphObjectCreated, GraphObjectUpdated,
                          GraphObjectDeleted, Ping, Pong, Clipboard],
                    Body(discriminator="type")]
    type: str
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

    # @model_serializer
    # def ser_model(self) -> Dict[str, Any]:
    #     res = {}
    #     for k, v in self.__dict__.items():
    #         res[k.capitalize()] = v

    #     return res

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


async def from_request(request: Request) -> MindwmEvent:
    body = await request.body()
    obj = json.loads(body)
    ev_dict = {}
    for k in request.headers.keys():
        if k.startswith('ce'):
            ev_dict[k.lstrip('ce-')] = request.headers.get(k)
        elif k == 'traceparent':
            ev_dict[k] = request.headers.get(k)

    ev_dict['data'] = obj
    logger.info(f"ev_dict: {ev_dict}")
    # TODO: (@omgbebebe) should we copy a type from obj?
    if 'type' in obj.keys():
        ev_dict['type'] = obj['type']
    else:
        obj['type'] = ev_dict['type']

    ev = MindwmEvent.model_validate(ev_dict)
    return ev


def from_response(response: Response) -> MindwmEvent:
    obj = response.json()
    ev_dict = {}
    for k in response.headers.keys():
        if k.startswith('ce'):
            ev_dict[k.lstrip('ce-')] = response.headers.get(k)

    ev_dict['data'] = obj
    logger.info(f"ev_dict: {ev_dict}")
    # TODO: (@omgbebebe) should we copy a type from obj?
    if 'type' in obj.keys():
        ev_dict['type'] = obj['type']
    else:
        obj['type'] = ev_dict['type']

    ev = MindwmEvent.model_validate(ev_dict)
    return ev


def to_request(ev: MindwmEvent, extra_headers: dict = {}):
    body = ev.data
    headers = {}
    ev_dict = ev.model_dump()
    to_headers = [k for k in ev_dict.keys() if k not in ['data']]
    for h in to_headers:
        if h == 'traceparent':
            headers['traceparent'] = ev_dict[h]
        else:
            headers[f"CE-{h.capitalize()}"] = str(ev_dict[h])

    #headers['content-type'] = 'application/cloudevents+json'
    headers['content-type'] = 'application/json'
    headers.update(extra_headers)
    return (headers, body.model_dump_json())


def to_response(ev: MindwmEvent, extra_headers: dict = {}) -> (Response):
    body = ev.data
    headers = {}
    ev_dict = ev.model_dump()
    to_headers = [k for k in ev_dict.keys() if k not in ['data']]
    for h in to_headers:
        if h == 'traceparent':
            headers['traceparent'] = ev_dict[h]
        else:
            headers[f"CE-{h.capitalize()}"] = str(ev_dict[h])

    #headers['content-type'] = 'application/cloudevents+json'
    headers['content-type'] = 'application/json'
    headers.update(extra_headers)
    return Response(content=body.model_dump_json(), headers=headers)
