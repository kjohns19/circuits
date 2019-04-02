from .tool import Tool


class DebugTool(Tool):
    def on_left_click(self, app, event, position, component):
        if component is not None:
            component.display.debug = not component.display.debug
            app.repaint()
