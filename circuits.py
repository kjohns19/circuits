#!/usr/bin/env python3.6

import gi
gi.require_version('Gtk', '3.0')

from application import Application
from circuit import Circuit
from component import Component


def main():
    circuit = Circuit()
    constant = make_constant(circuit, [1, 0])
    constant.display.position = (200, 200)
    adder = make_adder(circuit)
    adder.connect_input(0, constant, 0)
    adder.connect_input(1, constant, 1)
    adder.display.position = (400, 400)

    app = Application(circuit)
    app.loop()


def make_constant(circuit, values):
    def noop(component):
        pass
    component = Component(
        circuit, num_inputs=0, num_outputs=len(values), func=noop)
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
        circuit, num_inputs=num_inputs, num_outputs=1, func=adder)
    return component


if __name__ == '__main__':
    main()
