import typing as t

from gi.repository import Gdk  # type: ignore
import cairo

from .. import shapes
from .. import utils

if t.TYPE_CHECKING:
    from .. import application
    from .. import component as component_mod


class Tool:
    def __init__(self) -> None:
        self._app_pos: t.Optional[shapes.Vector2] = None
        self._mouse_pos: t.Optional[shapes.Vector2] = None
        self._mouse_screen_pos: t.Optional[shapes.Vector2] = None

    def on_click(self, app: 'application.Application', event: Gdk.EventButton,
                 button: utils.MouseButton, position: shapes.Vector2,
                 component: t.Optional['component_mod.Component']) -> None:
        {
            utils.MouseButton.LEFT: self.on_left_click,
            utils.MouseButton.RELEASE_LEFT: self.on_left_release,
            utils.MouseButton.MIDDLE: self.on_middle_click,
            utils.MouseButton.RELEASE_MIDDLE: self.on_middle_release,
            utils.MouseButton.RIGHT: self.on_right_click,
            utils.MouseButton.RELEASE_RIGHT: self.on_right_release,
        }.get(button, lambda *args: None)(app, event, position, component)

    def on_left_click(self, app: 'application.Application', event: Gdk.EventButton,
                      position: shapes.Vector2,
                      component: t.Optional['component_mod.Component']) -> None:
        pass

    def on_left_release(self, app: 'application.Application', event: Gdk.EventButton,
                        position: shapes.Vector2,
                        component: t.Optional['component_mod.Component']) -> None:
        pass

    def on_right_click(self, app: 'application.Application', event: Gdk.EventButton,
                       position: shapes.Vector2,
                       component: t.Optional['component_mod.Component']) -> None:
        pass

    def on_right_release(self, app: 'application.Application', event: Gdk.EventButton,
                         position: shapes.Vector2,
                         component: t.Optional['component_mod.Component']) -> None:
        pass

    def on_middle_click(self, app: 'application.Application', event: Gdk.EventButton,
                        position: shapes.Vector2,
                        component: t.Optional['component_mod.Component']) -> None:
        self._app_pos = app.position
        self._mouse_screen_pos = app.screen_position(position)

    def on_middle_release(self, app: 'application.Application', event: Gdk.EventButton,
                          position: shapes.Vector2,
                          component: t.Optional['component_mod.Component']) -> None:
        self._app_pos = None
        self._mouse_screen_pos = None

    def on_move(self, app: 'application.Application', event: Gdk.EventButton,
                position: shapes.Vector2) -> None:
        if self._app_pos is not None:
            assert self._mouse_screen_pos is not None
            screen_pos = app.screen_position(position)
            app.position = self._app_pos + (self._mouse_screen_pos - screen_pos)

    def draw(self, app: 'application.Application', cr: cairo.Context,
             mouse_pos: shapes.Vector2) -> None:
        pass

    def reset(self, app: 'application.Application') -> None:
        pass
