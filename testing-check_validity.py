import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from main import gui_handler

class gui_handler(unittest.TestCase):
    def setUp(self):
        self.gui_handler = gui_handler()
        self.gui_handler.start_station_combobox = Mock()
        self.gui_handler.destination_combobox = Mock()
        self.gui_handler.cal = Mock()
        self.gui_handler.time_picker = Mock()
        self.gui_handler.no_of_trips_entry = Mock()
        self.gui_handler.show_selection_screen = Mock()
        self.gui_handler.show_train_screen = Mock()
        
        # Mocking valid and invalid stations
        self.gui_handler.start_stations = ['Norwest Station, Norwest Bvd', 'Windsor Rd opp Coronation Rd']
        self.gui_handler.destination_stations = ['Parramatta Station, Stand B3', 'Fairway Dr opp Parsons Cct']

        # Setup the show_selection_screen to define check_validity
        self.gui_handler.show_selection_screen()

        def get_check_validity_function(self):
            # Accessing the check_validity function defined in show_selection_screen
            for name, method in self.gui_handler.selection_screen.method_calls:
                if name == 'check_validity':
                    return method[0]
            return None
    
    def test_valid_inputs(self):
        self.gui_handler.start_station_combobox.get.return_value = 'Norwest Station, Norwest Bvd'
        self.gui_handler.destination_combobox.get.return_value = 'Parramatta Station, Stand B3'
        self.gui_handler.cal.get_date.return_value = datetime.now().strftime('%Y%m%d')
        self.gui_handler.time_picker.time.return_value = (12, 30)
        self.gui_handler.no_of_trips_entry.get.return_value = '1'
        
        check_validity = self.get_check_validity_function()
        check_validity()
        
        self.gui_handler.show_train_screen.assert_called_once_with(
            'Norwest Station, Norwest Bvd', 'Parramatta Station, Stand B3', datetime.now().strftime('%Y%m%d'), '1230', 1
        )
        self.gui_handler.show_selection_screen.assert_not_called()
    
    def test_invalid_origin(self):
        self.gui_handler.start_station_combobox.get.return_value = 'InvalidStation'
        self.gui_handler.destination_combobox.get.return_value = 'Parramatta Station, Stand B3'
        self.gui_handler.cal.get_date.return_value = datetime.now().strftime('%Y%m%d')
        self.gui_handler.time_picker.time.return_value = (12, 30)
        self.gui_handler.no_of_trips_entry.get.return_value = '1'
        
        check_validity = self.get_check_validity_function()
        with patch('easygui.msgbox') as mock_msgbox:
            check_validity()
        
        mock_msgbox.assert_called_once_with("Error: Please enter a valid origin!", title="INVALID INPUT")
        self.gui_handler.show_selection_screen.assert_called_once()
        self.gui_handler.show_train_screen.assert_not_called()
    
    def test_invalid_destination(self):
        self.gui_handler.start_station_combobox.get.return_value = 'Norwest Station, Norwest Bvd'
        self.gui_handler.destination_combobox.get.return_value = 'InvalidStation'
        self.gui_handler.cal.get_date.return_value = datetime.now().strftime('%Y%m%d')
        self.gui_handler.time_picker.time.return_value = (12, 30)
        self.gui_handler.no_of_trips_entry.get.return_value = '1'
        
        check_validity = self.get_check_validity_function()
        with patch('easygui.msgbox') as mock_msgbox:
            check_validity()
        
        mock_msgbox.assert_called_once_with("Error: Please enter a valid destination!", title="INVALID INPUT")
        self.gui_handler.show_selection_screen.assert_called_once()
        self.gui_handler.show_train_screen.assert_not_called()
    
    def test_invalid_number_of_trips(self):
        self.gui_handler.start_station_combobox.get.return_value = 'Norwest Station, Norwest Bvd'
        self.gui_handler.destination_combobox.get.return_value = 'Parramatta Station, Stand B3'
        self.gui_handler.cal.get_date.return_value = datetime.now().strftime('%Y%m%d')
        self.gui_handler.time_picker.time.return_value = (12, 30)
        self.gui_handler.no_of_trips_entry.get.return_value = '0'
        
        check_validity = self.get_check_validity_function()
        with patch('easygui.msgbox') as mock_msgbox:
            check_validity()
        
        mock_msgbox.assert_called_once_with("Error: Please enter a valid number of trips!", title="INVALID INPUT")
        self.gui_handler.show_selection_screen.assert_called_once()
        self.gui_handler.show_train_screen.assert_not_called()
    
    def test_invalid_date_format(self):
        self.gui_handler.start_station_combobox.get.return_value = 'Norwest Station, Norwest Bvd'
        self.gui_handler.destination_combobox.get.return_value = 'Parramatta Station, Stand B3'
        self.gui_handler.cal.get_date.return_value = 'invalid_date'
        self.gui_handler.time_picker.time.return_value = (12, 30)
        self.gui_handler.no_of_trips_entry.get.return_value = '1'
        
        check_validity = self.get_check_validity_function()
        with patch('easygui.msgbox') as mock_msgbox:
            check_validity()
        
        mock_msgbox.assert_called_once_with("Error: Please enter a valid date format!", title="INVALID INPUT")
        self.gui_handler.show_selection_screen.assert_called_once()
        self.gui_handler.show_train_screen.assert_not_called()
    
    def test_past_date(self):
        self.gui_handler.start_station_combobox.get.return_value = 'Norwest Station, Norwest Bvd'
        self.gui_handler.destination_combobox.get.return_value = 'Parramatta Station, Stand B3'
        self.gui_handler.cal.get_date.return_value = '20000101'
        self.gui_handler.time_picker.time.return_value = (12, 30)
        self.gui_handler.no_of_trips_entry.get.return_value = '1'
        
        check_validity = self.get_check_validity_function()
        with patch('easygui.msgbox') as mock_msgbox:
            check_validity()
        
        mock_msgbox.assert_called_once_with("Error: Please enter a valid date!", title="INVALID INPUT")
        self.gui_handler.show_selection_screen.assert_called_once()
        self.gui_handler.show_train_screen.assert_not_called()
    
    def test_invalid_time_format(self):
        self.gui_handler.start_station_combobox.get.return_value = 'Norwest Station, Norwest Bvd'
        self.gui_handler.destination_combobox.get.return_value = 'Parramatta Station, Stand B3'
        self.gui_handler.cal.get_date.return_value = datetime.now().strftime('%Y%m%d')
        self.gui_handler.time_picker.time.return_value = ('invalid', 'time')
        self.gui_handler.no_of_trips_entry.get.return_value = '1'
        
        check_validity = self.get_check_validity_function()
        with patch('easygui.msgbox') as mock_msgbox:
            check_validity()
        
        mock_msgbox.assert_called_once_with("Error: Please enter a valid time format!", title="INVALID INPUT")
        self.gui_handler.show_selection_screen.assert_called_once()
        self.gui_handler.show_train_screen.assert_not_called()

if __name__ == '__main__':
    unittest.main()
