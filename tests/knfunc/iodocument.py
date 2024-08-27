from mindwm import logging
from mindwm.model.events import IoDocument, IoDocumentEvent
from mindwm.knfunc.decorators import iodoc, app

logger = logging.getLogger(__name__)

@iodoc
async def func(iodocument: IoDocument, username: str, pane_title: str):
    logger.info(username)
    logger.info(iodocument)
    logger.info(pane_title)
    return IoDocumentEvent(data=iodocument)
