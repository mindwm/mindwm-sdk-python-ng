import json

from fastapi.testclient import TestClient

from .kafka_cdc import app

client = TestClient(app)

headers = {
    "ce-id": "partition:0/offset:52",
    "ce-key": "100-0",
    "ce-knativearrivaltime": "2024-08-27T08:13:50.963498004Z",
    "ce-knativekafkaoffset": "52",
    "ce-knativekafkapartition": "0",
    "ce-partitionkey": "100-0",
    "ce-source":
    "/apis/v1/namespaces/context-cyan/kafkasources/context-cyan-cdc-kafkasource#context-cyan-cdc",
    "ce-specversion": "1.0",
    "ce-subject": "partition:0#52",
    "ce-time": "2024-08-27T08:13:50.953Z",
    "ce-type": "dev.knative.kafka.event",
    "traceparent": "00-ef3d91a5a7326b22aaff9cbd1ecb7b95-6ab8abe47df00f48-01"
}

payload = {
    "meta": {
        "timestamp": 1724746430950,
        "username": "neo4j",
        "txId": 100,
        "txEventId": 0,
        "txEventsCount": 1,
        "operation": "updated",
        "source": {
            "hostname": "cyan-neo4j-0"
        }
    },
    "payload": {
        "id": "0",
        "before": {
            "properties": {
                "atime": 0,
                "traceparent":
                "00-db52d62377f5b810f0349eefc611f87d-93e0c542cf591bd9-01",
                "username": "pion"
            },
            "labels": ["User"]
        },
        "after": {
            "properties": {
                "atime": 0,
                "traceparent":
                "00-b117187d5c326ad085b053bbb5ed8002-034b60237f636967-01",
                "username": "pion"
            },
            "labels": ["User"]
        },
        "type": "node"
    },
    "schema": {
        "properties": {
            "atime": "Long",
            "traceparent": "String",
            "username": "String"
        },
        "constraints": [{
            "label": "User",
            "properties": ["username"],
            "type": "UNIQUE"
        }]
    }
}

iodoc_cdc = {'id': 'partition:0/offset:31', 'key': '"77-0"', 'knativearrivaltime': '2024-08-28T12:52:07.98231106Z', 'knativekafkaoffset': '31','knativekafkapartition': '0', 'partitionkey': '"77-0"', 'source': '/apis/v1/namespaces/context-cyan/kafkasources/context-cyan-cdc-kafkasource#context-cyan-cdc', 'specversion': '1.0', 'subject': 'partition:0#31', 'time': '2024-08-28T12:52:07.638Z', 'type': 'dev.knative.kafka.event', 'data': {'meta': {'timestamp': 1724849527636, 'username': 'neo4j', 'txId': 77, 'txEventId': 0, 'txEventsCount': 1, 'operation': 'created', 'source': {'hostname': 'cyan-neo4j-0'}}, 'payload': {'id': '7', 'before': None, 'after': {'properties': {'output': 'uid=1000(pion) gid=100(users) groups=100(users),1(wheel),26(video),27(dialout),57(networkmanager),67(libvirtd),131(docker),174(input),303(render)', 'input': 'id', 'tracestate': 'subject=id', 'atime': 0, 'traceparent': '00-4b8498bc123ab72f38e9e08c5c365187-516f32a90128c537-01', 'type': 'org.mindwm.v1.iodocument', 'uuid': 'f74f98dd-61c4-406c-9694-cf7cd45e228f','ps1': '❯'}, 'labels': ['IoDocument']}, 'type': 'node'}, 'schema': {'properties': {'output': 'String', 'input': 'String', 'tracestate': 'String', 'atime': 'Long', 'traceparent':'String', 'type': 'String', 'uuid': 'String', 'ps1': 'String'}, 'constraints': []}}}

def test_kafka_cdc():

    response = client.post("/", headers=headers, content=json.dumps(payload))
    assert response.status_code == 200
    assert response.headers['traceparent'] != {
        "traceparent": payload['payload']['after']['properties']['traceparent']
    }

def test_kafka_iodocument_cdc():

    response = client.post("/", headers=headers, content=json.dumps(payload))
    assert response.status_code == 200
    assert response.headers['traceparent'] != {
        "traceparent": payload['payload']['after']['properties']['traceparent']
    }
