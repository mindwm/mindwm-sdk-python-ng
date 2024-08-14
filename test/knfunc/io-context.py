from mindwm import logging
from mindwm.model.events import IoDocument
from mindwm.knfunc.decorators import iodoc, app

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@iodoc
async def func(
        iodocument: IoDocument,
        graph,
        uuid: str,
        username: str,
        hostname: str,
        socket_path: str,
        tmux_session: str,
        tmux_pane: str):

    logger.debug(f"received: {iodocument}")
    logger.debug(f"socket_path: {socket_path}")

    user = graph.User(username=username).merge()
    host = graph.Host(hostname=hostname).merge()

    socket_path = socket_path.strip("b'").strip('/')
    socket_path = f"{username}@{hostname}/{socket_path}"
    tmux = graph.Tmux(socket_path=socket_path).merge()

    session_id = f"{socket_path}:{tmux_session}"
    sess = graph.TmuxSession(name=session_id).merge()

    tmux_pane = f"{session_id}%{tmux_pane}"
    pane = graph.TmuxPane(title=tmux_pane).merge()

    iodoc = graph.IoDocument(
            uuid=uuid,
            input=iodocument.input,
            output=iodocument.output,
            ps1=iodocument.ps1
        ).create()
    graph.UserHasHost(source=user, target=host).merge()
    graph.HostHasTmux(source=host, target=tmux).merge()
    graph.TmuxHasTmuxSession(source=tmux, target=sess).merge()
    graph.UserHasTmux(source=user, target=tmux).merge()
    graph.TmuxSessionHasTmuxPane(source=sess, target=pane).merge()
    graph.TmuxPaneHasIoDocument(source=pane, target=iodoc).merge()
    graph.IoDocumentHasUser(source=iodoc, target=user).merge()
