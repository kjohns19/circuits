#!/usr/bin/env python3.6

import gi
gi.require_version('Gtk', '3.0')

from application import Application
from circuit import Circuit
from component import Component

import cairo


def main():
    circuit = Circuit()
    app = Application(circuit)

    constant = make_constant(circuit, [1])
    constant.display.position = (200, 200)

    adder = make_adder(circuit)
    adder.inputs[0].connect(constant.outputs[0])
    adder.inputs[1].connect(adder.outputs[0])
    adder.display.position = (400, 400)

    display = make_display(circuit)
    display.inputs[0].connect(adder.outputs[0])
    display.display.position = (500, 600)

    app.loop()


def make_constant(circuit, values):
    component = Component(circuit, num_inputs=0, num_outputs=len(values))
    outputs = component.outputs
    for i, value in enumerate(values):
        outputs[i].value = value
    return component


def make_adder(circuit):
    def on_update(component):
        try:
            values = (input.value for input in component.inputs)
            result = sum(val for val in values if val is not None)
        except TypeError:
            result = 0
        component.outputs[0].value = result
    return Component(
        circuit, num_inputs=2, num_outputs=1, on_update=on_update)


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


if __name__ == '__main__':
    main()
