from .clicker import Clicker

from gi.repository import Gtk


class WireClicker(Clicker):
    def __init__(self):
        self._input = None

    def on_click(self, app, event, position, component):
        if component is None:
            self._input = None
            return

        def input_callback(item):
            self._input = component.inputs[item]

        def output_callback(item):
            output = component.outputs[item]
            self._input.connect(output)
            self._input = None
            app.repaint()

        if self._input is None:
            popup = _create_popup(
                'Inputs', component.num_inputs, input_callback)
        else:
            popup = _create_popup(
                'Outputs', component.num_outputs, output_callback)

        popup.popup(None, None, None, None, event.button, event.time)


def _create_popup(title, item_count, callback):
    ui_xml_prefix = '<ui><popup name="popup"><menuitem action="title"/>'
    ui_xml_suffix = '</popup></ui>'

    ui_xml = ui_xml_prefix + ''.join(
        '<menuitem action="choice{}"/>'.format(item)
        for item in range(item_count)
    ) + ui_xml_suffix

    manager = Gtk.UIManager()
    manager.add_ui_from_string(ui_xml)

    action_group = Gtk.ActionGroup('actions')
    title_action = Gtk.Action('title', title, None, None)
    title_action.set_sensitive(False)
    action_group.add_action(title_action)
    for item in range(item_count):
        def action_callback(widget, item=item):
            callback(item)

        action = Gtk.Action(
            'choice{}'.format(item), str(item+1), None, None)
        action.connect('activate', action_callback)
        action_group.add_action(action)

    manager.insert_action_group(action_group)

    popup = manager.get_widget('/popup')
    return popup
