from gi.repository import Gdk  # type: ignore
import typing as t

from .. import utils

from . import tool

if t.TYPE_CHECKING:
    from .. import application
    from .. import component as component_mod


class InteractTool(tool.Tool):
    def __init__(self) -> None:
        super().__init__()
        self._component: t.Optional['component_mod.Component'] = None

    def on_left_click(self, app: 'application.Application', event: Gdk.EventButton,
                      position: tuple[float, float],
                      component: t.Optional['component_mod.Component']) -> None:
        self._do_click(
            app, event, utils.MouseButton.LEFT, position, component)

    def on_left_release(self, app: 'application.Application', event: Gdk.EventButton,
                        position: tuple[float, float],
                        component: t.Optional['component_mod.Component']) -> None:
        self._do_click(
            app, event, utils.MouseButton.RELEASE_LEFT, position, component)

    def on_right_click(self, app: 'application.Application', event: Gdk.EventButton,
                       position: tuple[float, float],
                       component: t.Optional['component_mod.Component']) -> None:
        self._do_click(
            app, event, utils.MouseButton.RIGHT, position, component)

    def on_right_release(self, app: 'application.Application', event: Gdk.EventButton,
                         position: tuple[float, float],
                         component: t.Optional['component_mod.Component']) -> None:
        self._do_click(
            app, event, utils.MouseButton.RELEASE_RIGHT, position, component)

    def _do_click(self, app: 'application.Application', event: Gdk.EventButton,
                  button: utils.MouseButton, position: tuple[float, float],
                  component: t.Optional['component_mod.Component']) -> None:
        if utils.MouseButton.is_press(button):
            self._component = component
        else:
            component = self._component
            self._component = None

        if component is None:
            return

        component.on_click(button)
        app.repaint()
