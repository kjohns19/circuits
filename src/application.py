from gi.repository import Gtk, Gdk

import component_registry
import save_load
import shapes
import tools
import utils

import cairo
import collections
import json
import threading


class Application:
    def __init__(self, circuit):
        self._tools = {
            'Create': tools.CreateTool(),
            'Edit': tools.EditTool(),
            'Interact': tools.InteractTool(),
            'Wire': tools.WireTool()
        }

        self._create_tool = self._tools['Create']
        self._tool = self._create_tool

        self._position = (0, 0)
        self._mouse_pos = (0, 0)
        self._grid_size = 20
        self._grid_surfaces = {
            20: cairo.ImageSurface.create_from_png(
                utils.data_file('grid20.png'))
        }

        builder = Gtk.Builder.new_from_file(utils.data_file('ui.glade'))
        builder.connect_signals(self)
        self._window = builder.get_object('main_window')
        self._draw_area = builder.get_object('draw_area')

        self._component_creators = {}
        selector_store = builder.get_object('component_selector_store')
        self.populate_selector_store(
            selector_store, component_registry.registry)

        self._property_box = builder.get_object('property_box')

        self._playing = threading.Event()
        self._update_time = 0.5
        speed_button = builder.get_object('play_speed_button')
        speed_button.set_value(self._update_time*1000)

        self._circuit = circuit

    @property
    def circuit(self):
        return self._circuit

    @property
    def grid_size(self):
        return self._grid_size

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = (value[0], value[1])
        self.repaint()

    def screen_position(self, position):
        return (
            position[0] - self._position[0],
            position[1] - self._position[1]
        )

    def loop(self):
        exit_event = threading.Event()

        def update_thread():
            while not exit_event.wait(self._update_time):
                self._playing.wait()
                self._circuit.update()
                self.repaint()

        update_thread = threading.Thread(target=update_thread)
        update_thread.start()

        self._window.show_all()
        Gtk.main()

        self._playing.set()  # so the update thread can exit
        exit_event.set()
        update_thread.join()

    def repaint(self):
        self._draw_area.queue_draw()

    def show_component_properties(self, component):
        def callback(property, component, value):
            self.repaint()
        creator = component.creator

        dialog = Gtk.Dialog(
            'Edit Properties', self._window, 0,
            (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))

        widgets = creator.get_property_widgets(component, callback)
        box = dialog.get_content_area()
        for widget in widgets:
            box.add(widget)

        dialog.run()
        dialog.destroy()

    def populate_selector_store(self, selector_store, registry):
        data = collections.defaultdict(list)
        for cd in registry.get_component_data():
            data[cd.category].append(cd.name)
            category_name = '/'.join([cd.category, cd.name])
            self._component_creators[category_name] = cd.creator

        for category, names in data.items():
            iter = selector_store.append(None, [category, None])
            for name in names:
                selector_store.append(iter, [name, category])

    def snap_position(self, position):
        def round_to_grid(value):
            return int(
                self._grid_size * round(
                    float(value) / self._grid_size))

        position = list(position)
        return shapes.Vector2((
            round_to_grid(position[0]), round_to_grid(position[1])))

    def handler_exit(self, widget):
        Gtk.main_quit()

    def handler_new(self, widget):
        self._circuit.clear()
        self.repaint()

    def handler_save(self, widget):
        filename = save_load.show_save_dialog(self._window, self._circuit)
        if filename is None:
            return

        data = json.dumps(
            self._circuit.get_save_data(),
            indent=4)

        with open(filename, 'w') as f:
            print(data, file=f)

    def handler_load(self, widget):
        filename = save_load.show_load_dialog(self._window)
        if filename is None:
            return

        with open(filename, 'r') as f:
            data = json.load(f)

        self._circuit.load(data)

    def handler_play(self, widget):
        active = widget.get_active()
        if active:
            widget.set_stock_id('gtk-media-pause')
            self._playing.set()
        else:
            widget.set_stock_id('gtk-media-play')
            self._playing.clear()

    def handler_speed_set(self, widget):
        self._update_time = widget.get_value_as_int() / 1000.0

    def handler_toggle_mode(self, widget):
        if widget.get_active():
            label = widget.get_label()
            self._tool.reset(self)
            self._tool = self._tools[label]

    def handler_component_selection(self, widget):
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

    def handler_draw_area_draw(self, widget, cr):
        cr.translate(-self._position[0], -self._position[1])
        cr.set_source_surface(self._grid_surfaces[self._grid_size], 0, 0)
        cr.get_source().set_extend(cairo.EXTEND_REPEAT)
        cr.paint()
        for component in self._circuit.components:
            component.display.draw(self, cr)
        for component in self._circuit.components:
            component.display.draw_input_wires(self, cr)
        if self._tool:
            self._tool.draw(self, cr, self._mouse_pos)

    def handler_draw_area_mouse_button(self, widget, event):
        position = (event.x + self._position[0], event.y + self._position[1])
        component = self._circuit.component_at_position(position)

        button = event.button
        if event.type == Gdk.EventType.BUTTON_RELEASE:
            button = -event.button

        self._tool.on_click(self, event, button, position, component)
        return True

    def handler_draw_area_mouse_move(self, widget, event):
        self._mouse_pos = (
            event.x + self._position[0],
            event.y + self._position[1]
        )
        self._tool.on_move(self, event, self._mouse_pos)
