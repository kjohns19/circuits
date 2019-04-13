from .tool import Tool
import shapes
import utils

import enum


class _Mode(enum.Enum):
    SET = 0
    ADD = 1
    SUBTRACT = 2


class EditTool(Tool):
    def __init__(self):
        super().__init__()
        self._components = set()
        self._move_data = []
        self._select_pos = None

    def _set(self, components, position):
        self._move_data = [
            (component, component.display.position - position)
            for component in components
        ]

    def on_left_click(self, app, event, position, component):
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

    def on_left_release(self, app, event, position, component):
        if self._select_pos:
            mode = _get_mode(app)
            rect = _get_rectangle(self._select_pos, position)
            components = app.circuit.components_in_rectangle(rect)
            self._modify_selection(mode, components)
            self._select_pos = None
            app.repaint()
        else:
            self._move_data = []

    def on_right_click(self, app, event, position, component):
        if component is not None:
            app.show_component_properties(component)

    def on_move(self, app, event, position):
        super().on_move(app, event, position)
        if self._move_data:
            for component, offset in self._move_data:
                component.display.position = (
                    app.snap_position(offset + position) - (0, app.grid_size/2)
                )
        if self._move_data or self._select_pos:
            app.repaint()

    def draw(self, app, cr, mouse_pos):
        color = (0, 0, 1)
        for component in self._components:
            rect = component.display.rect
            rect = shapes.Rectangle(
                size=rect.size+(20, 20),
                position=rect.position-(10, 10))
            utils.draw_rectangle(
                cr, rect, fill_color=None, outline_color=color)

        if self._select_pos:
            rect = _get_rectangle(self._select_pos, mouse_pos)
            utils.draw_rectangle(
                cr, rect, fill_color=None, outline_color=color)

    def reset(self, app):
        self._components.clear()

    def _modify_selection(self, mode, components):
        if mode == _Mode.SET:
            self._components.clear()

        for component in components:
            if component in self._components:
                if mode == _Mode.SUBTRACT:
                    self._components.remove(component)
            elif mode != _Mode.SUBTRACT:
                self._components.add(component)


def _get_rectangle(corner1, corner2):
    corner1 = shapes.Vector2(corner1)
    corner2 = shapes.Vector2(corner2)
    position = (min(corner1.x, corner2.x), min(corner1.y, corner2.y))
    size = (abs(corner1.x - corner2.x), abs(corner1.y - corner2.y))
    return shapes.Rectangle(size, position)


def _get_mode(app):
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
