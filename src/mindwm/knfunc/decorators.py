from functools import wraps
from fastapi import FastAPI
from mindwm.model.events import (
    IoDocument,
    IoDocumentEvent,
    Touch,
    TouchEvent,
    CloudEvent
)
import logging
logger = logging.getLogger(__name__)

app = FastAPI()

def ev2iodocev(e: CloudEvent) -> IoDocumentEvent:
    if e.data.type != "iodocument":
        msg = f"event.data.type should be 'iodocument' but {e.data.type} provided"
        raise Exception(msg)

    if isinstance(e.data, IoDocumentEvent):
        return e.data
    else:
        raise Exception(f"wrong document type")

def ev2touchev(e: CloudEvent) -> TouchEvent:
    if e.data.type != "touch":
        msg = f"event.data.type should be 'touch' but {e.data.type} provided"
        raise Exception(msg)

    if isinstance(e.data, TouchEvent):
        return e.data
    else:
        raise Exception(f"wrong document type")

def ev2touch(e: CloudEvent) -> Touch:
    ev = ev2touchev(e)
    return ev.data

def ev2iodoc(e: CloudEvent) -> IoDocument:
    ev = ev2iodocev(e)
    return ev.data

def iodocument(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(e : CloudEvent):
        x = ev2iodoc(e)
        value = func(x)
        return value

    return wrapper

def touch(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(e : CloudEvent):
        x = ev2touch(e)
        value = func(x)
        return value

    return wrapper
