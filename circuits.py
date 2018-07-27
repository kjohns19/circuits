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
    adder.connect_input(0, constant, 0)
    adder.connect_input(1, adder, 0)
    adder.display.position = (400, 400)

    display = make_display(circuit)
    display.connect_input(0, adder, 0)
    display.display.position = (500, 600)

    app.loop()


def make_constant(circuit, values):
    component = Component(circuit, num_inputs=0, num_outputs=len(values))
    component.outputs = values
    return component


def make_adder(circuit, num_inputs=2):
    def adder(component):
        try:
            result = sum(val for val in component.inputs if val is not None)
        except TypeError:
            result = 0
        component.outputs[0] = result
    component = Component(
        circuit, num_inputs=num_inputs, num_outputs=1, on_update=adder)
    return component


def make_display(circuit):
    def display_text(component, window, cr):
        cr.set_source_rgb(0, 0, 0)
        cr.select_font_face(
            'FreeSans',
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(12)

        text = str(component.inputs[0])
        x, y, w, h, dx, dy = cr.text_extents(text)

        cr.move_to(*(component.display.position - (w/2, -h/2)))
        cr.show_text(text)

    component = Component(
        circuit, num_inputs=1, num_outputs=0, on_draw=display_text)
    return component


if __name__ == '__main__':
    main()
