from component import Component
from component_registry import registry

import cairo


CATEGORY = 'Output'


@registry.register('Display', CATEGORY)
def make_display(circuit):
    def on_draw(component, window, cr):
        cr.set_source_rgb(0, 0, 0)
        cr.select_font_face(
            'FreeSans',
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(12)

        text = str(component.inputs[0].value)
        x, y, w, h, dx, dy = cr.text_extents(text)

        cr.move_to(*(component.display.position - (w/2, -h/2)))
        cr.show_text(text)

    return Component(
        circuit, num_inputs=1, num_outputs=0, on_draw=on_draw)
