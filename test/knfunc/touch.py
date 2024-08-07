from mindwm.model.events import Touch
from mindwm.knfunc.decorators import app, logger, touch

@touch
def func(touch: Touch):
    logger.warning(touch.ids)
