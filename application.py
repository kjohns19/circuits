from gi.repository import Gtk, Gdk

import clickers
import component_registry

import collections
import threading


class Application:
    def __init__(self, circuit, ui_config_file):
        self._clickers = {
            'Create': clickers.CreateClicker(),
            'Edit': clickers.EditClicker(),
            'Interact': clickers.InteractClicker(),
            'Wire': clickers.WireClicker()
        }

        self._create_clicker = self._clickers['Create']
        self._clicker = self._create_clicker

        self._mouse_pos = (0, 0)

        builder = Gtk.Builder.new_from_file(ui_config_file)
        builder.connect_signals(self)
        self._window = builder.get_object('main_window')
        self._draw_area = builder.get_object('draw_area')

        self._component_creators = {}
        selector_store = builder.get_object('component_selector_store')
        self.populate_selector_store(
            selector_store, component_registry.registry)

        self._circuit = circuit
        self._update_time = 0.5

    @property
    def circuit(self):
        return self._circuit

    @property
    def update_time(self):
        return self._update_time

    @update_time.setter
    def update_time(self, value):
        self._update_time = value

    def loop(self):
        exit_event = threading.Event()

        def update_thread():
            while not exit_event.wait(self._update_time):
                self._circuit.update()
                self.repaint()

        update_thread = threading.Thread(target=update_thread)
        update_thread.start()

        self._window.show_all()
        Gtk.main()

        exit_event.set()
        update_thread.join()

    def repaint(self):
        self._draw_area.queue_draw()

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

    def handler_exit(self, widget):
        Gtk.main_quit()

    def handler_new(self, widget):
        self._circuit.clear()
        self.repaint()

    def handler_toggle_mode(self, widget):
        if widget.get_active():
            label = widget.get_label()
            self._clicker = self._clickers[label]

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
            self._create_clicker.creator = creator

    def handler_draw_area_draw(self, widget, cr):
        for component in self._circuit.components:
            component.display.draw(self, cr)
        for component in self._circuit.components:
            component.display.draw_input_wires(self, cr)
        if self._clicker:
            self._clicker.draw(self, cr, self._mouse_pos)

    def handler_draw_area_mouse_button(self, widget, event):
        position = (event.x, event.y)
        component = self._circuit.component_at_position(position)

        button = event.button
        if event.type == Gdk.EventType.BUTTON_RELEASE:
            button = -event.button

        self._clicker.on_click(self, event, button, position, component)
        return True

    def handler_draw_area_mouse_move(self, widget, event):
        self._mouse_pos = (event.x, event.y)
        self._clicker.on_move(self, event, self._mouse_pos)
