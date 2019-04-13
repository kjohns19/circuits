from .tool import Tool
import shapes
import utils


class EditTool(Tool):
    def __init__(self):
        super().__init__()
        self._components = set()
        self._move_data = []

    def _set(self, components, position):
        self._move_data = [
            (component, component.display.position - position)
            for component in components
        ]

    def on_left_click(self, app, event, position, component):
        ctrl = any(
            app.is_key_pressed(key)
            for key in ['Control_R', 'Control_L']
        )
        shift = any(
            app.is_key_pressed(key)
            for key in ['Shift_R', 'Shift_L']
        )

        app.repaint()

        if component is not None:
            if component in self._components:
                if shift:
                    self._components.remove(component)
                    return
            else:
                if shift:
                    return
                if not ctrl:
                    self._components.clear()
                self._components.add(component)
        else:
            return

        self._move_data = [
            (component, component.display.position - position)
            for component in self._components
        ]

    def on_left_release(self, app, event, position, component):
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
            app.repaint()

    def draw(self, app, cr, mouse_pos):
        for component in self._components:
            rect = component.display.rect
            rect = shapes.Rectangle(
                size=rect.size+(20, 20),
                position=rect.position-(10, 10))
            utils.draw_rectangle(
                cr, rect, fill_color=None, outline_color=(0, 0, 1))

    def reset(self, app):
        self._components.clear()
