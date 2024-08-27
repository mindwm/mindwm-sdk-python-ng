from mindwm import logging
from mindwm.knfunc.decorators import Request, Response, app, event, kafka_cdc
from mindwm.model.events import from_request, to_response
from mindwm.model.graph import KafkaCdc

logger = logging.getLogger(__name__)


@event
async def func(obj: KafkaCdc, request: Request, response: Response):
    logger.info(obj)
    ev = await from_request(request)
    match obj.payload.type:
        case 'relationship':
            ev.traceparent = obj.payload.traceparent
        case 'node':
            if obj.meta.operation != 'deleted':
                ev.traceparent = obj.payload.after.properties.traceparent
            else:
                ev.traceparent = obj.payload.before.properties.traceparent

    resp = to_response(ev)
    return resp
