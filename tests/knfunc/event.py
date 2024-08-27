from mindwm import logging
from mindwm.model.events import MindwmEvent
from mindwm.model.objects import Ping, IoDocument, Pong
from mindwm.knfunc.decorators import event, app
from uuid import uuid4

logger = logging.getLogger(__name__)

@event
async def test_event(obj: IoDocument):
    logger.info(obj)
    logger.info(type(obj))
    return Pong(uuid=obj.uuid)
