from .tool import Tool


class EditTool(Tool):
    def on_left_click(self, app, event, position, component):
        if component is not None:
            app.show_component_properties(component)
