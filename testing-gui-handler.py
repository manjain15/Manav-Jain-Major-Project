import unittest
from unittest.mock import Mock, patch
import tkinter
import customtkinter
from main import gui_handler

class TestGuiHandler(unittest.TestCase):
    
    @patch('customtkinter.CTk')
    @patch('customtkinter.CTkFrame')
    @patch('customtkinter.CTkLabel')
    def test_initialization(self, mock_label, mock_frame, mock_tk):
        master = Mock()
        gui = gui_handler(master)

        # Check title is set correctly
        master.title.assert_called_with("ViewTrip")

        # Check the default color theme is set
        customtkinter.set_default_color_theme.assert_called_with("green-white.json")

        # Check the start screen is shown
        self.assertIsNotNone(gui.current_screen)

        # Ensure the start screen is a frame
        mock_frame.assert_called_with(master)
        mock_frame().pack.assert_called_with(side="top", fill="both", expand=True)
    
    @patch('customtkinter.CTkFrame')
    @patch('customtkinter.CTkLabel')
    @patch('customtkinter.CTkButton')
    def test_show_start_screen(self, mock_button, mock_label, mock_frame):
        master = Mock()
        gui = gui_handler(master)
        gui.show_start_screen()
        
        # Ensure current screen is destroyed if it exists
        mock_frame().destroy.assert_called()

        # Ensure start screen frame is created and packed
        mock_frame.assert_called_with(master)
        mock_frame().pack.assert_called_with(side="top", fill="both", expand=True)

        # Check labels and buttons are created
        self.assertTrue(mock_label.called)
        self.assertTrue(mock_button.called)
        
    @patch('customtkinter.CTkFrame')
    @patch('customtkinter.CTkLabel')
    @patch('customtkinter.CTkButton')
    @patch('customtkinter.CTkEntry')
    def test_show_selection_screen(self, mock_entry, mock_button, mock_label, mock_frame):
        master = Mock()
        gui = gui_handler(master)
        gui.show_selection_screen()

        # Ensure current screen is destroyed if it exists
        mock_frame().destroy.assert_called()

        # Ensure selection screen frame is created and packed
        mock_frame.assert_called_with(master)
        mock_frame().pack.assert_called_with(fill='both', expand=True, padx=10, pady=10)

        # Check labels, comboboxes, calendar, time picker, and entry are created
        self.assertTrue(mock_label.called)
        self.assertTrue(mock_button.called)
        self.assertTrue(mock_entry.called)
        
        # Simulate user input and check validity
        gui.current_screen = mock_frame()
        gui.show_selection_screen()
        
        start_station_combobox = mock_entry.return_value
        start_station_combobox.get.return_value = 'Valid Start'
        
        destination_combobox = mock_entry.return_value
        destination_combobox.get.return_value = 'Valid Destination'
        
        cal = Mock()
        cal.get_date.return_value = '20230518'
        
        time_picker = Mock()
        time_picker.time.return_value = ('10', '00')
        
        no_of_trips_entry = mock_entry.return_value
        no_of_trips_entry.get.return_value = '1'
        
        # Call check_validity with valid data
        gui.check_validity()
        
        # Ensure show_train_screen is called with valid data
        gui.show_train_screen.assert_called_with('Valid Start', 'Valid Destination', '20230518', '1000', 1)
    
    @patch('customtkinter.CTkFrame')
    @patch('customtkinter.CTkLabel')
    @patch('tkinter.ttk.Treeview')
    def test_show_train_screen(self, mock_treeview, mock_label, mock_frame):
        master = Mock()
        gui = gui_handler(master)
        gui.show_train_screen('Start', 'Destination', '20230518', '1000', 3)

        # Ensure current screen is destroyed if it exists
        mock_frame().destroy.assert_called()

        # Ensure train screen frame is created and packed
        mock_frame.assert_called_with(master)
        mock_frame().pack.assert_called_with(fill="both", expand=True, padx=10, pady=10)

        # Check labels and treeview are created
        self.assertTrue(mock_label.called)
        self.assertTrue(mock_treeview.called)
        
        # Ensure treeview is populated
        tree = mock_treeview.return_value
        self.assertTrue(tree.insert.called)
    
    @patch('customtkinter.CTkFrame')
    @patch('tkinter.ttk.Treeview')
    @patch('redis.Redis')
    def test_show_display_saved_trips_screen(self, mock_redis, mock_treeview, mock_frame):
        master = Mock()
        gui = gui_handler(master)
        mock_redis().keys.return_value = [b'trip1', b'trip2']
        
        gui.show_display_saved_trips_screen()

        # Ensure current screen is destroyed if it exists
        mock_frame().destroy.assert_called()

        # Ensure display saved trips screen frame is created and packed
        mock_frame.assert_called_with(master)
        mock_frame().pack.assert_called_with(fill="both", expand=True, padx=10, pady=10)

        # Check treeview is created and populated with trips
        self.assertTrue(mock_treeview.called)
        tree = mock_treeview.return_value
        self.assertTrue(tree.insert.called)
        self.assertEqual(tree.insert.call_count, 2)
        


        


