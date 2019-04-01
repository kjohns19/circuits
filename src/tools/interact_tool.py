from .tool import Tool
import utils


class InteractTool(Tool):
    def __init__(self):
        super().__init__()
        self._component = None

    def on_left_click(self, app, event, position, component):
        self._do_click(
            app, event, utils.MouseButton.LEFT, position, component)

    def on_left_release(self, app, event, position, component):
        self._do_click(
            app, event, utils.MouseButton.RELEASE_LEFT, position, component)

    def on_right_click(self, app, event, position, component):
        self._do_click(
            app, event, utils.MouseButton.RIGHT, position, component)

    def on_right_release(self, app, event, position, component):
        self._do_click(
            app, event, utils.MouseButton.RELEASE_RIGHT, position, component)

    def _do_click(self, app, event, button, position, component):
        if utils.MouseButton.is_press(button):
            self._component = component
        else:
            component = self._component
            self._component = None

        if component is None:
            return

        component.on_click(button)
        app.repaint()
