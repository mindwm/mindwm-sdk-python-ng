import inspect
import json
import os
from base64 import b64decode
from collections.abc import Callable
from functools import wraps
from uuid import uuid4

import mindwm.model.graph as graphModel
from cloudevents.conversion import to_structured
from cloudevents.http import CloudEvent as CE
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from mindwm import logging
from mindwm.model.events import (CloudEvent, IoDocumentEvent, KafkaCdcEvent,
                                 LLMAnswerEvent, TouchEvent)
from mindwm.model.graph import KafkaCdc
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
from opentelemetry.trace.propagation.tracecontext import \
    TraceContextTextMapPropagator

span_processor = BatchSpanProcessor(OTLPSpanGrpcExporter())
trace_provider = TracerProvider(active_span_processor=span_processor)
trace.set_tracer_provider(trace_provider)

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)
app = FastAPI()


def with_trace(carrier: dict = {}):

    def decorator(func: Callable):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            service_name = func.__name__
            tracer = trace.get_tracer(service_name)

            ctx = TraceContextTextMapPropagator().extract(carrier=carrier)
            logger.debug(f"ctx: {ctx}")
            with tracer.start_as_current_span(service_name) as span:
                span.set_attribute("omg", "bebebe")
                span.set_attribute("foo", "bar")
                if 'trace_context' in kwargs.keys():
                    kwargs['trace_context'] = span.context
                res = await func(*args, **kwargs)
                return res

        return wrapper

    return decorator


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
        kwargs = dict(func_sig.parameters)
        b = await r.body()
        iodoc_ev = IoDocumentEvent.model_validate_json(b)
        iodoc_obj = iodoc_ev.data
        carrier = None
        if 'traceparent' in r.headers.keys():
            carrier = r.headers.get('traceparent')
            iodoc_obj.traceparent = carrier

        if 'tracestate' in r.headers.keys():
            iodoc_obj.tracestate = r.headers.get('tracestate')

        logger.info(f"bebebe")
        logger.info(f"request headers: {r.headers}\nbody: {b}")
        logger.debug(f"with injected traces: {iodoc_obj}")
        uuid = r.headers.get('ce-id')
        source = r.headers.get('ce-source')
        [
            _, username, hostname, _, tmux_b64, _some_id, tmux_session,
            tmux_pane, _
        ] = source.split('.')
        tmux_socket_path = str(b64decode(tmux_b64)).strip()
        tmux_socket_path = tmux_socket_path.strip("b'").strip('/')
        socket_path = f"{username}@{hostname}/{tmux_socket_path}"
        session_id = f"{socket_path}:{tmux_session}"
        pane_title = f"{session_id}%{tmux_pane}"
        if 'iodocument' in kwargs:
            kwargs['iodocument'] = iodoc_obj
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

        @with_trace(carrier=r.headers)
        @wraps(func)
        async def inner(**kwargs):
            value = await func(**kwargs)

            logger.debug(f"return value: {value}")

            if not value:
                headers = {}
                if carrier:
                    headers = {"traceparent": carrier}
                return Response(status_code=status.HTTP_200_OK,
                                headers=headers)
            else:
                context_name = os.environ.get('CONTEXT_NAME', 'NO_CONTEXT')

                obj_ev = CloudEvent.make_obj_event(value)
                attributes = {
                    "id": uuid4().hex,
                    "source": f"mindwm.{context_name}.knfunc.{func.__name__}",
                    #"subject": f"{source}.feedback",
                    # TODO: fix the subject to variant from above when we implement new naming convention
                    "subject": f"mindwm.{username}.{hostname}.knfunc.feedback",
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
        #return inner

    return wrapper


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


def kafka_cdc(func):

    @app.post("/")
    async def wrapper(r: Request, response: Response):
        func_sig = inspect.signature(func)
        xx = [p.annotation for p in func_sig.parameters.values()]
        kwargs = dict(func_sig.parameters)
        b = await r.body()
        logger.debug(f"headers: {r.headers}")
        logger.debug(f"body: {b}")
        cdc_obj = KafkaCdc.model_validate_json(b)
        logger.info(f"cdc_obj: {cdc_obj}")
        if 'traceparent' in r.headers.keys():
            carrier = r.headers.get('traceparent')

        if 'obj' in kwargs:
            kwargs['obj'] = cdc_obj

        match cdc_obj.payload.type:
            case 'relationship':
                carrier = cdc_obj.payload.traceparent
            case 'node':
                if cdc_obj.meta.operation != 'deleted':
                    carrier = cdc_obj.payload.after.properties.traceparent
                else:
                    carrier = cdc_obj.payload.before.properties.traceparent

        @with_trace(carrier=r.headers)
        @wraps(func)
        async def inner(**kwargs):

            value = await func(**kwargs)

            logger.debug(f"return value: {value}")

            headers = {}
            if carrier:
                headers = {"traceparent": carrier}

            if not value:
                return Response(status_code=status.HTTP_200_OK,
                                headers=headers)
            else:
                context_name = os.environ.get('CONTEXT_NAME', 'NO_CONTEXT')

                obj_ev = CloudEvent.make_obj_event(value)
                match cdc_obj.payload.type:
                    case "node":
                        if cdc_obj.meta.operation != 'deleted':
                            event_type = cdc_obj.payload.after.labels[0].lower(
                            )
                        else:
                            event_type = cdc_obj.payload.before.labels[
                                0].lower()
                    case "relationship":
                        event_type = cdc_obj.payload.label.lower()
                    case _:
                        event_type = "UNKNOWN"

                #logger.info(f"ctx: {span.context}")
                ev = CloudEvent(
                    id=uuid4().hex,
                    source=
                    f"mindwm.{context_name}.graph.{ cdc_obj.payload.type.lower() }",
                    subject=f"{ cdc_obj.meta.operation }",
                    type=event_type,
                    data=obj_ev.model_dump(),
                    traceparent=carrier)

                headers['content-type'] = 'application/cloudevents+json'
                logger.debug(f"response headers: {headers}")
                logger.debug(f"response event: {ev}")
                return Response(content=ev.model_dump_json(), headers=headers)

        res = await inner(**kwargs)
        return res

    return wrapper
