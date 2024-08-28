from datetime import datetime
from typing import (Annotated, Any, ClassVar, Dict, List, Literal, Optional,
                    TypeVar, Union)

from neontology import BaseNode, BaseRelationship
from pydantic import BaseModel, ConfigDict, Field

from .objects import IoDocument


class MindwmNode(BaseNode):
    atime: Optional[int] = 0
    created: Optional[datetime] = None
    merged: Optional[datetime] = None
    traceparent: Optional[str] = None
    #    atime: datetime = Field(
    #    default_factory=datetime.now
    #)


class User(MindwmNode):
    __primarylabel__: ClassVar[str] = "User"
    __primaryproperty__: ClassVar[str] = "username"
    username: str


class Host(MindwmNode):
    __primarylabel__: ClassVar[str] = "Host"
    __primaryproperty__: ClassVar[str] = "hostname"
    hostname: str


class Tmux(MindwmNode):
    __primarylabel__: ClassVar[str] = "Tmux"
    __primaryproperty__: ClassVar[str] = "socket_path"
    # TODO: define a proper validator
    socket_path: str  # f"{username}@{hostname}/{socket_path}"


class TmuxSession(MindwmNode):
    __primarylabel__: ClassVar[str] = "TmuxSession"
    __primaryproperty__: ClassVar[str] = "name"
    name: str  # f"{username}@{hostname}/{socket_path}:{tmux_session}"


class TmuxPane(MindwmNode):
    __primarylabel__: ClassVar[str] = "TmuxPane"
    __primaryproperty__: ClassVar[str] = "title"
    title: str  # f"{username}@{hostname}/{socket_path}:{tmux_session}%{pane}"


class IoDocument(MindwmNode, IoDocument):
    __primarylabel__: ClassVar[str] = "IoDocument"
    __primaryproperty__: ClassVar[str] = "uuid"
    uuid: str


class Clipboard(MindwmNode):
    __primarylabel__: ClassVar[str] = "Clipboard"
    __primaryproperty__: ClassVar[str] = "uuid"
    uuid: str
    time: int
    data: str


class Parameter(MindwmNode):
    __primarylabel__: ClassVar[str] = "Parameter"
    __primaryproperty__: ClassVar[str] = "key"
    key: str
    val: str


# Relations
class MindwmRelationship(BaseRelationship):
    traceparent: Optional[str] = None
    created: Optional[datetime] = None
    merged: Optional[datetime] = None


class UserHasHost(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_HOST"
    source: User
    target: Host


class HostHasTmux(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_TMUX"
    source: Host
    target: Tmux


class TmuxHasTmuxSession(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_TMUX_SESSION"
    source: Tmux
    target: TmuxSession


class TmuxSessionHasTmuxPane(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_TMUX_PANE"
    source: TmuxSession
    target: TmuxPane


class TmuxPaneHasIoDocument(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_IO_DOCUMENT"
    source: TmuxPane
    target: IoDocument


class HostHasClipboard(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_CLIPBOARD"
    source: Host
    target: Clipboard


class UserHasTmux(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_TMUX"
    source: User
    target: Tmux


class IoDocumentHasUser(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_USER"
    source: IoDocument
    target: User


class UserHasParameter(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_PARAMETER"
    source: User
    target: Parameter


class HostHasParameter(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_PARAMETER"
    source: Host
    target: Parameter


class TmuxHasParameter(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_PARAMETER"
    source: Tmux
    target: Parameter


class TmuxSessionHasParameter(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_PARAMETER"
    source: TmuxSession
    target: Parameter


class TmuxPaneHasParameter(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_PARAMETER"
    source: TmuxPane
    target: Parameter


# kafka-source cdc events
class KafkaCdcMeta(BaseModel):
    timestamp: int
    username: str
    txId: int
    txEventId: int
    txEventsCount: int
    operation: str
    source: Dict[str, str]


Prop = TypeVar("Prop", User, Host, Tmux, TmuxSession, TmuxPane, IoDocument,
               Clipboard, Parameter)


class KafkaCdcRelNode(BaseModel):
    id: str
    labels: List[str]
    ids: Dict[str, str]


class KafkaCdcRelProp(BaseModel):
    # FIX: more pricise parametrization if needed
    properties: Any


class KafkaCdcRelation(BaseModel):
    id: int
    start: KafkaCdcRelNode
    end: KafkaCdcRelNode
    before: Optional[KafkaCdcRelProp] = None
    after: Optional[KafkaCdcRelProp] = None
    label: str
    type: Literal['relationship'] = 'relationship'
    traceparent: Optional[str] = None


class KafkaCdcNodeData(BaseModel):
    properties: Prop
    labels: List[str]


class KafkaCdcNode(BaseModel):
    id: int
    type: Literal['node'] = 'node'
    before: Optional[KafkaCdcNodeData] = None
    after: Optional[KafkaCdcNodeData] = None


class KafkaCdcSchema(BaseModel):
    properties: Dict[str, str]
    constraints: List[Any]


class KafkaCdc(BaseModel):
    meta: KafkaCdcMeta
    payload: Annotated[Union[KafkaCdcNode, KafkaCdcRelation],
                       Field(discriminator='type')]
    cdc_schema: KafkaCdcSchema = Field(..., alias='schema')
    type: Literal['dev.knative.kafka.event'] = 'dev.knative.kafka.event'

    model_config = ConfigDict(populate_by_name=True)

    def get_object_before(self):
        return self.payload.before.properties

    def get_object_after(self):
        return self.payload.after.properties

    def get_object(self):
        if self.payload.meta.operation != 'deleted':
            return self.get_object_after()
        else:
            return self.get_object_before()
