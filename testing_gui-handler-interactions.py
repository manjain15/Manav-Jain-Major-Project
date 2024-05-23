import pytest
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import customtkinter as ctk
from main import gui_handler

@pytest.fixture
def app(qtbot):
    test_app = QtWidgets.QApplication([])
    gui = gui_handler(test_app)
    qtbot.addWidget(gui.master)
    return gui

def test_add_new_trip_button(qtbot, app):
    button = app.add_new_trip
    qtbot.mouseClick(button, QtCore.Qt.LeftButton)

    # Check if the selection screen is displayed
    assert isinstance(app.current_screen, ctk.CTkFrame)
    assert app.current_screen.findChild(ctk.CTkLabel, "Select Starting Stop:")

def test_invalid_entry_shows_error(qtbot, app):
    qtbot.keyClicks(app.start_station_combobox, '')
    qtbot.keyClicks(app.destination_combobox, '')
    qtbot.keyClicks(app.no_of_trips_entry, '0')
    
    next_button = app.next_button
    qtbot.mouseClick(next_button, QtCore.Qt.LeftButton)

    # Check if error message or screen reload is triggered
    assert isinstance(app.current_screen, ctk.CTkFrame)
    assert app.current_screen.findChild(ctk.CTkLabel, "Error: Please enter valid input for all fields!")

