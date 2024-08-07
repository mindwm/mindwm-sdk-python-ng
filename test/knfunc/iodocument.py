from mindwm.model.events import IoDocument
from mindwm.knfunc.decorators import iodocument, app, logger

@iodocument
def func(iodocument: IoDocument):
    logger.warning(iodocument.input)
