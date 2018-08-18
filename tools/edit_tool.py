from .tool import Tool
import component_display
from utils import MouseButton


class EditTool(Tool):
    def __init__(self):
        self._move_component = None
        self._edit_component = None
        self._offset = None

    def on_click(self, app, event, button, position, component):
        if button == MouseButton.LEFT and component is not None:
            self._move_component = component
            self._offset = component.display.position - position
        elif button == MouseButton.RELEASE_LEFT:
            self._move_component = None
        elif button == MouseButton.RIGHT:
            if component is not None:
                self._edit_component = component
                display = self._edit_component.display
                display.outline_color = component_display.BLUE
                app.show_component_properties(self._edit_component)
                app.repaint()
            else:
                self.reset(app)

    def on_move(self, app, event, position):
        if self._move_component:
            self._move_component.display.position = self._offset + position
            app.repaint()

    def reset(self, app):
        if self._edit_component:
            display = self._edit_component.display
            display.outline_color = component_display.BLACK
            app.hide_component_properties()
            app.repaint()
        self._move_component = None
        self._edit_component = None
