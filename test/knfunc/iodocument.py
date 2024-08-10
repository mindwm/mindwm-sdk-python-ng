from mindwm.model.events import IoDocument
from mindwm.knfunc.decorators import iodocument, app, logger

@iodocument
async def func(iodocument: IoDocument):
    logger.warning(iodocument.model_dump())
    return {"result": "Success"}
