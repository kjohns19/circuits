import shapes

import math


WIDTH = 40

OUTLINE_WIDTH = 1

NODE_SEPARATION = 20
NODE_RADIUS = 8

BLACK = (0, 0, 0)
WHITE = (1, 1, 1)
RED   = (1, 0, 0)
GREEN = (0, 1, 0)


class ComponentDisplay:
    def __init__(self, component):
        self._component = component

        max_nodes = max(len(component.inputs), len(component.outputs))
        height = NODE_SEPARATION * max_nodes + NODE_SEPARATION//2
        self._rect = shapes.Rectangle(size=(WIDTH, height))

    @property
    def position(self):
        return self._rect.position

    @position.setter
    def position(self, value):
        self._rect.position = value

    def contains(self, point):
        return self._rect.contains(point)

    def _node_pos(self, input, idx):
        offset = WIDTH/2 * (-1 if input else 1)
        center = self._rect.position + (offset, 0)
        count = len(
            self._component.inputs if input else self._component.outputs)
        start_y = center.y - (count-1)*NODE_SEPARATION//2
        return (center.x, start_y + NODE_SEPARATION*idx)

    def draw(self, window, cr):
        cr.rectangle(*self._rect.top_left, *self._rect.size)

        cr.set_source_rgb(*WHITE)
        cr.fill_preserve()

        cr.set_source_rgb(*BLACK)
        cr.set_line_width(2)
        cr.stroke()

        def draw_nodes(input, count):
            for i in range(count):
                position = self._node_pos(input, i)
                cr.arc(*position, NODE_RADIUS, 0, math.pi*2)
                cr.set_source_rgb(*WHITE)
                cr.fill_preserve()

                cr.set_source_rgb(*BLACK)
                cr.set_line_width(2)
                cr.stroke()

        draw_nodes(True, len(self._component.inputs))
        draw_nodes(False, len(self._component.outputs))

    def draw_input_wires(self, window, cr):
        connections = self._component.input_connections

        for input_idx, connection in enumerate(connections):
            if connection is None:
                continue
            component, output_idx = connection

            input_pos = self._node_pos(True, input_idx)
            output_pos = component.display._node_pos(False, output_idx)

            color = GREEN if self._component.new_inputs[input_idx] else RED

            cr.set_source_rgb(*color)
            cr.move_to(*input_pos)
            cr.line_to(*output_pos)
            cr.set_line_width(2)
            cr.stroke()
