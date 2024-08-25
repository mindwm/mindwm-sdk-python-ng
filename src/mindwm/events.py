import asyncio
import json
import logging
import os
from datetime import datetime
from functools import partial
from time import sleep

import nats
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import \
    TraceContextTextMapPropagator
from pydantic import BaseModel

from mindwm import logging

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class NatsInterface:

    def __init__(self):
        logger.debug(f"get NATS_URL from environment")
        self.url = os.environ.get('NATS_URL', 'nats://localhost:4222')
        self.nc = None
        self.subs = {}

    async def init(self):
        logger.info(f"Initializing Nats interface for {self.url}")
        await self.connect()

    async def loop(self):
        logger.debug(f"Entering main Nats interface loop")

        # TODO: need to catch a signals about connection state
        await asyncio.Future()
        await self.nc.close()

    async def connect(self):
        if not self.nc:
            self.nc = await nats.connect(self.url)
            logger.info(f"Connected to {self.url}")
        else:
            logger.info("already connected")

    async def subscribe(self, subj, callback):
        self.subs[subj] = {}
        handler = partial(self.message_handler, subj, callback)
        await self.nc.subscribe(subj, cb=handler)
        logger.info(f"Subscribed to NATS subject: {subj}")

    async def publish(self, subj, payload):
        carrier = {}
        with tracer.start_as_current_span(__name__) as span:
            span.set_attribute("subject", subj)
            TraceContextTextMapPropagator().inject(carrier)
            logger.debug(f"publish carrier: {carrier}")
            headers = carrier
            if 'traceparent' in headers.keys():
                payload.traceparent = headers['traceparent']

            logger.debug(f"send message to {subj}: {headers} {payload}")

            await self.nc.publish(subj,
                                  bytes(payload.model_dump_json(),
                                        encoding='utf-8'),
                                  headers=headers)

    async def message_handler(self, subj, callback, msg):
        logger.debug(f"received: {subj}: {msg}")
        data = json.loads(msg.data.decode())
        carrier = {}
        if 'traceparent' in msg.headers.keys():
            carrier = {"traceparent": msg.headers['traceparent']}
            logger.debug(f"message_handler: carrier: {carrier}")

        ctx = TraceContextTextMapPropagator().extract(carrier=carrier)
        with tracer.start_as_current_span(__name__, context=ctx) as span:
            res = None
            if 'message' in data.keys():
                message = data['message']

                if callback:
                    res = await callback(message)

            return res


_nats = NatsInterface()


async def init():
    loop = asyncio.get_event_loop()
    await _nats.init()
    loop.create_task(_nats.loop())  #, "NATS interface")


async def subscribe(subject: str, callback: callable):
    await _nats.subscribe(subject, callback)


async def publish(subject: str, payload: BaseModel):
    await _nats.publish(subject, payload)
