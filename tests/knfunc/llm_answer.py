from mindwm import logging
from mindwm.model.objects import LLMAnswer, ShowMessage
from mindwm.knfunc.decorators import llm_answer, app

logger = logging.getLogger(__name__)

@llm_answer
async def llm_answer(answer: LLMAnswer):
    logger.info(f"{answer}")
    return ShowMessage(title="omg", message="bebebe", parent_uuid="qwe", targets=["a", "b"])
