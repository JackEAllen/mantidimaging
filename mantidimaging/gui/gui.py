from __future__ import absolute_import, division, print_function

import sys

from PyQt5.Qt import QApplication

from mantidimaging.core.algorithms import registrator
from mantidimaging.core.algorithms.registrator.gui_registrator import gui_register
from mantidimaging.gui.main_window.mw_view import MainWindowView

import mantidimaging.core.filters


def execute(config):
    # create the GUI event loop
    q_application = QApplication(sys.argv)
    application_window = MainWindowView(config)

    # register gui part of algorithms into view
    registrator.register_into(
            application_window.menuFilters, func=gui_register,
            package=mantidimaging.core.filters)

    application_window.show()

    return sys.exit(q_application.exec_())
