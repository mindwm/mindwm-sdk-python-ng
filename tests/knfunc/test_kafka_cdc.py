import json

import mindwm.model.events as events
import mindwm.model.graph as graph
import mindwm.model.objects as objects
from fastapi.testclient import TestClient

from .kafka_cdc import app

client = TestClient(app)

kafka_cdc_events = {
    "user":
    graph.KafkaCdc(
        meta=graph.KafkaCdcMeta(timestamp=1724929112463,
                                username='neo4j',
                                txId=166,
                                txEventId=0,
                                txEventsCount=1,
                                operation='updated',
                                source={'hostname': 'cyan-neo4j-0'}),
        payload=graph.KafkaCdcNode(
            id=0,
            type='node',
            before=graph.KafkaCdcNodeData(properties=graph.User(
                traceparent=
                '00-0244c99bf5fadc62cf25591940f1ae07-3d3c5f3dfc0911ab-01',
                tracestate=None,
                username='pion',
                type='org.mindwm.v1.graph.node.user',
                created=None,
                merged=None,
                atime=0),
                                          labels=['User']),
            after=graph.KafkaCdcNodeData(properties=graph.User(
                traceparent=
                '00-16d9962444064cca36566af09e332904-af337a466f860a0c-01',
                tracestate=None,
                username='pion',
                type='org.mindwm.v1.graph.node.user',
                created=None,
                merged=None,
                atime=0),
                                         labels=['User'])),
        cdc_schema=graph.KafkaCdcSchema(properties={
            'atime': 'Long',
            'traceparent': 'String',
            'type': 'String',
            'username': 'String'
        },
                                        constraints=[{
                                            'label': 'User',
                                            'properties': ['username'],
                                            'type': 'UNIQUE'
                                        }]),
        type='dev.knative.kafka.event'),
    "user_has_host":
    graph.KafkaCdc(
        meta=graph.KafkaCdcMeta(timestamp=1724929112908,
                                username='neo4j',
                                txId=172,
                                txEventId=0,
                                txEventsCount=1,
                                operation='updated',
                                source={'hostname': 'cyan-neo4j-0'}),
        payload=graph.KafkaCdcRelation(
            id=0,
            start=graph.KafkaCdcRelNode(id='0',
                                        labels=['User'],
                                        ids={'username': 'pion'}),
            end=graph.KafkaCdcRelNode(id='1',
                                      labels=['Host'],
                                      ids={'hostname': 'wrkeys'}),
            before=graph.KafkaCdcRelProp(
                properties={
                    'traceparent':
                    '00-0244c99bf5fadc62cf25591940f1ae07-3d3c5f3dfc0911ab-01',
                    'type': 'org.mindwm.v1.graph.relationship.user_has_host'
                }),
            after=graph.KafkaCdcRelProp(
                properties={
                    'traceparent':
                    '00-16d9962444064cca36566af09e332904-af337a466f860a0c-01',
                    'type': 'org.mindwm.v1.graph.relationship.user_has_host'
                }),
            label='HAS_HOST',
            type='relationship',
            traceparent=None),
        cdc_schema=graph.KafkaCdcSchema(properties={
            'traceparent': 'String',
            'type': 'String'
        },
                                        constraints=[{
                                            'label': 'User',
                                            'properties': ['username'],
                                            'type': 'UNIQUE'
                                        }, {
                                            'label': 'Host',
                                            'properties': ['hostname'],
                                            'type': 'UNIQUE'
                                        }]),
        type='dev.knative.kafka.event'),
    "iodocument_has_user":
    graph.KafkaCdc(
        meta=graph.KafkaCdcMeta(timestamp=1724935151817,
                                username='neo4j',
                                txId=191,
                                txEventId=0,
                                txEventsCount=1,
                                operation='created',
                                source={'hostname': 'cyan-neo4j-0'}),
        payload=graph.KafkaCdcRelation(
            id=10,
            start=graph.KafkaCdcRelNode(
                id='7',
                labels=['IoDocument'],
                ids={'uuid': 'f2bc024a-149f-4d49-9fb4-59fcc8239771'}),
            end=graph.KafkaCdcRelNode(id='0',
                                      labels=['User'],
                                      ids={'username': 'pion'}),
            before=None,
            after=graph.KafkaCdcRelProp(
                properties={
                    'traceparent':
                    '00-7f47a329488353fe16d96b191c2a935c-65f4f48c4dda62e9-01',
                    'type':
                    'org.mindwm.v1.graph.relationship.iodocument_has_user'
                }),
            label='HAS_USER',
            type='relationship',
            traceparent=None),
        cdc_schema=graph.KafkaCdcSchema(properties={
            'traceparent': 'String',
            'type': 'String'
        },
                                        constraints=[{
                                            'label': 'IoDocument',
                                            'properties': ['uuid'],
                                            'type': 'UNIQUE'
                                        }, {
                                            'label': 'User',
                                            'properties': ['username'],
                                            'type': 'UNIQUE'
                                        }]),
        type='dev.knative.kafka.event'),
}


def test_kafka_cdc():
    for k, v in kafka_cdc_events.items():
        ev = events.MindwmEvent(data=v, type=v.type)
        mindwm_cdc = graph.GraphObjectChanged.from_kafka_cdc(v)
        (headers, body) = events.to_request(ev)
        response = client.post("/", headers=headers, content=body)
        assert response.status_code == 200
        resp = events.from_response(response)
        resp_cdc = resp.data
