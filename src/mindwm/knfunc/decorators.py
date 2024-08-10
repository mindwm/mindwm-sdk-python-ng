from typing import Any
from functools import wraps
from fastapi import FastAPI, Request, Body
from neontology import init_neontology, auto_constrain
from base64 import b64decode
from mindwm.model.events import (
    IoDocument,
    IoDocumentEvent,
    Touch,
    TouchEvent,
    CloudEvent
)
import logging
import os

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def get_root():
    logger.warning("GET / received")

@app.get("/health/liveness")
def liveness():
    return "OK"

@app.get("/health/readiness")
def readiness():
    return "OK"

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

def touch_event(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(e : CloudEvent):
        x = ev2touchev(e)
        value = func(x, ev)
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

def event(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(e : CloudEvent):
        value = func(ev)
        return value

    return wrapper

def iodocument(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(r: Request):
        b = await r.body()
        res = await func(b)
        return res

def iodocument_event(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(r: Request):
        b = await r.body()
        uuid = r.headers.get('ce-id')
        source = r.headers.get('ce-source')
        [_, username, hostname, _, tmux_b64, some_id, session, pane, _] = e.source.split('.')
        init_neontology()
        auto_constrain()
        value = func(
                iodocument=x,
                uuid=uuid,
                username=username,
                hostname=hostname,
                socket_path=str(b64decode(tmux_b64)).strip(),
                tmux_session=session,
                tmux_pane=pane
                )
        return value

def request(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(r: Request):
        value = await func(r)
        return value

    return wrapper

def request_body(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(b: Any = Body(None)):
        value = await func(b)
        return value

    return wrapper
