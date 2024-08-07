from mindwm.model.events import IoDocument
import mindwm.model.graph as g
from mindwm.knfunc.decorators import iodocument_event, app, logger

@iodocument_event
def func(
        iodocument: IoDocument,
        uuid: str,
        username: str,
        hostname: str,
        socket_path: str,
        tmux_session: str,
        tmux_pane: str):

    user = g.User(username=username).merge()
    host = g.Host(hostname=hostname).merge()
    tmux = g.Tmux(socket_path=socket_path).merge()
    sess = g.TmuxSession(name=tmux_session).merge()
    pane = g.TmuxPane(title=tmux_pane).merge()
    iodoc = g.IoDocument(
            uuid=uuid,
            input=iodocument.input,
            output=iodocument.output,
            ps1=iodocument.ps1
        ).merge()
    g.UserHasHost(source=user, target=host).merge()
    g.HostHasTmux(source=host, target=tmux).merge()
    g.TmuxHasTmuxSession(source=tmux, target=sess).merge()
    g.TmuxSessionHasTmuxPane(source=sess, target=pane).merge()
    g.TmuxPaneHasIoDocument(source=pane, target=iodoc).merge()

#    logger.warning(ev.source.split('.'))
