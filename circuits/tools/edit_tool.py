import collections.abc as abc
import enum
import typing as t

from gi.repository import Gdk  # type: ignore
import cairo

from .. import draw
from .. import shapes

from . import tool

if t.TYPE_CHECKING:
    from .. import application
    from .. import component as component_mod


class _Mode(enum.Enum):
    SET = 0
    ADD = 1
    SUBTRACT = 2


class EditTool(tool.Tool):
    def __init__(self) -> None:
        super().__init__()
        self._components: set['component_mod.Component'] = set()
        self._move_data: list[tuple['component_mod.Component', shapes.Vector2]] = []
        self._select_pos: t.Optional[shapes.Vector2] = None

    def selected_components(self) -> list['component_mod.Component']:
        return list(self._components)

    def select(self, components: abc.Iterable['component_mod.Component']) -> None:
        self._components.clear()
        self._components.update(components)

    def on_left_click(self, app: 'application.Application', event: Gdk.EventButton,
                      position: shapes.Vector2,
                      component: t.Optional['component_mod.Component']) -> None:
        app.repaint()
        mode = _get_mode(app)

        if component is not None:
            if component not in self._components:
                self._modify_selection(mode, [component])
            self._move_data = [
                (component, component.display.position - position)
                for component in self._components
            ]
        else:
            self._select_pos = position

    def on_left_release(self, app: 'application.Application', event: Gdk.EventButton,
                        position: shapes.Vector2,
                        component: t.Optional['component_mod.Component']) -> None:
        if self._select_pos:
            mode = _get_mode(app)
            rect = _get_rectangle(self._select_pos, position)
            components = app.circuit.components_in_rectangle(rect)
            self._modify_selection(mode, components)
            self._select_pos = None
            app.repaint()
        else:
            self._move_data = []

    def on_right_click(self, app: 'application.Application', event: Gdk.EventButton,
                       position: shapes.Vector2,
                       component: t.Optional['component_mod.Component']) -> None:
        if component is not None:
            app.show_component_properties(component)

    def on_move(self, app: 'application.Application', event: Gdk.EventButton,
                position: shapes.Vector2) -> None:
        super().on_move(app, event, position)
        if self._move_data:
            for component, offset in self._move_data:
                component.display.position = (
                    app.snap_position(offset + position) - (0, app.grid_size/2)
                )
        if self._move_data or self._select_pos:
            app.repaint()

    def draw(self, app: 'application.Application', cr: cairo.Context,
             mouse_pos: shapes.Vector2) -> None:
        color = (0, 0, 1)
        for component in self._components:
            rect = component.display.rect
            rect = shapes.Rectangle(
                size=rect.size+(20, 20),
                position=rect.position-(10, 10))
            draw.rectangle(
                cr, rect, fill_color=None, outline_color=color)

        if self._select_pos:
            rect = _get_rectangle(self._select_pos, mouse_pos)
            draw.rectangle(
                cr, rect, fill_color=None, outline_color=color)

    def reset(self, app: 'application.Application') -> None:
        self._components.clear()
        app.repaint()

    def _modify_selection(self, mode: _Mode,
                          components: abc.Iterable['component_mod.Component']) -> None:
        if mode == _Mode.SET:
            self._components.clear()

        for component in components:
            if component in self._components:
                if mode == _Mode.SUBTRACT:
                    self._components.remove(component)
            elif mode != _Mode.SUBTRACT:
                self._components.add(component)


def _get_rectangle(corner1: shapes.Vector2,
                   corner2: shapes.Vector2) -> shapes.Rectangle:
    position = (min(corner1.x, corner2.x), min(corner1.y, corner2.y))
    size = (abs(corner1.x - corner2.x), abs(corner1.y - corner2.y))
    return shapes.Rectangle(size, position)


def _get_mode(app: 'application.Application') -> _Mode:
    ctrl = any(
        app.is_key_pressed(key)
        for key in ['Control_R', 'Control_L']
    )
    shift = any(
        app.is_key_pressed(key)
        for key in ['Shift_R', 'Shift_L']
    )
    if ctrl:
        return _Mode.ADD
    elif shift:
        return _Mode.SUBTRACT
    return _Mode.SET
