from typing import Any
from functools import wraps
from fastapi import FastAPI, Request, Body, Response, status
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

def touch(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(touch_ev: TouchEvent):
        value = func(touch_ev.data)
        return value

    return wrapper

def iodocument(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(iodoc_ev: IoDocumentEvent):
        res = await func(iodoc_ev.data)
        return res

def iodocument_with_source(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(r: Request):
        b = await r.body()
        uuid = r.headers.get('ce-id')
        source = r.headers.get('ce-source')
        [_, username, hostname, _, tmux_b64, some_id, session, pane, _] = source.split('.')
        init_neontology()
        auto_constrain()
        iodoc_ev = IoDocumentEvent.model_validate_json(b)
        value = await func(
                iodocument=iodoc_ev.data,
                uuid=uuid,
                username=username,
                hostname=hostname,
                socket_path=str(b64decode(tmux_b64)).strip(),
                tmux_session=session,
                tmux_pane=pane
                )
        logger.debug(f"return value: {value}")
        if not value:
            return Response(status_code=status.HTTP_200_OK)
        else:
            return value
        return value
