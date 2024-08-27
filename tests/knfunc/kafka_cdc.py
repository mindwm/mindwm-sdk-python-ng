from mindwm import logging
from mindwm.model.graph import KafkaCdc
from mindwm.knfunc.decorators import kafka_cdc, app

logger = logging.getLogger(__name__)

@kafka_cdc
async def func(obj: KafkaCdc):
    logger.info(obj)
    return obj
