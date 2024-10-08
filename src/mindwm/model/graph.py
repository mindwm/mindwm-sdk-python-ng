from datetime import datetime
from typing import (Annotated, Any, ClassVar, Dict, List, Literal, Optional,
                    TypeVar, Union)

import mindwm.model.objects as objects
from neontology import BaseNode, BaseRelationship
from pydantic import BaseModel, ConfigDict, Field, model_validator


class MindwmNode(BaseNode):
    atime: Optional[int] = 0
    created: Optional[datetime] = None
    merged: Optional[datetime] = None
    traceparent: Optional[str] = None
    #    atime: datetime = Field(
    #    default_factory=datetime.now
    #)


class User(MindwmNode, objects.User):
    __primarylabel__: ClassVar[str] = "User"
    __primaryproperty__: ClassVar[str] = "username"
    type: Literal[
        'org.mindwm.v1.graph.node.user'] = 'org.mindwm.v1.graph.node.user'


class Host(MindwmNode, objects.Host):
    __primarylabel__: ClassVar[str] = "Host"
    __primaryproperty__: ClassVar[str] = "hostname"
    type: Literal[
        'org.mindwm.v1.graph.node.host'] = 'org.mindwm.v1.graph.node.host'


class Tmux(MindwmNode, objects.Tmux):
    __primarylabel__: ClassVar[str] = "Tmux"
    __primaryproperty__: ClassVar[str] = "socket_path"
    type: Literal[
        'org.mindwm.v1.graph.node.tmux'] = 'org.mindwm.v1.graph.node.tmux'


class TmuxSession(MindwmNode, objects.TmuxSession):
    __primarylabel__: ClassVar[str] = "TmuxSession"
    __primaryproperty__: ClassVar[str] = "name"
    type: Literal[
        'org.mindwm.v1.graph.node.tmuxsession'] = 'org.mindwm.v1.graph.node.tmuxsession'


class TmuxPane(MindwmNode, objects.TmuxPane):
    __primarylabel__: ClassVar[str] = "TmuxPane"
    __primaryproperty__: ClassVar[str] = "title"
    type: Literal[
        'org.mindwm.v1.graph.node.tmuxpane'] = 'org.mindwm.v1.graph.node.tmuxpane'


class IoDocument(MindwmNode, objects.IoDocument):
    __primarylabel__: ClassVar[str] = "IoDocument"
    __primaryproperty__: ClassVar[str] = "uuid"
    type: Literal[
        'org.mindwm.v1.graph.node.iodocument'] = 'org.mindwm.v1.graph.node.iodocument'
    # TODO: (@omgbebebe) need to define a proper validator for
    # relationship validation which fill only primaryproperty field
    # and fail validation iodocument_has_user
    input: Optional[str] = None
    output: Optional[str] = None
    ps1: Optional[str] = None


class Clipboard(MindwmNode, objects.Clipboard):
    __primarylabel__: ClassVar[str] = "Clipboard"
    __primaryproperty__: ClassVar[str] = "uuid"
    data: Optional[str] = None
    time: Optional[int] = None
    uuid: Optional[str] = None
    type: Literal[
        'org.mindwm.v1.graph.node.clipboard'] = 'org.mindwm.v1.graph.node.clipboard'


class Parameter(MindwmNode, objects.Parameter):
    __primarylabel__: ClassVar[str] = "Parameter"
    __primaryproperty__: ClassVar[str] = "key"
    type: Literal[
        'org.mindwm.v1.graph.node.parameter'] = 'org.mindwm.v1.graph.node.parameter'


# Relations
class MindwmRelationship(BaseRelationship):
    traceparent: Optional[str] = None
    created: Optional[datetime] = None
    merged: Optional[datetime] = None
    type: str


class UserHasHost(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_HOST"
    source: User
    target: Host
    type: Literal[
        'org.mindwm.v1.graph.relationship.user_has_host'] = 'org.mindwm.v1.graph.relationship.user_has_host'


class HostHasTmux(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_TMUX"
    source: Host
    target: Tmux
    type: Literal[
        'org.mindwm.v1.graph.relationship.host_has_tmux'] = 'org.mindwm.v1.graph.relationship.host_has_tmux'


class TmuxHasTmuxSession(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_TMUXSESSION"
    source: Tmux
    target: TmuxSession
    type: Literal[
        'org.mindwm.v1.graph.relationship.tmux_has_tmuxsession'] = 'org.mindwm.v1.graph.relationship.tmux_has_tmuxsession'


class TmuxSessionHasTmuxPane(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_TMUXPANE"
    source: TmuxSession
    target: TmuxPane
    type: Literal[
        'org.mindwm.v1.graph.relationship.tmuxsession_has_tmuxpane'] = 'org.mindwm.v1.graph.relationship.tmuxsession_has_tmuxpane'


class TmuxPaneHasIoDocument(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_IODOCUMENT"
    source: TmuxPane
    target: IoDocument
    type: Literal[
        'org.mindwm.v1.graph.relationship.tmuxpane_has_iodocument'] = 'org.mindwm.v1.graph.relationship.tmuxpane_has_iodocument'


class HostHasClipboard(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_CLIPBOARD"
    source: Host
    target: Clipboard
    type: Literal[
        'org.mindwm.v1.graph.relationship.host_has_clipboard'] = 'org.mindwm.v1.graph.relationship.host_has_clipboard'


class UserHasTmux(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_TMUX"
    source: User
    target: Tmux
    type: Literal[
        'org.mindwm.v1.graph.relationship.user_has_tmux'] = 'org.mindwm.v1.graph.relationship.user_has_tmux'


class IoDocumentHasUser(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_USER"
    source: IoDocument
    target: User
    type: Literal[
        'org.mindwm.v1.graph.relationship.iodocument_has_user'] = 'org.mindwm.v1.graph.relationship.iodocument_has_user'


class UserHasParameter(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_PARAMETER"
    source: User
    target: Parameter
    type: Literal[
        'org.mindwm.v1.graph.relationship.user_has_parameter'] = 'org.mindwm.v1.graph.relationship.user_has_parameter'


class HostHasParameter(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_PARAMETER"
    source: Host
    target: Parameter
    type: Literal[
        'org.mindwm.v1.graph.relationship.host_has_parameter'] = 'org.mindwm.v1.graph.relationship.host_has_parameter'


class TmuxHasParameter(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_PARAMETER"
    source: Tmux
    target: Parameter
    type: Literal[
        'org.mindwm.v1.graph.relationship.tmux_has_parameter'] = 'org.mindwm.v1.graph.relationship.tmux_has_parameter'


class TmuxSessionHasParameter(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_PARAMETER"
    source: TmuxSession
    target: Parameter
    type: Literal[
        'org.mindwm.v1.graph.relationship.tmuxsession_has_parameter'] = 'org.mindwm.v1.graph.relationship.tmuxsession_has_parameter'


class TmuxPaneHasParameter(MindwmRelationship):
    __relationshiptype__: ClassVar[str] = "HAS_PARAMETER"
    source: TmuxPane
    target: Parameter
    type: Literal[
        'org.mindwm.v1.graph.relationship.tmuxpane_has_parameter'] = 'org.mindwm.v1.graph.relationship.tmuxpane_has_parameter'


# cloudvent
# source: `org.midwm.context.cyan.knfunc.kafka_cdc
# subject: org.mindwm.context.cyan.graph.node
# type: 'org.mibndwm.v1.graph_change' # payload type

Prop = TypeVar("Prop", User, Host, Tmux, TmuxSession, TmuxPane, IoDocument,
               Clipboard, Parameter)

ChangedObject = Annotated[Union[User, Host, Tmux, TmuxSession, TmuxPane,
                                IoDocument, Clipboard, Parameter, UserHasHost,
                                HostHasTmux, HostHasClipboard,
                                HostHasParameter, TmuxHasTmuxSession,
                                TmuxHasParameter, TmuxSessionHasTmuxPane,
                                TmuxSessionHasParameter, TmuxPaneHasIoDocument,
                                TmuxPaneHasParameter, IoDocumentHasUser,
                                TmuxPaneHasIoDocument, UserHasTmux],
                          Field(discriminator='type')]


class GraphObjectCreated(BaseModel):
    type: Literal[
        'org.mindwm.v1.graph.created'] = 'org.mindwm.v1.graph.created'
    obj: ChangedObject


class GraphObjectUpdated(BaseModel):
    type: Literal[
        'org.mindwm.v1.graph.updated'] = 'org.mindwm.v1.graph.updated'
    obj: ChangedObject


class GraphObjectDeleted(BaseModel):
    type: Literal[
        'org.mindwm.v1.graph.deleted'] = 'org.mindwm.v1.graph.deleted'
    obj: ChangedObject


# kafka-source cdc events
class KafkaCdcMeta(BaseModel):
    timestamp: int
    username: str
    txId: int
    txEventId: int
    txEventsCount: int
    operation: str
    source: Dict[str, str]


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
        if self.meta.operation != 'deleted':
            if type(self.payload) is KafkaCdcRelation:
                return self.payload.before.properties
            else:
                return self.get_object_after()
        else:
            if type(self.payload) is KafkaCdcRelation:
                return self.payload.after.properties
            else:
                return self.get_object_before()


class GraphObjectChanged(BaseModel):

    @classmethod
    def from_kafka_cdc(self, cdc: KafkaCdc):
        match cdc.payload.type:
            case 'node':
                if cdc.meta.operation == 'deleted':
                    obj_payload = cdc.payload.before
                else:
                    obj_payload = cdc.payload.after

                label = obj_payload.labels[0].lower()
                props = obj_payload.properties
                obj_dict = {
                    "type": f"org.mindwm.v1.graph.{cdc.meta.operation}",
                    "obj": props.model_dump(),
                }

            case 'relationship':
                start_label = cdc.payload.start.labels[0].lower()
                start_ids = cdc.payload.start.ids
                start_node = {
                    "type": f"org.mindwm.v1.graph.node.{start_label}"
                } | start_ids
                end_label = cdc.payload.end.labels[0].lower()
                end_ids = cdc.payload.end.ids
                end_node = {
                    "type": f"org.mindwm.v1.graph.node.{end_label}"
                } | end_ids
                obj_type = f"org.mindwm.v1.graph.relationship.{start_label}_{cdc.payload.label.lower()}"
                obj_dict = {
                    "type": f"org.mindwm.v1.graph.{cdc.meta.operation}",
                    "obj": {
                        "source": start_node,
                        "target": end_node,
                        "type": obj_type,
                    }
                }
        match cdc.meta.operation:
            case 'created':
                return GraphObjectCreated.model_validate(obj_dict)
            case 'updated':
                return GraphObjectUpdated.model_validate(obj_dict)
            case 'deleted':
                return GraphObjectDeleted.model_validate(obj_dict)
