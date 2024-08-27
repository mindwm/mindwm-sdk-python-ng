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


def test_kafka_cdc():

    response = client.post("/", headers=headers, content=json.dumps(payload))
    assert response.status_code == 200
    #assert response.json() == {"msg": "Hello World"}
