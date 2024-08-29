from typing import (Annotated, Any, ClassVar, Dict, List, Literal, Optional,
                    Union)
from uuid import uuid4

from pydantic import BaseModel, Field, TypeAdapter, model_validator
from pydantic_core.core_schema import ValidatorFunctionWrapHandler


class MindwmObject(BaseModel):
    _subclasses: ClassVar[dict[str, type[Any]]] = {}
    _discriminating_type_adapter: ClassVar[TypeAdapter]
    traceparent: Optional[str] = None
    tracestate: Optional[str] = None

    @model_validator(mode='wrap')
    @classmethod
    def _parse_into_subclass(
            cls, v: Any,
            handler: ValidatorFunctionWrapHandler) -> 'MindwmObject':
        if cls is MindwmObject:
            return MindwmObject._discriminating_type_adapter.validate_python(v)
        return handler(v)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        MindwmObject._subclasses[cls.model_fields['type'].default] = cls

        # The following will create a new type adapter every time a new subclass is created,
        # which is fine if there aren't that many classes (as far as performance goes)
        MindwmObject._discriminating_type_adapter = TypeAdapter(
            Annotated[Union[tuple(MindwmObject._subclasses.values())],
                      Field(discriminator='type')])

    def to_json(self):
        return self.model_dump_json()

    def model_dump(self, **kwargs):
        """
        This Overrides the default model dump method to exclude None values
        """
        return super().model_dump(exclude_none=True)

    def model_dump_json(self, **kwargs):
        """
        This Overrides the default model dump method to exclude None values
        """
        return super().model_dump_json(exclude_none=True)


class IoDocument(MindwmObject):
    uuid: str = Field(description="uniq action id",
                      default_factory=lambda: uuid4().hex)
    input: str
    output: str
    ps1: str
    type: Literal['org.mindwm.v1.iodocument'] = 'org.mindwm.v1.iodocument'


class Touch(MindwmObject):
    ids: List[int]
    type: Literal['org.mindwm.v1.touch'] = 'org.mindwm.v1.touch'


class LLMAnswer(MindwmObject):
    iodoc_uuid: str = Field(description='An original IoDocument uuid')
    codesnippet: str
    description: str
    type: Literal['org.mindwm.v1.llm_answer'] = 'org.mindwm.v1.llm_answer'


class Clipboard(MindwmObject):
    uuid: str
    time: int
    data: str
    type: Literal['org.mindwm.v1.clipboard'] = 'org.mindwm.v1.clipboard'


class Parameter(MindwmObject):
    key: str
    val: str
    type: Literal['org.mindwm.v1.parameter'] = 'org.mindwm.v1.parameter'


class Ping(MindwmObject):
    uuid: str = Field(description="uniq action id",
                      default_factory=lambda: uuid4().hex)
    payload: Optional[str] = None
    type: Literal['org.mindwm.v1.ping'] = 'org.mindwm.v1.ping'


class Pong(MindwmObject):
    payload: Optional[str] = None
    uuid: str
    type: Literal['org.mindwm.v1.pong'] = 'org.mindwm.v1.pong'


# Actions
class Action(MindwmObject):
    uuid: str = Field(description="uniq action id",
                      default_factory=lambda: uuid4().hex)
    parent_uuid: str = Field(description="uuid of a parent document")
    targets: List[str] = Field(
        description=
        "non-empty list of targets to execute the action on. I.e. identifier of tmux pane"
    )
    type: Literal[
        'org.mindwm.v1.abstract_action'] = 'org.mindwm.v1.abstract_action'


class ShowMessage(Action):
    title: str
    message: str
    type: Literal['org.mindwm.v1.show_message'] = 'org.mindwm.v1.show_message'


class TypeText(Action):
    title: str
    description: str
    snippet: str
    type: Literal['org.mindwm.v1.type_text'] = 'org.mindwm.v1.type_text'


class User(MindwmObject):
    username: str
    type: Literal['org.mindwm.v1.user'] = 'org.mindwm.v1.user'


class Host(MindwmObject):
    hostname: str
    type: Literal['org.mindwm.v1.host'] = 'org.mindwm.v1.host'


class Tmux(MindwmObject):
    # TODO: define a proper validator
    socket_path: str  # f"{username}@{hostname}/{socket_path}"
    type: Literal['org.mindwm.v1.tmux'] = 'org.mindwm.v1.tmux'


class TmuxSession(MindwmObject):
    name: str  # f"{username}@{hostname}/{socket_path}:{tmux_session}"
    type: Literal['org.mindwm.v1.tmux_session'] = 'org.mindwm.v1.tmux_session'


class TmuxPane(MindwmObject):
    title: str  # f"{username}@{hostname}/{socket_path}:{tmux_session}%{pane}"
    type: Literal['org.mindwm.v1.tmux_pane'] = 'org.mindwm.v1.tmux_pane'
