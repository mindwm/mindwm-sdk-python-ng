import mindwm.model.events as events
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from test_objects import models

base_source = "org.mindwm.alice.laptop.tmux.L3RtcC90bXV4LTEwMDAvZGVmYXVsdA==.e3f65957-a3d9-7c45-13b7-9e0a4c61bc0c.23.36"
evs = {
    "manager_iodoc":
    events.MindwmEvent(source=base_source,
                       subject="uptime",
                       data=models['iodoc'],
                       type=models['iodoc'].type),
}


def test_conversion_model_dump_validate():
    for k, v in evs.items():
        x = v.model_dump()
        y = events.MindwmEvent.model_validate(x)
        assert v == y


def test_conversion_model_dump_json_validate():
    for k, v in evs.items():
        x = v.model_dump_json()
        y = events.MindwmEvent.model_validate_json(x)
        assert v == y


app = FastAPI()


@app.post('/')
async def process_event(req: Request):
    ev = await events.from_request(req)
    return events.to_response(ev)


client = TestClient(app)


def test_conversion_isomorphism():
    for k, v in evs.items():
        (headers, body) = events.to_request(v)
        response = client.post("/", headers=headers, content=body)
        assert response.status_code == 200
        obj = events.from_response(response)
        assert obj == v
