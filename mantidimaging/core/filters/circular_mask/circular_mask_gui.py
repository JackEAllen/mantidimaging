from __future__ import absolute_import, division, print_function

from functools import partial

from . import execute, NAME


def _gui_register(main_window):
    from mantidimaging.gui.algorithm_dialog import AlgorithmDialog

    dialog = AlgorithmDialog(main_window)
    dialog.setWindowTitle(NAME)

    _, radius_field = dialog.add_property('Radius', 'float', 0.95, (0.0, 1.0))

    _, value_field = dialog.add_property(
            'Set to value', 'float', 0, (-10000, 10000))

    def custom_execute():
        return partial(execute,
                       circular_mask_ratio=radius_field.value(),
                       circular_mask_value=value_field.value())

    # replace dialog function with this one
    dialog.set_execute(custom_execute)
    return dialog


def _gui_register_2(form):
    from mantidimaging.gui.filters_window import add_property_to_form

    _, radius_field = add_property_to_form('Radius', 'float', 0.95, (0.0, 1.0), form=form)

    _, value_field = add_property_to_form(
            'Set to value', 'float', 0, (-10000, 10000), form=form)

    def custom_execute():
        return partial(execute,
                       circular_mask_ratio=radius_field.value(),
                       circular_mask_value=value_field.value())

    return (None, custom_execute, None)
