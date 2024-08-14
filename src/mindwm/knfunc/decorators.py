from typing import Any
from functools import wraps
import inspect
from fastapi import FastAPI, Request, Body, Response, status
from neontology import init_neontology, auto_constrain
from base64 import b64decode
import mindwm.model.graph as graphModel
from mindwm.model.events import (
    IoDocument,
    IoDocumentEvent,
    Touch,
    TouchEvent,
    CloudEvent
)
from mindwm import logging

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
        if not value:
            return Response(status_code=status.HTTP_200_OK)
        else:
            return value
        return value

def iodocument(func):
    @wraps(func)
    @app.post("/")
    async def wrapper(iodoc_ev: IoDocumentEvent):
        value = await func(iodoc_ev.data)
        logger.warning("@iodocument is deprecated. Use @iodoc instead")
        if not value:
            return Response(status_code=status.HTTP_200_OK)
        else:
            return value
        return value

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
        logger.warning("@iodocument_with_source is deprecated. Use @iodoc instead")
        if not value:
            return Response(status_code=status.HTTP_200_OK)
        else:
            return value
        return value

def iodoc(func):
    @app.post("/")
    async def wrapper(r: Request):
        func_sig = inspect.signature(func)
        xx = [p.annotation for p in func_sig.parameters.values()]
        logger.info(f"params: {xx}")
        kwargs = dict(func_sig.parameters)
        b = await r.body()
        uuid = r.headers.get('ce-id')
        source = r.headers.get('ce-source')
        [_, username, hostname, _, tmux_b64, some_id, session, pane, _] = source.split('.')
        if 'iodocument' in kwargs:
            iodoc_ev = IoDocumentEvent.model_validate_json(b)
            kwargs['iodocument'] = iodoc_ev.data
        if 'uuid' in kwargs:
            kwargs['uuid'] = r.headers.get('ce-id')
        if 'username' in kwargs:
            kwargs['username'] = username
        if 'hostname' in kwargs:
            kwargs['hostname'] = hostname
        if 'tmux_b64' in kwargs:
            kwargs['tmux_b64'] = tmux_b64
        if 'session_id' in kwargs:
            kwargs['session_id'] = some_id
        if 'tmux_session' in kwargs:
            kwargs['tmux_session'] = session
        if 'socket_path' in kwargs:
            kwargs['socket_path'] = str(b64decode(tmux_b64)).strip()
        if 'pane' in kwargs:
            kwargs['pane'] = str(pane)
        if 'graph' in kwargs:
            if init_neontology():
                auto_constrain()

            kwargs['graph'] = graphModel

        value = await func(**kwargs)
        logger.debug(f"return value: {value}")
        if not value:
            return Response(status_code=status.HTTP_200_OK)
        else:
            return value
        return value
