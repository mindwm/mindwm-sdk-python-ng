from mindwm import logging
from mindwm.knfunc.decorators import Request, Response, app, event
from mindwm.model.events import MindwmEvent, from_request, to_response
from mindwm.model.graph import (GraphObjectCreated, GraphObjectDeleted,
                                GraphObjectUpdated, KafkaCdc)

logger = logging.getLogger(__name__)


@event
async def func(obj: KafkaCdc, request: Request, response: Response):
    logger.info(obj)
    cdc_ev = await from_request(request)
    graph_object = obj.get_object()
    match obj.meta.operation:
        case 'created':
            ev_payload = GraphObjectCreated(properties=graph_object)
        case 'updated':
            ev_payload = GraphObjectUpdated(properties=graph_object)
        case 'deleted':
            GraphObjectDeleted(properties=graph_object)

    new_ev = MindwmEvent(
        source=f"org.mindwm.context.cyan.knfunc.kafka_cdc",
        subject=f"org.mindwm.context.cyan.graph.{cdc_ev.data.payload.type}",
        type=ev_payload.type,
        data=ev_payload,
        traceparent=graph_object.traceparent)
    resp = to_response(new_ev)
    return resp
