from mindwm import logging
from mindwm.model.events import IoDocument
from mindwm.knfunc.decorators import iodoc, app

logger = logging.getLogger(__name__)

@iodoc
async def func(iodocument: IoDocument, username: str):
    logger.info(username)
    logger.info(iodocument)
