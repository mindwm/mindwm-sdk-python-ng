from cloudevents.conversion import to_structured
from cloudevents.http import CloudEvent as CE
import os
from uuid import uuid4
from typing import Any
from functools import wraps
import inspect
from fastapi import FastAPI, Request, Body, Response, status
from fastapi.responses import JSONResponse
from neontology import init_neontology, auto_constrain
from base64 import b64decode
import mindwm.model.graph as graphModel
import mindwm
from mindwm.model.events import (
    IoDocument,
    IoDocumentEvent,
    Touch,
    TouchEvent,
    LLMAnswer,
    LLMAnswerEvent,
    CloudEvent,
)
from mindwm import logging
import json

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

def iodoc(func):
    @app.post("/")
    async def wrapper(r: Request, response: Response):
        func_sig = inspect.signature(func)
        xx = [p.annotation for p in func_sig.parameters.values()]
        logger.info(f"params: {xx}")
        kwargs = dict(func_sig.parameters)
        b = await r.body()
        uuid = r.headers.get('ce-id')
        source = r.headers.get('ce-source')
        [_, username, hostname, _, tmux_b64, _some_id, tmux_session, tmux_pane, _] = source.split('.')
        tmux_socket_path = str(b64decode(tmux_b64)).strip()
        tmux_socket_path = tmux_socket_path.strip("b'").strip('/')
        socket_path = f"{username}@{hostname}/{tmux_socket_path}"
        session_id = f"{socket_path}:{tmux_session}"
        pane_title = f"{session_id}%{tmux_pane}"
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
        if 'tmux_session' in kwargs:
            kwargs['tmux_session'] = tmux_session
        if 'tmux_pane' in kwargs:
            kwargs['tmux_pane'] = tmux_pane
        if 'tmux_socket_path' in kwargs:
            kwargs['tmux_socket_path'] = tmux_socket_path
        if 'socket_path' in kwargs:
            kwargs['socket_path'] = socket_path
        if 'session_id' in kwargs:
            kwargs['session_id'] = session_id
        if 'pane_title' in kwargs:
            kwargs['pane_title'] = pane_title
        if 'graph' in kwargs:
            if init_neontology():
                auto_constrain()

            kwargs['graph'] = graphModel

        value = await func(**kwargs)
        logger.debug(f"return value: {value}")
        if not value:
            return Response(status_code=status.HTTP_200_OK)
        else:
            context_name = os.environ.get('CONTEXT_NAME', 'NO_CONTEXT')
            obj_ev = CloudEvent.make_obj_event(value)
            attributes = {
                "id": uuid4().hex,
                "source": f"mindwm.{context_name}.knfunc.{func.__name__}",
                #"subject": f"{source}.feedback",
                # TODO: fix the subject to variant from above when we implement new naming convention
                "subject": f"mindwm.pion.mindwm-stg1.knfunc.feedback",
                "type": obj_ev.type,
                #"ce-traceparent": r.headers.get('ce-traceparent')
            }
            data = obj_ev.model_dump()
            event = CE(attributes, data)
            headers, body = to_structured(event)
            #headers['content-type'] = 'application/cloudevents+json'
            logger.debug(f"response: {headers}\n{body}")
            response.headers.update(headers)
            return JSONResponse(content=json.loads(body), headers=headers)
        return value

def llm_answer(func):
    @app.post("/")
    async def wrapper(r: Request, response: Response):
        func_sig = inspect.signature(func)
        xx = [p.annotation for p in func_sig.parameters.values()]
        kwargs = dict(func_sig.parameters)
        b = await r.body()
        uuid = r.headers.get('ce-id')
        source = r.headers.get('ce-source')
        if 'answer' in kwargs:
            answer_ev = LLMAnswerEvent.model_validate_json(b)
            kwargs['answer'] = answer_ev.data

        value = await func(**kwargs)
        logger.debug(f"return value: {value}")
        if not value:
            return Response(status_code=status.HTTP_200_OK)
        else:
            context_name = os.environ.get('CONTEXT_NAME', 'NO_CONTEXT')
            obj_ev = CloudEvent.make_obj_event(value)
            attributes = {
                "id": uuid4().hex,
                "source": f"mindwm.{context_name}.knfunc.{func.__name__}",
                #"subject": f"{source}.feedback",
                # TODO: fix the subject to variant from above when we implement new naming convention
                "subject": f"mindwm.pion.mindwm-stg1.knfunc.feedback",
                "type": obj_ev.type,
                #"ce-traceparent": r.headers.get('ce-traceparent')
            }
            data = obj_ev.model_dump()
            event = CE(attributes, data)
            headers, body = to_structured(event)
            #headers['content-type'] = 'application/cloudevents+json'
            logger.debug(f"response: {headers}\n{body}")
            response.headers.update(headers)
            return JSONResponse(content=json.loads(body), headers=headers)
        return value
