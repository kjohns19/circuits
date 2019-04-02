from .tool import Tool
import utils


class WireTool(Tool):
    def __init__(self):
        super().__init__()
        self._input = None
        self._wire_positions = []

    def on_right_click(self, app, event, position, component):
        if self._input is None and component is not None:
            def callback(idx, selection):
                component.inputs[idx].disconnect()
                app.repaint()

            title = 'Delete Input?'
            options = [input.label for input in component.inputs]
            utils.show_popup(title, options, event, callback)
        else:
            if self._wire_positions:
                self._wire_positions.pop()
            else:
                self._input = None
            app.repaint()

    def on_left_click(self, app, event, position, component):
        if component is None:
            if self._input is not None:
                position = app.snap_position(position)
                self._wire_positions.append(position)
                app.repaint()
            return

        def input_callback(idx, selection):
            self._input = component.inputs[idx]

        def output_callback(idx, selection):
            output = component.outputs[idx]
            self._input.connect(output, self._wire_positions)
            self._input = None
            self._wire_positions = []
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
        end_pos = app.snap_position(mouse_pos)

        positions = [node_pos] + self._wire_positions + [end_pos]
        color = (0, 0, 0)
        utils.draw_lines(cr, positions, color)
        for pos in self._wire_positions:
            utils.draw_circle(cr, pos, 2, color, color)
