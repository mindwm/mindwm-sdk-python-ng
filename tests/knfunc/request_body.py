from mindwm import logging
from mindwm.knfunc.decorators import app, request,  request_body

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#@request_body
#async def func(b):
#    logger.error(f"received: {b}")
#    return {"result": "Success"}

@request
async def func(r):
    body = await r.body()
    logger.error(f"headers: {r.headers}\nbody: {body}")
    return {"result": "Success"}
