import mindwm.model.graph as graph
from mindwm import logging
from mindwm.knfunc.decorators import Request, Response, app, event
from mindwm.model.events import (KafkaCdc, MindwmEvent, from_request,
                                 to_response)

logger = logging.getLogger(__name__)


@event
async def func(obj: KafkaCdc, request: Request, response: Response):
    logger.info(obj)
    cdc_ev = await from_request(request)
    res = graph.GraphObjectChanged.from_kafka_cdc(cdc_ev.data)

    new_ev = MindwmEvent(
        source=f"org.mindwm.context.cyan.knfunc.kafka_cdc",
        subject=f"org.mindwm.context.cyan.graph.{cdc_ev.data.payload.type}",
        type=res.type,
        data=res,
        traceparent=res.obj.traceparent,
    )
    resp = to_response(new_ev)
    return resp
