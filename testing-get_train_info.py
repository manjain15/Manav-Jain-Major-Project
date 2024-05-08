import unittest
from unittest.mock import patch, MagicMock
import requests
from main import get_train_info  # Adjust as needed

class TestGetTrainInfo(unittest.TestCase):
    @patch('requests.get')
    def test_get_train_info_success(self, mock_get):
        # Create a mock response with a 200 status code and sample JSON data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "journeys": [
                {
                    "legs": [
                        {
                            "origin": {
                                "departureTimeEstimated": "2024-05-07T14:30:00"
                            },
                            "destination": {
                                "arrivalTimeEstimated": "2024-05-07T16:30:00"
                            }
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        api_key = 'testapikey'
        start_station = 'Sydney Central'
        destination_station = 'Newcastle'
        departure_day = '20240507'
        departure_time = '1430'
        no_of_trips = 1
        
        train_info, trip_info_dict = get_train_info(api_key, start_station, destination_station, departure_day, departure_time, no_of_trips)
        
        self.assertEqual(len(train_info), 1)
        self.assertEqual(train_info[0], (1, '14:30', '16:30'))
        self.assertIsNotNone(trip_info_dict)
    
    @patch('requests.get')
    def test_get_train_info_error(self, mock_get):
        # Mock a non-200 response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'Not Found'
        mock_get.return_value = mock_response
        
        api_key = 'testapikey'
        start_station = 'Sydney Central'
        destination_station = 'Newcastle'
        departure_day = '20240507'
        departure_time = '1430'
        no_of_trips = 1
        
        train_info, trip_info_dict = get_train_info(api_key, start_station, destination_station, departure_day, departure_time, no_of_trips)
        
        # Check that train_info is empty and trip_info_dict is None
        self.assertEqual(len(train_info), 0)
        self.assertIsNone(trip_info_dict)

    @patch('requests.get')
    def test_get_train_info_exception(self, mock_get):
        # Simulate an exception during the request
        mock_get.side_effect = Exception("Network error")
        
        api_key = 'testapikey'
        start_station = 'Sydney Central'
        destination_station = 'Newcastle'
        departure_day = '20240507'
        departure_time = '1430'
        no_of_trips = 1
        
        train_info, trip_info_dict = get_train_info(api_key, start_station, destination_station, departure_day, departure_time, no_of_trips)
        
        # Again, train_info should be empty and trip_info_dict should be None
        self.assertEqual(len(train_info), 0)
        self.assertIsNone(trip_info_dict)

if __name__ == '__main__':
    unittest.main()
