import collections.abc as abc
import json
import typing as t

from gi.repository import Gtk  # type: ignore

from . import save_load
from . import utils


def create_value_bool_widget(label: str, callback: abc.Callable[[bool], None],
                             initial_value: bool = False) -> Gtk.Widget:
    ''' Return a widget for setting a boolean '''
    builder = Gtk.Builder.new_from_file(utils.data_file('one_value.glade'))
    utils.get_builder_obj(builder, 'bool_label', Gtk.Label).set_text(label)
    utils.get_builder_obj(builder, 'bool_button', Gtk.Switch).set_active(initial_value)

    class Handler:
        def handler_value_set(self, widget: Gtk.Widget, value: bool) -> None:
            callback(value)

    builder.connect_signals(Handler())
    return utils.get_builder_obj(builder, 'bool_widget', Gtk.Box)


def create_value_int_widget(label: str, callback: abc.Callable[[int], None],
                            min_value: int = 0, max_value: int = 10,
                            initial_value: int = 0) -> Gtk.Widget:
    ''' Return a widget for setting an integer '''
    builder = Gtk.Builder.new_from_file(utils.data_file('one_value.glade'))
    utils.get_builder_obj(builder, 'number_label', Gtk.Label).set_text(label)
    utils.get_builder_obj(builder, 'number_button',
                          Gtk.SpinButton).set_value(initial_value)
    adjustment = utils.get_builder_obj(builder, 'number_adjustment', Gtk.Adjustment)
    adjustment.set_lower(min_value)
    adjustment.set_upper(max_value)

    class Handler:
        def handler_value_set(self, widget: Gtk.SpinButton) -> None:
            callback(widget.get_value_as_int())

    builder.connect_signals(Handler())
    return utils.get_builder_obj(builder, 'number_widget', Gtk.Box)


def create_value_string_widget(label: str, callback: abc.Callable[[str], None],
                               initial_value: str = '') -> Gtk.Widget:
    ''' Return a widget for setting a boolean '''
    builder = Gtk.Builder.new_from_file(utils.data_file('one_value.glade'))
    utils.get_builder_obj(builder, 'string_label', Gtk.Label).set_text(label)
    utils.get_builder_obj(builder, 'string_entry', Gtk.Entry).set_text(initial_value)

    class Handler:
        def handler_value_set(self, widget: Gtk.Entry) -> None:
            callback(widget.get_text())

    builder.connect_signals(Handler())
    return utils.get_builder_obj(builder, 'string_widget', Gtk.Box)


def create_multi_value_widget(title: str, callback: abc.Callable[[list[t.Any]], None],
                              labels: list[str],
                              initial_values: list[t.Any]) -> Gtk.Widget:
    ''' Return a widget for setting a constant number of values '''
    assert len(labels) == len(initial_values)

    def label_func(idx: int) -> str:
        return labels[idx]

    return _create_generic_multi_value_widget(
        title, callback, label_func,
        len(initial_values), len(initial_values),
        initial_values)


def create_ranged_multi_value_widget(title: str,
                                     callback: abc.Callable[[list[t.Any]], None],
                                     initial_values: list[t.Any],
                                     min_values: int = 1, max_values: int = 10,
                                     start_index: int = 1) -> Gtk.Widget:
    ''' Return a widget for setting a variable number of values '''
    def label_func(idx: int) -> str:
        return str(idx+start_index)

    return _create_generic_multi_value_widget(
        title, callback, label_func, min_values, max_values, initial_values)


def _create_generic_multi_value_widget(title: str,
                                       callback: abc.Callable[[list[t.Any]], None],
                                       label_func: abc.Callable[[int], str],
                                       min_values: int, max_values: int,
                                       initial_values: list[int]) -> Gtk.Widget:
    assert min_values <= len(initial_values) <= max_values
    builder = Gtk.Builder.new_from_file(utils.data_file('list_values.glade'))

    utils.get_builder_obj(builder, 'title', Gtk.Label).set_text(title)

    # Only show count selection if it can change
    if min_values == max_values:
        main_box = utils.get_builder_obj(builder, 'main_box', Gtk.Box)
        count_box = utils.get_builder_obj(builder, 'count_box', Gtk.Box)
        main_box.remove(count_box)
    else:
        adjustment = utils.get_builder_obj(builder, 'count_adjustment', Gtk.Adjustment)
        adjustment.set_lower(min_values)
        adjustment.set_upper(max_values)

    widget = utils.get_builder_obj(builder, 'main', Gtk.Frame)

    count = utils.get_builder_obj(builder, 'count', Gtk.SpinButton)
    values_store = utils.get_builder_obj(builder, 'values_store', Gtk.ListStore)

    def to_number(value: str) -> t.Union[int, float]:
        # Try converting to an int first, then fall back to float
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                pass
        return 0

    def to_bool(value: str) -> bool:
        try:
            # Try to convert to a number, then to bool
            # this way '0' will be False
            return bool(float(value))
        except ValueError:
            pass
        if value == 'False':
            return False
        return True

    def to_none(value: str) -> None:
        return None

    types: dict[str, abc.Callable[[str], t.Any]] = {
        'String': lambda s: s,
        'Number': to_number,
        'Boolean': to_bool,
        'None': to_none
    }
    defaults: dict[str, t.Any] = {
        'String': '',
        'Number': 0,
        'Boolean': False,
        'None': None
    }
    default_type = 'None'
    default_value = str(defaults[default_type])

    class RowValue:
        def __init__(self, row: list[str], type_str: str, value_str: str):
            self._row = row  # The actual row - changing this changes what's displayed
            self.type = types[type_str]
            self.value: t.Any = self.type(value_str)

        def set_type(self, type_str: str) -> None:
            self.type = types[type_str]
            self.value = defaults[type_str]
            self._row[1] = type_str
            self._row[2] = str(self.value)

        def set_value(self, value_str: str) -> None:
            self.value = self.type(value_str)
            self._row[2] = str(self.value)

    # Actual values are stored here rather than in the Gtk object
    # to use real python types instead of Gtk ones
    row_values: list[RowValue] = []

    def set_values() -> None:
        callback([value.value for value in row_values])

    def add_row() -> None:
        # Copy the last row into new rows (if it's there)
        type_str = default_type
        value_str = default_value
        if len(values_store) > 0:
            type_str, value_str = list(values_store[-1])[1:3]
        label = label_func(len(values_store))
        values_store.append([label, type_str, value_str])
        row_values.append(RowValue(values_store[-1], type_str, value_str))

    def delete_row() -> None:
        del values_store[-1]
        del row_values[-1]

    def initialize(values: list[t.Any]) -> None:
        for i, value in enumerate(values):
            if value is None:
                type_str = 'None'
            elif isinstance(value, str):
                type_str = 'String'
            elif isinstance(value, bool):  # Must be before number check
                type_str = 'Boolean'
            elif isinstance(value, (int, float)):
                type_str = 'Number'
            else:
                raise TypeError('Invalid type for initial value: {}'.format(
                    type(value).__name__))
            label = label_func(i)
            values_store.append([label, type_str, str(value)])
            row_values.append(RowValue(values_store[-1], type_str, str(value)))

        # Make sure it's within the limits
        while len(row_values) < min_values:
            add_row()
        while len(row_values) > max_values:
            delete_row()

        count.set_value(len(row_values))

    if initial_values is not None:
        initialize(initial_values)

    class Handler:
        def handler_count_set(self, widget: Gtk.SpinButton) -> None:
            current_count = len(values_store)
            new_count = widget.get_value_as_int()
            diff = new_count - current_count
            if diff > 0:
                for _ in range(diff):
                    add_row()
            elif diff < 0:
                for _ in range(-diff):
                    delete_row()
            set_values()

        def handler_type_set(self, widget: Gtk.Widget, path: str, value: str) -> None:
            row_values[int(path)].set_type(value)
            set_values()

        def handler_value_set(self, widget: Gtk.Widget, path: str, value: str) -> None:
            row_values[int(path)].set_value(value)
            set_values()

        def handler_import(self, widget: Gtk.Widget) -> None:
            filename = save_load.show_load_dialog(
                'Import values', 'JSON Files', '*.json')
            if filename is None:
                return

            with open(filename, 'r') as f:
                values = json.load(f)

            row_values.clear()
            values_store.clear()
            initialize(values)
            set_values()

        def handler_export(self, widget: Gtk.Widget) -> None:
            filename = save_load.show_save_dialog(
                'Export values', 'JSON Files', '*.json')
            if filename is None:
                return

            values = [row.value for row in row_values]

            with open(filename, 'w') as f:
                json.dump(values, f)

    builder.connect_signals(Handler())
    return widget
