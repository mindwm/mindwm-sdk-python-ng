import inspect
import json
import os
from base64 import b64decode
from collections.abc import Callable
from functools import wraps
from typing import Optional
from uuid import uuid4

import mindwm.model.graph as graphModel
from cloudevents.conversion import to_structured
from cloudevents.http import CloudEvent as CE
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from mindwm import logging
from mindwm.model.events import MindwmEvent, from_request, to_response
from mindwm.model.graph import KafkaCdc
from mindwm.model.objects import IoDocument, LLMAnswer, Touch, Clipboard
from neontology import auto_constrain, init_neontology
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import \
    OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter as OTLPSpanGrpcExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import HOST_NAME, SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)
from opentelemetry.trace.propagation import set_span_in_context
from opentelemetry.trace.propagation.tracecontext import \
    TraceContextTextMapPropagator

span_processor = BatchSpanProcessor(OTLPSpanGrpcExporter())
trace_provider = TracerProvider(active_span_processor=span_processor)
trace.set_tracer_provider(trace_provider)

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))
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


def event(func):

    @app.post('/')
    async def wrapper(request: Request,
                      response: Response) -> Optional[MindwmEvent]:
        ev = await from_request(request)
        logger.debug(f"event received: {ev}")
        logger.debug(f"request headers: {request.headers}")
        service_name = f"knfunc.{func.__name__}"
        func_sig = inspect.signature(func)
        xx = [p.annotation for p in func_sig.parameters.values()]
        kwargs = dict(func_sig.parameters)
        ctx = TraceContextTextMapPropagator().extract(carrier=request.headers)
        headers = response.headers
        tracer = trace.get_tracer(service_name)
        logger.info(f"my service_name: {service_name}")

        headers = {}
        with tracer.start_as_current_span(service_name, context=ctx) as span:
            extra_headers = {}
            ctx = set_span_in_context(span)
            TraceContextTextMapPropagator().inject(extra_headers, ctx)

            new_kwargs = {}
            if 'request' in kwargs.keys():
                new_kwargs['request'] = request
            if 'response' in kwargs.keys():
                new_kwargs['response'] = response

            res_obj = await func(ev.data, **new_kwargs)
            if type(res_obj) is Response:
                return res_obj

            context_name = os.environ.get('CONTEXT_NAME', 'NO_CONTEXT')
            if res_obj:
                res_ev = MindwmEvent(data=res_obj, type=res_obj.type)
                if 'traceparent' in headers.keys():
                    res_ev.traceparent = extra_headers['traceparent']

                res_ev.source = f"org.mindwm.{context_name}.knfunc.{func.__name__}"
                res_ev.subject = request.headers['ce-source']
                logger.debug(f'reply with MindwmEvent: {res_ev}')
                resp = to_response(res_ev, extra_headers)
                # extra_headers['content-type'] = 'application/cloudevents+json'
                # extra_headers['ce-knativebrokerttl'] = '255'
                # resp = Response(content=res_ev.model_dump_json(),
                #                 headers=extra_headers)
                #logger.debug(f'response body: {resp.body}')
                #logger.debug(f'response headers: {resp.headers}')
                return resp
            else:
                logger.debug('reply with empty response')
                return Response(status_code=status.HTTP_200_OK,
                                headers=headers)


def iodoc(func):

    @event
    async def wrapper(iodoc_obj: IoDocument,
                      request: Request = None) -> MindwmEvent:
        logger.info(f"input iodoc: {iodoc_obj}")
        logger.info(f"input request headers: {request.headers}")
        ev = await from_request(request)
        logger.info(f"event: {ev}")
        func_sig = inspect.signature(func)
        xx = [p.annotation for p in func_sig.parameters.values()]
        kwargs = dict(func_sig.parameters)
        logger.info(f"kwargs: {kwargs}")
        carrier = None
        if 'traceparent' in request.headers.keys():
            carrier = request.headers.get('traceparent')
            iodoc_obj.traceparent = carrier

        if 'tracestate' in request.headers.keys():
            iodoc_obj.tracestate = request.headers.get('tracestate')

        uuid = iodoc_obj.uuid
        [username, hostname, _, tmux_b64, _some_id, tmux_session, tmux_pane
         ] = ev.source.lstrip('mindwm').lstrip('org.mindwm').split('.')
        tmux_socket_path = str(b64decode(tmux_b64)).strip()
        tmux_socket_path = tmux_socket_path.strip("b'").strip('/')
        socket_path = f"{username}@{hostname}/{tmux_socket_path}"
        session_id = f"{socket_path}:{tmux_session}"
        pane_title = f"{session_id}%{tmux_pane}"
        if 'iodocument' in kwargs:
            kwargs['iodocument'] = iodoc_obj
        if 'uuid' in kwargs:
            kwargs['uuid'] = uuid
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
            try:
                init_neontology()
                auto_constrain()
            except Exception as e:
                logger.error("failed to initialize Neontology", e)

            kwargs['graph'] = graphModel

        return await func(**kwargs)

    return wrapper


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


def llm_answer(func):

    @app.post("/")
    async def wrapper(r: Request, response: Response):
        func_sig = inspect.signature(func)
        xx = [p.annotation for p in func_sig.parameters.values()]
        kwargs = dict(func_sig.parameters)
        b = await r.body()
        logger.debug(f"request headers: {r.headers}\nbody: {b}")
        uuid = r.headers.get('ce-id')
        source = r.headers.get('ce-source')
        subject = r.headers.get('ce-subject')
        if 'answer' in kwargs:
            answer_ev = LLMAnswerEvent.model_validate_json(b)
            kwargs['answer'] = answer_ev.data

        @with_trace(carrier=r.headers)
        @wraps(func)
        async def inner(**kwargs):
            value = await func(**kwargs)
            logger.debug(f"return value: {value}")
            logger.info(f"inner")
            carrier = None
            if 'traceparent' in r.headers.keys():
                carrier = r.headers.get('traceparent')
                value.traceparent = carrier
                value.traceparent = carrier

            if 'tracestate' in r.headers.keys():
                value.tracestate = r.headers.get('tracestate')

            logger.debug(f"with injected traces: {value}")
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
                    "subject": subject,
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

        res = await inner(**kwargs)
        return res

    return wrapper

def clipboard(func):

    @app.post("/")
    async def wrapper(r: Request, response: Response):
        func_sig = inspect.signature(func)
        xx = [p.annotation for p in func_sig.parameters.values()]
        kwargs = dict(func_sig.parameters)
        b = await r.body()
        logger.debug(f"request headers: {r.headers}\nbody: {b}")
        uuid = r.headers.get('ce-id')
        source = r.headers.get('ce-source')
        subject = r.headers.get('ce-subject')
        ce_type = r.headers.get('ce-type')
        # TODO(@metacoma) fix usage
        ce_traceparent = r.headers.get('traceparent')

        ev = await from_request(r)
        logger.info(f"event: {ev}")

        clipboard_ev = Clipboard.model_validate_json(b)

        user = "bebebeka"
        host = "laptop"

        if 'clipboard' in kwargs:
            kwargs['clipboard'] = ev
        if 'traceparent' in kwargs:
            kwargs['traceparent'] = ce_traceparent
        if 'uuid' in kwargs:
            kwargs['uuid'] = uuid
        if 'time' in kwargs:
            kwargs['time'] = ev.data.time
        if 'data' in kwargs:
            kwargs['data'] = ev.data.data
        if 'username' in kwargs:
            kwargs['username'] = user
        if 'hostname' in kwargs:
            kwargs['hostname'] = host
        if 'graph' in kwargs:
            try:
                init_neontology()
                auto_constrain()
            except Exception as e:
                logger.error("failed to initialize Neontology", e)

            kwargs['graph'] = graphModel


        @wraps(func)
        async def inner(**kwargs):
            value = await func(**kwargs)
            logger.debug(f"return value: {value}")
            logger.info(f"inner")
            carrier = None
            # if 'traceparent' in r.headers.keys():
            #     carrier = r.headers.get('traceparent')
            #     value.traceparent = carrier
            #     value.traceparent = carrier
            #
            # if 'tracestate' in r.headers.keys():
            #     value.tracestate = r.headers.get('tracestate')

            logger.debug(f"with injected traces: {value}")
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
                    "subject": subject,
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

        res = await inner(**kwargs)
        return res

    return wrapper
