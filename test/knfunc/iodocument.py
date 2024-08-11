from mindwm import logger
from mindwm.model.events import IoDocument
from mindwm.knfunc.decorators import iodocument, app

@iodocument
async def func(iodocument: IoDocument):
    logger.info(iodocument.model_dump())
    return {"result": "Success"}
