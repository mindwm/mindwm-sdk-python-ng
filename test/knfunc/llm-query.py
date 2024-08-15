from mindwm import logging
from mindwm.model.events import IoDocument, LLMAnswer
from mindwm.knfunc.decorators import iodoc, app

logger = logging.getLogger(__name__)

@iodoc
async def llm_answer(iodocument: IoDocument, username: str, pane_title: str):
    logger.info(username)
    logger.info(iodocument)
    logger.info(pane_title)
    return LLMAnswer(codesnippet="omg", description="bebebe")
