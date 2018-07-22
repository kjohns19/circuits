#!/usr/bin/env python3.6

from circuit import Circuit
from component import Component


def main():
    circuit = Circuit()
    constant = make_constant(circuit, [1, 2])
    adder = make_adder(circuit)
    adder.connect_input(0, constant, 0)
    adder.connect_input(1, constant, 1)
    print(adder)
    circuit.update()
    print(adder)


def make_constant(circuit, values):
    def noop(component):
        pass
    component = Component(
        circuit, num_inputs=0, num_outputs=len(values), func=noop)
    component.outputs = values
    return component


def make_adder(circuit, num_inputs=2):
    def adder(component):
        component.outputs[0] = sum(component.inputs)
    component = Component(
        circuit, num_inputs=num_inputs, num_outputs=1, func=adder)
    return component


if __name__ == '__main__':
    main()
