from component import Component
from component_registry import registry
import utils


CATEGORY = 'Output'


@registry.register('Display', CATEGORY)
def make_display(circuit):
    def on_draw(component, app, cr):
        text = str(component.inputs[0].value)
        position = component.display.position + (0, 8)
        utils.draw_text(cr, text, position)

    return Component(
        circuit, num_inputs=1, num_outputs=0, on_draw=on_draw)
