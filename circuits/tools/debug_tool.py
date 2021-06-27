import typing as t

from gi.repository import Gdk  # type: ignore

from . import tool

if t.TYPE_CHECKING:
    from .. import application
    from .. import component as component_mod


class DebugTool(tool.Tool):
    def on_left_click(self, app: 'application.Application', event: Gdk.EventButton,
                      position: tuple[float, float],
                      component: t.Optional['component_mod.Component']) -> None:
        if component is not None:
            component.display.debug = not component.display.debug
            app.repaint()
