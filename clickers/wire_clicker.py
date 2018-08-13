from .clicker import Clicker
import utils


class WireClicker(Clicker):
    def __init__(self):
        self._input = None

    def on_click(self, app, event, button, position, component):
        if button == utils.MouseButton.RIGHT:
            self.right_click(app, event, button, position, component)
        elif button == utils.MouseButton.LEFT:
            self.left_click(app, event, button, position, component)

    def right_click(self, app, event, button, position, component):
        if self._input is None and component is not None:
            def callback(selection):
                component.inputs[int(selection)].disconnect()
                app.repaint()

            title = 'Delete Input?'
            options = [str(i) for i in range(component.num_inputs)]
            utils.show_popup(title, options, event, callback)
        else:
            self._input = None
            app.repaint()

    def left_click(self, app, event, button, position, component):
        if component is None:
            return

        def input_callback(selection):
            self._input = component.inputs[int(selection)]

        def output_callback(selection):
            output = component.outputs[int(selection)]
            self._input.connect(output)
            self._input = None
            app.repaint()

        if self._input is None:
            count = component.num_inputs
            title = 'Inputs'
            callback = input_callback
        else:
            count = component.num_outputs
            title = 'Outputs'
            callback = output_callback

        options = [str(i) for i in range(count)]
        utils.show_popup(title, options, event, callback)

    def on_move(self, app, event, position):
        if self._input is not None:
            app.repaint()

    def draw(self, app, cr, mouse_pos):
        if self._input is None:
            return

        display = self._input.component.display

        node_pos = display.node_pos(input=True, idx=self._input.index)
        color = (0, 0, 0)
        utils.draw_line(cr, mouse_pos, node_pos, color)
