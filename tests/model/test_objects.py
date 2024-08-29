from uuid import uuid4

import mindwm.model.objects as objects

models = {
    "iodoc":
    objects.IoDocument(
        input="uptime",
        output=
        "11:55:06  up 17 days 19:23,  3 users,  load average: 0.24, 0.32, 0.48",
        ps1="user@mindwm-host:~/work/dev$"),
    "touch":
    objects.Touch(ids=[1, 2, 3]),
    "llm_answer":
    objects.LLMAnswer(iodoc_uuid=uuid4().hex,
                      codesnippet="ssh user@host -A",
                      description="some description"),
    "ping":
    objects.Ping(uuid=uuid4().hex, payload="1234567890"),
    "pong":
    objects.Pong(uuid=uuid4().hex, payload="1234567890"),
    "show_message":
    objects.ShowMessage(uuid=uuid4().hex,
                        parent_uuid=uuid4().hex,
                        targets=["targetA", "pane0"],
                        title="some title",
                        message="some message"),
    "type_text":
    objects.TypeText(uuid=uuid4().hex,
                     parent_uuid=uuid4().hex,
                     targets=["targetA", "pane0"],
                     title="some title",
                     description="some description",
                     snippet="ip r sh"),
    "clipboard":
    objects.Clipboard(uuid=uuid4().hex, time=12345,
                      data="some clipboard data"),
    "parameter":
    objects.Parameter(key="some_key", val="some value"),
    "user":
    objects.User(username="alice"),
    "host":
    objects.Host(hostname="host.local"),
    "tmux":
    objects.Tmux(socket_path="alice@host.local/tmp/tmux-1000/default"),
    "tmux_session":
    objects.TmuxSession(name="alice@host.local/tmp/tmux-1000/default:23"),
    "tmux_pane":
    objects.TmuxPane(title="alice@host.local/tmp/tmux-1000/default:23%36"),
}


def test_model_dump_validate():
    for k, v in models.items():
        x = v.model_dump()
        y = objects.MindwmObject.model_validate(x, strict=True)
        assert v == y


def test_model_dump_json_validate():
    for k, v in models.items():
        x = v.model_dump_json()
        y = objects.MindwmObject.model_validate_json(x, strict=True)
        assert v == y
