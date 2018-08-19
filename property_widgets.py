from gi.repository import Gtk


def create_value_bool_widget(label, callback, initial_value=False):
    ''' Return a widget for setting a boolean '''
    builder = Gtk.Builder.new_from_file('./data/one_value.glade')
    builder.get_object('bool_label').set_text(label)
    builder.get_object('bool_button').set_active(initial_value)

    class Handler:
        def handler_value_set(self, widget, value):
            callback(value)

    builder.connect_signals(Handler())
    return builder.get_object('bool_widget')


def create_value_int_widget(label, callback,
                            min_value=0, max_value=10,
                            initial_value=0):
    ''' Return a widget for setting an integer '''
    builder = Gtk.Builder.new_from_file('./data/one_value.glade')
    builder.get_object('number_label').set_text(label)
    builder.get_object('number_button').set_value(initial_value)
    adjustment = builder.get_object('number_adjustment')
    adjustment.set_lower(min_value)
    adjustment.set_upper(max_value)

    class Handler:
        def handler_value_set(self, widget):
            callback(widget.get_value_as_int())

    builder.connect_signals(Handler())
    return builder.get_object('number_widget')


def create_value_string_widget(label, callback, initial_value=''):
    ''' Return a widget for setting a boolean '''
    builder = Gtk.Builder.new_from_file('./data/one_value.glade')
    builder.get_object('string_label').set_text(label)
    builder.get_object('string_entry').set_text(initial_value)

    class Handler:
        def handler_value_set(self, widget):
            callback(widget.get_text())

    builder.connect_signals(Handler())
    return builder.get_object('string_widget')


def create_multi_value_widget(title, callback, labels, initial_values):
    ''' Return a widget for setting a constant number of values '''
    assert len(labels) == len(initial_values)

    def label_func(idx):
        return labels[idx]

    return _create_generic_multi_value_widget(
        title, callback, label_func,
        len(initial_values), len(initial_values),
        initial_values)


def create_ranged_multi_value_widget(title, callback,
                                     min_values=1, max_values=10,
                                     initial_values=None):
    ''' Return a widget for setting a variable number of values '''
    def label_func(idx):
        return str(idx+1)

    return _create_generic_multi_value_widget(
        title, callback, label_func, min_values, max_values, initial_values)


def _create_generic_multi_value_widget(title, callback,
                                       label_func,
                                       min_values, max_values,
                                       initial_values):
    assert min_values <= len(initial_values) <= max_values
    builder = Gtk.Builder.new_from_file('./data/list_values.glade')

    builder.get_object('title').set_text(title)

    # Only show count selection if it can change
    if min_values == max_values:
        main_box = builder.get_object('main_box')
        count_box = builder.get_object('count_box')
        main_box.remove(count_box)
    else:
        adjustment = builder.get_object('count_adjustment')
        adjustment.set_lower(min_values)
        adjustment.set_upper(max_values)

    widget = builder.get_object('main')

    count = builder.get_object('count')
    values_store = builder.get_object('values_store')

    def to_number(value):
        # Try converting to an int first, then fall back to float
        for type in (int, float):
            try:
                value = type(value)
                return value
            except ValueError:
                pass
        return 0

    def to_bool(value):
        try:
            # Try to convert to a number, then to bool
            # this way '0' will be False
            value = bool(float(value))
            return value
        except ValueError:
            pass
        if value == 'False':
            return False
        return True

    types = {
        'String': str,
        'Number': to_number,
        'Boolean': to_bool
    }
    defaults = {
        'String': '',
        'Number': 0,
        'Boolean': False
    }
    default_type = 'Number'
    default_row = [None, default_type, str(defaults[default_type])]

    class RowValue:
        def __init__(self, row):
            self.row = row
            self.type = types[row[1]]
            self.value = self.type(row[2])

        def set_type(self, typestr):
            self.row[1] = typestr
            self.type = types[typestr]
            self.value = defaults[typestr]
            self.row[2] = str(self.value)

        def set_value(self, value):
            self.value = self.type(value)
            self.row[2] = str(self.value)

    # Actual values are stored here rather than in the Gtk object
    # to use real python types instead of Gtk ones
    row_values = []

    def set_values():
        callback([value.value for value in row_values])

    if initial_values is not None:
        for i, value in enumerate(initial_values):
            if isinstance(value, str):
                typestr = 'String'
            elif isinstance(value, bool):  # Must be before number check
                typestr = 'Boolean'
            elif isinstance(value, (int, float)):
                typestr = 'Number'
            else:
                raise TypeError('Invalid type for initial value: {}'.format(
                    type(value).__name__))
            new_row = [label_func(i), typestr, str(value)]
            values_store.append(new_row)
            row_values.append(RowValue(values_store[-1]))
        count.set_value(i+1)

    class Handler:
        def handler_count_set(self, widget):
            current_count = len(values_store)
            new_count = widget.get_value_as_int()
            diff = new_count - current_count
            if diff > 0:
                # Copy the last row into new rows
                if current_count == 0:
                    row = list(default_row)
                else:
                    row = list(values_store[-1])
                for _ in range(diff):
                    row[0] = label_func(len(values_store))
                    values_store.append(row)
                    row_values.append(RowValue(values_store[-1]))
            elif diff < 0:
                # Delete rows
                for _ in range(-diff):
                    del values_store[-1]
                    del row_values[-1]
            set_values()

        def handler_type_set(self, widget, path, value):
            row_values[int(path)].set_type(value)
            set_values()

        def handler_value_set(self, widget, path, value):
            row_values[int(path)].set_value(value)
            set_values()

    builder.connect_signals(Handler())
    return widget
