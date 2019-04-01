from .tool import Tool
import utils


class WireTool(Tool):
    def __init__(self):
        super().__init__()
        self._input = None

    def on_right_click(self, app, event, position, component):
        if self._input is None and component is not None:
            def callback(idx, selection):
                component.inputs[idx].disconnect()
                app.repaint()

            title = 'Delete Input?'
            options = [input.label for input in component.inputs]
            utils.show_popup(title, options, event, callback)
        else:
            self._input = None
            app.repaint()

    def on_left_click(self, app, event, position, component):
        if component is None:
            return

        def input_callback(idx, selection):
            self._input = component.inputs[idx]

        def output_callback(idx, selection):
            output = component.outputs[idx]
            self._input.connect(output)
            self._input = None
            app.repaint()

        if self._input is None:
            nodes = component.inputs
            title = 'Inputs'
            callback = input_callback
        else:
            nodes = component.outputs
            title = 'Outputs'
            callback = output_callback

        options = [node.label for node in nodes]
        utils.show_popup(title, options, event, callback)

    def on_move(self, app, event, position):
        super().on_move(app, event, position)
        if self._input is not None:
            app.repaint()

    def draw(self, app, cr, mouse_pos):
        if self._input is None:
            return

        display = self._input.component.display

        node_pos = display.node_pos(input=True, idx=self._input.index)
        color = (0, 0, 0)
        utils.draw_line(cr, mouse_pos, node_pos, color)
