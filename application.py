from gi.repository import Gtk, Gdk

import tools
import component_registry
import save_load

import collections
import threading
import json


class Application:
    def __init__(self, circuit, ui_config_file):
        self._tools = {
            'Create': tools.CreateTool(),
            'Edit': tools.EditTool(),
            'Interact': tools.InteractTool(),
            'Wire': tools.WireTool()
        }

        self._create_tool = self._tools['Create']
        self._tool = self._create_tool

        self._mouse_pos = (0, 0)

        builder = Gtk.Builder.new_from_file(ui_config_file)
        builder.connect_signals(self)
        self._window = builder.get_object('main_window')
        self._draw_area = builder.get_object('draw_area')

        self._component_creators = {}
        selector_store = builder.get_object('component_selector_store')
        self.populate_selector_store(
            selector_store, component_registry.registry)

        self._property_box = builder.get_object('property_box')

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

    def show_component_properties(self, component):
        def callback(property, component, value):
            self.repaint()
        creator = component.creator
        widgets = creator.get_property_widgets(component, callback)
        self._recreate_properties_section(widgets)

    def hide_component_properties(self):
        for widget in self._property_box.get_children():
            self._property_box.remove(widget)

    def _recreate_properties_section(self, widgets):
        self.hide_component_properties()
        for widget in widgets:
            self._property_box.pack_start(widget, False, True, 0)

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
        save_load.show_load_dialog(self._window)

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
            self._recreate_properties_section(widgets)

    def handler_draw_area_draw(self, widget, cr):
        for component in self._circuit.components:
            component.display.draw(self, cr)
        for component in self._circuit.components:
            component.display.draw_input_wires(self, cr)
        if self._tool:
            self._tool.draw(self, cr, self._mouse_pos)

    def handler_draw_area_mouse_button(self, widget, event):
        position = (event.x, event.y)
        component = self._circuit.component_at_position(position)

        button = event.button
        if event.type == Gdk.EventType.BUTTON_RELEASE:
            button = -event.button

        self._tool.on_click(self, event, button, position, component)
        return True

    def handler_draw_area_mouse_move(self, widget, event):
        self._mouse_pos = (event.x, event.y)
        self._tool.on_move(self, event, self._mouse_pos)
