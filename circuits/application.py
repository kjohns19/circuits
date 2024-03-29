import collections
import itertools
import json
import threading
import typing as t

from gi.repository import Gtk, Gdk  # type: ignore
import cairo

from . import component_registry
from . import draw
from . import save_load
from . import shapes
from . import tools
from . import utils

if t.TYPE_CHECKING:
    from . import circuit as circuit_mod
    from . import component as component_mod
    from . import creator
    from . import properties


class Application:
    def __init__(self, circuit: 'circuit_mod.Circuit') -> None:
        self._create_tool = tools.CreateTool()
        self._edit_tool = tools.EditTool()
        self._tool: tools.Tool = self._create_tool

        self._tools: dict[str, tools.Tool] = {
            'Create': self._create_tool,
            'Edit': self._edit_tool,
            'Interact': tools.InteractTool(),
            'Wire': tools.WireTool(),
            'Debug': tools.DebugTool()
        }

        self._position = shapes.Vector2((0.0, 0.0))
        self._mouse_pos = shapes.Vector2((0.0, 0.0))
        self._grid_size = 20

        self._zoom_levels = [0.25, 0.5, 1.0, 2.0]
        self._grid_surfaces = [
            cairo.ImageSurface.create_from_png(utils.data_file(f'grid{size:02}.png'))
            for size in [5, 10, 20, 40]
        ]

        self._zoom_idx = 2

        builder = Gtk.Builder.new_from_file(utils.data_file('ui.glade'))
        builder.connect_signals(self)

        self._window = utils.get_builder_obj(
            builder, 'main_window', Gtk.Window)
        self._draw_area = utils.get_builder_obj(
            builder, 'draw_area', Gtk.DrawingArea)

        self._component_creators: dict[str, creator.Creator] = {}
        selector_store = utils.get_builder_obj(
            builder, 'component_selector_store', Gtk.TreeStore)
        self.populate_selector_store(
            selector_store, component_registry.registry)

        self._property_box = utils.get_builder_obj(
            builder, 'property_box', Gtk.Box)

        self._edit_tool_button = utils.get_builder_obj(
            builder, 'tool_button_mode_edit', Gtk.ToolButton)

        self._step_button = utils.get_builder_obj(
            builder, 'tool_button_step', Gtk.ToolButton)
        self._playing = threading.Event()
        self._stepping = threading.Event()
        self._update_time = 0.5
        speed_button = utils.get_builder_obj(
            builder, 'play_speed_button', Gtk.SpinButton)
        speed_button.set_value(self._update_time*1000)

        self._circuit = circuit
        self._color_updates = False
        self._keys: set[str] = set()

        save_load.register_window(self._window)

    @property
    def circuit(self) -> 'circuit_mod.Circuit':
        return self._circuit

    @property
    def grid_size(self) -> int:
        return self._grid_size

    @property
    def position(self) -> shapes.Vector2:
        return self._position

    @position.setter
    def position(self, value: shapes.Vector2) -> None:
        self._position = value
        self.repaint()

    def center_position(self) -> None:
        def min_bounds(r1: shapes.Rectangle, r2: shapes.Rectangle) -> shapes.Rectangle:
            left = min(r1.left, r2.left)
            right = max(r1.right, r2.right)
            top = min(r1.top, r2.top)
            bottom = max(r1.bottom, r2.bottom)
            return shapes.Rectangle((right - left, bottom - top), (left, top))

        rect: t.Optional[shapes.Rectangle] = None
        for component in self._circuit.components:
            if rect is None:
                rect = component.display.bounds
            else:
                rect = min_bounds(rect, component.display.bounds)

        if rect is not None:
            self.position = rect.center

    @property
    def size(self) -> shapes.Vector2:
        draw_size = self._draw_area.get_allocated_size().allocation
        return shapes.Vector2((draw_size.width, draw_size.height))

    @property
    def scale(self) -> float:
        return self._zoom_levels[self._zoom_idx]

    def is_key_pressed(self, keyname: str) -> bool:
        return keyname in self._keys

    def screen_position(self, position: shapes.Vector2) -> shapes.Vector2:
        return (position - self._position) * self.scale + self.size / 2

    def position_from_screen(self, position: shapes.Vector2) -> shapes.Vector2:
        return (position - self.size / 2) / self.scale + self._position

    def loop(self) -> None:
        exit_event = threading.Event()

        def update_thread_func() -> None:
            while True:
                self._playing.wait()
                if exit_event.is_set():
                    break
                self._circuit.update()
                self.repaint()
                if self._stepping.is_set():
                    self._playing.clear()
                    self._stepping.clear()
                elif exit_event.wait(self._update_time):
                    break

        update_thread = threading.Thread(target=update_thread_func)
        update_thread.start()

        self._window.show_all()
        Gtk.main()

        self._playing.set()  # so the update thread can exit
        exit_event.set()
        update_thread.join()

    def repaint(self) -> None:
        self._draw_area.queue_draw()

    def show_component_properties(self, component: 'component_mod.Component') -> None:
        def callback(property: 'properties.Property[t.Any]',
                     component: 'component_mod.Component',
                     value: t.Any) -> None:
            self.repaint()
        creator = component.creator
        if creator is None:
            return

        dialog = Gtk.Dialog(
            'Edit Properties', self._window, 0,
            (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))

        widgets = creator.get_property_widgets(component, callback)
        box = dialog.get_content_area()

        box.add(Gtk.Label(label=f'Component: {creator.name}'))

        for widget in widgets:
            box.add(widget)

        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def populate_selector_store(self, selector_store: Gtk.TreeStore,
                                registry: component_registry.Registry) -> None:
        data: dict[str, list[str]] = collections.defaultdict(list)
        for cd in registry.get_component_data():
            data[cd.category].append(cd.name)
            category_name = '/'.join([cd.category, cd.name])
            self._component_creators[category_name] = cd.creator

        for category, names in data.items():
            iter = selector_store.append(None, [category, None])
            for name in names:
                selector_store.append(iter, [name, category])

    def snap_position(self, position: shapes.Vector2) -> shapes.Vector2:
        return (position / self._grid_size).round() * self._grid_size

    def handler_exit(self, widget: Gtk.Widget) -> None:
        Gtk.main_quit()

    def handler_new(self, widget: Gtk.Widget) -> None:
        self._circuit.clear()
        for tool in self._tools.values():
            tool.reset(self)
        self._position = shapes.Vector2((0.0, 0.0))
        self.repaint()

    def handler_save(self, widget: Gtk.Widget) -> None:
        filename = save_load.show_save_dialog(
            'Save Circuit', 'Circuit files', '*.circuit')
        if filename is None:
            return

        data = {
            'position': tuple(self._position),
            'circuit': self._circuit.get_save_data()
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def handler_load(self, widget: Gtk.Widget) -> None:
        filename = save_load.show_load_dialog(
            'Load Circuit', 'Circuit files', '*.circuit')
        if filename is None:
            return

        with open(filename, 'r') as f:
            data = json.load(f)

        pos: list[float] = data['position']
        self._position = shapes.Vector2((pos[0], pos[1]))

        self._circuit.load(data['circuit'])
        self.center_position()

    def handler_export_module(self, widget: Gtk.Widget) -> None:
        filename = save_load.show_save_dialog(
            'Export Module', 'Circuit files', '*.circuit')
        if filename is None:
            return

        selected = self._edit_tool.selected_components()
        components = utils.get_connected_components(selected)

        data = {
            'position': tuple(self._position),
            'circuit': self._circuit.get_save_data(components)
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def handler_import_module(self, widget: Gtk.Widget) -> None:
        filename = save_load.show_load_dialog(
            'Import Module', 'Circuit files', '*.circuit')
        if filename is None:
            return

        with open(filename, 'r') as f:
            data = json.load(f)

        new_components = self._circuit.load_module(data['circuit'])
        wire_nodes: list['component_mod.WireNode'] = []
        for component in new_components:
            for input in component.inputs:
                wire_nodes.extend(input.wire_nodes)
        self._edit_tool_button.set_active(True)
        self._edit_tool.select(new_components, wire_nodes)

    def handler_play(self, widget: Gtk.ToggleToolButton) -> None:
        active = widget.get_active()
        self._step_button.set_sensitive(not active)
        if active:
            widget.set_stock_id('gtk-media-pause')
            self._playing.set()
        else:
            widget.set_stock_id('gtk-media-play')
            self._playing.clear()

    def handler_step(self, widget: Gtk.Widget) -> None:
        self._stepping.set()
        self._playing.set()

    def handler_speed_set(self, widget: Gtk.SpinButton) -> None:
        self._update_time = widget.get_value_as_int() / 1000.0

    def handler_toggle_color_updates(self, widget: Gtk.ToggleToolButton) -> None:
        self._color_updates = widget.get_active()

    def handler_toggle_mode(self, widget: Gtk.RadioToolButton) -> None:
        if widget.get_active():
            label = widget.get_label()
            self._tool.reset(self)
            self._tool = self._tools[label]

    def handler_component_selection(self, widget: Gtk.TreeSelection) -> None:
        model, iter = widget.get_selected()
        if iter is not None:
            selected = model[iter]
            name = selected[0]
            category = selected[1]
            if category is None:
                return
            category_name = '/'.join([category, name])
            creator = self._component_creators[category_name]
            self._create_tool.creator = creator

            widgets = creator.get_property_widgets()
            for widget in self._property_box.get_children():
                self._property_box.remove(widget)
            for widget in widgets:
                self._property_box.add(widget)

    def handler_draw_area_draw(self, widget: Gtk.Widget, cr: cairo.Context) -> None:
        with draw.save_state(cr):
            # Round to prevent issues drawing images at fractional positions
            cr.translate(*-(self._position * self.scale - self.size / 2).round())
            grid = self._grid_surfaces[self._zoom_idx]
            cr.set_source_surface(grid, 0, 0)
            cr.get_source().set_extend(cairo.EXTEND_REPEAT)
            cr.paint()

        with draw.save_state(cr):
            cr.translate(*self.size/2)
            cr.scale(self.scale, self.scale)
            cr.translate(*-self._position)

            # Color components that are updating in the next step
            if self._color_updates:
                next_updates, later_updates = self._circuit.components_to_update()
                save_colors = {
                    component: component.display.fill_color
                    for component in itertools.chain(next_updates, later_updates)
                }
                # Components updating next are slightly blue
                for component in next_updates:
                    component.display.fill_color = draw.Color((0.9, 0.9, 1.0))
                # Components updating later are light gray
                for component in later_updates:
                    component.display.fill_color = draw.Color((0.9, 0.9, 0.9))

            for component in self._circuit.components:
                component.display.draw(self, cr)
            for component in self._circuit.components:
                component.display.draw_input_wires(self, cr, debugging=False)
            for component in self._circuit.components:
                component.display.draw_input_wires(self, cr, debugging=True)
            for component in self._circuit.components:
                component.display.draw_debug_values(self, cr)
            self._tool.draw(self, cr, self._mouse_pos)

        # Reset the color of the components that will update
        if self._color_updates:
            for component in next_updates:
                component.display.fill_color = save_colors[component]
            for component in later_updates:
                component.display.fill_color = save_colors[component]

        with draw.save_state(cr):
            mouse_pos = (self._mouse_pos / self._grid_size).round()
            draw_pos = shapes.Vector2((10, self.size.y - 10))
            draw.text(cr, str(mouse_pos), draw_pos, size=12,
                      h_align=draw.TextHAlign.LEFT, v_align=draw.TextVAlign.BOTTOM)

    def handler_draw_area_mouse_button(self, widget: Gtk.Widget,
                                       event: Gdk.EventButton) -> bool:
        position = self.position_from_screen(shapes.Vector2((event.x, event.y)))
        component = self._circuit.component_at_position(position)

        if event.type == Gdk.EventType.BUTTON_PRESS:
            self._draw_area.grab_focus()

        button = event.button
        if event.type == Gdk.EventType.BUTTON_RELEASE:
            button = -event.button

        self._tool.on_click(self, event, button, position, component)
        return True

    def handler_draw_area_mouse_move(self, widget: Gtk.Widget,
                                     event: Gdk.EventMotion) -> None:
        self._mouse_pos = self.position_from_screen(shapes.Vector2((event.x, event.y)))
        self._tool.on_move(self, event, self._mouse_pos)
        self.repaint()

    def handler_draw_area_key_press(self, widget: Gtk.Widget,
                                    event: Gdk.EventKey) -> None:
        self._circuit.handle_key_press(event)
        self.repaint()

    def handler_draw_area_key_release(self, widget: Gtk.Widget,
                                      event: Gdk.EventKey) -> None:
        self._circuit.handle_key_release(event)
        self.repaint()

    def handler_key_press(self, window: Gtk.Window, event: Gdk.EventKey) -> None:
        keyname = Gdk.keyval_name(event.keyval)
        self._keys.add(keyname)

    def handler_key_release(self, window: Gtk.Window, event: Gdk.EventKey) -> None:
        keyname = Gdk.keyval_name(event.keyval)
        if keyname in self._keys:
            self._keys.remove(keyname)

    def handler_zoom_in(self, widget: Gtk.Widget) -> None:
        if self._zoom_idx < len(self._zoom_levels) - 1:
            self._zoom_idx += 1
            self.repaint()

    def handler_zoom_out(self, widget: Gtk.Widget) -> None:
        self.repaint()
        if self._zoom_idx > 0:
            self._zoom_idx -= 1
            self.repaint()
