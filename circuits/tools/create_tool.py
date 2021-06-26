from gi.repository import Gdk  # type: ignore
import typing as t

from .. import utils

from . import tool

if t.TYPE_CHECKING:
    from .. import application
    from .. import component as component_mod
    from .. import creator as creator_mod


class CreateTool(tool.Tool):
    def __init__(self, creator: t.Optional['creator_mod.Creator'] = None) -> None:
        super().__init__()
        self._creator = creator
        self._component: t.Optional['component_mod.Component'] = None

    @property
    def creator(self) -> t.Optional['creator_mod.Creator']:
        return self._creator

    @creator.setter
    def creator(self, value: t.Optional['creator_mod.Creator']) -> None:
        self._creator = value

    def on_left_click(self, app: 'application.Application', event: Gdk.EventButton,
                      position: tuple[float, float],
                      component: t.Optional['component_mod.Component']) -> None:
        if self._creator is not None:
            self._component = self._creator(app.circuit)
            self._component.display.position = (
                app.snap_position(position) - (0, app.grid_size/2))
            app.repaint()

    def on_left_release(self, app: 'application.Application', event: Gdk.EventButton,
                        position: tuple[float, float],
                        component: t.Optional['component_mod.Component']) -> None:
        self._component = None

    def on_right_click(self, app: 'application.Application', event: Gdk.EventButton,
                       position: tuple[float, float],
                       component: t.Optional['component_mod.Component']) -> None:
        if not component:
            return

        if component is self._component:
            component.delete()
            app.repaint()
            self._component = None
            return

        def callback(idx: int, selection: str) -> None:
            assert component is not None
            if selection == 'Yes':
                component.delete()
                app.repaint()

        utils.show_popup('Delete?', ['Yes', 'No'], event, callback)

    def on_move(self, app: 'application.Application', event: Gdk.EventButton,
                position: tuple[float, float]) -> None:
        super().on_move(app, event, position)
        if self._component:
            self._component.display.position = (
                app.snap_position(position) - (0, app.grid_size/2))
            app.repaint()
