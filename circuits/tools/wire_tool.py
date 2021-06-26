from gi.repository import Gdk  # type: ignore
import cairo
import typing as t

from .. import utils
from .. import shapes

from . import tool

if t.TYPE_CHECKING:
    from .. import application
    from .. import component as component_mod


class WireTool(tool.Tool):
    def __init__(self) -> None:
        super().__init__()
        self._input: t.Optional['component_mod._Input'] = None
        self._wire_positions: list[shapes.Vector2] = []

    def on_left_click(self, app: 'application.Application', event: Gdk.EventButton,
                      position: tuple[float, float],
                      component: t.Optional['component_mod.Component']) -> None:
        if component is None:
            if self._input is not None:
                snap_position = app.snap_position(position)
                self._wire_positions.append(snap_position)
                app.repaint()
            return

        def input_callback(idx: int, selection: str) -> None:
            assert component is not None
            self._input = component.inputs[idx]

        def output_callback(idx: int, selection: str) -> None:
            assert component is not None
            assert self._input is not None
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

    def on_right_click(self, app: 'application.Application', event: Gdk.EventButton,
                       position: tuple[float, float],
                       component: t.Optional['component_mod.Component']) -> None:
        if self._input is None and component is not None:
            def callback(idx: int, selection: str) -> None:
                assert component is not None
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

    def on_move(self, app: 'application.Application', event: Gdk.EventButton,
                position: tuple[float, float]) -> None:
        super().on_move(app, event, position)
        if self._input is not None:
            app.repaint()

    def draw(self, app: 'application.Application', cr: cairo.Context,
             mouse_pos: tuple[float, float]) -> None:
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

    def reset(self, app: 'application.Application') -> None:
        self._input = None
        self._wire_positions = []
        app.repaint()
